from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
import os

from pgvector.psycopg import register_vector

load_dotenv()

DATABASE_CONNECTION = (f"postgresql://postgres:{os.environ["POSTGRES_PASSWORD"]}@127.0.0.1:5432/rag")

pool = ConnectionPool(
    DATABASE_CONNECTION,
    open=False
)

def get_conn() -> ConnectionPool:
    with pool.connection() as conn:
        yield conn

async def insert_ingest_job(conn, path: str):
    try:
        return conn.execute(
            "INSERT INTO ingest_jobs(path) VALUES (%s) RETURNING id",
            (str(path),)
        ).fetchone()
    except:
        print("errror occured during job ingest")

async def get_job():
    with get_conn as conn:
        rows = conn.execute("SELECT * FROM ingest_jobs")
        print("got job")
        print(rows[0])
        return rows[0]

def insert_chunks(conn, job_id: int, texts: list[str], vectors):
    register_vector(conn)

    rows = [
        (job_id, i, text, vector)
        for i, (text, vector) in enumerate(zip(texts, vectors))
    ]

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO chunks (job_id, chunk_index, content, embedding)
            VALUES (%s, %s, %s, %s)
            """,
            rows,
        )