"""Example 1: Basic Hybrid Search

This example demonstrates how to build a simple hybrid search system
that combines vector similarity search with BM25 keyword search.
"""

import numpy as np

from hybrid_search.fusion import weighted_fusion
from hybrid_search.keyword_search import BM25Searcher
from hybrid_search.vector_search import VectorSearcher


def main() -> None:
    """Run the basic hybrid search example."""
    print("Example 1: Basic Hybrid Search")
    print("=" * 60)

    # Sample documents about programming and data science
    documents = [
        "Python is a versatile programming language for data science",
        "Machine learning algorithms learn patterns from data",
        "JavaScript is primarily used for web development",
        "Deep learning uses neural networks with many layers",
        "SQL databases store structured data in tables",
        "Natural language processing analyzes human language",
        "React is a JavaScript library for building user interfaces",
        "Pandas is a Python library for data manipulation",
        "TensorFlow is an open-source machine learning framework",
        "Docker containers package applications with their dependencies",
    ]

    print("\n1. Indexing documents...")
    print(f"   Number of documents: {len(documents)}")

    # Initialize searchers
    print("\n2. Initializing vector search (this may download model on first run)...")
    vector_searcher = VectorSearcher(model_name="all-MiniLM-L6-v2")
    vector_searcher.index(documents)

    print("   Initializing keyword search...")
    keyword_searcher = BM25Searcher()
    keyword_searcher.index(documents)

    # Search queries to demonstrate different behaviors
    queries = [
        "Python data analysis",  # Both methods should work well
        "ML framework",  # Semantic understanding helps (machine learning = ML)
        "JavaScript",  # Keyword search excels (exact match)
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: '{query}'")
        print("-" * 60)

        # Get scores from both methods
        vector_scores = vector_searcher.get_scores(query)
        keyword_scores = keyword_searcher.get_scores(query)

        # Combine with different alpha values
        for alpha in [0.3, 0.5, 0.7]:
            hybrid_scores = weighted_fusion(vector_scores, keyword_scores, alpha=alpha)
            top_idx = np.argsort(hybrid_scores)[::-1][:3]

            print(f"\nalpha={alpha} (vector={alpha:.0%}, keyword={1-alpha:.0%}):")
            for rank, idx in enumerate(top_idx, 1):
                print(f"  {rank}. [{hybrid_scores[idx]:.3f}] {documents[idx][:50]}...")

    # Show how the methods differ
    print(f"\n{'='*60}")
    print("Comparison: Vector vs Keyword for 'AI neural network'")
    print("-" * 60)

    query = "AI neural network"
    vector_results = vector_searcher.search(query, top_k=3)
    keyword_results = keyword_searcher.search(query, top_k=3)

    print("\nVector Search (semantic understanding):")
    for r in vector_results:
        print(f"  [{r.score:.3f}] {r.document[:50]}...")

    print("\nKeyword Search (exact matching):")
    for r in keyword_results:
        print(f"  [{r.score:.3f}] {r.document[:50]}...")

    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
