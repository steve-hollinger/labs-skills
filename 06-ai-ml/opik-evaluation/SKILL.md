---
name: evaluating-with-opik
description: LLM evaluation using the Opik framework, including tracing, metrics, and experiment tracking. Use when writing or improving tests.
---

# Opik Evaluation

## Quick Start
```python
from opik.evaluation import evaluate
from opik.evaluation.metrics import Equals

dataset = [
    {"input": "2+2", "expected_output": "4"},
]

def my_task(item):
    return {"output": call_llm(item["input"])}

results = evaluate(
    experiment_name="math-eval",
    dataset=dataset,
    task=my_task,
    scoring_metrics=[Equals(name="exact_match")],
    # ... see docs/patterns.md for more
```


## Key Points
- Evaluation
- Tracing
- Metrics

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples