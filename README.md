# RAG

## Setup on a new machine

1. Copy `.env.example` to `.env` and set `POSTGRES_PASSWORD`.
2. Start Postgres:

   ```sh
   docker compose up -d
   ```

3. Create the tables. The database starts empty, so this has to be done once per machine (and again after `docker compose down -v`, which deletes the data volume):

   ```sh
   docker exec -i rag_postgres psql -U postgres -d rag < schema.sql
   ```

   This creates `ingest_jobs`, the queue that `POST /ingest` writes to and the worker reads from. Without it the app starts but the worker fails with `relation "ingest_jobs" does not exist`. The script is safe to re-run.

4. Create the upload directory (`POST /ingest` saves PDFs here and does not create it itself):

   ```sh
   mkdir -p data/uploads
   ```

5. Install dependencies and run the API:

   ```sh
   uv sync
   uv run fastapi dev main.py
   ```
