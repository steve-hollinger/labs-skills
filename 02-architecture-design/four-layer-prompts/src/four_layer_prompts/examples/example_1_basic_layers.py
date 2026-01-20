"""Example 1: Basic Four-Layer Prompt Construction.

This example demonstrates the fundamental concept of constructing
prompts using the four-layer architecture.

Run with: make example-1
Or: uv run python -m four_layer_prompts.examples.example_1_basic_layers
"""

from four_layer_prompts.layers import PromptBuilder, PromptLayers


def example_basic_layers() -> None:
    """Demonstrate basic layer construction."""
    print("=== Basic Four-Layer Prompt ===\n")

    # Define each layer separately
    system = """
You are a senior Python developer with expertise in code review.
You provide constructive, specific feedback focused on code quality.
"""

    context = """
Code to review:
```python
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price'] * item['quantity']
    return total
```

Project guidelines:
- Use type hints
- Follow PEP 8
- Prefer functional patterns where appropriate
"""

    instruction = """
Review this code and provide feedback on:
1. Code correctness
2. Style and readability
3. Potential improvements
"""

    constraint = """
Format your response as:
- Summary (1-2 sentences)
- Issues Found (bullet points)
- Suggested Improvements (bullet points)
Keep total response under 200 words.
"""

    # Compose using PromptLayers
    layers = PromptLayers(
        system=system.strip(),
        context=context.strip(),
        instruction=instruction.strip(),
        constraint=constraint.strip(),
    )

    prompt = layers.compose()

    print("Composed Prompt:")
    print("-" * 50)
    print(prompt)
    print("-" * 50)
    print(f"\nTotal length: {len(prompt)} characters")


def example_builder_pattern() -> None:
    """Demonstrate the fluent builder pattern."""
    print("\n=== Builder Pattern ===\n")

    prompt = (
        PromptBuilder()
        .system("You are a helpful AI assistant specialized in data analysis.")
        .context("""
Dataset: Customer purchase history (10,000 records)
Fields: customer_id, product_category, amount, date
Time period: 2023-01-01 to 2023-12-31
""")
        .instruction("Suggest 3 interesting analyses we could perform on this dataset.")
        .constraint("List suggestions as numbered items with brief explanations.")
        .build()
    )

    print("Built Prompt:")
    print("-" * 50)
    print(prompt)
    print("-" * 50)


def example_layer_variations() -> None:
    """Show different prompt compositions for different purposes."""
    print("\n=== Layer Variations ===\n")

    # Base builder with system layer
    base = PromptBuilder().system(
        "You are an expert technical writer."
    )

    # Variation 1: Documentation task
    doc_prompt = (
        base.copy()
        .context("Function: def fetch_user(user_id: int) -> User")
        .instruction("Write a docstring for this function.")
        .constraint("Use Google-style docstring format.")
        .build()
    )

    # Variation 2: Tutorial task
    tutorial_prompt = (
        base.copy()
        .context("Topic: Python decorators")
        .instruction("Write a beginner-friendly tutorial section.")
        .constraint("Include one simple example. Avoid jargon.")
        .build()
    )

    print("Documentation Prompt:")
    print(doc_prompt)
    print("\n" + "=" * 50 + "\n")
    print("Tutorial Prompt:")
    print(tutorial_prompt)


def example_minimal_prompts() -> None:
    """Show that not all layers are always required."""
    print("\n=== Minimal Prompts ===\n")

    # Simple question - system + instruction only
    simple = (
        PromptBuilder()
        .system("You are a helpful assistant.")
        .instruction("What is the capital of France?")
        .build()
    )
    print("Simple Q&A (2 layers):")
    print(simple)
    print()

    # Code generation - instruction + constraint only
    code_gen = (
        PromptBuilder()
        .instruction("Write a Python function to reverse a string.")
        .constraint("Use only built-in functions. Include type hints.")
        .build()
    )
    print("Code Generation (2 layers):")
    print(code_gen)


def main() -> None:
    """Run all basic layer examples."""
    example_basic_layers()
    example_builder_pattern()
    example_layer_variations()
    example_minimal_prompts()
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
