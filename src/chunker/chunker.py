from chonkie import TokenChunker, Pipeline
from pgvector import psycopg
from pypdf import PdfReader
from pathlib import Path
from src.chunker.services.database.database import get_job

UPLOAD_DIR = Path("data/uploads")

def process_docs(path: str):
    pipe = Pipeline().chunk_with("recursive")

    # with psycopg.connect(DATABASE_CONNECTION) as conn:
    #     row = conn.execute(
    #         "INSERT INTO ingest_jobs(path) VALUES (%s) RETURNING id",
    #         (str(path),)
    #     ).fetchone()

    reader = PdfReader(path)
    str = [page.extract_text() for page in reader.pages]

    docs = pipe.run(texts=str)

    print(docs)
    return docs
