"""Exercise 2: Implement Weighted Score Fusion

In this exercise, you'll implement score normalization and weighted
fusion to combine vector and keyword search results.

Instructions:
1. Implement `min_max_normalize` to normalize scores to [0, 1]
2. Implement `z_score_normalize` using mean and standard deviation
3. Implement `weighted_combine` to combine normalized scores
4. Compare both normalization methods

Expected Output:
When you run this file, the tests at the bottom should pass.

Hints:
- Min-max: (x - min) / (max - min)
- Z-score: (x - mean) / std
- Handle edge cases: empty arrays, all same values
"""

import numpy as np
from numpy.typing import NDArray


def min_max_normalize(scores: NDArray[np.float64]) -> NDArray[np.float64]:
    """Normalize scores to [0, 1] range using min-max normalization.

    Args:
        scores: Array of scores to normalize.

    Returns:
        Normalized scores in [0, 1] range.

    Edge cases:
        - Empty array: return empty array
        - All same values: return array of zeros
    """
    # TODO: Implement this function
    # 1. Handle empty array
    # 2. Compute min and max
    # 3. Handle case where all values are the same
    # 4. Apply min-max formula
    pass


def z_score_normalize(scores: NDArray[np.float64]) -> NDArray[np.float64]:
    """Normalize scores using z-score (standard score) normalization.

    Args:
        scores: Array of scores to normalize.

    Returns:
        Z-score normalized values (mean=0, std=1).

    Edge cases:
        - Empty array: return empty array
        - Zero standard deviation: return array of zeros
    """
    # TODO: Implement this function
    # 1. Handle empty array
    # 2. Compute mean and standard deviation
    # 3. Handle case where std is zero
    # 4. Apply z-score formula
    pass


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
    # TODO: Implement this function
    # 1. Validate inputs (same length, alpha in [0, 1])
    # 2. Normalize both score arrays using specified method
    # 3. Combine with weighted sum: alpha * vector + (1-alpha) * keyword
    pass


def exercise() -> None:
    """Run exercise tests."""
    print("Exercise 2: Weighted Score Fusion")
    print("=" * 50)

    # Test 1: Min-max normalization
    print("\nTest 1: Min-Max Normalization")
    scores = np.array([0.5, 1.0, 2.0, 3.0, 10.0])
    normalized = min_max_normalize(scores)

    print(f"  Original: {scores}")
    print(f"  Normalized: {normalized}")

    assert normalized is not None, "min_max_normalize not implemented"
    assert np.isclose(normalized.min(), 0.0), "Min should be 0"
    assert np.isclose(normalized.max(), 1.0), "Max should be 1"
    assert np.all(normalized >= 0) and np.all(normalized <= 1), "All values should be in [0, 1]"
    print("  PASSED!")

    # Test edge case: all same values
    same_scores = np.array([5.0, 5.0, 5.0])
    same_normalized = min_max_normalize(same_scores)
    assert np.all(same_normalized == 0), "Same values should normalize to zeros"
    print("  Edge case (same values): PASSED!")

    # Test 2: Z-score normalization
    print("\nTest 2: Z-Score Normalization")
    scores = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    z_normalized = z_score_normalize(scores)

    print(f"  Original: {scores}")
    print(f"  Z-normalized: {z_normalized}")

    assert z_normalized is not None, "z_score_normalize not implemented"
    assert np.isclose(z_normalized.mean(), 0.0, atol=1e-10), "Mean should be ~0"
    assert np.isclose(z_normalized.std(), 1.0, atol=1e-10), "Std should be ~1"
    print("  PASSED!")

    # Test 3: Weighted combination
    print("\nTest 3: Weighted Combination")

    # Simulate search scores
    # Vector search: doc 0 is best semantically
    vector_scores = np.array([0.9, 0.7, 0.3, 0.2, 0.1])
    # Keyword search: doc 2 has best keyword match
    keyword_scores = np.array([1.0, 5.0, 15.0, 2.0, 0.5])

    combined_05 = weighted_combine(vector_scores, keyword_scores, alpha=0.5)
    combined_08 = weighted_combine(vector_scores, keyword_scores, alpha=0.8)
    combined_02 = weighted_combine(vector_scores, keyword_scores, alpha=0.2)

    print(f"  Vector scores: {vector_scores}")
    print(f"  Keyword scores: {keyword_scores}")
    print(f"  Combined (α=0.5): {combined_05}")
    print(f"  Combined (α=0.8): {combined_08}")
    print(f"  Combined (α=0.2): {combined_02}")

    assert combined_05 is not None, "weighted_combine not implemented"

    # With alpha=0.8, vector should dominate, so doc 0 should be highest
    assert np.argmax(combined_08) == 0, "With high alpha, vector-best doc should win"

    # With alpha=0.2, keyword should dominate, so doc 2 should be highest
    assert np.argmax(combined_02) == 2, "With low alpha, keyword-best doc should win"

    print("  PASSED!")

    # Test 4: Compare normalization methods
    print("\nTest 4: Normalization Method Comparison")

    # Scores with outlier
    vector_with_outlier = np.array([0.8, 0.7, 0.6, 0.5, 0.01])
    keyword_with_outlier = np.array([10.0, 8.0, 100.0, 5.0, 3.0])  # doc 2 is outlier

    minmax_result = weighted_combine(
        vector_with_outlier, keyword_with_outlier, alpha=0.5, normalization="minmax"
    )
    zscore_result = weighted_combine(
        vector_with_outlier, keyword_with_outlier, alpha=0.5, normalization="zscore"
    )

    print(f"  Vector: {vector_with_outlier}")
    print(f"  Keyword (with outlier): {keyword_with_outlier}")
    print(f"  MinMax fusion: {minmax_result}")
    print(f"  Z-score fusion: {zscore_result}")

    # Min-max: outlier will dominate because it becomes 1.0
    # Z-score: outlier effect is reduced but still significant
    print("  Note: Min-max is more affected by outliers")
    print("  PASSED!")

    # Test 5: Edge cases
    print("\nTest 5: Error Handling")

    try:
        weighted_combine(np.array([1.0, 2.0]), np.array([1.0]), alpha=0.5)
        print("  ERROR: Should have raised ValueError for different lengths")
    except ValueError:
        print("  Different lengths: PASSED!")

    try:
        weighted_combine(np.array([1.0]), np.array([1.0]), alpha=1.5)
        print("  ERROR: Should have raised ValueError for invalid alpha")
    except ValueError:
        print("  Invalid alpha: PASSED!")

    print("\n" + "=" * 50)
    print("All tests passed! Great job!")


if __name__ == "__main__":
    exercise()
