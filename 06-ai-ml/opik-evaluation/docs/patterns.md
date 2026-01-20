# Common Patterns

## Overview

This document covers common patterns and best practices for evaluating LLM applications.

## Pattern 1: Dataset Design

### When to Use

When creating evaluation datasets for LLM testing.

### Implementation

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class TestCase:
    input: str
    expected_output: str
    metadata: dict[str, Any] = None

    def to_dict(self) -> dict:
        return {
            "input": self.input,
            "expected_output": self.expected_output,
            **(self.metadata or {}),
        }

def create_diverse_dataset() -> list[dict]:
    """Create a dataset with diverse test cases."""
    cases = []

    # Edge cases
    cases.append(TestCase(
        input="",
        expected_output="I need more information to help you.",
        metadata={"category": "edge_case"},
    ))

    # Normal cases
    cases.append(TestCase(
        input="What is 2+2?",
        expected_output="4",
        metadata={"category": "math", "difficulty": "easy"},
    ))

    # Complex cases
    cases.append(TestCase(
        input="Explain quantum entanglement in simple terms.",
        expected_output="...",  # Multiple acceptable answers
        metadata={"category": "science", "difficulty": "hard"},
    ))

    return [c.to_dict() for c in cases]
```

### Example

```python
# Good dataset characteristics:
# 1. Representative: Covers real-world use cases
# 2. Diverse: Different types, difficulties, edge cases
# 3. Labeled: Clear expected outputs or quality labels
# 4. Balanced: Fair distribution across categories

dataset = [
    # Category: Simple Q&A
    {"input": "What is the capital of France?", "expected_output": "Paris", "category": "qa"},
    {"input": "Who wrote Romeo and Juliet?", "expected_output": "Shakespeare", "category": "qa"},

    # Category: Reasoning
    {"input": "If A > B and B > C, is A > C?", "expected_output": "Yes", "category": "reasoning"},

    # Category: Edge cases
    {"input": "", "expected_output": "Please provide a question.", "category": "edge"},
    {"input": "??!!", "expected_output": "I don't understand.", "category": "edge"},
]
```

### Pitfalls to Avoid

- Don't make all test cases easy
- Include edge cases and error conditions
- Avoid bias toward common scenarios

## Pattern 2: Metric Composition

### When to Use

When you need to combine multiple metrics into a single quality score.

### Implementation

```python
class CompositeMetric(BaseMetric):
    """Combine multiple metrics with weights."""

    def __init__(
        self,
        name: str,
        metrics: list[BaseMetric],
        weights: list[float] | None = None,
    ):
        super().__init__(name)
        self.metrics = metrics
        self.weights = weights or [1.0] * len(metrics)
        assert len(self.weights) == len(self.metrics)

    def score(self, output: str, **kwargs) -> ScoreResult:
        scores = []
        reasons = []

        for metric, weight in zip(self.metrics, self.weights):
            result = metric.score(output, **kwargs)
            scores.append(result.value * weight)
            reasons.append(f"{metric.name}: {result.value:.2f}")

        total_weight = sum(self.weights)
        final_score = sum(scores) / total_weight

        return ScoreResult(
            value=final_score,
            name=self.name,
            reason="; ".join(reasons),
        )
```

### Example

```python
# Create a composite quality metric
quality_metric = CompositeMetric(
    name="overall_quality",
    metrics=[
        AccuracyMetric(),           # 40% weight
        SimilarityMetric(),         # 30% weight
        ResponseQualityMetric(),    # 30% weight
    ],
    weights=[0.4, 0.3, 0.3],
)

# Single score that combines all aspects
result = quality_metric.score(output, expected_output=expected)
print(f"Overall quality: {result.value:.2%}")
```

### Pitfalls to Avoid

- Don't weight all metrics equally without justification
- Consider metric correlations (redundant metrics)
- Document weight choices

## Pattern 3: Evaluation Pipeline

### When to Use

When building automated evaluation workflows for CI/CD.

### Implementation

```python
from typing import Callable
import json
from datetime import datetime

class EvaluationPipeline:
    """Automated evaluation pipeline."""

    def __init__(self, name: str):
        self.name = name
        self.stages: list[Callable] = []

    def add_stage(self, stage: Callable) -> "EvaluationPipeline":
        self.stages.append(stage)
        return self

    def run(self, dataset: list[dict]) -> dict:
        """Run all pipeline stages."""
        context = {
            "dataset": dataset,
            "results": {},
            "start_time": datetime.now(),
        }

        for stage in self.stages:
            context = stage(context)

        context["end_time"] = datetime.now()
        return context

# Define stages
def load_data_stage(ctx):
    """Load and validate dataset."""
    ctx["dataset_size"] = len(ctx["dataset"])
    return ctx

def generate_outputs_stage(ctx):
    """Generate LLM outputs."""
    for item in ctx["dataset"]:
        item["output"] = generate(item["input"])
    return ctx

def evaluate_stage(ctx):
    """Run evaluation metrics."""
    evaluator = create_simple_evaluator("pipeline", [AccuracyMetric()])
    ctx["results"] = evaluator.evaluate_batch(ctx["dataset"])
    return ctx

def check_threshold_stage(ctx):
    """Fail if scores below threshold."""
    threshold = 0.8
    avg = ctx["results"].average_scores.get("accuracy", 0)
    ctx["passed"] = avg >= threshold
    return ctx
```

### Example

```python
# Build and run pipeline
pipeline = (
    EvaluationPipeline("qa-pipeline")
    .add_stage(load_data_stage)
    .add_stage(generate_outputs_stage)
    .add_stage(evaluate_stage)
    .add_stage(check_threshold_stage)
)

result = pipeline.run(dataset)

if not result["passed"]:
    raise Exception("Evaluation failed threshold check!")
```

### Pitfalls to Avoid

- Don't ignore pipeline failures in CI/CD
- Log intermediate results for debugging
- Set appropriate thresholds

## Pattern 4: A/B Testing

### When to Use

When comparing two or more LLM configurations.

### Implementation

```python
def run_ab_test(
    dataset: list[dict],
    variants: dict[str, Callable],
    metrics: list[BaseMetric],
) -> dict:
    """Run A/B test across variants."""
    results = {}

    for variant_name, generate_fn in variants.items():
        # Generate outputs with this variant
        variant_data = [item.copy() for item in dataset]
        for item in variant_data:
            item["output"] = generate_fn(item["input"])

        # Evaluate
        evaluator = create_simple_evaluator(variant_name, metrics)
        result = evaluator.evaluate_batch(variant_data)
        results[variant_name] = result

    return results

def compare_variants(results: dict) -> str:
    """Compare variant results and determine winner."""
    scores = {}
    for name, result in results.items():
        avg = sum(result.average_scores.values()) / len(result.average_scores)
        scores[name] = avg

    winner = max(scores, key=scores.get)
    return winner
```

### Example

```python
# Define variants
def baseline_generate(input: str) -> str:
    return llm.generate(input, temperature=0.7)

def improved_generate(input: str) -> str:
    return llm.generate(input, temperature=0.5, max_tokens=200)

# Run A/B test
results = run_ab_test(
    dataset=test_dataset,
    variants={
        "baseline": baseline_generate,
        "improved": improved_generate,
    },
    metrics=[AccuracyMetric(), SimilarityMetric()],
)

# Find winner
winner = compare_variants(results)
print(f"Winner: {winner}")
```

## Pattern 5: Error Analysis

### When to Use

When you need to understand why evaluation scores are low.

### Implementation

```python
def analyze_errors(results: ExperimentResults) -> dict:
    """Analyze evaluation errors."""
    analysis = {
        "low_scores": [],
        "patterns": {},
        "recommendations": [],
    }

    for result in results.results:
        for metric_name, score in result.scores.items():
            if score.value < 0.5:  # Low score threshold
                analysis["low_scores"].append({
                    "input": result.input,
                    "output": result.output,
                    "expected": result.expected_output,
                    "metric": metric_name,
                    "score": score.value,
                    "reason": score.reason,
                })

    # Find patterns in low scores
    for error in analysis["low_scores"]:
        # Group by metric
        metric = error["metric"]
        if metric not in analysis["patterns"]:
            analysis["patterns"][metric] = []
        analysis["patterns"][metric].append(error)

    # Generate recommendations
    for metric, errors in analysis["patterns"].items():
        if len(errors) > 2:
            analysis["recommendations"].append(
                f"Investigate {metric}: {len(errors)} failures"
            )

    return analysis
```

### Example

```python
# Run evaluation
results = evaluator.evaluate_batch(dataset)

# Analyze errors
analysis = analyze_errors(results)

print("Error Analysis:")
print(f"  Low score cases: {len(analysis['low_scores'])}")

for metric, errors in analysis["patterns"].items():
    print(f"\n  {metric} failures:")
    for error in errors[:3]:  # Show first 3
        print(f"    Input: {error['input'][:50]}...")
        print(f"    Reason: {error['reason']}")

print("\nRecommendations:")
for rec in analysis["recommendations"]:
    print(f"  - {rec}")
```

## Anti-Patterns

### Anti-Pattern 1: Single Metric Evaluation

Using only one metric to evaluate complex outputs.

```python
# Bad: Single metric
result = evaluate(metrics=[AccuracyMetric()])
```

### Better Approach

Use multiple metrics that capture different quality aspects:

```python
# Good: Multiple metrics
result = evaluate(metrics=[
    AccuracyMetric(),
    SimilarityMetric(),
    ResponseQualityMetric(),
    LengthMetric(),
])
```

### Anti-Pattern 2: Overfitting to Test Data

Tuning prompts to pass specific test cases without generalizing.

### Better Approach

- Use separate training and test sets
- Test on unseen data periodically
- Monitor production performance

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| New project | Dataset Design + Metric Composition |
| CI/CD integration | Evaluation Pipeline |
| Model comparison | A/B Testing |
| Quality debugging | Error Analysis |
| Production monitoring | Tracing + Alerting |
