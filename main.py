from contextlib import asynccontextmanager
from typing import Annotated
import shutil
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, UploadFile, Depends
from src.services.database.database import pool, get_conn, insert_ingest_job, insert_chunks
from psycopg import Connection
import threading
from src.chunker.chunker import chunk_document

from sentence_transformers import SentenceTransformer

UPLOAD_DIR = Path("data/uploads")
SCHEMA_FILE = Path("schema.sql")

stop = threading.Event()

def init_db():
    with pool.connection() as conn:
        conn.execute(SCHEMA_FILE.read_text())

@asynccontextmanager
async def lifespan(app):
    pool.open()
    init_db()
    worker = threading.Thread(target=worker_loop)
    worker.start()
    yield
    stop.set()
    worker.join()
    pool.close()

app = FastAPI(lifespan=lifespan)

Db = Annotated[Connection, Depends(get_conn)]

# TODO seperate to its own process
def worker_loop():
    while not stop.is_set():
        with pool.connection() as conn:
            job = conn.execute("""
                SELECT id, path FROM ingest_jobs
                WHERE status = 0
                ORDER BY id
                FOR UPDATE SKIP LOCKED
                LIMIT 1
            """).fetchone()

            if job is None:
                print("no jobs")
                stop.wait(2)
            else:
                print(job)

                job_id, path = job

                docs = chunk_document(path)
                texts = [chunk.text for doc in docs for chunk in doc.chunks]

                model = SentenceTransformer("BAAI/bge-small-en-v1.5")
                vectors = model.encode(texts, normalize_embeddings=True)

                insert_chunks(conn, job_id, texts, vectors)

                conn.execute(f"UPDATE ingest_jobs SET status=1 WHERE id={job_id}")

        stop.wait(2)

@app.post("/ingest", status_code=202)
async def ingest(file: UploadFile, conn: Db):
    path = UPLOAD_DIR / f"{uuid4()}.pdf"
    with path.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    # with psycopgas conn:
    row = await insert_ingest_job(conn, path)

    return { "job_id", row[0] }