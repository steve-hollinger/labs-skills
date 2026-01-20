"""Example 2: Score Fusion Strategies

This example compares different score fusion strategies:
- Weighted linear combination
- Reciprocal Rank Fusion (RRF)
- Max score fusion
- Distribution-based fusion
"""

import numpy as np

from hybrid_search.fusion import (
    distribution_based_fusion,
    max_score_fusion,
    reciprocal_rank_fusion,
    weighted_fusion,
)
from hybrid_search.keyword_search import BM25Searcher
from hybrid_search.vector_search import VectorSearcher


def main() -> None:
    """Run the fusion strategies comparison example."""
    print("Example 2: Score Fusion Strategies Comparison")
    print("=" * 60)

    # Technical documentation corpus
    documents = [
        "Introduction to Python programming language basics",
        "Advanced Python: decorators, generators, and metaclasses",
        "Machine learning with scikit-learn: a practical guide",
        "Deep learning fundamentals: neural networks explained",
        "TensorFlow 2.0 tutorial for beginners",
        "PyTorch vs TensorFlow: which framework to choose",
        "Natural language processing with transformers",
        "BERT and GPT: understanding large language models",
        "Building REST APIs with FastAPI",
        "Docker containerization best practices",
        "Kubernetes deployment strategies",
        "MLOps: machine learning operations guide",
        "Data preprocessing techniques for ML",
        "Feature engineering for machine learning models",
        "Model evaluation metrics: accuracy, precision, recall",
    ]

    print(f"\nIndexing {len(documents)} documents...")

    # Initialize searchers
    vector_searcher = VectorSearcher(model_name="all-MiniLM-L6-v2")
    vector_searcher.index(documents)

    keyword_searcher = BM25Searcher()
    keyword_searcher.index(documents)

    # Test queries that benefit from different fusion strategies
    test_cases = [
        {
            "query": "Python ML tutorial",
            "description": "Mixed query - has both specific keywords and semantic intent",
        },
        {
            "query": "how to train neural networks",
            "description": "Conceptual query - benefits from semantic search",
        },
        {
            "query": "TensorFlow 2.0",
            "description": "Specific query - benefits from keyword search",
        },
        {
            "query": "LLM transformer architecture",
            "description": "Technical query - needs both semantic and keyword",
        },
    ]

    for case in test_cases:
        query = case["query"]
        print(f"\n{'='*60}")
        print(f"Query: '{query}'")
        print(f"Type: {case['description']}")
        print("-" * 60)

        # Get scores and rankings
        vector_scores = vector_searcher.get_scores(query)
        keyword_scores = keyword_searcher.get_scores(query)
        vector_ranking = vector_searcher.get_ranking(query)
        keyword_ranking = keyword_searcher.get_ranking(query)

        # Apply different fusion strategies
        fusion_results = {}

        # 1. Weighted fusion (alpha=0.5)
        weighted_scores = weighted_fusion(vector_scores, keyword_scores, alpha=0.5)
        fusion_results["Weighted (α=0.5)"] = np.argsort(weighted_scores)[::-1][:5]

        # 2. Weighted fusion (alpha=0.7 - more vector)
        weighted_scores_v = weighted_fusion(vector_scores, keyword_scores, alpha=0.7)
        fusion_results["Weighted (α=0.7)"] = np.argsort(weighted_scores_v)[::-1][:5]

        # 3. Reciprocal Rank Fusion
        rrf_results = reciprocal_rank_fusion(vector_ranking, keyword_ranking, k=60)
        fusion_results["RRF (k=60)"] = [doc_id for doc_id, _ in rrf_results[:5]]

        # 4. Max score fusion
        max_scores = max_score_fusion(vector_scores, keyword_scores)
        fusion_results["Max Score"] = np.argsort(max_scores)[::-1][:5]

        # 5. Distribution-based fusion
        dist_scores = distribution_based_fusion(vector_scores, keyword_scores, alpha=0.5)
        fusion_results["Z-Score (α=0.5)"] = np.argsort(dist_scores)[::-1][:5]

        # Print results
        for method_name, top_indices in fusion_results.items():
            print(f"\n{method_name}:")
            for rank, idx in enumerate(top_indices[:3], 1):
                doc_preview = documents[idx][:45] + "..." if len(documents[idx]) > 45 else documents[idx]
                print(f"  {rank}. {doc_preview}")

        # Show individual method rankings for comparison
        print("\n[Individual Methods]")
        print(f"Vector top-3: {[documents[i][:30] + '...' for i in vector_ranking[:3]]}")
        print(f"Keyword top-3: {[documents[i][:30] + '...' for i in keyword_ranking[:3]]}")

    # Demonstrate RRF with more than 2 rankers
    print(f"\n{'='*60}")
    print("Bonus: RRF with Multiple Rankers")
    print("-" * 60)

    # Simulate a third ranker (e.g., a different embedding model or reranker)
    # For demo, we'll just use keyword search with different tokenization
    keyword_searcher_v2 = BM25Searcher(k1=2.0, b=0.5)  # Different BM25 params
    keyword_searcher_v2.index(documents)

    query = "machine learning python"
    ranking1 = vector_searcher.get_ranking(query)
    ranking2 = keyword_searcher.get_ranking(query)
    ranking3 = keyword_searcher_v2.get_ranking(query)

    # RRF with 3 rankers
    rrf_3way = reciprocal_rank_fusion(ranking1, ranking2, ranking3, k=60)

    print(f"\nQuery: '{query}'")
    print("\nRRF with 3 rankers (vector + 2 keyword variants):")
    for rank, (doc_id, score) in enumerate(rrf_3way[:5], 1):
        print(f"  {rank}. [{score:.4f}] {documents[doc_id][:45]}...")

    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
