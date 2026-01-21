# Core Concepts

## Overview

Hybrid search combines two complementary search paradigms: vector similarity search (semantic) and keyword search (lexical). Understanding when and how to use each, and how to combine them effectively, is crucial for building high-quality search systems.

## Concept 1: Vector Similarity Search

### What It Is

Vector search represents text as dense numerical vectors (embeddings) in a high-dimensional space. Documents with similar meanings cluster together, enabling semantic search that understands concepts rather than just matching keywords.

### Why It Matters

- Finds conceptually related content even without keyword overlap
- Handles synonyms automatically ("car" matches "automobile")
- Works across paraphrases ("How to cook pasta" matches "pasta preparation guide")
- Enables cross-lingual search with multilingual models

### How It Works

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Load a pre-trained embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Documents to search
documents = [
    "Python is a programming language",
    "Machine learning uses algorithms to learn from data",
    "Cats are popular pets",
]

# Generate embeddings (dense vectors)
doc_embeddings = model.encode(documents)
print(f"Embedding shape: {doc_embeddings.shape}")  # (3, 384)

# Search with a query
query = "artificial intelligence"
query_embedding = model.encode(query)

# Compute cosine similarity
similarities = np.dot(doc_embeddings, query_embedding) / (
    np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(query_embedding)
)

# "Machine learning..." will score highest despite no keyword overlap
```

### Key Embedding Models

| Model | Dimensions | Speed | Quality | Use Case |
|-------|------------|-------|---------|----------|
| all-MiniLM-L6-v2 | 384 | Fast | Good | General purpose |
| all-mpnet-base-v2 | 768 | Medium | Better | Higher quality needs |
| e5-large-v2 | 1024 | Slow | Best | Maximum quality |

## Concept 2: BM25 Keyword Search

### What It Is

BM25 (Best Matching 25) is a ranking function used by search engines. It scores documents based on query term frequency, document length, and how rare the terms are across the corpus.

### Why It Matters

- Excellent for exact matches (product IDs, names, codes)
- Handles rare terms and technical jargon well
- No training required - works out of the box
- Computationally efficient
- Users often know exactly what they're looking for

### How It Works

```python
from rank_bm25 import BM25Okapi

# Documents to search
documents = [
    "Python is a programming language",
    "Machine learning uses algorithms to learn from data",
    "Python machine learning tutorial with scikit-learn",
]

# Tokenize documents (simple whitespace tokenization)
tokenized_docs = [doc.lower().split() for doc in documents]

# Create BM25 index
bm25 = BM25Okapi(tokenized_docs)

# Search
query = "python machine learning"
tokenized_query = query.lower().split()
scores = bm25.get_scores(tokenized_query)

# Document 3 will score highest (has both "python" and "machine learning")
print(f"BM25 Scores: {scores}")
```

### BM25 Formula (Simplified)

```
score(D, Q) = sum over query terms t:
    IDF(t) * (tf(t,D) * (k1 + 1)) / (tf(t,D) + k1 * (1 - b + b * |D|/avgdl))
```

Where:
- `tf(t,D)` = term frequency of t in document D
- `IDF(t)` = inverse document frequency (rarer terms score higher)
- `|D|` = document length
- `avgdl` = average document length
- `k1` = term frequency saturation parameter (typically 1.2-2.0)
- `b` = length normalization parameter (typically 0.75)

## Concept 3: Score Fusion Strategies

### What It Is

Score fusion combines results from multiple retrieval systems into a single ranked list. Since vector and keyword search produce scores on different scales, careful fusion is required.

### Why It Matters

- Neither search method is universally better
- Different queries benefit from different approaches
- Proper fusion captures the strengths of both methods
- Wrong fusion can make results worse than either method alone

### How It Works

#### Reciprocal Rank Fusion (RRF)

RRF combines rankings (not scores) using the formula:

```python
def reciprocal_rank_fusion(
    rankings: list[list[int]],
    k: int = 60
) -> dict[int, float]:
    """
    Combine multiple rankings using RRF.

    Args:
        rankings: List of ranked document ID lists
        k: Smoothing constant (default 60)

    Returns:
        Dictionary mapping doc_id to RRF score
    """
    rrf_scores: dict[int, float] = {}

    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            # RRF formula: 1 / (k + rank)
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (k + rank + 1)

    return rrf_scores

# Example
vector_ranking = [2, 0, 1]  # Doc 2 is best by vector search
keyword_ranking = [1, 2, 0]  # Doc 1 is best by keyword search

rrf_scores = reciprocal_rank_fusion([vector_ranking, keyword_ranking])
# Doc 2: 1/61 + 1/62 = 0.0326
# Doc 1: 1/63 + 1/61 = 0.0323
# Doc 0: 1/62 + 1/63 = 0.0320
```

#### Weighted Linear Combination

```python
import numpy as np

def weighted_fusion(
    vector_scores: np.ndarray,
    keyword_scores: np.ndarray,
    alpha: float = 0.5
) -> np.ndarray:
    """
    Combine normalized scores with weight alpha.

    alpha=1.0 -> pure vector search
    alpha=0.0 -> pure keyword search
    alpha=0.5 -> equal weight
    """
    # Min-max normalization to [0, 1]
    def normalize(scores: np.ndarray) -> np.ndarray:
        min_s, max_s = scores.min(), scores.max()
        if max_s - min_s < 1e-10:
            return np.zeros_like(scores)
        return (scores - min_s) / (max_s - min_s)

    v_norm = normalize(vector_scores)
    k_norm = normalize(keyword_scores)

    return alpha * v_norm + (1 - alpha) * k_norm
```

### Choosing a Fusion Strategy

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Unknown query distribution | RRF | Robust, no tuning needed |
| Domain expertise available | Weighted | Can optimize alpha |
| Score distributions vary | RRF | Uses ranks, not scores |
| Need interpretable scores | Weighted | Direct score combination |
| Multi-modal search (text + image) | RRF | Handles different score scales |

## Summary

Key takeaways from these concepts:

1. **Vector search** understands meaning but may miss exact matches
2. **BM25** excels at exact matches but misses semantic similarity
3. **Hybrid search** combines both for better overall retrieval
4. **RRF** is the safest fusion choice when you can't tune
5. **Weighted fusion** gives more control but needs tuning
6. Always **normalize scores** before weighted combination
7. Consider **query-dependent fusion** for best results
