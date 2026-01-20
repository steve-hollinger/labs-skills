"""Score fusion strategies for hybrid search."""

from collections import defaultdict

import numpy as np
from numpy.typing import NDArray


def normalize_scores(scores: NDArray[np.floating]) -> NDArray[np.float64]:  # type: ignore[type-arg]
    """Normalize scores to [0, 1] range using min-max normalization.

    Args:
        scores: Array of scores to normalize.

    Returns:
        Normalized scores in [0, 1] range.
    """
    scores = np.asarray(scores, dtype=np.float64)
    if len(scores) == 0:
        return scores

    min_score = scores.min()
    max_score = scores.max()

    if max_score - min_score < 1e-10:
        # All scores are the same, return zeros or ones
        return np.zeros_like(scores, dtype=np.float64)

    return (scores - min_score) / (max_score - min_score)


def weighted_fusion(
    vector_scores: NDArray[np.floating],  # type: ignore[type-arg]
    keyword_scores: NDArray[np.floating],  # type: ignore[type-arg]
    alpha: float = 0.5,
) -> NDArray[np.float64]:
    """Combine scores using weighted linear combination.

    Args:
        vector_scores: Scores from vector search.
        keyword_scores: Scores from keyword search.
        alpha: Weight for vector scores (1-alpha for keyword).
               - alpha=1.0: pure vector search
               - alpha=0.0: pure keyword search
               - alpha=0.5: equal weight

    Returns:
        Combined scores for each document.
    """
    if len(vector_scores) != len(keyword_scores):
        raise ValueError(
            f"Score arrays must have same length: "
            f"{len(vector_scores)} vs {len(keyword_scores)}"
        )

    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"Alpha must be between 0 and 1, got {alpha}")

    # Normalize both score arrays
    v_norm = normalize_scores(vector_scores)
    k_norm = normalize_scores(keyword_scores)

    # Weighted combination
    return alpha * v_norm + (1 - alpha) * k_norm


def reciprocal_rank_fusion(
    *rankings: list[int],
    k: int = 60,
) -> list[tuple[int, float]]:
    """Combine multiple rankings using Reciprocal Rank Fusion.

    RRF is robust to different score scales and works well when combining
    diverse rankers. It uses ranks rather than scores.

    Formula: RRF_score(d) = sum over rankings r: 1 / (k + rank_r(d))

    Args:
        rankings: Variable number of ranked document ID lists.
                  Each list should have document IDs sorted by relevance.
        k: Smoothing constant. Higher values give more weight to lower ranks.
           Default is 60, which works well in practice.

    Returns:
        List of (doc_id, rrf_score) tuples sorted by score descending.
    """
    if k <= 0:
        raise ValueError(f"k must be positive, got {k}")

    rrf_scores: dict[int, float] = defaultdict(float)

    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            # RRF formula: 1 / (k + rank + 1)
            # Using rank + 1 so first position (rank=0) gives 1/(k+1)
            rrf_scores[doc_id] += 1.0 / (k + rank + 1)

    # Sort by score descending
    sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    return sorted_results


def max_score_fusion(
    vector_scores: NDArray[np.floating],  # type: ignore[type-arg]
    keyword_scores: NDArray[np.floating],  # type: ignore[type-arg]
) -> NDArray[np.float64]:
    """Combine scores by taking the maximum of normalized scores.

    This is useful when you want a document to rank high if it scores
    well on either method.

    Args:
        vector_scores: Scores from vector search.
        keyword_scores: Scores from keyword search.

    Returns:
        Combined scores (max of normalized scores for each document).
    """
    if len(vector_scores) != len(keyword_scores):
        raise ValueError(
            f"Score arrays must have same length: "
            f"{len(vector_scores)} vs {len(keyword_scores)}"
        )

    v_norm = normalize_scores(vector_scores)
    k_norm = normalize_scores(keyword_scores)

    return np.maximum(v_norm, k_norm)


def distribution_based_fusion(
    vector_scores: NDArray[np.floating],  # type: ignore[type-arg]
    keyword_scores: NDArray[np.floating],  # type: ignore[type-arg]
    alpha: float = 0.5,
) -> NDArray[np.float64]:
    """Combine scores using z-score normalization.

    Z-score normalization accounts for the distribution of scores,
    making it more robust when score distributions differ significantly.

    Args:
        vector_scores: Scores from vector search.
        keyword_scores: Scores from keyword search.
        alpha: Weight for vector scores.

    Returns:
        Combined z-normalized scores.
    """
    if len(vector_scores) != len(keyword_scores):
        raise ValueError(
            f"Score arrays must have same length: "
            f"{len(vector_scores)} vs {len(keyword_scores)}"
        )

    def z_normalize(scores: NDArray[np.floating]) -> NDArray[np.float64]:  # type: ignore[type-arg]
        scores = np.asarray(scores, dtype=np.float64)
        if len(scores) == 0:
            return scores
        mean = scores.mean()
        std = scores.std()
        if std < 1e-10:
            return np.zeros_like(scores, dtype=np.float64)
        return (scores - mean) / std

    v_norm = z_normalize(vector_scores)
    k_norm = z_normalize(keyword_scores)

    return alpha * v_norm + (1 - alpha) * k_norm
