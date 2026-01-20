"""Tests for Opik Evaluation examples."""

import pytest

from opik_evaluation.evaluator import (
    Evaluator,
    EvaluationConfig,
    EvaluationResult,
    ExperimentResults,
    create_simple_evaluator,
)
from opik_evaluation.metrics import (
    AccuracyMetric,
    BaseMetric,
    ContainsKeywordsMetric,
    LengthMetric,
    ResponseQualityMetric,
    ScoreResult,
    SimilarityMetric,
)


class TestScoreResult:
    """Tests for ScoreResult dataclass."""

    def test_creation(self) -> None:
        """Test creating a ScoreResult."""
        result = ScoreResult(value=0.85, name="test", reason="Good match")

        assert result.value == 0.85
        assert result.name == "test"
        assert result.reason == "Good match"

    def test_default_reason(self) -> None:
        """Test ScoreResult with default empty reason."""
        result = ScoreResult(value=1.0, name="test")
        assert result.reason == ""


class TestAccuracyMetric:
    """Tests for AccuracyMetric."""

    def test_exact_match(self) -> None:
        """Test exact match returns 1.0."""
        metric = AccuracyMetric()
        result = metric.score("Paris", expected_output="Paris")
        assert result.value == 1.0

    def test_case_insensitive(self) -> None:
        """Test case insensitive matching."""
        metric = AccuracyMetric(case_sensitive=False)
        result = metric.score("PARIS", expected_output="paris")
        assert result.value == 1.0

    def test_case_sensitive(self) -> None:
        """Test case sensitive matching."""
        metric = AccuracyMetric(case_sensitive=True)
        result = metric.score("PARIS", expected_output="Paris")
        assert result.value == 0.0

    def test_whitespace_normalization(self) -> None:
        """Test whitespace normalization."""
        metric = AccuracyMetric(normalize_whitespace=True)
        result = metric.score("Hello  World", expected_output="Hello World")
        assert result.value == 1.0

    def test_no_expected_output(self) -> None:
        """Test handling missing expected output."""
        metric = AccuracyMetric()
        result = metric.score("Some output")
        assert result.value == 0.0


class TestContainsKeywordsMetric:
    """Tests for ContainsKeywordsMetric."""

    def test_all_keywords_present(self) -> None:
        """Test when all keywords are found."""
        metric = ContainsKeywordsMetric(keywords=["Paris", "France"])
        result = metric.score("The capital of France is Paris.")
        assert result.value == 1.0

    def test_some_keywords_present(self) -> None:
        """Test partial keyword match."""
        metric = ContainsKeywordsMetric(keywords=["Paris", "London"])
        result = metric.score("I visited Paris last summer.")
        assert result.value == 0.5

    def test_no_keywords_present(self) -> None:
        """Test when no keywords are found."""
        metric = ContainsKeywordsMetric(keywords=["Tokyo", "Japan"])
        result = metric.score("I visited Paris last summer.")
        assert result.value == 0.0

    def test_case_insensitive_keywords(self) -> None:
        """Test case insensitive keyword matching."""
        metric = ContainsKeywordsMetric(keywords=["PARIS"], case_sensitive=False)
        result = metric.score("paris is beautiful")
        assert result.value == 1.0


class TestLengthMetric:
    """Tests for LengthMetric."""

    def test_within_range(self) -> None:
        """Test output within acceptable range."""
        metric = LengthMetric(min_length=5, max_length=50)
        result = metric.score("This is a test output.")
        assert result.value == 1.0

    def test_too_short(self) -> None:
        """Test output too short."""
        metric = LengthMetric(min_length=50, max_length=100)
        result = metric.score("Short")
        assert result.value == 0.0

    def test_too_long(self) -> None:
        """Test output too long."""
        metric = LengthMetric(min_length=5, max_length=10)
        result = metric.score("This is a much longer output than allowed.")
        assert result.value == 0.0

    def test_optimal_length_scoring(self) -> None:
        """Test scoring based on optimal length."""
        metric = LengthMetric(min_length=10, max_length=100, optimal_length=50)
        # Exactly optimal
        result = metric.score("x" * 50)
        assert result.value > 0.9


class TestSimilarityMetric:
    """Tests for SimilarityMetric."""

    def test_jaccard_identical(self) -> None:
        """Test Jaccard similarity for identical texts."""
        metric = SimilarityMetric(method="jaccard")
        result = metric.score("hello world", expected_output="hello world")
        assert result.value == 1.0

    def test_jaccard_different(self) -> None:
        """Test Jaccard similarity for different texts."""
        metric = SimilarityMetric(method="jaccard")
        result = metric.score("hello world", expected_output="goodbye moon")
        assert result.value == 0.0

    def test_jaccard_partial(self) -> None:
        """Test Jaccard similarity for partially matching texts."""
        metric = SimilarityMetric(method="jaccard")
        result = metric.score("hello world", expected_output="hello moon")
        # 1 word in common out of 3 unique words
        assert 0.3 <= result.value <= 0.4

    def test_levenshtein_identical(self) -> None:
        """Test Levenshtein similarity for identical texts."""
        metric = SimilarityMetric(method="levenshtein")
        result = metric.score("hello", expected_output="hello")
        assert result.value == 1.0

    def test_levenshtein_similar(self) -> None:
        """Test Levenshtein similarity for similar texts."""
        metric = SimilarityMetric(method="levenshtein")
        result = metric.score("hello", expected_output="hallo")
        # 1 edit out of 5 characters
        assert result.value == 0.8


class TestResponseQualityMetric:
    """Tests for ResponseQualityMetric."""

    def test_high_quality(self) -> None:
        """Test high quality response."""
        metric = ResponseQualityMetric()
        result = metric.score("This is a complete and well-formed response.")
        assert result.value > 0.8

    def test_empty_output(self) -> None:
        """Test empty output."""
        metric = ResponseQualityMetric()
        result = metric.score("")
        assert result.value == 0.0

    def test_incomplete_sentence(self) -> None:
        """Test incomplete sentence (no punctuation)."""
        metric = ResponseQualityMetric(check_completeness=True)
        result = metric.score("This is an incomplete response")
        assert result.value < 1.0


class TestEvaluator:
    """Tests for the Evaluator class."""

    def test_evaluate_single(self) -> None:
        """Test evaluating a single item."""
        config = EvaluationConfig(
            experiment_name="test",
            metrics=[AccuracyMetric()],
        )
        evaluator = Evaluator(config)

        result = evaluator.evaluate_single(
            input_text="What is 2+2?",
            output="4",
            expected_output="4",
        )

        assert isinstance(result, EvaluationResult)
        assert result.input == "What is 2+2?"
        assert result.output == "4"
        assert "accuracy" in result.scores

    def test_evaluate_batch(self) -> None:
        """Test batch evaluation."""
        config = EvaluationConfig(
            experiment_name="batch-test",
            metrics=[AccuracyMetric()],
        )
        evaluator = Evaluator(config)

        dataset = [
            {"input": "Q1", "output": "A1", "expected_output": "A1"},
            {"input": "Q2", "output": "A2", "expected_output": "A2"},
        ]

        results = evaluator.evaluate_batch(dataset)

        assert isinstance(results, ExperimentResults)
        assert len(results.results) == 2
        assert results.experiment_name == "batch-test"

    def test_evaluate_with_task(self) -> None:
        """Test evaluation with task function."""
        config = EvaluationConfig(
            experiment_name="task-test",
            metrics=[AccuracyMetric()],
        )
        evaluator = Evaluator(config)

        dataset = [
            {"input": "2+2", "expected_output": "4"},
        ]

        def mock_task(item: dict) -> dict:
            return {"output": "4"}

        results = evaluator.evaluate_batch(dataset, task=mock_task)

        assert len(results.results) == 1
        assert results.results[0].output == "4"


class TestExperimentResults:
    """Tests for ExperimentResults."""

    def test_average_scores(self) -> None:
        """Test calculating average scores."""
        results = [
            EvaluationResult(
                input="q1",
                output="a1",
                expected_output="a1",
                scores={"accuracy": ScoreResult(value=1.0, name="accuracy")},
            ),
            EvaluationResult(
                input="q2",
                output="a2",
                expected_output="a2",
                scores={"accuracy": ScoreResult(value=0.5, name="accuracy")},
            ),
        ]

        from datetime import datetime

        exp = ExperimentResults(
            experiment_name="test",
            results=results,
            config=EvaluationConfig(experiment_name="test"),
            start_time=datetime.now(),
        )

        assert exp.average_scores["accuracy"] == 0.75

    def test_to_dataframe(self) -> None:
        """Test converting to DataFrame."""
        results = [
            EvaluationResult(
                input="q1",
                output="a1",
                expected_output="a1",
                scores={"accuracy": ScoreResult(value=1.0, name="accuracy")},
            ),
        ]

        from datetime import datetime

        exp = ExperimentResults(
            experiment_name="test",
            results=results,
            config=EvaluationConfig(experiment_name="test"),
            start_time=datetime.now(),
        )

        df = exp.to_dataframe()

        assert len(df) == 1
        assert "input" in df.columns
        assert "score_accuracy" in df.columns


class TestCreateSimpleEvaluator:
    """Tests for create_simple_evaluator helper."""

    def test_creates_evaluator(self) -> None:
        """Test helper creates configured evaluator."""
        evaluator = create_simple_evaluator(
            experiment_name="simple-test",
            metrics=[AccuracyMetric(), LengthMetric()],
        )

        assert isinstance(evaluator, Evaluator)
        assert evaluator.config.experiment_name == "simple-test"
        assert len(evaluator.config.metrics) == 2
