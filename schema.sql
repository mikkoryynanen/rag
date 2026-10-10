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
