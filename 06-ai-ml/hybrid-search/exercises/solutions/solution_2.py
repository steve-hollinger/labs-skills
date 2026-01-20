"""Solution for Exercise 2: Implement Weighted Score Fusion"""

import numpy as np
from numpy.typing import NDArray


def min_max_normalize(scores: NDArray[np.float64]) -> NDArray[np.float64]:
    """Normalize scores to [0, 1] range using min-max normalization.

    Args:
        scores: Array of scores to normalize.

    Returns:
        Normalized scores in [0, 1] range.
    """
    # Handle empty array
    if len(scores) == 0:
        return scores.copy()

    min_val = scores.min()
    max_val = scores.max()

    # Handle case where all values are the same
    if max_val - min_val < 1e-10:
        return np.zeros_like(scores)

    # Apply min-max normalization
    return (scores - min_val) / (max_val - min_val)


def z_score_normalize(scores: NDArray[np.float64]) -> NDArray[np.float64]:
    """Normalize scores using z-score (standard score) normalization.

    Args:
        scores: Array of scores to normalize.

    Returns:
        Z-score normalized values (mean=0, std=1).
    """
    # Handle empty array
    if len(scores) == 0:
        return scores.copy()

    mean = scores.mean()
    std = scores.std()

    # Handle zero standard deviation
    if std < 1e-10:
        return np.zeros_like(scores)

    # Apply z-score normalization
    return (scores - mean) / std


def weighted_combine(
    vector_scores: NDArray[np.float64],
    keyword_scores: NDArray[np.float64],
    alpha: float = 0.5,
    normalization: str = "minmax",
) -> NDArray[np.float64]:
    """Combine vector and keyword scores with weighted fusion.

    Args:
        vector_scores: Scores from vector search.
        keyword_scores: Scores from keyword search.
        alpha: Weight for vector scores (1-alpha for keyword).
        normalization: "minmax" or "zscore".

    Returns:
        Combined scores.

    Raises:
        ValueError: If arrays have different lengths or alpha is invalid.
    """
    # Validate inputs
    if len(vector_scores) != len(keyword_scores):
        raise ValueError(
            f"Arrays must have same length: {len(vector_scores)} vs {len(keyword_scores)}"
        )

    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"Alpha must be in [0, 1], got {alpha}")

    # Choose normalization method
    if normalization == "minmax":
        normalize_fn = min_max_normalize
    elif normalization == "zscore":
        normalize_fn = z_score_normalize
    else:
        raise ValueError(f"Unknown normalization: {normalization}")

    # Normalize both score arrays
    v_norm = normalize_fn(vector_scores.astype(np.float64))
    k_norm = normalize_fn(keyword_scores.astype(np.float64))

    # Weighted combination
    return alpha * v_norm + (1 - alpha) * k_norm


def solution() -> None:
    """Run solution demonstration."""
    print("Solution 2: Weighted Score Fusion")
    print("=" * 50)

    # Create sample scores
    vector_scores = np.array([0.9, 0.7, 0.3, 0.2, 0.1])
    keyword_scores = np.array([1.0, 5.0, 15.0, 2.0, 0.5])

    print("\nOriginal Scores:")
    print(f"  Vector:  {vector_scores}")
    print(f"  Keyword: {keyword_scores}")

    print("\nMin-Max Normalized:")
    print(f"  Vector:  {min_max_normalize(vector_scores)}")
    print(f"  Keyword: {min_max_normalize(keyword_scores)}")

    print("\nZ-Score Normalized:")
    print(f"  Vector:  {z_score_normalize(vector_scores)}")
    print(f"  Keyword: {z_score_normalize(keyword_scores)}")

    print("\nWeighted Combinations (minmax):")
    for alpha in [0.2, 0.5, 0.8]:
        combined = weighted_combine(vector_scores, keyword_scores, alpha=alpha)
        best_idx = np.argmax(combined)
        print(f"  α={alpha}: {combined} -> best=doc[{best_idx}]")

    print("\nWeighted Combinations (zscore):")
    for alpha in [0.2, 0.5, 0.8]:
        combined = weighted_combine(
            vector_scores, keyword_scores, alpha=alpha, normalization="zscore"
        )
        best_idx = np.argmax(combined)
        print(f"  α={alpha}: {combined} -> best=doc[{best_idx}]")


if __name__ == "__main__":
    solution()
