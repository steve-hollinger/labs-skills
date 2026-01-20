"""Example 1: README Structure

This example demonstrates the essential sections every README should have
and how to create well-structured project documentation.
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

from component_documentation.readme_builder import (
    ReadmeBuilder,
    generate_readme,
    validate_readme,
)
from component_documentation.models import SectionType


def main() -> None:
    """Run the README structure example."""
    console = Console()

    console.print(Panel.fit(
        "[bold blue]Example 1: README Structure[/bold blue]\n"
        "Learn the essential sections every README should have.",
        title="Component Documentation"
    ))

    # Show essential sections
    console.print("\n[bold]Essential README Sections:[/bold]\n")

    sections = [
        ("Title & Description", "What is this project?", "Required", 1),
        ("Installation", "How do I install it?", "Required", 2),
        ("Quick Start", "How do I use it immediately?", "Required", 3),
        ("Usage Examples", "How do I do common tasks?", "Recommended", 4),
        ("API Reference", "What functions are available?", "Recommended", 5),
        ("Configuration", "How do I customize it?", "If applicable", 6),
        ("Contributing", "How can I help?", "Recommended", 7),
        ("License", "Can I use this?", "Required", 8),
    ]

    table = Table(show_header=True, header_style="bold")
    table.add_column("Section")
    table.add_column("Question It Answers")
    table.add_column("Priority")
    table.add_column("Order")

    for name, question, priority, order in sections:
        priority_color = "green" if priority == "Required" else "yellow" if priority == "Recommended" else "dim"
        table.add_row(name, question, f"[{priority_color}]{priority}[/{priority_color}]", str(order))

    console.print(table)

    # Build a README using the builder
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Building a README with ReadmeBuilder:[/bold]\n")

    readme = (
        ReadmeBuilder("data-validator")
        .with_description(
            "A fast, type-safe data validation library for Python. "
            "Validate dictionaries, JSON, and dataclasses with minimal boilerplate."
        )
        .with_badges(["pypi", "tests", "coverage"])
        .with_features([
            "Type-safe validation with full mypy support",
            "Fast: 10x faster than similar libraries",
            "Extensible: Create custom validators easily",
            "Great error messages for debugging",
        ])
        .with_installation("pip install data-validator")
        .with_quick_start('''from data_validator import validate, Schema

schema = Schema({
    "name": str,
    "age": int,
    "email": str,
})

data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
result = validate(data, schema)
print(result.is_valid)  # True''')
        .with_usage("Basic Validation", '''from data_validator import validate

# Validate a dictionary
result = validate({"name": "Bob"}, {"name": str})
assert result.is_valid''')
        .with_usage("Custom Validators", '''from data_validator import validator

@validator
def positive_int(value):
    if not isinstance(value, int) or value <= 0:
        raise ValueError("Must be a positive integer")
    return value

result = validate({"count": 5}, {"count": positive_int})''')
        .with_config_option("strict_mode", "Fail on unknown fields", "False")
        .with_config_option("coerce_types", "Automatically convert types", "True")
        .with_contributing("See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.")
        .with_license("MIT")
        .build()
    )

    # Show the generated README
    console.print(Panel(
        Markdown(readme.render()),
        title="Generated README.md",
        border_style="green",
    ))

    # Validate the README
    console.print("\n" + "=" * 60)
    console.print("\n[bold]README Validation:[/bold]\n")

    score = validate_readme(readme.render())

    console.print(f"Score: [{('green' if score.is_passing else 'red')}]{score.score}/100[/]")

    if score.issues:
        console.print("\n[red]Issues:[/red]")
        for issue in score.issues:
            console.print(f"  - {issue}")

    if score.suggestions:
        console.print("\n[yellow]Suggestions:[/yellow]")
        for suggestion in score.suggestions:
            console.print(f"  - {suggestion}")

    # Show quick generation
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Quick README Generation:[/bold]\n")

    quick_readme = generate_readme(
        project_name="my-cli-tool",
        description="A command-line tool for doing useful things.",
        features=["Fast execution", "Easy configuration", "Cross-platform"],
        install_command="pip install my-cli-tool",
        quick_start_code='''from my_cli_tool import run
run("hello world")''',
        license_type="Apache 2.0",
    )

    console.print(Markdown(quick_readme[:800] + "\n\n*... (truncated) ...*"))

    # Key takeaways
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Key Takeaways:[/bold]\n")

    takeaways = [
        "Every README needs: title, description, installation, quick start",
        "Order matters: most important information first",
        "Show, don't tell: include working code examples",
        "Answer the user's first questions immediately",
        "Use badges to show project health at a glance",
        "Keep it scannable with clear headers",
    ]

    for takeaway in takeaways:
        console.print(f"  - {takeaway}")

    console.print("\n[bold green]Example completed successfully![/bold green]")


if __name__ == "__main__":
    main()
