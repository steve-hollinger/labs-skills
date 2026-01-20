# Common Patterns

## Overview

This document covers common patterns and best practices for building hybrid search systems.

## Pattern 1: Basic Hybrid Search Pipeline

### When to Use

When you need a simple, working hybrid search with minimal configuration.

### Implementation

```python
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import numpy as np


@dataclass
class SearchResult:
    doc_id: int
    document: str
    score: float


class BasicHybridSearcher:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.documents: list[str] = []
        self.doc_embeddings: np.ndarray | None = None
        self.bm25: BM25Okapi | None = None

    def index(self, documents: list[str]) -> None:
        """Index documents for both vector and keyword search."""
        self.documents = documents

        # Vector index
        self.doc_embeddings = self.model.encode(documents)

        # BM25 index
        tokenized = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)

    def search(self, query: str, top_k: int = 10, alpha: float = 0.5) -> list[SearchResult]:
        """Search with hybrid scoring."""
        if not self.documents or self.doc_embeddings is None or self.bm25 is None:
            return []

        # Vector scores
        query_embedding = self.model.encode(query)
        vector_scores = np.dot(self.doc_embeddings, query_embedding)

        # BM25 scores
        keyword_scores = self.bm25.get_scores(query.lower().split())

        # Normalize and combine
        v_norm = self._normalize(vector_scores)
        k_norm = self._normalize(keyword_scores)
        hybrid_scores = alpha * v_norm + (1 - alpha) * k_norm

        # Get top-k
        top_indices = np.argsort(hybrid_scores)[::-1][:top_k]

        return [
            SearchResult(
                doc_id=int(idx),
                document=self.documents[idx],
                score=float(hybrid_scores[idx])
            )
            for idx in top_indices
        ]

    def _normalize(self, scores: np.ndarray) -> np.ndarray:
        min_s, max_s = scores.min(), scores.max()
        if max_s - min_s < 1e-10:
            return np.zeros_like(scores)
        return (scores - min_s) / (max_s - min_s)
```

### Example

```python
searcher = BasicHybridSearcher()
searcher.index([
    "Introduction to machine learning with Python",
    "Deep learning neural networks explained",
    "Python programming basics for beginners",
])

results = searcher.search("python ML tutorial")
for r in results:
    print(f"{r.score:.3f}: {r.document}")
```

### Pitfalls to Avoid

- Not handling empty document lists
- Forgetting to re-index when documents change
- Using inconsistent tokenization

## Pattern 2: Reciprocal Rank Fusion (RRF)

### When to Use

When you want robust fusion without tuning alpha, or when combining more than two rankers.

### Implementation

```python
from collections import defaultdict


def reciprocal_rank_fusion(
    *rankings: list[int],
    k: int = 60
) -> list[tuple[int, float]]:
    """
    Combine multiple rankings using RRF.

    Args:
        rankings: Variable number of ranked document ID lists
        k: Smoothing constant (higher = more weight to lower ranks)

    Returns:
        List of (doc_id, score) sorted by score descending
    """
    scores: dict[int, float] = defaultdict(float)

    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            scores[doc_id] += 1.0 / (k + rank + 1)

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


class RRFHybridSearcher:
    """Hybrid searcher using RRF fusion."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", rrf_k: int = 60):
        self.model = SentenceTransformer(model_name)
        self.rrf_k = rrf_k
        self.documents: list[str] = []
        self.doc_embeddings: np.ndarray | None = None
        self.bm25: BM25Okapi | None = None

    def index(self, documents: list[str]) -> None:
        self.documents = documents
        self.doc_embeddings = self.model.encode(documents)
        tokenized = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)

    def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        if not self.documents:
            return []

        # Get vector ranking
        query_embedding = self.model.encode(query)
        vector_scores = np.dot(self.doc_embeddings, query_embedding)
        vector_ranking = np.argsort(vector_scores)[::-1].tolist()

        # Get keyword ranking
        keyword_scores = self.bm25.get_scores(query.lower().split())
        keyword_ranking = np.argsort(keyword_scores)[::-1].tolist()

        # RRF fusion
        fused = reciprocal_rank_fusion(vector_ranking, keyword_ranking, k=self.rrf_k)

        return [
            SearchResult(doc_id=doc_id, document=self.documents[doc_id], score=score)
            for doc_id, score in fused[:top_k]
        ]
```

### Example

```python
searcher = RRFHybridSearcher(rrf_k=60)
searcher.index(documents)
results = searcher.search("data science python")
```

### Pitfalls to Avoid

- Using k=0 (causes division issues)
- Not including all documents in rankings

## Pattern 3: Query-Dependent Alpha

### When to Use

When different query types benefit from different fusion weights.

### Implementation

```python
import re


def estimate_query_alpha(query: str) -> float:
    """
    Estimate optimal alpha based on query characteristics.

    Returns higher alpha (more vector) for conceptual queries,
    lower alpha (more keyword) for specific/technical queries.
    """
    query_lower = query.lower()
    words = query_lower.split()

    # Heuristics for query type
    has_code_terms = bool(re.search(r'[A-Z]{2,}|v\d+|\d+\.\d+', query))
    has_question_words = any(w in words for w in ['how', 'what', 'why', 'when', 'explain'])
    is_short = len(words) <= 2
    has_quotes = '"' in query

    # Base alpha
    alpha = 0.5

    # Adjust based on heuristics
    if has_code_terms or has_quotes:
        alpha -= 0.2  # More keyword weight for specific terms

    if has_question_words:
        alpha += 0.1  # More semantic for questions

    if is_short and not has_question_words:
        alpha -= 0.1  # Short specific queries need keyword

    # Clamp to valid range
    return max(0.1, min(0.9, alpha))


class AdaptiveHybridSearcher(BasicHybridSearcher):
    """Hybrid searcher with query-dependent alpha."""

    def search(self, query: str, top_k: int = 10, alpha: float | None = None) -> list[SearchResult]:
        if alpha is None:
            alpha = estimate_query_alpha(query)
        return super().search(query, top_k=top_k, alpha=alpha)
```

### Example

```python
searcher = AdaptiveHybridSearcher()
searcher.index(documents)

# Conceptual query -> higher alpha (more vector)
results1 = searcher.search("how do neural networks learn")

# Specific query -> lower alpha (more keyword)
results2 = searcher.search("tensorflow v2.15 API")
```

### Pitfalls to Avoid

- Over-engineering the heuristics
- Not validating against real user queries
- Forgetting to clamp alpha to valid range

## Pattern 4: Cached Embeddings

### When to Use

When you have a stable document corpus and want faster queries.

### Implementation

```python
import hashlib
import json
from pathlib import Path


class CachedHybridSearcher:
    """Hybrid searcher with embedding caching."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        cache_dir: Path | None = None
    ):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.cache_dir = cache_dir or Path(".embedding_cache")
        self.cache_dir.mkdir(exist_ok=True)

    def _cache_key(self, documents: list[str]) -> str:
        """Generate cache key from documents and model."""
        content = json.dumps(documents, sort_keys=True) + self.model_name
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def index(self, documents: list[str]) -> None:
        self.documents = documents
        cache_key = self._cache_key(documents)
        cache_file = self.cache_dir / f"{cache_key}.npy"

        if cache_file.exists():
            self.doc_embeddings = np.load(cache_file)
            print(f"Loaded embeddings from cache: {cache_file}")
        else:
            self.doc_embeddings = self.model.encode(documents)
            np.save(cache_file, self.doc_embeddings)
            print(f"Cached embeddings to: {cache_file}")

        tokenized = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)
```

### Pitfalls to Avoid

- Not invalidating cache when model changes
- Caching query embeddings (usually not worth it)
- Running out of disk space with many caches

## Anti-Patterns

### Anti-Pattern 1: Combining Raw Scores Directly

Description: Adding vector similarity (0-1) and BM25 scores (unbounded) without normalization.

```python
# BAD: Scores are on different scales
final_score = vector_score + bm25_score  # BM25 dominates!
```

### Better Approach

```python
# GOOD: Normalize first
final_score = alpha * normalize(vector_score) + (1-alpha) * normalize(bm25_score)
```

### Anti-Pattern 2: One-Size-Fits-All Alpha

Description: Using the same alpha for all queries regardless of type.

```python
# BAD: Fixed alpha
results = search(query, alpha=0.5)  # Works poorly for some queries
```

### Better Approach

```python
# GOOD: Adaptive or RRF
alpha = estimate_query_alpha(query)
results = search(query, alpha=alpha)

# OR use RRF which is robust to query variation
results = rrf_search(query)
```

### Anti-Pattern 3: Ignoring Empty Results

Description: Not handling when one ranker returns no results.

```python
# BAD: Crashes or gives wrong results
vector_ranking = get_vector_results(query)  # Might be empty
keyword_ranking = get_keyword_results(query)  # Might be empty
fused = rrf(vector_ranking, keyword_ranking)  # What if one is empty?
```

### Better Approach

```python
# GOOD: Handle missing results gracefully
vector_ranking = get_vector_results(query) or list(range(len(documents)))
keyword_ranking = get_keyword_results(query) or list(range(len(documents)))
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Quick prototype | Basic Hybrid Search |
| Production system | RRF or Adaptive |
| Large corpus, stable docs | Cached Embeddings |
| Varied query types | Query-Dependent Alpha |
| Multiple retrieval sources | RRF (extends to N rankers) |
| Need interpretable scores | Weighted fusion |
