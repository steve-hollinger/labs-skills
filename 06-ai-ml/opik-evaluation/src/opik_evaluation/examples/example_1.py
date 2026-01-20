"""Example 1: Basic Evaluation with Built-in Metrics

This example demonstrates running a simple evaluation on LLM outputs
using various metrics to measure quality.

Key concepts:
- Creating an evaluation dataset
- Using built-in metrics (accuracy, similarity, etc.)
- Running evaluations and analyzing results
- Interpreting metric scores
"""

from opik_evaluation.evaluator import Evaluator, EvaluationConfig, create_simple_evaluator
from opik_evaluation.metrics import (
    AccuracyMetric,
    ContainsKeywordsMetric,
    LengthMetric,
    SimilarityMetric,
)


def main() -> None:
    """Run the basic evaluation example."""
    print("Example 1: Basic Evaluation with Built-in Metrics")
    print("=" * 60)

    # Define a test dataset with inputs and expected outputs
    dataset = [
        {
            "input": "What is the capital of France?",
            "expected_output": "Paris",
            "output": "The capital of France is Paris.",  # Simulated LLM output
        },
        {
            "input": "What is 2 + 2?",
            "expected_output": "4",
            "output": "2 + 2 equals 4.",
        },
        {
            "input": "Who wrote Romeo and Juliet?",
            "expected_output": "William Shakespeare",
            "output": "Romeo and Juliet was written by Shakespeare.",
        },
        {
            "input": "What is the largest planet?",
            "expected_output": "Jupiter",
            "output": "Jupiter is the largest planet in our solar system.",
        },
        {
            "input": "What color is the sky?",
            "expected_output": "Blue",
            "output": "The sky appears blue during the day.",
        },
    ]

    # Define metrics
    metrics = [
        AccuracyMetric(name="exact_match", case_sensitive=False),
        ContainsKeywordsMetric(name="contains_answer"),
        SimilarityMetric(name="jaccard_similarity", method="jaccard"),
        LengthMetric(name="response_length", min_length=5, max_length=100),
    ]

    # Create evaluator
    evaluator = create_simple_evaluator(
        experiment_name="basic-qa-evaluation",
        metrics=metrics,
    )

    print("\n1. Dataset:")
    print("-" * 40)
    for i, item in enumerate(dataset, 1):
        print(f"{i}. Q: {item['input']}")
        print(f"   Expected: {item['expected_output']}")
        print(f"   Output: {item['output']}")
        print()

    # For ContainsKeywordsMetric, we need to set keywords based on expected output
    # Let's run with the expected output as the keyword
    for item in dataset:
        item["keywords"] = [item["expected_output"]]

    # Run evaluation
    print("2. Running evaluation...")
    print("-" * 40)
    results = evaluator.evaluate_batch(dataset)

    # Display individual results
    print("\n3. Individual Results:")
    print("-" * 40)
    for i, result in enumerate(results.results, 1):
        print(f"\nSample {i}: {result.input[:50]}...")
        print(f"  Output: {result.output[:50]}...")
        print(f"  Average Score: {result.average_score:.2%}")
        print("  Metric Scores:")
        for name, score in result.scores.items():
            print(f"    - {name}: {score.value:.2%}")
            if score.reason:
                print(f"      Reason: {score.reason}")

    # Display summary
    print("\n4. Summary:")
    print("-" * 40)
    print(results.summary())

    # Convert to DataFrame for analysis
    print("\n5. Results as DataFrame:")
    print("-" * 40)
    df = results.to_dataframe()
    print(df[["input", "average_score"]].to_string())

    # Show metric comparison
    print("\n6. Metric Comparison:")
    print("-" * 40)
    score_cols = [col for col in df.columns if col.startswith("score_")]
    for col in score_cols:
        metric_name = col.replace("score_", "")
        avg = df[col].mean()
        min_val = df[col].min()
        max_val = df[col].max()
        print(f"  {metric_name}:")
        print(f"    Average: {avg:.2%}")
        print(f"    Range: {min_val:.2%} - {max_val:.2%}")

    print("\n" + "=" * 60)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()
