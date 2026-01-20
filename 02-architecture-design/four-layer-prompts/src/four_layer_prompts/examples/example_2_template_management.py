"""Example 2: Template Management.

This example demonstrates creating reusable templates for each layer
with variable substitution.

Run with: make example-2
Or: uv run python -m four_layer_prompts.examples.example_2_template_management
"""

from four_layer_prompts.templates import (
    LayerTemplate,
    TemplateRegistry,
    create_default_registry,
)
from four_layer_prompts.layers import PromptBuilder


def example_simple_templates() -> None:
    """Demonstrate simple template usage."""
    print("=== Simple Templates ===\n")

    # Create templates with variables
    system_template = LayerTemplate(
        template="You are a $role with expertise in $domain.",
        name="expert_system",
    )

    context_template = LayerTemplate(
        template="""
Project: $project_name
Language: $language
Framework: $framework
""",
        name="project_context",
    )

    # Render templates with different values
    system1 = system_template.render(role="software architect", domain="microservices")
    system2 = system_template.render(role="data scientist", domain="machine learning")

    context1 = context_template.render(
        project_name="E-Commerce API",
        language="Python",
        framework="FastAPI",
    )

    print("System Template Variations:")
    print(f"  1: {system1}")
    print(f"  2: {system2}")
    print(f"\nContext: {context1}")


def example_jinja_templates() -> None:
    """Demonstrate Jinja2 templates for complex logic."""
    print("\n=== Jinja2 Templates ===\n")

    # Jinja2 template with conditionals and loops
    context_template = LayerTemplate(
        template="""
Project Analysis Request:
- Name: {{ project_name }}
- Type: {{ project_type }}
{% if team_size %}
- Team Size: {{ team_size }} developers
{% endif %}

{% if requirements %}
Key Requirements:
{% for req in requirements %}
  - {{ req }}
{% endfor %}
{% endif %}
""",
        name="project_analysis",
        use_jinja=True,
    )

    # Render with full data
    full_context = context_template.render(
        project_name="CustomerPortal",
        project_type="Web Application",
        team_size=5,
        requirements=["High availability", "Real-time updates", "Mobile support"],
    )

    # Render with minimal data
    minimal_context = context_template.render(
        project_name="InternalTool",
        project_type="CLI Application",
    )

    print("Full Context:")
    print(full_context)
    print("\nMinimal Context:")
    print(minimal_context)


def example_template_registry() -> None:
    """Demonstrate the template registry pattern."""
    print("\n=== Template Registry ===\n")

    # Create a registry
    registry = TemplateRegistry()

    # Register templates
    registry.register_system(
        "code_reviewer",
        LayerTemplate(
            template="""You are a senior $language developer conducting code reviews.
You focus on $focus_areas.
You provide constructive, actionable feedback.""",
        ),
    )

    registry.register_context(
        "code_review",
        LayerTemplate(
            template="""Code to review:
```$language
$code
```

File: $filename
Author: $author""",
        ),
    )

    registry.register_instruction(
        "review",
        "Review this code for $review_type issues.",
    )

    registry.register_constraint(
        "structured",
        LayerTemplate(
            template="""Format your response as:
$format

Maximum length: $max_words words.""",
        ),
    )

    # Compose a prompt using registry templates
    system = registry.get_system("code_reviewer").render(
        language="Python",
        focus_areas="security, performance, and maintainability",
    )

    context = registry.get_context("code_review").render(
        language="python",
        code="def login(user, pwd): return db.check(user, pwd)",
        filename="auth.py",
        author="junior_dev",
    )

    instruction = registry.get_instruction("review").render(
        review_type="security",
    )

    constraint = registry.get_constraint("structured").render(
        format="- Critical Issues\n- Warnings\n- Suggestions",
        max_words="150",
    )

    prompt = (
        PromptBuilder()
        .system(system)
        .context(context)
        .instruction(instruction)
        .constraint(constraint)
        .build()
    )

    print("Available templates:")
    print(f"  Systems: {registry.list_systems()}")
    print(f"  Contexts: {registry.list_contexts()}")
    print(f"  Instructions: {registry.list_instructions()}")
    print(f"  Constraints: {registry.list_constraints()}")
    print("\nComposed Prompt:")
    print("-" * 50)
    print(prompt)


def example_default_registry() -> None:
    """Demonstrate using the default registry."""
    print("\n=== Default Registry ===\n")

    registry = create_default_registry()

    # Use default templates
    system = registry.get_system("code_reviewer").render()
    context = registry.get_context("code").render(
        language="python",
        code="print('hello')",
    )
    instruction = registry.get_instruction("summarize").render()
    constraint = registry.get_constraint("concise").render(max_words="100")

    print("Default Templates Used:")
    print(f"  System: code_reviewer")
    print(f"  Context: code")
    print(f"  Instruction: summarize")
    print(f"  Constraint: concise")

    prompt = (
        PromptBuilder()
        .system(system)
        .context(context)
        .instruction(instruction)
        .constraint(constraint)
        .build()
    )

    print("\nResulting Prompt:")
    print("-" * 50)
    print(prompt)


def example_template_validation() -> None:
    """Demonstrate template variable validation."""
    print("\n=== Template Validation ===\n")

    template = LayerTemplate(
        template="Review $code_type code in $language for $review_focus.",
        name="review_instruction",
    )

    # Check required variables
    required = template.required_variables()
    print(f"Required variables: {required}")

    # Validate with missing variables
    missing = template.validate_variables(code_type="API", language="Python")
    print(f"Missing variables: {missing}")

    # Validate with all variables
    missing = template.validate_variables(
        code_type="API",
        language="Python",
        review_focus="security",
    )
    print(f"Missing variables (complete): {missing}")


def main() -> None:
    """Run all template management examples."""
    example_simple_templates()
    example_jinja_templates()
    example_template_registry()
    example_default_registry()
    example_template_validation()
    print("\n=== Example Complete ===")


if __name__ == "__main__":
    main()
