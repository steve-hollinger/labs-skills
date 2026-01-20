# CLAUDE.md - Opik Evaluation Framework

This skill teaches LLM evaluation using the Opik framework, including tracing, metrics, and experiment tracking.

## Key Concepts

- **Evaluation**: Measuring LLM output quality against ground truth or criteria
- **Tracing**: Recording LLM calls with inputs, outputs, and metadata
- **Metrics**: Functions that score LLM outputs (accuracy, relevance, etc.)
- **Experiments**: Named evaluation runs for comparison and tracking
- **Datasets**: Collections of test cases with inputs and expected outputs

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run specific example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
opik-evaluation/
├── src/opik_evaluation/
│   ├── __init__.py
│   ├── metrics.py        # Custom metrics
│   ├── evaluator.py      # Evaluation helpers
│   ├── tracing.py        # Tracing utilities
│   └── examples/
│       ├── example_1.py  # Basic evaluation
│       ├── example_2.py  # Tracing
│       └── example_3.py  # Custom metrics
├── exercises/
│   ├── exercise_1.py
│   ├── exercise_2.py
│   ├── exercise_3.py
│   └── solutions/
├── tests/
│   └── test_examples.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Evaluation
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
)
```

### Pattern 2: Tracing Functions
```python
from opik import track

@track
def llm_pipeline(query: str) -> str:
    # This function is traced
    context = retrieve_context(query)
    response = generate_response(query, context)
    return response
```

### Pattern 3: Custom Metric
```python
from opik.evaluation.metrics import BaseMetric, ScoreResult

class RelevanceMetric(BaseMetric):
    def __init__(self):
        super().__init__(name="relevance")

    def score(self, output: str, input: str, **kwargs) -> ScoreResult:
        # Check if output is relevant to input
        relevance = calculate_relevance(output, input)
        return ScoreResult(value=relevance, name=self.name)
```

## Common Mistakes

1. **Missing expected outputs**
   - Evaluation needs ground truth data
   - Include "expected_output" in dataset items

2. **Not awaiting async traces**
   - Async functions need proper await
   - Use `async with` for span contexts

3. **Ignoring metric errors**
   - Handle None/empty values gracefully
   - Return 0.0 score with reason for failures

4. **Not configuring Opik**
   - Set OPIK_API_KEY environment variable
   - Or use local file-based storage for development

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make example-1`. The basic evaluation example shows the core workflow.

### "How do I create custom metrics?"
Direct them to example-3 which shows extending BaseMetric. Key methods are `__init__` and `score`.

### "How do I trace my LLM calls?"
Show the @track decorator from example-2. It automatically captures inputs, outputs, and timing.

### "How do I compare experiments?"
Opik tracks experiments by name. Run with different experiment names and compare in the UI or export results.

## Testing Notes

- Tests use pytest with pytest-asyncio for async tests
- Mock LLM calls for unit tests
- Use small datasets for fast tests
- Mark slow tests with @pytest.mark.slow

## Dependencies

Key dependencies in pyproject.toml:
- opik: Main evaluation framework
- openai: For LLM API calls (optional)
- pandas: For result analysis
- pytest-asyncio: For async testing
