"""Custom evaluation metrics for LLM outputs.

This module provides custom metrics for evaluating LLM outputs beyond
the built-in Opik metrics.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ScoreResult:
    """Result of a metric scoring operation.

    Attributes:
        value: The numeric score (typically 0.0 to 1.0)
        name: Name of the metric
        reason: Optional explanation of the score
    """

    value: float
    name: str
    reason: str = ""


class BaseMetric:
    """Base class for custom evaluation metrics.

    Custom metrics should inherit from this class and implement
    the score() method.
    """

    def __init__(self, name: str) -> None:
        """Initialize the metric.

        Args:
            name: The name of this metric (used in reports)
        """
        self.name = name

    def score(self, output: str, **kwargs: Any) -> ScoreResult:
        """Score an LLM output.

        Args:
            output: The LLM's output text
            **kwargs: Additional arguments (input, expected_output, etc.)

        Returns:
            A ScoreResult with the computed score
        """
        raise NotImplementedError("Subclasses must implement score()")


class AccuracyMetric(BaseMetric):
    """Metric that measures exact match accuracy.

    Compares output to expected_output and returns 1.0 for exact match,
    0.0 otherwise. Optionally normalizes whitespace and case.
    """

    def __init__(
        self,
        name: str = "accuracy",
        normalize_whitespace: bool = True,
        case_sensitive: bool = False,
    ) -> None:
        """Initialize accuracy metric.

        Args:
            name: Metric name
            normalize_whitespace: Whether to normalize whitespace before comparison
            case_sensitive: Whether comparison should be case-sensitive
        """
        super().__init__(name)
        self.normalize_whitespace = normalize_whitespace
        self.case_sensitive = case_sensitive

    def _normalize(self, text: str) -> str:
        """Normalize text for comparison."""
        if self.normalize_whitespace:
            text = " ".join(text.split())
        if not self.case_sensitive:
            text = text.lower()
        return text

    def score(self, output: str, **kwargs: Any) -> ScoreResult:
        """Score based on exact match with expected output."""
        expected = kwargs.get("expected_output", "")

        if not output and not expected:
            return ScoreResult(
                value=1.0,
                name=self.name,
                reason="Both output and expected are empty",
            )

        if not expected:
            return ScoreResult(
                value=0.0,
                name=self.name,
                reason="No expected output provided",
            )

        normalized_output = self._normalize(output)
        normalized_expected = self._normalize(expected)

        is_match = normalized_output == normalized_expected
        return ScoreResult(
            value=1.0 if is_match else 0.0,
            name=self.name,
            reason="Exact match" if is_match else "Output does not match expected",
        )


class ContainsKeywordsMetric(BaseMetric):
    """Metric that checks if output contains required keywords.

    Returns a score based on the fraction of keywords found in the output.
    """

    def __init__(
        self,
        name: str = "contains_keywords",
        keywords: list[str] | None = None,
        case_sensitive: bool = False,
    ) -> None:
        """Initialize contains keywords metric.

        Args:
            name: Metric name
            keywords: List of required keywords (can also be passed in score())
            case_sensitive: Whether keyword matching is case-sensitive
        """
        super().__init__(name)
        self.keywords = keywords or []
        self.case_sensitive = case_sensitive

    def score(self, output: str, **kwargs: Any) -> ScoreResult:
        """Score based on presence of keywords."""
        # Get keywords from init or kwargs
        keywords = kwargs.get("keywords", self.keywords)

        if not keywords:
            return ScoreResult(
                value=1.0,
                name=self.name,
                reason="No keywords to check",
            )

        if not output:
            return ScoreResult(
                value=0.0,
                name=self.name,
                reason="Empty output",
            )

        check_output = output if self.case_sensitive else output.lower()
        found = []
        missing = []

        for keyword in keywords:
            check_keyword = keyword if self.case_sensitive else keyword.lower()
            if check_keyword in check_output:
                found.append(keyword)
            else:
                missing.append(keyword)

        score = len(found) / len(keywords)
        reason = f"Found {len(found)}/{len(keywords)} keywords"
        if missing:
            reason += f". Missing: {', '.join(missing)}"

        return ScoreResult(value=score, name=self.name, reason=reason)


class LengthMetric(BaseMetric):
    """Metric that evaluates response length.

    Scores based on whether output length falls within acceptable range.
    """

    def __init__(
        self,
        name: str = "length",
        min_length: int = 10,
        max_length: int = 1000,
        optimal_length: int | None = None,
    ) -> None:
        """Initialize length metric.

        Args:
            name: Metric name
            min_length: Minimum acceptable length
            max_length: Maximum acceptable length
            optimal_length: Optimal length (if provided, scores decay from this)
        """
        super().__init__(name)
        self.min_length = min_length
        self.max_length = max_length
        self.optimal_length = optimal_length

    def score(self, output: str, **kwargs: Any) -> ScoreResult:
        """Score based on output length."""
        length = len(output)

        if length < self.min_length:
            return ScoreResult(
                value=0.0,
                name=self.name,
                reason=f"Output too short ({length} < {self.min_length})",
            )

        if length > self.max_length:
            return ScoreResult(
                value=0.0,
                name=self.name,
                reason=f"Output too long ({length} > {self.max_length})",
            )

        # If no optimal length, score is 1.0 if within range
        if self.optimal_length is None:
            return ScoreResult(
                value=1.0,
                name=self.name,
                reason=f"Length {length} within acceptable range",
            )

        # Score decays based on distance from optimal
        if length <= self.optimal_length:
            range_size = self.optimal_length - self.min_length
            if range_size == 0:
                score = 1.0
            else:
                score = (length - self.min_length) / range_size
        else:
            range_size = self.max_length - self.optimal_length
            if range_size == 0:
                score = 1.0
            else:
                score = 1.0 - (length - self.optimal_length) / range_size

        return ScoreResult(
            value=max(0.0, score),
            name=self.name,
            reason=f"Length {length}, optimal {self.optimal_length}",
        )


class ResponseQualityMetric(BaseMetric):
    """Composite metric for overall response quality.

    Combines multiple quality signals into a single score.
    """

    def __init__(
        self,
        name: str = "response_quality",
        check_completeness: bool = True,
        check_coherence: bool = True,
        min_words: int = 5,
    ) -> None:
        """Initialize response quality metric.

        Args:
            name: Metric name
            check_completeness: Whether to check for complete sentences
            check_coherence: Whether to check for coherent structure
            min_words: Minimum number of words expected
        """
        super().__init__(name)
        self.check_completeness = check_completeness
        self.check_coherence = check_coherence
        self.min_words = min_words

    def score(self, output: str, **kwargs: Any) -> ScoreResult:
        """Score based on multiple quality factors."""
        if not output or not output.strip():
            return ScoreResult(
                value=0.0,
                name=self.name,
                reason="Empty output",
            )

        scores: list[float] = []
        reasons: list[str] = []

        # Check word count
        word_count = len(output.split())
        if word_count >= self.min_words:
            scores.append(1.0)
            reasons.append(f"Word count OK ({word_count})")
        else:
            scores.append(word_count / self.min_words)
            reasons.append(f"Low word count ({word_count}/{self.min_words})")

        # Check completeness (ends with punctuation)
        if self.check_completeness:
            if output.rstrip()[-1] in ".!?":
                scores.append(1.0)
                reasons.append("Complete sentence")
            else:
                scores.append(0.5)
                reasons.append("May be incomplete (no ending punctuation)")

        # Check coherence (no obvious issues)
        if self.check_coherence:
            issues = []
            if output.startswith((" ", "\t")):
                issues.append("starts with whitespace")
            if "  " in output:
                issues.append("has double spaces")
            if output.count("\n\n\n") > 0:
                issues.append("has excessive newlines")

            if not issues:
                scores.append(1.0)
                reasons.append("No coherence issues")
            else:
                scores.append(0.7)
                reasons.append(f"Coherence issues: {', '.join(issues)}")

        # Average all scores
        final_score = sum(scores) / len(scores) if scores else 0.0

        return ScoreResult(
            value=final_score,
            name=self.name,
            reason="; ".join(reasons),
        )


class SimilarityMetric(BaseMetric):
    """Metric that measures text similarity using various methods.

    Supports Levenshtein ratio, Jaccard similarity, and cosine similarity.
    """

    def __init__(
        self,
        name: str = "similarity",
        method: str = "jaccard",
    ) -> None:
        """Initialize similarity metric.

        Args:
            name: Metric name
            method: Similarity method - 'jaccard' or 'levenshtein'
        """
        super().__init__(name)
        self.method = method

    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def _levenshtein_ratio(self, s1: str, s2: str) -> float:
        """Calculate Levenshtein similarity ratio."""
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0

        # Simple Levenshtein distance implementation
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

        distance = dp[m][n]
        max_len = max(m, n)
        return 1.0 - (distance / max_len)

    def score(self, output: str, **kwargs: Any) -> ScoreResult:
        """Score based on similarity to expected output."""
        expected = kwargs.get("expected_output", "")

        if not expected:
            return ScoreResult(
                value=0.0,
                name=self.name,
                reason="No expected output for comparison",
            )

        if self.method == "jaccard":
            similarity = self._jaccard_similarity(output, expected)
        elif self.method == "levenshtein":
            similarity = self._levenshtein_ratio(output.lower(), expected.lower())
        else:
            return ScoreResult(
                value=0.0,
                name=self.name,
                reason=f"Unknown method: {self.method}",
            )

        return ScoreResult(
            value=similarity,
            name=self.name,
            reason=f"{self.method} similarity: {similarity:.2%}",
        )
