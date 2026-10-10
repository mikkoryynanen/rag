from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
import os

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