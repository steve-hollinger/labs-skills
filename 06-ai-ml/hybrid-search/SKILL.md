---
name: implementing-hybrid-search
description: This skill teaches how to build hybrid search systems that combine vector similarity search with keyword-based (BM25) search for optimal retrieval performance. Use when writing or improving tests.
---

# Hybrid Search

## Quick Start
```python
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import numpy as np

# Vector search
model = SentenceTransformer('all-MiniLM-L6-v2')
doc_embeddings = model.encode(documents)
query_embedding = model.encode(query)
vector_scores = np.dot(doc_embeddings, query_embedding)

# Keyword search
tokenized = [doc.lower().split() for doc in documents]
bm25 = BM25Okapi(tokenized)
keyword_scores = bm25.get_scores(query.lower().split())
```

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run basic hybrid search example
make example-2  # Run score fusion comparison
make example-3  # Run production pipeline example
make test       # Run pytest
```

## Key Points
- Vector Search
- BM25 Search
- Score Fusion

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples