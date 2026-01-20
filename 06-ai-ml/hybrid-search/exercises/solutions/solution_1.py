"""Solution for Exercise 1: Implement Basic BM25 Search"""

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
    """
    n = len(documents)  # Total number of documents

    # Count documents containing the term
    df = sum(1 for doc in documents if term in doc)

    # Apply IDF formula
    # Adding 1 at the end ensures IDF is always positive
    idf = math.log((n - df + 0.5) / (df + 0.5) + 1)

    return idf


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
    # Compute average document length
    total_length = sum(len(doc) for doc in documents)
    avg_doc_length = total_length / len(documents) if documents else 0

    # Document length
    doc_length = len(document)

    # Count term frequencies in the document
    term_freqs = Counter(document)

    # Compute BM25 score
    score = 0.0

    for term in query_terms:
        if term not in term_freqs:
            continue

        # Get term frequency
        tf = term_freqs[term]

        # Get IDF
        idf = compute_idf(term, documents)

        # BM25 formula
        # score = IDF * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len/avg_len))
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * doc_length / avg_doc_length)

        score += idf * (numerator / denominator)

    return score


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
    # Tokenize query and all documents
    query_terms = tokenize(query)
    tokenized_docs = [tokenize(doc) for doc in documents]

    # Compute BM25 score for each document
    scores = []
    for doc_id, doc in enumerate(tokenized_docs):
        score = compute_bm25_score(query_terms, doc, tokenized_docs)
        scores.append((doc_id, score))

    # Sort by score descending
    scores.sort(key=lambda x: x[1], reverse=True)

    # Return top_k
    return scores[:top_k]


def solution() -> None:
    """Run solution demonstration."""
    documents = [
        "the quick brown fox jumps over the lazy dog",
        "a quick brown dog outpaces a lazy fox",
        "the fox and the dog are friends",
        "machine learning with python and tensorflow",
        "deep learning neural networks",
    ]

    print("Solution 1: BM25 Search Implementation")
    print("=" * 50)

    # Demonstrate IDF
    tokenized_docs = [tokenize(doc) for doc in documents]

    print("\nIDF Values:")
    for term in ["the", "quick", "fox", "python", "neural"]:
        idf = compute_idf(term, tokenized_docs)
        df = sum(1 for doc in tokenized_docs if term in doc)
        print(f"  '{term}': IDF={idf:.3f} (appears in {df} docs)")

    # Search demonstration
    print("\nSearch Results:")
    queries = ["quick brown fox", "machine learning", "the dog"]

    for query in queries:
        print(f"\nQuery: '{query}'")
        results = search(query, documents, top_k=3)
        for doc_id, score in results:
            print(f"  [{score:.3f}] {documents[doc_id]}")


if __name__ == "__main__":
    solution()
