# Hybrid Search (Vector + Keyword)

Learn how to build powerful search systems that combine the semantic understanding of vector similarity search with the precision of traditional keyword-based (BM25) search.

## Learning Objectives

After completing this skill, you will be able to:
- Understand the strengths and weaknesses of vector vs keyword search
- Implement vector similarity search using sentence-transformers
- Implement BM25 keyword search
- Combine results using score fusion strategies (RRF, weighted, etc.)
- Choose the right fusion strategy for your use case
- Build a complete hybrid search pipeline

## Prerequisites

- Python 3.11+
- UV package manager
- Basic understanding of embeddings and vector spaces
- Familiarity with text search concepts

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### Why Hybrid Search?

**Vector search** excels at:
- Semantic similarity (understanding meaning)
- Finding conceptually related content
- Handling synonyms and paraphrases
- Cross-lingual search

**Keyword search (BM25)** excels at:
- Exact matches (product IDs, names, codes)
- Rare terms and technical jargon
- Acronyms and abbreviations
- When users know exactly what they want

**Hybrid search** combines both to get the best of both worlds.

```python
from hybrid_search import HybridSearcher

searcher = HybridSearcher(
    embedding_model="all-MiniLM-L6-v2",
    fusion_method="rrf"  # Reciprocal Rank Fusion
)

# Index documents
searcher.index(documents)

# Search combines vector + keyword results
results = searcher.search("machine learning tutorial python")
```

### Score Fusion Strategies

#### Reciprocal Rank Fusion (RRF)
The most popular method - combines ranks rather than raw scores.

```python
# RRF formula: score = sum(1 / (k + rank))
# Default k=60 works well in practice
```

#### Weighted Combination
Directly combines normalized scores with configurable weights.

```python
# alpha controls the balance
# alpha=0.5 -> equal weight
# alpha=0.7 -> more vector search
# alpha=0.3 -> more keyword search
```

## Examples

### Example 1: Basic Hybrid Search

Demonstrates setting up a simple hybrid search system with default settings.

```bash
make example-1
```

### Example 2: Score Fusion Strategies

Compare different fusion methods (RRF, weighted, max-of) on the same dataset.

```bash
make example-2
```

### Example 3: Production-Ready Pipeline

Build a complete hybrid search pipeline with batching, caching, and reranking.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Implement basic BM25 search from scratch
2. **Exercise 2**: Build a weighted fusion function
3. **Exercise 3**: Create a hybrid search system for a FAQ database

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Using Raw Scores for Fusion
Vector similarity scores (cosine) and BM25 scores are on different scales. Always normalize before combining.

```python
# Wrong: Directly adding scores
final_score = vector_score + bm25_score

# Right: Normalize first
final_score = alpha * normalize(vector_score) + (1-alpha) * normalize(bm25_score)
```

### Ignoring Query Characteristics
Different queries benefit from different alpha values. Short queries with specific terms often need more keyword weight.

### Not Handling Missing Results
A document might appear in vector results but not keyword results (or vice versa). Handle this gracefully.

## Further Reading

- [Official sentence-transformers Documentation](https://www.sbert.net/)
- [BM25 Explained](https://en.wikipedia.org/wiki/Okapi_BM25)
- [Reciprocal Rank Fusion Paper](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
- Related skills in this repository:
  - [LLM Evaluation](../llm-evaluation/)
  - [RAG Patterns](../rag-patterns/)
