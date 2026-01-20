"""Exercise 1: Evaluate a Q&A System with Accuracy Metrics

Build an evaluation pipeline for a Q&A system that measures:
1. Answer accuracy (exact match)
2. Whether the answer contains key information
3. Response length appropriateness

Instructions:
1. Create a dataset of Q&A pairs with expected answers
2. Implement a mock LLM function that generates answers
3. Configure and run the evaluation
4. Analyze the results

Expected Output:
- Evaluation scores for each metric
- Summary statistics
- Identification of weak areas

Hints:
- Use AccuracyMetric for exact matching
- Use ContainsKeywordsMetric to check for key facts
- Use LengthMetric to ensure appropriate response length
"""

from typing import Any

from opik_evaluation.evaluator import EvaluationConfig, Evaluator
from opik_evaluation.metrics import AccuracyMetric, ContainsKeywordsMetric, LengthMetric


def mock_qa_system(question: str) -> str:
    """Simulate a Q&A system.

    TODO: Implement a simple Q&A system that returns answers based on the question.
    You can use a dictionary of known Q&A pairs.
    """
    # TODO: Implement this function
    # Example:
    # qa_pairs = {
    #     "What is the capital of France?": "Paris",
    #     "Who wrote Hamlet?": "Shakespeare",
    # }
    # Return a matching answer or a default response
    pass


def create_dataset() -> list[dict[str, Any]]:
    """Create a dataset of Q&A pairs for evaluation.

    TODO: Create a list of dictionaries with:
    - 'input': The question
    - 'expected_output': The correct answer
    - 'keywords': List of key terms that should appear in the answer
    """
    # TODO: Create at least 5 Q&A pairs
    dataset = [
        # {
        #     "input": "What is the capital of France?",
        #     "expected_output": "Paris",
        #     "keywords": ["Paris", "capital"],
        # },
    ]
    return dataset


def main() -> None:
    """Run the Q&A evaluation exercise."""
    print("Exercise 1: Q&A System Evaluation")
    print("=" * 50)

    # TODO: Create the dataset
    dataset = create_dataset()

    # TODO: Generate outputs using the mock QA system
    for item in dataset:
        item["output"] = mock_qa_system(item["input"])

    # TODO: Configure metrics
    metrics = [
        # Add AccuracyMetric
        # Add ContainsKeywordsMetric
        # Add LengthMetric
    ]

    # TODO: Create evaluator and run evaluation
    config = EvaluationConfig(
        experiment_name="qa-evaluation",
        metrics=metrics,
    )
    evaluator = Evaluator(config)

    # TODO: Run evaluation
    # results = evaluator.evaluate_batch(dataset)

    # TODO: Print results
    # print(results.summary())

    # TODO: Analyze weak areas
    # - Which questions had low accuracy?
    # - Which keywords were missing?

    print("\nExercise not yet implemented. Complete the TODOs above!")


if __name__ == "__main__":
    main()
