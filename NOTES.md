# Teaching notes

- **Snippets yes, building it out no** (rule changed by the learner on 2026-10-09; CURRICULUM.md "For AI assistants" updated). Show code snippets and small examples in chat and in lessons when they clarify a technique. Do not write the pipeline's files or finished implementations for them. Lesson 0001 was written under the old no-code rule and has no snippets.
- Mission in MISSION.md was drafted from one multiple-choice answer ("Career move to AI eng") on 2026-10-09. Confirm the wording with the learner.
- Corpus (2026-10-09): learner is leaning towards synthetic invoices instead of a code repo, and asked the assistant to write `tests/generate_invoices.py` (PDF invoices into `data/invoices/`, via dev dependency `fpdf2`; the learner asked for PDF specifically, so lesson 2 on ingestion must cover PDF text extraction and what it does to tables). My reading: test-data tooling is outside the no-code rule, pipeline code is still theirs to write. Not yet confirmed as the final corpus. Consequences to raise when relevant: milestone 3's syntax-aware code chunker has nothing to split, and exact lookups (totals, invoice numbers) are where pure vector search is weakest, which makes milestone 4 more interesting.
- Hardware question was answered with "could use free remote model" instead of naming hardware. The curriculum says local Ollama. Settle this before the generation lesson: find out the actual machine, and check current Ollama docs for hosted options that keep the same HTTP API.
- Project uses `uv` (uv.lock present), Python >= 3.14.

## Lesson plan for milestone 1

1. Cosine similarity (0001, written; hands-on task and quiz NOT yet done by the learner as of 2026-10-09, they went straight to building)
2. PDF to chunks: pypdf extraction, token counting, fixed 500-token chunks (0002, written)
3. Embed and store in pgvector, completing `ingest_file`; then the worker loop
4. Retrieve then generate: top 5, prompt assembly, context window budget, Ollama API
5. `POST /query` in FastAPI, loading the model once with lifespan; then the failure hunt (bridge to milestone 2)

## State of the learner's build (2026-10-09)

- `compose.yaml` runs Postgres (pgvector pg16), db `rag`, password in `.env`, loaded with python-dotenv (their choice over pydantic-settings).
- `main.py` has a working `POST /ingest` that saves the PDF to `data/uploads` and inserts a row in `ingest_jobs`. They chose the job-queue design (API + separate worker, Postgres table as queue) over the curriculum's plain script. Worker not written yet.
- Measured: sample invoice is 186 words / 358 tokens, so most invoices fit one 500-token chunk. Use this in milestone 3.
