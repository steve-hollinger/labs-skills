"""Example 3: Prompt Composition Patterns.

This example demonstrates advanced patterns for building complex prompts
from layer components.

Run with: make example-3
Or: uv run python -m four_layer_prompts.examples.example_3_composition_patterns
"""

from four_layer_prompts.composer import (
    PromptComposer,
    compose_layers,
    compose_with_headers,
    ConditionalComposer,
)
from four_layer_prompts.templates import TemplateRegistry, LayerTemplate


def example_simple_composition() -> None:
    """Demonstrate simple layer composition."""
    print("=== Simple Composition ===\n")

    prompt = compose_layers(
        system="You are a helpful coding assistant.",
        context="User is building a REST API in Python.",
        instruction="Suggest best practices for error handling.",
        constraint="Provide 3-5 bullet points.",
    )

    print("Composed Prompt:")
    print("-" * 50)
    print(prompt)


def example_headers_composition() -> None:
    """Demonstrate composition with explicit headers."""
    print("\n=== Composition with Headers ===\n")

    prompt = compose_with_headers(
        system="You are an expert database administrator.",
        context="Database: PostgreSQL 15\nCurrent tables: users, orders, products",
        instruction="Optimize the following query for better performance.",
        constraint="Explain your optimizations step by step.",
    )

    print("Prompt with Headers (useful for debugging):")
    print("-" * 50)
    print(prompt)


def example_composer_with_transforms() -> None:
    """Demonstrate composer with layer transformations."""
    print("\n=== Composer with Transforms ===\n")

    # Define transformation functions
    def add_timestamp(content: str) -> str:
        from datetime import datetime

        timestamp = datetime.now().isoformat()
        return f"{content}\n[Generated: {timestamp}]"

    def wrap_in_xml(content: str) -> str:
        return f"<context>\n{content}\n</context>"

    def add_word_limit(content: str) -> str:
        return f"{content}\nWord limit: 200 words."

    # Create composer with transforms
    composer = PromptComposer()
    composer.add_transform("system", add_timestamp)
    composer.add_transform("context", wrap_in_xml)
    composer.add_transform("constraint", add_word_limit)

    prompt = composer.compose_from_strings(
        system="You are a technical writer.",
        context="API endpoint documentation for /users",
        instruction="Write clear documentation.",
        constraint="Use markdown format.",
    )

    print("Transformed Prompt:")
    print("-" * 50)
    print(prompt)


def example_template_composition() -> None:
    """Demonstrate composition from templates."""
    print("\n=== Template Composition ===\n")

    # Setup registry
    registry = TemplateRegistry()

    registry.register_system(
        "analyst",
        LayerTemplate(template="You are a $specialty analyst with $years years of experience."),
    )

    registry.register_context(
        "data_analysis",
        LayerTemplate(template="Dataset: $dataset\nRecords: $record_count\nFields: $fields"),
    )

    registry.register_instruction(
        "analyze",
        LayerTemplate(template="Perform $analysis_type analysis and identify key $findings."),
    )

    registry.register_constraint(
        "report_format",
        LayerTemplate(template="Format as a $format_type with:\n$sections"),
    )

    # Compose using templates
    composer = PromptComposer(registry=registry)

    prompt = composer.compose_from_templates(
        system_name="analyst",
        context_name="data_analysis",
        instruction_name="analyze",
        constraint_name="report_format",
        variables={
            "specialty": "business intelligence",
            "years": "10",
            "dataset": "Q4 Sales Data",
            "record_count": "50,000",
            "fields": "date, product, quantity, revenue, region",
            "analysis_type": "trend",
            "findings": "patterns and anomalies",
            "format_type": "executive summary",
            "sections": "- Key Findings\n- Trends\n- Recommendations",
        },
    )

    print("Template-based Prompt:")
    print("-" * 50)
    print(prompt)


def example_hybrid_composition() -> None:
    """Demonstrate hybrid composition (mix of strings and templates)."""
    print("\n=== Hybrid Composition ===\n")

    # Setup registry
    registry = TemplateRegistry()
    registry.register_system(
        "expert",
        LayerTemplate(template="You are an expert in $domain."),
    )
    registry.register_constraint(
        "json_output",
        LayerTemplate(template="Return response as JSON with keys: $keys"),
    )

    composer = PromptComposer(registry=registry)

    # Mix template references with direct strings
    prompt = composer.compose_hybrid(
        system=("expert", {"domain": "cloud architecture"}),  # Template
        context="Current setup: 3 EC2 instances, RDS PostgreSQL, S3 bucket",  # String
        instruction="Suggest improvements for scalability.",  # String
        constraint=("json_output", {"keys": "suggestions, priority, effort"}),  # Template
    )

    print("Hybrid Prompt:")
    print("-" * 50)
    print(prompt)


def example_conditional_composition() -> None:
    """Demonstrate conditional layer composition."""
    print("\n=== Conditional Composition ===\n")

    # Simulate runtime conditions
    user_level = "beginner"
    include_examples = True
    is_premium = False

    composer = (
        ConditionalComposer()
        .default("system", "You are a coding tutor.")
        .default("instruction", "Explain the concept of recursion.")
        .default("constraint", "Be clear and concise.")
        # Add beginner-specific content
        .when(
            lambda: user_level == "beginner",
            "system",
            "You adjust your explanations for beginners.",
        )
        .when(
            lambda: user_level == "beginner",
            "constraint",
            "Avoid technical jargon.",
        )
        # Add examples if requested
        .when(
            lambda: include_examples,
            "constraint",
            "Include at least 2 code examples.",
        )
        # Premium features
        .when(
            lambda: is_premium,
            "constraint",
            "Provide advanced optimization tips.",
        )
    )

    prompt = composer.build()

    print(f"Conditions: user_level={user_level}, examples={include_examples}, premium={is_premium}")
    print("-" * 50)
    print(prompt)

    # Change conditions and rebuild
    print("\n--- With different conditions ---")
    user_level = "expert"
    is_premium = True

    composer2 = (
        ConditionalComposer()
        .default("system", "You are a coding tutor.")
        .default("instruction", "Explain the concept of recursion.")
        .default("constraint", "Be clear and concise.")
        .when(
            lambda: user_level == "expert",
            "system",
            "You provide advanced technical insights.",
        )
        .when(
            lambda: is_premium,
            "constraint",
            "Include performance benchmarks and edge cases.",
        )
    )

    prompt2 = composer2.build()

    print(f"Conditions: user_level={user_level}, premium={is_premium}")
    print("-" * 50)
    print(prompt2)


def example_pipeline_composition() -> None:
    """Demonstrate pipeline-based composition."""
    print("\n=== Pipeline Composition ===\n")

    # Define composable functions
    def base_prompt() -> dict:
        return {
            "system": "",
            "context": "",
            "instruction": "",
            "constraint": "",
        }

    def with_role(layers: dict, role: str) -> dict:
        layers["system"] = f"You are a {role}."
        return layers

    def with_data(layers: dict, data: str) -> dict:
        layers["context"] = f"Data:\n{data}"
        return layers

    def with_task(layers: dict, task: str) -> dict:
        layers["instruction"] = task
        return layers

    def with_format(layers: dict, fmt: str) -> dict:
        layers["constraint"] = f"Output format: {fmt}"
        return layers

    def to_prompt(layers: dict) -> str:
        return compose_layers(**layers)

    # Build prompt through pipeline
    layers = base_prompt()
    layers = with_role(layers, "data analyst")
    layers = with_data(layers, "Monthly sales: Jan=100, Feb=120, Mar=95")
    layers = with_task(layers, "Identify the trend in this data.")
    layers = with_format(layers, "One sentence summary followed by bullet points.")

    prompt = to_prompt(layers)

    print("Pipeline-built Prompt:")
    print("-" * 50)
    print(prompt)


def main() -> None:
    """Run all composition pattern examples."""
    example_simple_composition()
    example_headers_composition()
    example_composer_with_transforms()
    example_template_composition()
    example_hybrid_composition()
    example_conditional_composition()
    example_pipeline_composition()
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
