"""Example 3: Custom Metrics and Experiments

This example demonstrates creating custom evaluation metrics and
running comparison experiments across different model configurations.

Key concepts:
- Creating domain-specific custom metrics
- Running multiple experiments
- Comparing results across experiments
- Visualizing evaluation results
"""

from typing import Any

from opik_evaluation.evaluator import Evaluator, EvaluationConfig
from opik_evaluation.metrics import BaseMetric, ScoreResult


# Custom metrics for specific use cases


class FactualAccuracyMetric(BaseMetric):
    """Metric that checks for factual accuracy using known facts.

    This metric checks if the output contains correct facts based
    on a fact database.
    """

    def __init__(
        self,
        name: str = "factual_accuracy",
        fact_db: dict[str, list[str]] | None = None,
    ) -> None:
        """Initialize factual accuracy metric.

        Args:
            name: Metric name
            fact_db: Dictionary mapping topics to lists of facts
        """
        super().__init__(name)
        self.fact_db = fact_db or {
            "france": ["paris", "capital", "europe"],
            "jupiter": ["largest", "planet", "gas giant"],
            "shakespeare": ["playwright", "romeo", "juliet", "hamlet"],
            "python": ["programming", "language", "guido"],
        }

    def score(self, output: str, **kwargs: Any) -> ScoreResult:
        """Score based on factual content."""
        input_text = kwargs.get("input", "").lower()
        output_lower = output.lower()

        # Find relevant topic
        relevant_topic = None
        for topic in self.fact_db:
            if topic in input_text:
                relevant_topic = topic
                break

        if relevant_topic is None:
            return ScoreResult(
                value=0.5,
                name=self.name,
                reason="No known topic found in input",
            )

        # Check for facts
        facts = self.fact_db[relevant_topic]
        found_facts = [f for f in facts if f in output_lower]

        score = len(found_facts) / len(facts) if facts else 0.0
        return ScoreResult(
            value=score,
            name=self.name,
            reason=f"Found {len(found_facts)}/{len(facts)} facts about {relevant_topic}",
        )


class ToneMetric(BaseMetric):
    """Metric that evaluates the tone of a response.

    Checks for professional, casual, or neutral tone based on
    keyword presence.
    """

    def __init__(
        self,
        name: str = "tone",
        target_tone: str = "professional",
    ) -> None:
        """Initialize tone metric.

        Args:
            name: Metric name
            target_tone: Desired tone (professional, casual, neutral)
        """
        super().__init__(name)
        self.target_tone = target_tone

        self.tone_indicators = {
            "professional": {
                "positive": ["therefore", "furthermore", "regarding", "accordingly", "please"],
                "negative": ["hey", "cool", "awesome", "lol", "btw", "gonna"],
            },
            "casual": {
                "positive": ["hey", "cool", "awesome", "nice", "great"],
                "negative": ["whereas", "furthermore", "accordingly", "hereby"],
            },
            "neutral": {
                "positive": [],
                "negative": ["!!!", "???", "lol", "omg"],
            },
        }

    def score(self, output: str, **kwargs: Any) -> ScoreResult:
        """Score based on tone analysis."""
        output_lower = output.lower()
        indicators = self.tone_indicators.get(self.target_tone, {"positive": [], "negative": []})

        positive_count = sum(1 for word in indicators["positive"] if word in output_lower)
        negative_count = sum(1 for word in indicators["negative"] if word in output_lower)

        # Score calculation
        if positive_count > 0 and negative_count == 0:
            score = 1.0
            reason = f"Matches {self.target_tone} tone"
        elif positive_count > negative_count:
            score = 0.7
            reason = f"Mostly {self.target_tone} tone with some deviation"
        elif negative_count > 0:
            score = 0.3
            reason = f"Contains {negative_count} non-{self.target_tone} indicators"
        else:
            score = 0.5
            reason = "Neutral tone detected"

        return ScoreResult(value=score, name=self.name, reason=reason)


class ConcisenessMetric(BaseMetric):
    """Metric that evaluates response conciseness.

    Prefers responses that are informative without being verbose.
    """

    def __init__(
        self,
        name: str = "conciseness",
        ideal_word_count: int = 20,
        tolerance: int = 10,
    ) -> None:
        """Initialize conciseness metric.

        Args:
            name: Metric name
            ideal_word_count: Target word count
            tolerance: Acceptable deviation from ideal
        """
        super().__init__(name)
        self.ideal_word_count = ideal_word_count
        self.tolerance = tolerance

    def score(self, output: str, **kwargs: Any) -> ScoreResult:
        """Score based on word count relative to ideal."""
        word_count = len(output.split())
        deviation = abs(word_count - self.ideal_word_count)

        if deviation <= self.tolerance:
            score = 1.0
            reason = f"Word count ({word_count}) is within ideal range"
        elif deviation <= self.tolerance * 2:
            score = 0.7
            reason = f"Word count ({word_count}) is slightly off ideal ({self.ideal_word_count})"
        elif deviation <= self.tolerance * 3:
            score = 0.4
            reason = f"Word count ({word_count}) deviates from ideal ({self.ideal_word_count})"
        else:
            score = 0.2
            reason = f"Word count ({word_count}) far from ideal ({self.ideal_word_count})"

        return ScoreResult(value=score, name=self.name, reason=reason)


# Simulated LLM with different configurations


def simulate_llm_response(prompt: str, config: dict[str, Any]) -> str:
    """Simulate LLM responses with different configurations."""
    style = config.get("style", "default")
    verbosity = config.get("verbosity", "medium")

    # Base responses
    responses = {
        "france": "Paris is the capital of France",
        "jupiter": "Jupiter is the largest planet",
        "shakespeare": "Shakespeare wrote Romeo and Juliet",
        "python": "Python is a programming language",
    }

    # Find matching response
    prompt_lower = prompt.lower()
    base_response = "I don't have information about that topic"
    for key, resp in responses.items():
        if key in prompt_lower:
            base_response = resp
            break

    # Adjust based on style
    if style == "professional":
        base_response = f"I would like to inform you that {base_response.lower()}."
    elif style == "casual":
        base_response = f"Hey! So, {base_response.lower()}!"
    elif style == "academic":
        base_response = f"According to established knowledge, {base_response.lower()}. This is well-documented."

    # Adjust based on verbosity
    if verbosity == "high":
        base_response += " Furthermore, this is a well-known fact that has been documented extensively."
    elif verbosity == "low":
        # Keep it short
        pass
    else:
        base_response += " This is commonly known."

    return base_response


def run_experiment(
    name: str,
    dataset: list[dict[str, Any]],
    llm_config: dict[str, Any],
    metrics: list[BaseMetric],
) -> dict[str, Any]:
    """Run an evaluation experiment with specific LLM configuration."""
    # Generate outputs with this config
    for item in dataset:
        item["output"] = simulate_llm_response(item["input"], llm_config)

    # Create evaluator
    config = EvaluationConfig(
        experiment_name=name,
        metrics=metrics,
    )
    evaluator = Evaluator(config)

    # Run evaluation
    results = evaluator.evaluate_batch(dataset)

    return {
        "name": name,
        "config": llm_config,
        "results": results,
        "average_scores": results.average_scores,
    }


def main() -> None:
    """Run the custom metrics and experiments example."""
    print("Example 3: Custom Metrics and Experiments")
    print("=" * 60)

    # Create test dataset
    dataset = [
        {"input": "What is the capital of France?"},
        {"input": "Tell me about Jupiter."},
        {"input": "Who wrote Romeo and Juliet?"},
        {"input": "Explain Python programming."},
    ]

    # Define custom metrics
    metrics = [
        FactualAccuracyMetric(),
        ToneMetric(target_tone="professional"),
        ConcisenessMetric(ideal_word_count=15, tolerance=5),
    ]

    print("\n1. Custom Metrics Defined:")
    print("-" * 40)
    for metric in metrics:
        print(f"  - {metric.name}")

    # Run experiments with different configurations
    print("\n2. Running Experiments:")
    print("-" * 40)

    experiments = [
        ("baseline", {"style": "default", "verbosity": "medium"}),
        ("professional", {"style": "professional", "verbosity": "medium"}),
        ("casual", {"style": "casual", "verbosity": "low"}),
        ("academic", {"style": "academic", "verbosity": "high"}),
    ]

    results_list = []
    for exp_name, config in experiments:
        print(f"\n  Running: {exp_name}")
        print(f"  Config: {config}")

        # Need to copy dataset for each experiment
        exp_dataset = [item.copy() for item in dataset]
        result = run_experiment(
            name=exp_name,
            dataset=exp_dataset,
            llm_config=config,
            metrics=metrics,
        )
        results_list.append(result)

        print(f"  Average scores: {result['average_scores']}")

    # Compare experiments
    print("\n3. Experiment Comparison:")
    print("-" * 40)

    # Create comparison table
    metric_names = [m.name for m in metrics]

    # Header
    header = f"{'Experiment':<15}"
    for name in metric_names:
        header += f"{name:<20}"
    header += f"{'Overall':<10}"
    print(header)
    print("-" * len(header))

    # Rows
    for result in results_list:
        row = f"{result['name']:<15}"
        overall = 0.0
        for name in metric_names:
            score = result["average_scores"].get(name, 0.0)
            row += f"{score:.2%}".ljust(20)
            overall += score
        overall /= len(metric_names)
        row += f"{overall:.2%}"
        print(row)

    # Find best configuration
    print("\n4. Best Configuration per Metric:")
    print("-" * 40)

    for metric_name in metric_names:
        best_exp = max(results_list, key=lambda r: r["average_scores"].get(metric_name, 0))
        best_score = best_exp["average_scores"].get(metric_name, 0)
        print(f"  {metric_name}: {best_exp['name']} ({best_score:.2%})")

    # Show sample outputs
    print("\n5. Sample Outputs by Configuration:")
    print("-" * 40)

    sample_input = dataset[0]["input"]
    print(f"  Input: {sample_input}")
    print()

    for exp_name, config in experiments:
        output = simulate_llm_response(sample_input, config)
        print(f"  [{exp_name}]")
        print(f"  {output}")
        print()

    # Overall winner
    print("\n6. Overall Best Configuration:")
    print("-" * 40)

    best_overall = max(
        results_list,
        key=lambda r: sum(r["average_scores"].values()) / len(r["average_scores"]),
    )
    overall_score = sum(best_overall["average_scores"].values()) / len(best_overall["average_scores"])
    print(f"  Winner: {best_overall['name']}")
    print(f"  Config: {best_overall['config']}")
    print(f"  Overall Score: {overall_score:.2%}")

    print("\n" + "=" * 60)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()
