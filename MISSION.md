# Mission: Retrieval-Augmented Generation (RAG)

## Why
Move into an AI engineering role. A hand-built, measured RAG system over a real codebase is the proof of skill: something to show, and something to talk through in depth in an interview.

## Success looks like
- A working context-aware knowledge base over an open-source repo, built by hand through the seven milestones in [CURRICULUM.md](./CURRICULUM.md), every line written by the learner.
- An eval table showing what each technique (chunking, hybrid search, reranking) gained or cost, with an explanation for each number.
- Able to explain every stage of the pipeline, and its failure modes, to an interviewer without notes.

## Constraints
- Strong software engineering background, no prior ML.
- Roughly 25-35 hours in total.
- The assistant instructs, reviews and may show code snippets, but does not build the pipeline out for the learner.
- Free tooling only. Stack is fixed by the curriculum (Python, Postgres + pgvector, sentence-transformers, Ollama, FastAPI). No LangChain or LlamaIndex.

## Out of scope
- Training or fine-tuning models.
- Agent frameworks and orchestration libraries.
- Stretch goals, unless the eval points at them.
