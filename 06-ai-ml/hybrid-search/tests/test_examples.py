"""Tests for hybrid search examples and core functionality."""

import numpy as np
import pytest

from hybrid_search.fusion import (
    distribution_based_fusion,
    max_score_fusion,
    normalize_scores,
    reciprocal_rank_fusion,
    weighted_fusion,
)
from hybrid_search.keyword_search import BM25Searcher, simple_tokenize
from hybrid_search.vector_search import VectorSearcher


class TestNormalizeScores:
    """Tests for score normalization."""

    def test_basic_normalization(self) -> None:
        """Test basic min-max normalization."""
        scores = np.array([0.0, 5.0, 10.0])
        normalized = normalize_scores(scores)

        assert np.isclose(normalized[0], 0.0)
        assert np.isclose(normalized[1], 0.5)
        assert np.isclose(normalized[2], 1.0)

    def test_already_normalized(self) -> None:
        """Test scores already in [0, 1]."""
        scores = np.array([0.0, 0.5, 1.0])
        normalized = normalize_scores(scores)

        np.testing.assert_array_almost_equal(scores, normalized)

    def test_same_values(self) -> None:
        """Test when all values are the same."""
        scores = np.array([5.0, 5.0, 5.0])
        normalized = normalize_scores(scores)

        np.testing.assert_array_equal(normalized, np.zeros(3))

    def test_empty_array(self) -> None:
        """Test empty array."""
        scores = np.array([])
        normalized = normalize_scores(scores)

        assert len(normalized) == 0

    def test_negative_values(self) -> None:
        """Test with negative values."""
        scores = np.array([-10.0, 0.0, 10.0])
        normalized = normalize_scores(scores)

        assert np.isclose(normalized[0], 0.0)
        assert np.isclose(normalized[1], 0.5)
        assert np.isclose(normalized[2], 1.0)


class TestWeightedFusion:
    """Tests for weighted score fusion."""

    def test_equal_weights(self) -> None:
        """Test with alpha=0.5 (equal weights)."""
        v_scores = np.array([1.0, 0.0])
        k_scores = np.array([0.0, 1.0])

        combined = weighted_fusion(v_scores, k_scores, alpha=0.5)

        # Both should have same combined score
        assert np.isclose(combined[0], combined[1])

    def test_pure_vector(self) -> None:
        """Test with alpha=1.0 (pure vector)."""
        v_scores = np.array([1.0, 0.5, 0.0])
        k_scores = np.array([0.0, 0.5, 1.0])

        combined = weighted_fusion(v_scores, k_scores, alpha=1.0)

        # Should follow vector scores order
        assert combined[0] > combined[1] > combined[2]

    def test_pure_keyword(self) -> None:
        """Test with alpha=0.0 (pure keyword)."""
        v_scores = np.array([1.0, 0.5, 0.0])
        k_scores = np.array([0.0, 0.5, 1.0])

        combined = weighted_fusion(v_scores, k_scores, alpha=0.0)

        # Should follow keyword scores order
        assert combined[2] > combined[1] > combined[0]

    def test_invalid_alpha(self) -> None:
        """Test with invalid alpha values."""
        v_scores = np.array([1.0])
        k_scores = np.array([1.0])

        with pytest.raises(ValueError):
            weighted_fusion(v_scores, k_scores, alpha=-0.1)

        with pytest.raises(ValueError):
            weighted_fusion(v_scores, k_scores, alpha=1.1)

    def test_mismatched_lengths(self) -> None:
        """Test with different length arrays."""
        v_scores = np.array([1.0, 2.0])
        k_scores = np.array([1.0])

        with pytest.raises(ValueError):
            weighted_fusion(v_scores, k_scores)


class TestReciprocalRankFusion:
    """Tests for RRF fusion."""

    def test_basic_rrf(self) -> None:
        """Test basic RRF fusion."""
        ranking1 = [0, 1, 2]  # Doc 0 is best
        ranking2 = [2, 1, 0]  # Doc 2 is best

        results = reciprocal_rank_fusion(ranking1, ranking2, k=60)

        # Doc 1 should be best (rank 2 in both)
        assert results[0][0] == 1

    def test_single_ranker(self) -> None:
        """Test with single ranker."""
        ranking = [2, 0, 1]

        results = reciprocal_rank_fusion(ranking, k=60)

        # Should preserve original ranking
        assert [doc_id for doc_id, _ in results] == [2, 0, 1]

    def test_multiple_rankers(self) -> None:
        """Test with three rankers."""
        r1 = [0, 1, 2]
        r2 = [1, 0, 2]
        r3 = [0, 2, 1]

        results = reciprocal_rank_fusion(r1, r2, r3, k=60)

        # Doc 0 appears at rank 0 twice, should be top
        assert results[0][0] == 0

    def test_invalid_k(self) -> None:
        """Test with invalid k value."""
        with pytest.raises(ValueError):
            reciprocal_rank_fusion([0, 1], k=0)

        with pytest.raises(ValueError):
            reciprocal_rank_fusion([0, 1], k=-1)


class TestMaxScoreFusion:
    """Tests for max score fusion."""

    def test_max_fusion(self) -> None:
        """Test max score fusion takes maximum."""
        v_scores = np.array([0.9, 0.1])
        k_scores = np.array([0.1, 0.9])

        combined = max_score_fusion(v_scores, k_scores)

        # Both should have high scores (0.9 normalized)
        assert combined[0] > 0.5
        assert combined[1] > 0.5


class TestDistributionBasedFusion:
    """Tests for z-score based fusion."""

    def test_distribution_fusion(self) -> None:
        """Test z-score normalization preserves relative ordering."""
        v_scores = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        k_scores = np.array([10.0, 20.0, 30.0, 40.0, 50.0])

        combined = distribution_based_fusion(v_scores, k_scores, alpha=0.5)

        # Relative ordering should be preserved
        for i in range(len(combined) - 1):
            assert combined[i] < combined[i + 1]


class TestBM25Searcher:
    """Tests for BM25 keyword search."""

    def test_basic_search(self) -> None:
        """Test basic BM25 search."""
        documents = [
            "python programming language",
            "java programming language",
            "python data science",
        ]

        searcher = BM25Searcher()
        searcher.index(documents)

        results = searcher.search("python", top_k=3)

        # Python docs should rank higher
        assert results[0].doc_id in [0, 2]
        assert results[1].doc_id in [0, 2]

    def test_exact_match_scores_higher(self) -> None:
        """Test that exact matches score higher."""
        documents = [
            "machine learning algorithms",
            "deep learning neural networks",
            "machine learning with python",
        ]

        searcher = BM25Searcher()
        searcher.index(documents)

        results = searcher.search("machine learning", top_k=3)

        # Docs with "machine learning" should be top 2
        top_ids = {results[0].doc_id, results[1].doc_id}
        assert top_ids == {0, 2}

    def test_empty_query(self) -> None:
        """Test with empty query."""
        searcher = BM25Searcher()
        searcher.index(["doc1", "doc2"])

        scores = searcher.get_scores("")
        assert all(s == 0 for s in scores)

    def test_get_ranking(self) -> None:
        """Test ranking method."""
        documents = ["python only", "java only", "python java"]

        searcher = BM25Searcher()
        searcher.index(documents)

        ranking = searcher.get_ranking("python")

        # "python only" or "python java" should be first
        assert ranking[0] in [0, 2]


class TestSimpleTokenize:
    """Tests for tokenization."""

    def test_basic_tokenize(self) -> None:
        """Test basic tokenization."""
        text = "Hello World!"
        tokens = simple_tokenize(text)

        assert tokens == ["hello", "world"]

    def test_punctuation_removal(self) -> None:
        """Test punctuation is handled."""
        text = "Hello, World! How's it going?"
        tokens = simple_tokenize(text)

        assert "hello" in tokens
        assert "world" in tokens


@pytest.mark.slow
class TestVectorSearcher:
    """Tests for vector search (requires model download)."""

    @pytest.fixture
    def searcher(self) -> VectorSearcher:
        """Create a vector searcher."""
        return VectorSearcher(model_name="all-MiniLM-L6-v2")

    def test_basic_search(self, searcher: VectorSearcher) -> None:
        """Test basic vector search."""
        documents = [
            "machine learning with python",
            "cooking recipes for dinner",
            "artificial intelligence and deep learning",
        ]

        searcher.index(documents)
        results = searcher.search("AI and ML", top_k=3)

        # AI/ML docs should rank higher than cooking
        ml_results = [r for r in results if r.doc_id in [0, 2]]
        assert len(ml_results) >= 1
        assert results[0].doc_id in [0, 2]

    def test_semantic_similarity(self, searcher: VectorSearcher) -> None:
        """Test semantic understanding."""
        documents = [
            "I love cats and dogs",
            "Programming in Python",
            "My favorite pets are felines and canines",
        ]

        searcher.index(documents)
        results = searcher.search("animals I like", top_k=3)

        # Pet-related docs should rank higher
        top_ids = {results[0].doc_id, results[1].doc_id}
        assert 0 in top_ids or 2 in top_ids

    def test_get_scores(self, searcher: VectorSearcher) -> None:
        """Test score retrieval."""
        searcher.index(["doc1", "doc2", "doc3"])
        scores = searcher.get_scores("test")

        assert len(scores) == 3
        assert all(isinstance(s, (float, np.floating)) for s in scores)


class TestIntegration:
    """Integration tests combining vector and keyword search."""

    @pytest.mark.slow
    def test_hybrid_search_pipeline(self) -> None:
        """Test complete hybrid search pipeline."""
        documents = [
            "Python is great for machine learning",
            "JavaScript is used for web development",
            "TensorFlow is a machine learning framework",
            "React is a JavaScript library",
        ]

        # Initialize both searchers
        vector_searcher = VectorSearcher()
        vector_searcher.index(documents)

        keyword_searcher = BM25Searcher()
        keyword_searcher.index(documents)

        query = "Python ML"

        # Get scores
        vector_scores = vector_searcher.get_scores(query)
        keyword_scores = keyword_searcher.get_scores(query)

        # Test weighted fusion
        hybrid_scores = weighted_fusion(vector_scores, keyword_scores, alpha=0.5)
        top_idx = np.argmax(hybrid_scores)

        # Python ML doc should rank high
        assert top_idx == 0  # "Python is great for machine learning"

    @pytest.mark.slow
    def test_rrf_vs_weighted(self) -> None:
        """Test that RRF and weighted give reasonable results."""
        documents = [
            "deep learning neural networks",
            "shallow learning decision trees",
            "neural network architecture design",
        ]

        vector_searcher = VectorSearcher()
        vector_searcher.index(documents)

        keyword_searcher = BM25Searcher()
        keyword_searcher.index(documents)

        query = "neural networks"

        # Get rankings and scores
        v_ranking = vector_searcher.get_ranking(query)
        k_ranking = keyword_searcher.get_ranking(query)
        v_scores = vector_searcher.get_scores(query)
        k_scores = keyword_searcher.get_scores(query)

        # RRF
        rrf_results = reciprocal_rank_fusion(v_ranking, k_ranking)
        rrf_top = rrf_results[0][0]

        # Weighted
        weighted_scores = weighted_fusion(v_scores, k_scores, alpha=0.5)
        weighted_top = int(np.argmax(weighted_scores))

        # Both should return neural network related docs at top
        assert rrf_top in [0, 2]
        assert weighted_top in [0, 2]
