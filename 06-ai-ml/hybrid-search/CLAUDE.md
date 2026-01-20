# CLAUDE.md - Hybrid Search

This skill teaches how to build hybrid search systems that combine vector similarity search with keyword-based (BM25) search for optimal retrieval performance.

## Key Concepts

- **Vector Search**: Uses embeddings to find semantically similar documents based on meaning
- **BM25 Search**: Traditional keyword search using term frequency-inverse document frequency
- **Score Fusion**: Combining results from multiple search methods into a single ranked list
- **Reciprocal Rank Fusion (RRF)**: Rank-based fusion that's robust to score scale differences
- **Weighted Combination**: Direct score combination with tunable alpha parameter

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run basic hybrid search example
make example-2  # Run score fusion comparison
make example-3  # Run production pipeline example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
hybrid-search/
├── src/hybrid_search/
│   ├── __init__.py
│   ├── vector_search.py      # Vector similarity implementation
│   ├── keyword_search.py     # BM25 implementation
│   ├── fusion.py             # Score fusion strategies
│   └── examples/
│       ├── example_1.py      # Basic hybrid search
│       ├── example_2.py      # Fusion strategies comparison
│       └── example_3.py      # Production pipeline
├── exercises/
│   ├── exercise_1.py         # Implement BM25
│   ├── exercise_2.py         # Build weighted fusion
│   ├── exercise_3.py         # FAQ search system
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Hybrid Search
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

### Pattern 2: Reciprocal Rank Fusion
```python
def reciprocal_rank_fusion(rankings: list[list[int]], k: int = 60) -> list[tuple[int, float]]:
    """Combine multiple rankings using RRF."""
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

### Pattern 3: Weighted Score Fusion
```python
def weighted_fusion(
    vector_scores: np.ndarray,
    keyword_scores: np.ndarray,
    alpha: float = 0.5
) -> np.ndarray:
    """Combine scores with configurable weight."""
    # Normalize to [0, 1]
    v_norm = (vector_scores - vector_scores.min()) / (vector_scores.max() - vector_scores.min() + 1e-10)
    k_norm = (keyword_scores - keyword_scores.min()) / (keyword_scores.max() - keyword_scores.min() + 1e-10)
    return alpha * v_norm + (1 - alpha) * k_norm
```

## Common Mistakes

1. **Not normalizing scores before fusion**
   - Why it happens: Vector similarity and BM25 produce scores on different scales
   - How to fix it: Always normalize scores to [0,1] or use rank-based fusion (RRF)

2. **Using a fixed alpha for all queries**
   - Why it happens: Assuming one alpha works for all query types
   - How to fix it: Consider query-dependent alpha or use RRF which is more robust

3. **Forgetting to handle documents missing from one ranker**
   - Why it happens: A doc might match semantically but not have keyword matches
   - How to fix it: Use default scores (0) for missing documents

4. **Not tokenizing consistently**
   - Why it happens: Using different tokenization for indexing vs querying
   - How to fix it: Create a shared tokenizer function used everywhere

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make example-1` for a basic working example.

### "What alpha value should I use?"
Start with 0.5 for balanced results. Use 0.7+ if semantic matching is more important, 0.3 or lower if exact keyword matches matter more. Consider RRF if unsure.

### "Why are my results poor?"
Check:
1. Is the embedding model appropriate for your domain?
2. Are documents and queries tokenized consistently?
3. Is the alpha value appropriate for your query types?
4. Are you normalizing scores correctly?

### "How do I improve performance?"
- Cache embeddings (they're expensive to compute)
- Use approximate nearest neighbor (ANN) for large datasets
- Batch queries when possible
- Consider a reranker for top-k results

### "Should I use RRF or weighted fusion?"
- Use **RRF** when: you don't want to tune hyperparameters, score distributions vary
- Use **weighted** when: you have domain knowledge about the right balance, want more control

## Testing Notes

- Tests use pytest with markers
- Run specific tests: `pytest -k "test_name"`
- Some tests require the sentence-transformers model download (first run will be slow)
- Tests mock expensive operations where possible

## Dependencies

Key dependencies in pyproject.toml:
- sentence-transformers: For generating embeddings
- rank-bm25: For BM25 keyword search
- numpy: For efficient array operations
- scikit-learn: For cosine similarity and normalization utilities
