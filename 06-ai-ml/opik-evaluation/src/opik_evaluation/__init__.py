"""Opik Evaluation - LLM evaluation and tracing patterns.

This module provides utilities and patterns for evaluating LLM applications
using the Opik framework.
"""

from opik_evaluation.evaluator import Evaluator, EvaluationConfig, EvaluationResult
from opik_evaluation.metrics import (
    AccuracyMetric,
    ContainsKeywordsMetric,
    LengthMetric,
    ResponseQualityMetric,
)

__all__ = [
    "Evaluator",
    "EvaluationConfig",
    "EvaluationResult",
    "AccuracyMetric",
    "ContainsKeywordsMetric",
    "LengthMetric",
    "ResponseQualityMetric",
]

__version__ = "0.1.0"
