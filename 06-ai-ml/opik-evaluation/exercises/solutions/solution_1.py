"""Solution for Exercise 1: Evaluate a Q&A System with Accuracy Metrics"""

from typing import Any

from opik_evaluation.evaluator import EvaluationConfig, Evaluator
from opik_evaluation.metrics import AccuracyMetric, ContainsKeywordsMetric, LengthMetric


# Q&A knowledge base
QA_KNOWLEDGE = {
    "What is the capital of France?": "The capital of France is Paris.",
    "Who wrote Hamlet?": "William Shakespeare wrote Hamlet.",
    "What is the largest planet in our solar system?": "Jupiter is the largest planet in our solar system.",
    "When did World War II end?": "World War II ended in 1945.",
    "What is the chemical symbol for water?": "The chemical symbol for water is H2O.",
    "Who painted the Mona Lisa?": "Leonardo da Vinci painted the Mona Lisa.",
    "What is the speed of light?": "The speed of light is approximately 299,792,458 meters per second.",
}


def mock_qa_system(question: str) -> str:
    """Simulate a Q&A system with some variations in answers."""
    # Check for exact match
    if question in QA_KNOWLEDGE:
        return QA_KNOWLEDGE[question]

    # Check for partial matches (case-insensitive)
    question_lower = question.lower()
    for q, a in QA_KNOWLEDGE.items():
        if q.lower() in question_lower or question_lower in q.lower():
            return a

    # Default response
    return "I don't have information about that topic."


def create_dataset() -> list[dict[str, Any]]:
    """Create a dataset of Q&A pairs for evaluation."""
    dataset = [
        {
            "input": "What is the capital of France?",
            "expected_output": "The capital of France is Paris.",
            "keywords": ["Paris", "capital", "France"],
        },
        {
            "input": "Who wrote Hamlet?",
            "expected_output": "William Shakespeare wrote Hamlet.",
            "keywords": ["Shakespeare", "Hamlet"],
        },
        {
            "input": "What is the largest planet in our solar system?",
            "expected_output": "Jupiter is the largest planet in our solar system.",
            "keywords": ["Jupiter", "largest", "planet"],
        },
        {
            "input": "When did World War II end?",
            "expected_output": "World War II ended in 1945.",
            "keywords": ["1945", "World War II", "ended"],
        },
        {
            "input": "What is the chemical symbol for water?",
            "expected_output": "The chemical symbol for water is H2O.",
            "keywords": ["H2O", "water", "chemical"],
        },
        {
            "input": "Who painted the Mona Lisa?",
            "expected_output": "Leonardo da Vinci painted the Mona Lisa.",
            "keywords": ["Leonardo", "da Vinci", "Mona Lisa"],
        },
        # Test case with intentionally wrong answer
        {
            "input": "What is the capital of Japan?",
            "expected_output": "The capital of Japan is Tokyo.",
            "keywords": ["Tokyo", "capital", "Japan"],
        },
    ]
    return dataset


def main() -> None:
    """Run the Q&A evaluation solution."""
    print("Solution 1: Q&A System Evaluation")
    print("=" * 60)

    # Create the dataset
    dataset = create_dataset()
    print(f"\n1. Created dataset with {len(dataset)} Q&A pairs")

    # Generate outputs using the mock QA system
    print("\n2. Generating answers...")
    for item in dataset:
        item["output"] = mock_qa_system(item["input"])
        print(f"   Q: {item['input'][:40]}...")
        print(f"   A: {item['output'][:50]}...")

    # Configure metrics
    metrics = [
        AccuracyMetric(name="exact_match", case_sensitive=False),
        ContainsKeywordsMetric(name="keyword_coverage"),
        LengthMetric(name="length", min_length=10, max_length=100, optimal_length=50),
    ]
    print(f"\n3. Configured {len(metrics)} metrics")

    # Create evaluator and run evaluation
    config = EvaluationConfig(
        experiment_name="qa-evaluation",
        metrics=metrics,
    )
    evaluator = Evaluator(config)

    # Run evaluation
    print("\n4. Running evaluation...")
    results = evaluator.evaluate_batch(dataset)

    # Print summary
    print("\n5. Results Summary:")
    print("-" * 40)
    print(results.summary())

    # Detailed analysis
    print("\n6. Detailed Analysis:")
    print("-" * 40)

    # Find weak areas
    weak_accuracy = []
    weak_keywords = []

    for result in results.results:
        if result.scores["exact_match"].value < 1.0:
            weak_accuracy.append({
                "input": result.input,
                "expected": result.expected_output,
                "output": result.output,
            })

        if result.scores["keyword_coverage"].value < 1.0:
            weak_keywords.append({
                "input": result.input,
                "reason": result.scores["keyword_coverage"].reason,
            })

    # Report weak areas
    print("\nQuestions with low accuracy:")
    if weak_accuracy:
        for item in weak_accuracy:
            print(f"  - Q: {item['input']}")
            print(f"    Expected: {item['expected']}")
            print(f"    Got: {item['output']}")
    else:
        print("  All questions answered correctly!")

    print("\nQuestions with missing keywords:")
    if weak_keywords:
        for item in weak_keywords:
            print(f"  - Q: {item['input']}")
            print(f"    {item['reason']}")
    else:
        print("  All keywords covered!")

    # Convert to DataFrame for additional analysis
    print("\n7. Score Distribution:")
    print("-" * 40)
    df = results.to_dataframe()
    for metric in metrics:
        col = f"score_{metric.name}"
        if col in df.columns:
            avg = df[col].mean()
            min_val = df[col].min()
            max_val = df[col].max()
            print(f"  {metric.name}:")
            print(f"    Average: {avg:.2%}")
            print(f"    Min: {min_val:.2%}, Max: {max_val:.2%}")

    print("\n" + "=" * 60)
    print("Evaluation complete!")


if __name__ == "__main__":
    main()
