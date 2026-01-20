# Core Concepts

## Overview

LLM evaluation is the practice of measuring the quality of language model outputs against various criteria. This skill covers evaluation concepts, metrics, tracing, and experiment tracking using patterns inspired by the Opik framework.

## Concept 1: LLM Evaluation Fundamentals

### What It Is

LLM evaluation is the systematic measurement of language model output quality. Unlike traditional software testing, LLM outputs are often subjective and require specialized metrics.

### Why It Matters

- **Quality Assurance**: Ensure LLM outputs meet standards before deployment
- **Regression Detection**: Catch quality degradation when models change
- **Comparison**: Compare different models, prompts, or configurations
- **Optimization**: Guide prompt engineering and fine-tuning efforts

### How It Works

Evaluation follows a standard pipeline:

```python
# 1. Define test cases
dataset = [
    {"input": "What is 2+2?", "expected_output": "4"},
    {"input": "Capital of France?", "expected_output": "Paris"},
]

# 2. Generate outputs
for item in dataset:
    item["output"] = llm.generate(item["input"])

# 3. Score with metrics
metrics = [AccuracyMetric(), SimilarityMetric()]
scores = []
for item in dataset:
    for metric in metrics:
        score = metric.score(item["output"], expected_output=item["expected_output"])
        scores.append(score)

# 4. Analyze results
average_score = sum(s.value for s in scores) / len(scores)
```

## Concept 2: Evaluation Metrics

### What It Is

Metrics are functions that quantify specific aspects of LLM output quality. They take an output (and optionally expected output or input) and return a score.

### Why It Matters

- **Objectivity**: Provide consistent, reproducible measurements
- **Focus**: Different metrics capture different quality aspects
- **Automation**: Enable automated testing and CI/CD integration

### How It Works

Metrics implement a common interface:

```python
class BaseMetric:
    def __init__(self, name: str):
        self.name = name

    def score(self, output: str, **kwargs) -> ScoreResult:
        """Return a score between 0.0 and 1.0 with explanation."""
        raise NotImplementedError

@dataclass
class ScoreResult:
    value: float      # 0.0 to 1.0
    name: str         # Metric name
    reason: str = ""  # Explanation
```

Common metric types:

| Metric Type | What It Measures | Example Use Case |
|-------------|-----------------|------------------|
| Accuracy | Exact match | Q&A systems |
| Similarity | Text closeness | Paraphrasing |
| Contains | Keyword presence | Fact checking |
| Length | Response size | Format compliance |
| Fluency | Grammar/style | Content generation |
| Relevance | Topic alignment | Search/RAG |

## Concept 3: Tracing and Observability

### What It Is

Tracing records the execution flow of LLM applications, capturing inputs, outputs, timing, and metadata at each step.

### Why It Matters

- **Debugging**: Understand why outputs are good or bad
- **Performance**: Identify slow operations
- **Cost**: Track token usage and API calls
- **Compliance**: Maintain audit trails

### How It Works

Tracing uses decorators and context managers:

```python
@track
def rag_pipeline(query: str) -> str:
    """This function is traced - all sub-calls are recorded."""
    # Span 1: Retrieval
    context = retrieve_documents(query)

    # Span 2: Generation
    response = generate_response(query, context)

    return response
```

Trace data includes:
- Function name and parameters
- Start and end timestamps
- Return value or error
- Parent-child relationships (for nested calls)

## Concept 4: Experiments and Comparison

### What It Is

Experiments are named evaluation runs that allow comparing different configurations, models, or prompts over time.

### Why It Matters

- **Reproducibility**: Track exactly what was evaluated
- **Comparison**: A/B test different approaches
- **Progress**: Monitor improvement over time
- **Documentation**: Record what works and what doesn't

### How It Works

```python
# Run multiple experiments
configs = [
    {"name": "baseline", "temperature": 0.7},
    {"name": "creative", "temperature": 1.0},
    {"name": "precise", "temperature": 0.3},
]

results = []
for config in configs:
    evaluator = Evaluator(EvaluationConfig(
        experiment_name=config["name"],
        metrics=[AccuracyMetric()],
    ))

    # Configure LLM with this config
    llm.temperature = config["temperature"]

    # Run evaluation
    result = evaluator.evaluate_batch(dataset)
    results.append(result)

# Compare experiments
for result in results:
    print(f"{result.experiment_name}: {result.average_scores}")
```

## Concept 5: Custom Metrics

### What It Is

Custom metrics are domain-specific scoring functions that capture quality aspects unique to your application.

### Why It Matters

- **Domain Relevance**: Generic metrics may miss important factors
- **Business Logic**: Incorporate business rules into evaluation
- **Flexibility**: Adapt to specific use cases

### How It Works

```python
class MedicalAccuracyMetric(BaseMetric):
    """Custom metric for medical Q&A systems."""

    def __init__(self, medical_db: dict):
        super().__init__(name="medical_accuracy")
        self.medical_db = medical_db

    def score(self, output: str, **kwargs) -> ScoreResult:
        input_text = kwargs.get("input", "")

        # Check for medical accuracy
        if self._contains_dangerous_advice(output):
            return ScoreResult(
                value=0.0,
                name=self.name,
                reason="Contains potentially dangerous medical advice",
            )

        # Check against medical database
        accuracy = self._verify_facts(output, self.medical_db)

        return ScoreResult(
            value=accuracy,
            name=self.name,
            reason=f"Verified {accuracy:.0%} of medical facts",
        )
```

Guidelines for custom metrics:

1. **Return 0.0 to 1.0**: Normalized scores enable comparison
2. **Provide reasons**: Explain why the score was given
3. **Handle edge cases**: Empty inputs, missing expected outputs
4. **Be deterministic**: Same inputs should produce same scores

## Summary

Key takeaways:

1. **Evaluation Pipeline**: Dataset -> Generation -> Scoring -> Analysis

2. **Metrics Measure Quality**: Use appropriate metrics for your use case

3. **Tracing Provides Visibility**: Record execution for debugging and analysis

4. **Experiments Enable Comparison**: Name and track evaluation runs

5. **Custom Metrics Add Value**: Domain-specific evaluation catches important issues

These concepts work together to create a robust evaluation system for LLM applications.
