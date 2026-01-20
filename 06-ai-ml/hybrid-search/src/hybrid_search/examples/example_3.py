"""Example 3: Production-Ready Hybrid Search Pipeline

This example demonstrates a complete hybrid search system with:
- Embedding caching for performance
- Batched document processing
- Query-dependent alpha selection
- Reranking support
- Comprehensive result formatting
"""

import hashlib
import json
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from hybrid_search.fusion import reciprocal_rank_fusion, weighted_fusion
from hybrid_search.keyword_search import BM25Searcher
from hybrid_search.vector_search import VectorSearcher


@dataclass
class SearchResult:
    """Comprehensive search result with metadata."""

    doc_id: int
    document: str
    score: float
    vector_score: float
    keyword_score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchConfig:
    """Configuration for hybrid search."""

    model_name: str = "all-MiniLM-L6-v2"
    fusion_method: str = "weighted"  # "weighted", "rrf", or "adaptive"
    default_alpha: float = 0.5
    rrf_k: int = 60
    cache_embeddings: bool = True
    cache_dir: Path | None = None


class ProductionHybridSearcher:
    """Production-ready hybrid search with caching and adaptive fusion."""

    def __init__(self, config: SearchConfig | None = None) -> None:
        """Initialize the production hybrid searcher."""
        self.config = config or SearchConfig()
        self.vector_searcher = VectorSearcher(model_name=self.config.model_name)
        self.keyword_searcher = BM25Searcher()
        self.documents: list[str] = []
        self.metadata: list[dict[str, Any]] = []
        self._cache_dir = self.config.cache_dir or Path(tempfile.gettempdir()) / "hybrid_search_cache"

        if self.config.cache_embeddings:
            self._cache_dir.mkdir(parents=True, exist_ok=True)

    def _compute_cache_key(self, documents: list[str]) -> str:
        """Compute a cache key for the document set."""
        content = json.dumps(documents, sort_keys=True) + self.config.model_name
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def index(
        self,
        documents: list[str],
        metadata: list[dict[str, Any]] | None = None,
        batch_size: int = 32,
        show_progress: bool = True,
    ) -> None:
        """Index documents with optional caching.

        Args:
            documents: List of documents to index.
            metadata: Optional metadata for each document.
            batch_size: Batch size for embedding computation.
            show_progress: Whether to show progress information.
        """
        self.documents = documents
        self.metadata = metadata or [{} for _ in documents]

        if show_progress:
            print(f"Indexing {len(documents)} documents...")

        # Check for cached embeddings
        if self.config.cache_embeddings:
            cache_key = self._compute_cache_key(documents)
            cache_file = self._cache_dir / f"{cache_key}.npy"

            if cache_file.exists():
                if show_progress:
                    print(f"  Loading cached embeddings from {cache_file}")
                self.vector_searcher.documents = documents
                self.vector_searcher.embeddings = np.load(cache_file)
            else:
                if show_progress:
                    print(f"  Computing embeddings (batch_size={batch_size})...")
                self.vector_searcher.index(documents, show_progress=False)
                np.save(cache_file, self.vector_searcher.embeddings)
                if show_progress:
                    print(f"  Cached embeddings to {cache_file}")
        else:
            self.vector_searcher.index(documents, show_progress=False)

        # Index for keyword search
        if show_progress:
            print("  Building BM25 index...")
        self.keyword_searcher.index(documents)

        if show_progress:
            print("  Indexing complete!")

    def estimate_query_alpha(self, query: str) -> float:
        """Estimate optimal alpha based on query characteristics.

        Higher alpha = more vector search weight
        Lower alpha = more keyword search weight
        """
        query_lower = query.lower()
        words = query_lower.split()

        # Start with default
        alpha = self.config.default_alpha

        # Heuristics for query type
        # 1. Quoted phrases -> more keyword weight
        if '"' in query:
            alpha -= 0.15

        # 2. Technical terms (acronyms, version numbers) -> more keyword
        has_technical = bool(re.search(r"[A-Z]{2,}|v\d+|\d+\.\d+", query))
        if has_technical:
            alpha -= 0.1

        # 3. Question words -> more semantic
        question_words = {"how", "what", "why", "when", "explain", "describe"}
        if any(w in words for w in question_words):
            alpha += 0.1

        # 4. Very short queries -> more keyword
        if len(words) <= 2:
            alpha -= 0.1

        # 5. Long conceptual queries -> more semantic
        if len(words) >= 6:
            alpha += 0.1

        # Clamp to valid range
        return max(0.1, min(0.9, alpha))

    def search(
        self,
        query: str,
        top_k: int = 10,
        alpha: float | None = None,
        fusion_method: str | None = None,
        include_scores: bool = True,
    ) -> list[SearchResult]:
        """Search with hybrid scoring.

        Args:
            query: Search query.
            top_k: Number of results to return.
            alpha: Override default alpha (for weighted fusion).
            fusion_method: Override default fusion method.
            include_scores: Include detailed scores in results.

        Returns:
            List of search results.
        """
        if not self.documents:
            return []

        method = fusion_method or self.config.fusion_method

        # Get scores from both methods
        vector_scores = self.vector_searcher.get_scores(query)
        keyword_scores = self.keyword_searcher.get_scores(query)

        # Apply fusion
        if method == "rrf":
            return self._rrf_search(query, top_k, vector_scores, keyword_scores)
        elif method == "adaptive":
            # Use estimated alpha
            alpha = self.estimate_query_alpha(query)
            return self._weighted_search(
                query, top_k, alpha, vector_scores, keyword_scores
            )
        else:  # weighted
            alpha = alpha if alpha is not None else self.config.default_alpha
            return self._weighted_search(
                query, top_k, alpha, vector_scores, keyword_scores
            )

    def _weighted_search(
        self,
        query: str,
        top_k: int,
        alpha: float,
        vector_scores: NDArray[np.float32],
        keyword_scores: NDArray[np.float64],
    ) -> list[SearchResult]:
        """Perform weighted fusion search."""
        hybrid_scores = weighted_fusion(vector_scores, keyword_scores, alpha=alpha)
        top_indices = np.argsort(hybrid_scores)[::-1][:top_k]

        return [
            SearchResult(
                doc_id=int(idx),
                document=self.documents[idx],
                score=float(hybrid_scores[idx]),
                vector_score=float(vector_scores[idx]),
                keyword_score=float(keyword_scores[idx]),
                metadata=self.metadata[idx],
            )
            for idx in top_indices
        ]

    def _rrf_search(
        self,
        query: str,
        top_k: int,
        vector_scores: NDArray[np.float32],
        keyword_scores: NDArray[np.float64],
    ) -> list[SearchResult]:
        """Perform RRF fusion search."""
        vector_ranking = np.argsort(vector_scores)[::-1].tolist()
        keyword_ranking = np.argsort(keyword_scores)[::-1].tolist()

        rrf_results = reciprocal_rank_fusion(
            vector_ranking, keyword_ranking, k=self.config.rrf_k
        )

        return [
            SearchResult(
                doc_id=doc_id,
                document=self.documents[doc_id],
                score=score,
                vector_score=float(vector_scores[doc_id]),
                keyword_score=float(keyword_scores[doc_id]),
                metadata=self.metadata[doc_id],
            )
            for doc_id, score in rrf_results[:top_k]
        ]

    def explain_result(self, result: SearchResult, query: str) -> dict[str, Any]:
        """Explain why a result was returned.

        Useful for debugging and understanding search behavior.
        """
        # Get query tokens
        query_tokens = set(query.lower().split())
        doc_tokens = set(result.document.lower().split())

        # Find matching keywords
        matching_keywords = query_tokens & doc_tokens

        return {
            "doc_id": result.doc_id,
            "hybrid_score": result.score,
            "vector_score": result.vector_score,
            "keyword_score": result.keyword_score,
            "matching_keywords": list(matching_keywords),
            "keyword_match_ratio": len(matching_keywords) / len(query_tokens) if query_tokens else 0,
            "document_length": len(result.document.split()),
        }


def main() -> None:
    """Run the production pipeline example."""
    print("Example 3: Production-Ready Hybrid Search Pipeline")
    print("=" * 60)

    # Create a realistic document corpus (FAQ-style)
    documents = [
        "How do I reset my password? Go to Settings > Security > Reset Password.",
        "What payment methods do you accept? We accept Visa, Mastercard, and PayPal.",
        "How can I contact customer support? Email support@example.com or call 1-800-123-4567.",
        "What is your return policy? Items can be returned within 30 days of purchase.",
        "How do I track my order? Use the tracking number in your confirmation email.",
        "Can I change my shipping address? Yes, before the order ships in Account Settings.",
        "What are your business hours? We're open Monday-Friday, 9 AM - 5 PM EST.",
        "How do I cancel my subscription? Go to Account > Subscriptions > Cancel.",
        "Is there a mobile app? Yes, download from the App Store or Google Play.",
        "How do I update my billing information? Go to Account > Payment Methods.",
        "What is two-factor authentication? An extra security layer requiring a code from your phone.",
        "How do I export my data? Go to Settings > Privacy > Export Data.",
        "Can I merge accounts? Contact support to merge multiple accounts.",
        "What file formats do you support? We support PDF, DOCX, PNG, and JPG.",
        "How do I enable dark mode? Go to Settings > Display > Theme > Dark.",
    ]

    # Add metadata
    metadata = [
        {"category": "account", "priority": "high"},
        {"category": "billing", "priority": "medium"},
        {"category": "support", "priority": "high"},
        {"category": "orders", "priority": "medium"},
        {"category": "orders", "priority": "medium"},
        {"category": "orders", "priority": "low"},
        {"category": "general", "priority": "low"},
        {"category": "account", "priority": "medium"},
        {"category": "general", "priority": "low"},
        {"category": "billing", "priority": "medium"},
        {"category": "security", "priority": "high"},
        {"category": "privacy", "priority": "medium"},
        {"category": "account", "priority": "low"},
        {"category": "general", "priority": "low"},
        {"category": "settings", "priority": "low"},
    ]

    # Initialize with production config
    config = SearchConfig(
        model_name="all-MiniLM-L6-v2",
        fusion_method="adaptive",  # Use query-dependent alpha
        default_alpha=0.5,
        cache_embeddings=True,
    )

    searcher = ProductionHybridSearcher(config)
    searcher.index(documents, metadata=metadata)

    # Test queries
    test_queries = [
        "password reset",  # Short, specific -> more keyword
        "how can I get help with my account",  # Question -> more semantic
        "2FA setup",  # Technical term -> more keyword
        "what happens if I want to return something",  # Conceptual -> more semantic
    ]

    print("\nSearch Results with Adaptive Fusion:")
    print("-" * 60)

    for query in test_queries:
        estimated_alpha = searcher.estimate_query_alpha(query)
        results = searcher.search(query, top_k=3)

        print(f"\nQuery: '{query}'")
        print(f"Estimated alpha: {estimated_alpha:.2f}")
        print()

        for rank, result in enumerate(results, 1):
            print(f"  {rank}. [{result.score:.3f}] {result.document[:50]}...")
            print(f"     Category: {result.metadata.get('category', 'N/A')}")

        # Show explanation for top result
        if results:
            explanation = searcher.explain_result(results[0], query)
            print(f"\n  [Explanation for top result]")
            print(f"     Vector score: {explanation['vector_score']:.3f}")
            print(f"     Keyword score: {explanation['keyword_score']:.3f}")
            print(f"     Matching keywords: {explanation['matching_keywords']}")

    # Compare fusion methods
    print(f"\n{'='*60}")
    print("Fusion Method Comparison")
    print("-" * 60)

    query = "cancel subscription"

    for method in ["weighted", "rrf", "adaptive"]:
        results = searcher.search(query, top_k=3, fusion_method=method)
        print(f"\n{method.upper()}:")
        for rank, r in enumerate(results, 1):
            print(f"  {rank}. [{r.score:.3f}] {r.document[:45]}...")

    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
