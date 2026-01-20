"""Evaluation utilities for LLM applications.

This module provides helper classes for running evaluations on LLM outputs.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

import pandas as pd

from opik_evaluation.metrics import BaseMetric, ScoreResult


@dataclass
class EvaluationConfig:
    """Configuration for an evaluation run.

    Attributes:
        experiment_name: Name for this evaluation experiment
        metrics: List of metrics to compute
        parallel: Whether to run evaluations in parallel
        save_results: Whether to save results to disk
        output_dir: Directory for saving results
    """

    experiment_name: str
    metrics: list[BaseMetric] = field(default_factory=list)
    parallel: bool = False
    save_results: bool = True
    output_dir: str = "./evaluation_results"


@dataclass
class EvaluationResult:
    """Result of evaluating a single item.

    Attributes:
        input: The input that was evaluated
        output: The LLM output
        expected_output: The expected output (if provided)
        scores: Dictionary mapping metric names to ScoreResults
        metadata: Additional metadata about the evaluation
    """

    input: str
    output: str
    expected_output: str | None
    scores: dict[str, ScoreResult]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def average_score(self) -> float:
        """Calculate average score across all metrics."""
        if not self.scores:
            return 0.0
        return sum(s.value for s in self.scores.values()) / len(self.scores)


@dataclass
class ExperimentResults:
    """Results from a complete evaluation experiment.

    Attributes:
        experiment_name: Name of the experiment
        results: List of individual evaluation results
        config: The evaluation configuration used
        start_time: When the experiment started
        end_time: When the experiment ended
    """

    experiment_name: str
    results: list[EvaluationResult]
    config: EvaluationConfig
    start_time: datetime
    end_time: datetime | None = None

    @property
    def duration_seconds(self) -> float:
        """Calculate experiment duration in seconds."""
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()

    @property
    def average_scores(self) -> dict[str, float]:
        """Calculate average scores across all results for each metric."""
        if not self.results:
            return {}

        metric_totals: dict[str, float] = {}
        metric_counts: dict[str, int] = {}

        for result in self.results:
            for name, score in result.scores.items():
                metric_totals[name] = metric_totals.get(name, 0.0) + score.value
                metric_counts[name] = metric_counts.get(name, 0) + 1

        return {
            name: metric_totals[name] / metric_counts[name]
            for name in metric_totals
        }

    def to_dataframe(self) -> pd.DataFrame:
        """Convert results to a pandas DataFrame."""
        rows = []
        for result in self.results:
            row = {
                "input": result.input,
                "output": result.output,
                "expected_output": result.expected_output,
                "average_score": result.average_score,
            }
            for name, score in result.scores.items():
                row[f"score_{name}"] = score.value
                row[f"reason_{name}"] = score.reason
            row.update(result.metadata)
            rows.append(row)

        return pd.DataFrame(rows)

    def summary(self) -> str:
        """Generate a summary string of the results."""
        lines = [
            f"Experiment: {self.experiment_name}",
            f"Total samples: {len(self.results)}",
            f"Duration: {self.duration_seconds:.2f}s",
            "",
            "Average Scores:",
        ]

        for name, avg in self.average_scores.items():
            lines.append(f"  {name}: {avg:.2%}")

        return "\n".join(lines)


class Evaluator:
    """Evaluator for running LLM evaluations.

    This class manages the evaluation process, applying metrics to
    LLM outputs and collecting results.
    """

    def __init__(self, config: EvaluationConfig) -> None:
        """Initialize the evaluator.

        Args:
            config: Evaluation configuration
        """
        self.config = config

    def evaluate_single(
        self,
        input_text: str,
        output: str,
        expected_output: str | None = None,
        **metadata: Any,
    ) -> EvaluationResult:
        """Evaluate a single LLM output.

        Args:
            input_text: The input prompt
            output: The LLM's output
            expected_output: The expected output (optional)
            **metadata: Additional metadata to store

        Returns:
            EvaluationResult with all metric scores
        """
        scores: dict[str, ScoreResult] = {}

        for metric in self.config.metrics:
            score = metric.score(
                output=output,
                input=input_text,
                expected_output=expected_output,
            )
            scores[metric.name] = score

        return EvaluationResult(
            input=input_text,
            output=output,
            expected_output=expected_output,
            scores=scores,
            metadata=metadata,
        )

    def evaluate_batch(
        self,
        dataset: list[dict[str, Any]],
        task: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
    ) -> ExperimentResults:
        """Evaluate a batch of items.

        Args:
            dataset: List of dictionaries with 'input' and optionally 'expected_output'
            task: Optional function to generate outputs (if not in dataset)

        Returns:
            ExperimentResults containing all evaluation results
        """
        start_time = datetime.now()
        results: list[EvaluationResult] = []

        for item in dataset:
            input_text = item.get("input", "")

            # Get output from task or dataset
            if task is not None:
                task_result = task(item)
                output = task_result.get("output", "")
            else:
                output = item.get("output", "")

            expected_output = item.get("expected_output")

            # Get any additional fields as metadata
            metadata = {
                k: v
                for k, v in item.items()
                if k not in ("input", "output", "expected_output")
            }

            result = self.evaluate_single(
                input_text=input_text,
                output=output,
                expected_output=expected_output,
                **metadata,
            )
            results.append(result)

        end_time = datetime.now()

        return ExperimentResults(
            experiment_name=self.config.experiment_name,
            results=results,
            config=self.config,
            start_time=start_time,
            end_time=end_time,
        )

    def save_results(self, results: ExperimentResults) -> str:
        """Save evaluation results to a file.

        Args:
            results: The experiment results to save

        Returns:
            Path to the saved file
        """
        import os

        os.makedirs(self.config.output_dir, exist_ok=True)

        timestamp = results.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config.experiment_name}_{timestamp}.csv"
        filepath = os.path.join(self.config.output_dir, filename)

        df = results.to_dataframe()
        df.to_csv(filepath, index=False)

        return filepath


def create_simple_evaluator(
    experiment_name: str,
    metrics: list[BaseMetric],
) -> Evaluator:
    """Create an evaluator with default configuration.

    Args:
        experiment_name: Name for the experiment
        metrics: List of metrics to use

    Returns:
        Configured Evaluator instance
    """
    config = EvaluationConfig(
        experiment_name=experiment_name,
        metrics=metrics,
    )
    return Evaluator(config)
