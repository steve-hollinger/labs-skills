# Opik Evaluation Framework

Learn to evaluate LLM applications using Opik. This skill teaches how to measure LLM quality, track experiments, analyze traces, and implement evaluation metrics for AI applications.

## Learning Objectives

After completing this skill, you will be able to:
- Understand LLM evaluation concepts and metrics
- Use Opik for tracing LLM interactions
- Implement custom evaluation metrics
- Run evaluation experiments and compare results
- Analyze evaluation data for insights
- Build evaluation pipelines for CI/CD

## Prerequisites

- Python 3.11+
- UV package manager
- Basic understanding of LLMs and prompts
- Familiarity with async Python

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### LLM Evaluation Overview

Evaluating LLM outputs is crucial for building reliable AI applications. Key aspects include:

```python
from opik import Opik
from opik.evaluation import evaluate
from opik.evaluation.metrics import Equals, Contains, LevenshteinRatio

# Initialize Opik client
client = Opik()

# Define evaluation metrics
metrics = [
    Equals(name="exact_match"),
    Contains(name="contains_answer"),
    LevenshteinRatio(name="text_similarity"),
]

# Run evaluation
results = evaluate(
    experiment_name="qa-evaluation",
    dataset=dataset,
    task=my_llm_task,
    scoring_metrics=metrics,
)
```

### Tracing LLM Calls

Opik provides decorators and context managers for tracing:

```python
from opik import track

@track
def process_query(query: str) -> str:
    """Traced function - Opik records inputs, outputs, and timing."""
    response = llm.generate(query)
    return response

# Traces are automatically sent to Opik
result = process_query("What is the capital of France?")
```

### Evaluation Metrics

Opik includes built-in metrics and supports custom metrics:

```python
from opik.evaluation.metrics import BaseMetric, ScoreResult

class CustomMetric(BaseMetric):
    """Custom metric for domain-specific evaluation."""

    def __init__(self, name: str = "custom_metric"):
        super().__init__(name=name)

    def score(self, output: str, expected: str, **kwargs) -> ScoreResult:
        # Your evaluation logic
        score = calculate_score(output, expected)
        return ScoreResult(
            value=score,
            name=self.name,
            reason="Explanation of the score",
        )
```

## Examples

### Example 1: Basic Evaluation

Running a simple evaluation with built-in metrics.

```bash
make example-1
```

### Example 2: Tracing and Spans

Using Opik's tracing to monitor LLM applications.

```bash
make example-2
```

### Example 3: Custom Metrics and Experiments

Building custom evaluation metrics and running experiments.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Evaluate a Q&A system with accuracy metrics
2. **Exercise 2**: Create a custom metric for response quality
3. **Exercise 3**: Build an evaluation pipeline for a chatbot

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Not Setting Expected Values
Evaluation requires ground truth data:
```python
# Good: Include expected outputs in dataset
dataset = [
    {"input": "What is 2+2?", "expected_output": "4"},
    {"input": "Capital of France?", "expected_output": "Paris"},
]
```

### Forgetting Async in Traces
When using async functions with tracing:
```python
from opik import track

@track  # Works with async too
async def async_llm_call(prompt: str) -> str:
    return await async_llm.generate(prompt)
```

### Not Handling Metric Errors
Metrics should handle edge cases gracefully:
```python
def score(self, output: str, expected: str, **kwargs) -> ScoreResult:
    if not output or not expected:
        return ScoreResult(value=0.0, name=self.name, reason="Empty input")
    # Normal scoring logic...
```

## Further Reading

- [Opik Documentation](https://www.comet.com/docs/opik/)
- Related skills in this repository:
  - [Pydantic V2](../../01-language-frameworks/python/pydantic-v2/) - Data validation
  - [pytest Markers](../../03-testing/python/pytest-markers/) - Testing patterns
