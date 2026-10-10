from contextlib import asynccontextmanager
from typing import Annotated
import shutil
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, UploadFile, Depends
from src.chunker.services.database.database import pool, get_conn, insert_ingest_job
from psycopg import Connection
import threading
from src.chunker.chunker import process_docs

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

                process_docs(path)

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