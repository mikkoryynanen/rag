-- Database schema for the RAG project. Safe to re-run.
--   docker exec -i rag_postgres psql -U postgres -d rag < schema.sql

-- Queue of uploaded PDFs waiting to be chunked by the worker in main.py.
-- status: 0 = pending, 1 = done
CREATE TABLE IF NOT EXISTS ingest_jobs (
    id         BIGSERIAL PRIMARY KEY,
    path       TEXT NOT NULL,
    status     SMALLINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    id          BIGSERIAL PRIMARY KEY,
    job_id      BIGINT NOT NULL REFERENCES ingest_jobs(id),
    chunk_index INT NOT NULL,
    content     TEXT NOT NULL,
    embedding   vector(384) NOT NULL
);