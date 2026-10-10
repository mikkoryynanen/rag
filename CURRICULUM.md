# RAG Curriculum: Context-Aware Enterprise Knowledge Base

One project, built in seven milestones. Each milestone adds one technique and measures whether it helped.
Assumes strong software engineering background and no prior ML. Roughly 25-35 hours in total.

## For AI assistants

Your job is to instruct, not to build the project. The learner builds the pipeline themselves.

- Explain concepts, point to the relevant docs, and ask questions that lead to the answer.
- Show code snippets and small examples when they make a technique clearer.
- Do not build things out for the learner: no creating or editing the project's pipeline files with finished implementations.
- Review code the learner wrote: say what is wrong and why. A snippet that shows the idea is fine.

## Stack

| Concern | Choice | Why |
|---|---|---|
| Language | Python | Where the ecosystem lives |
| Store | Postgres + pgvector (Docker) | Vectors, keyword search and metadata in one database |
| Embeddings | `sentence-transformers` (`bge-small-en-v1.5`), local | Free, and fast enough to re-embed often |
| Keyword search | Postgres full-text search (`tsvector`) | No second system to run |
| Reranker | `sentence-transformers` `CrossEncoder` (`BAAI/bge-reranker-base`), local | Free; same library as the embeddings |
| Generation | Ollama (`llama3.1:8b`, or `llama3.2:3b` without a GPU) | Free, local, plain HTTP API |
| Serving | FastAPI | One `POST /query` endpoint, extended in later milestones |

Every model runs locally, so there are no API keys and no usage costs.

No LangChain or LlamaIndex. Writing the pipeline by hand is the point; it is about 300 lines.

**Corpus:** pick one open-source repo you already know well (code plus its docs). You need to be able to tell a good answer from a bad one without looking it up.

## Milestones

### 1. Naive RAG end to end (3-4 h)
- **Build:** load files, split into fixed 500-token chunks, embed, store in pgvector, retrieve top 5 by cosine similarity, pass them to the Ollama model with the question. Expose it as `POST /query` in FastAPI, with ingestion as a separate script.
- **Learn:** embeddings, cosine similarity, the retrieve-then-generate loop, context window budgeting, loading models once at startup instead of per request.
- **Done when:** `curl` to `/query` answers a question about your corpus, and you have found three questions it gets wrong.

### 2. Evaluation harness (3-4 h)
- **Build:** 30-40 questions, each labelled with the file or section that answers it. A script that reports recall@k and MRR for retrieval.
- **Learn:** retrieval quality and answer quality are separate problems, and retrieval is the one you can measure cheaply.
- **Done when:** one command prints a baseline score. Every later milestone reruns it.

Do this second, not last. Without it, every later change is a guess.

### 3. Chunking strategies (4-5 h)
- **Build:** three chunkers behind one function signature: fixed size with overlap, structure-aware (Markdown headings), and syntax-aware for code (split on functions and classes with `tree-sitter` or `ast`).
- **Learn:** chunk size versus precision, overlap, why code and prose need different splitting, prepending the parent heading or file path to each chunk.
- **Done when:** you have a table of eval scores per chunker and can explain the winner.

### 4. Hybrid search (4-5 h)
- **Build:** add a `tsvector` column and GIN index. Run keyword and vector queries separately, then merge with Reciprocal Rank Fusion.
- **Learn:** where semantic search fails (exact identifiers, error codes, version numbers) and where keyword search fails (paraphrase). BM25 conceptually. HNSW versus IVFFlat indexes.
- **Done when:** eval shows hybrid beating both single methods, and you can name the query types each one wins.

### 5. Metadata filtering (2-3 h)
- **Build:** store path, language, doc type and last-modified per chunk. Accept filters as optional fields on the `/query` request body (`lang`, `path_prefix`), validated by the Pydantic model.
- **Learn:** pre-filtering versus post-filtering, and how a filter interacts with an approximate index (a selective filter can leave you with fewer than k results).
- **Done when:** filtered queries return correct results, and you have seen the under-filled result problem for yourself.

### 6. Reranking (3-4 h)
- **Build:** retrieve the top 50 with hybrid search, rerank with the local cross-encoder, keep the top 5.
- **Learn:** bi-encoders versus cross-encoders, why the two-stage design exists, the latency of the second stage on your own hardware.
- **Done when:** eval shows the gain in recall@5, and you have measured the added latency per query.

### 7. Citations and grounding (4-5 h)
- **Build:** number each chunk in the prompt, require the answer to cite those numbers, map them back to file and line range. Return them in the response as `{answer, citations: [{file, start_line, end_line, snippet}]}`. Verify that each cited chunk exists and refuse to answer when retrieval scores are low.
- **Learn:** grounding prompts, the "I don't know" path, checking faithfulness (does the cited chunk support the claim). Small local models skip or invent citation numbers more often than hosted ones, so the verification step matters here.
- **Done when:** every claim in an answer links to a source, and out-of-corpus questions get a refusal instead of an invention.

## Stretch goals

Pick these up only if the eval points at them.

- Query rewriting or HyDE, when user questions are phrased unlike the documents.
- Contextual chunk descriptions (an LLM-written sentence of context per chunk), when chunks lose meaning out of their file.
- Incremental re-indexing, by hashing chunks and embedding only what changed.
- LLM-as-judge answer scoring, to evaluate generation as well as retrieval.
- Streaming responses from `/query`, when local generation feels slow.
- Swap pgvector for Qdrant, to see what a dedicated vector database changes.

## Reading, in the order you will need it

1. pgvector README (milestones 1, 4, 5).
2. Anthropic, "Contextual Retrieval" (milestones 3, 4, 6 in one article).
3. Cormack et al., "Reciprocal Rank Fusion" (milestone 4; two pages).
4. Sentence-Transformers documentation, "Retrieve & Re-Rank" (milestone 6).
5. Ollama API documentation (milestones 1, 7).
6. FastAPI documentation on lifespan events and request bodies (milestones 1, 5).
