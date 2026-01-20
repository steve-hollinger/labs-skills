"""Exercise 1: Implement Basic BM25 Search

In this exercise, you'll implement a simplified BM25 scoring function
from scratch to understand how keyword search works.

Instructions:
1. Implement the `compute_idf` function to calculate inverse document frequency
2. Implement the `compute_bm25_score` function using the BM25 formula
3. Implement the `search` function to rank documents

Expected Output:
When you run this file, the tests at the bottom should pass.

Hints:
- IDF(term) = log((N - df + 0.5) / (df + 0.5) + 1) where N=total docs, df=docs containing term
- BM25 score for a term = IDF * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len/avg_len))
- tf = term frequency in document
- k1 = 1.5 (typical), b = 0.75 (typical)
"""

import math
from collections import Counter


def tokenize(text: str) -> list[str]:
    """Simple tokenization - lowercase and split."""
    return text.lower().split()


def compute_idf(term: str, documents: list[list[str]]) -> float:
    """Compute inverse document frequency for a term.

    Args:
        term: The term to compute IDF for.
        documents: List of tokenized documents.

    Returns:
        IDF score for the term.

    Formula: log((N - df + 0.5) / (df + 0.5) + 1)
    where N = total number of documents
          df = number of documents containing the term
    """
    # TODO: Implement this function
    # 1. Count how many documents contain the term (df)
    # 2. Apply the IDF formula
    pass


def compute_bm25_score(
    query_terms: list[str],
    document: list[str],
    documents: list[list[str]],
    k1: float = 1.5,
    b: float = 0.75,
) -> float:
    """Compute BM25 score for a document given a query.

    Args:
        query_terms: Tokenized query.
        document: Tokenized document to score.
        documents: All tokenized documents (for IDF computation).
        k1: Term frequency saturation parameter.
        b: Length normalization parameter.

    Returns:
        BM25 score for the document.
    """
    # TODO: Implement this function
    # 1. Compute average document length
    # 2. For each query term in the document:
    #    a. Compute IDF
    #    b. Compute term frequency in document
    #    c. Apply BM25 formula
    # 3. Sum scores for all query terms
    pass


def search(
    query: str,
    documents: list[str],
    top_k: int = 5,
) -> list[tuple[int, float]]:
    """Search documents using BM25 scoring.

    Args:
        query: Search query string.
        documents: List of document strings.
        top_k: Number of results to return.

    Returns:
        List of (doc_id, score) tuples, sorted by score descending.
    """
    # TODO: Implement this function
    # 1. Tokenize query and all documents
    # 2. Compute BM25 score for each document
    # 3. Sort by score and return top_k
    pass


def exercise() -> None:
    """Run exercise tests."""
    # Test documents
    documents = [
        "the quick brown fox jumps over the lazy dog",
        "a quick brown dog outpaces a lazy fox",
        "the fox and the dog are friends",
        "machine learning with python and tensorflow",
        "deep learning neural networks",
    ]

    # Test 1: IDF computation
    tokenized_docs = [tokenize(doc) for doc in documents]

    idf_the = compute_idf("the", tokenized_docs)
    idf_quick = compute_idf("quick", tokenized_docs)
    idf_python = compute_idf("python", tokenized_docs)

    print("Test 1: IDF Computation")
    print(f"  IDF('the') = {idf_the:.3f} (common word, lower IDF)")
    print(f"  IDF('quick') = {idf_quick:.3f} (less common)")
    print(f"  IDF('python') = {idf_python:.3f} (rare, higher IDF)")

    assert idf_the is not None, "compute_idf not implemented"
    assert idf_the < idf_quick < idf_python, "IDF should be higher for rarer terms"
    print("  PASSED!\n")

    # Test 2: BM25 scoring
    query_terms = tokenize("quick fox")
    score_0 = compute_bm25_score(query_terms, tokenized_docs[0], tokenized_docs)
    score_1 = compute_bm25_score(query_terms, tokenized_docs[1], tokenized_docs)
    score_3 = compute_bm25_score(query_terms, tokenized_docs[3], tokenized_docs)

    print("Test 2: BM25 Scoring")
    print(f"  Score doc[0] (has quick, fox) = {score_0:.3f}")
    print(f"  Score doc[1] (has quick, fox) = {score_1:.3f}")
    print(f"  Score doc[3] (no quick, fox) = {score_3:.3f}")

    assert score_0 is not None, "compute_bm25_score not implemented"
    assert score_0 > 0, "Document with query terms should have positive score"
    assert score_3 == 0, "Document without query terms should have zero score"
    print("  PASSED!\n")

    # Test 3: Search ranking
    results = search("quick brown fox", documents)

    print("Test 3: Search Ranking")
    print(f"  Query: 'quick brown fox'")
    for doc_id, score in results[:3]:
        print(f"  [{score:.3f}] {documents[doc_id][:40]}...")

    assert results is not None, "search not implemented"
    assert len(results) > 0, "Should return results"
    assert results[0][0] in [0, 1], "Top result should be doc 0 or 1"
    print("  PASSED!\n")

    print("All tests passed! Great job!")


if __name__ == "__main__":
    exercise()
