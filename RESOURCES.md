# RAG Resources

## Knowledge

- [Book: _Introduction to Information Retrieval_ by Manning, Raghavan & Schütze, section 6.3.1 "Dot products"](https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html)
  The standard IR textbook, free online. Use for: cosine similarity, length normalisation, and later for ranking metrics (milestone 2) and BM25 intuition (milestone 4).
- [Model card: BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5)
  The embedding model's own documentation. Use for: dimensions (384), max sequence length (512 tokens), the query instruction, and the FAQ on why scores cluster in roughly [0.6, 1].
- [Docs: Sentence-Transformers, "Semantic Textual Similarity"](https://sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html)
  Use for: the library's similarity functions (cosine is the default) and the note that dot product on normalised embeddings equals cosine similarity.
- [Docs: Sentence-Transformers quickstart](https://sbert.net/docs/quickstart.html)
  Use for: loading a model and encoding text.
- [Docs: pypdf, "Extract Text from a PDF"](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)
  Use for: extraction calls, layout mode, and why tables and reading order come out wrong.
- [Docs: Sentence-Transformers API reference, SentenceTransformer](https://sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html)
  Use for: `max_seq_length` ("Longer inputs will be truncated"), the `tokenizer` property, `encode` parameters.
- [README: pgvector](https://github.com/pgvector/pgvector)
  Use for: distance operators, "for cosine similarity, use 1 - cosine distance", index types (milestones 1, 4, 5).
- Listed in CURRICULUM.md, not yet read for a lesson: Anthropic "Contextual Retrieval"; Cormack et al. "Reciprocal Rank Fusion"; Sentence-Transformers "Retrieve & Re-Rank"; Ollama API docs; FastAPI docs on lifespan events and request bodies.

## Wisdom (Communities)

- [Hugging Face forums](https://discuss.huggingface.co/)
  Use for: questions about sentence-transformers and embedding model behaviour.
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/)
  Use for: running local models, Ollama hardware questions, sanity-checking model choices.

## Gaps

- No vetted community yet for RAG system design and evaluation specifically. Neither community above has been checked for moderation quality.
- No primary source chosen yet for context window budgeting (lesson 3 of milestone 1).
