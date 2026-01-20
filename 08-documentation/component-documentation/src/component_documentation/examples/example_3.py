"""Example 3: Code Documentation

This example demonstrates how to write effective docstrings, use type hints,
and analyze documentation quality for Python code.
"""

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from component_documentation.code_docs import (
    analyze_docstring,
    check_documentation,
    generate_docstring,
    check_module_documentation,
)


# Example functions with different documentation levels
def poorly_documented(x, y):
    """Does stuff."""
    return x + y


def partially_documented(items: list, limit: int = 10):
    """Process a list of items.

    Args:
        items: The items to process.
    """
    return items[:limit]


def well_documented(
    user_id: str,
    include_profile: bool = True,
    fields: list[str] | None = None,
) -> dict[str, any]:
    """Retrieve user data from the database.

    Fetches user information including optional profile data and
    custom field selection. Results are cached for 5 minutes.

    Args:
        user_id: The unique identifier of the user.
        include_profile: Whether to include extended profile data.
            Default is True.
        fields: Optional list of specific fields to return.
            If None, all fields are returned.

    Returns:
        Dictionary containing user data with requested fields.
        Always includes 'id' and 'email' regardless of field selection.

    Raises:
        UserNotFoundError: If no user exists with the given ID.
        DatabaseError: If the database connection fails.

    Example:
        >>> user = get_user("usr_123", include_profile=True)
        >>> print(user["email"])
        "user@example.com"
        >>> user = get_user("usr_123", fields=["name", "email"])
        >>> print(user.keys())
        dict_keys(['id', 'name', 'email'])
    """
    return {"id": user_id, "email": "example@example.com"}


def main() -> None:
    """Run the code documentation example."""
    console = Console()

    console.print(Panel.fit(
        "[bold blue]Example 3: Code Documentation[/bold blue]\n"
        "Learn to write effective docstrings and inline documentation.",
        title="Component Documentation"
    ))

    # Show documentation comparison
    console.print("\n[bold]Documentation Quality Comparison:[/bold]\n")

    functions = [
        ("Poorly Documented", poorly_documented),
        ("Partially Documented", partially_documented),
        ("Well Documented", well_documented),
    ]

    for name, func in functions:
        console.print(f"\n[cyan]{name}:[/cyan]")

        # Show the docstring
        doc = func.__doc__ or "(no docstring)"
        console.print(Panel(doc, title="Docstring", border_style="dim"))

        # Analyze it
        score = check_documentation(func)

        console.print(f"Score: [{('green' if score.is_passing else 'red')}]{score.score}/100[/]")

        if score.issues:
            for issue in score.issues[:3]:
                console.print(f"  [red]- {issue}[/red]")

        if score.suggestions:
            for suggestion in score.suggestions[:2]:
                console.print(f"  [yellow]- {suggestion}[/yellow]")

    # Analyze docstring structure
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Docstring Analysis:[/bold]\n")

    doc_info = analyze_docstring(well_documented.__doc__)

    table = Table(show_header=True, header_style="bold")
    table.add_column("Component")
    table.add_column("Present")
    table.add_column("Content Preview")

    components = [
        ("Summary", bool(doc_info.summary), doc_info.summary[:50] + "..."),
        ("Description", bool(doc_info.description), doc_info.description[:50] + "..." if doc_info.description else ""),
        ("Args", bool(doc_info.args), f"{len(doc_info.args)} documented"),
        ("Returns", bool(doc_info.returns), doc_info.returns[:50] + "..." if doc_info.returns else ""),
        ("Raises", bool(doc_info.raises), f"{len(doc_info.raises)} documented"),
        ("Examples", bool(doc_info.examples), f"{len(doc_info.examples)} lines"),
    ]

    for name, present, preview in components:
        check = "[green]Yes[/green]" if present else "[red]No[/red]"
        table.add_row(name, check, preview)

    console.print(table)
    console.print(f"\nCompleteness Score: [bold]{doc_info.completeness_score}/100[/bold]")

    # Show docstring generation
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Generating Docstrings:[/bold]\n")

    generated = generate_docstring(
        func_name="send_notification",
        params=[
            ("user_id", "str", "The unique identifier of the user."),
            ("message", "str", "The notification message content."),
            ("channel", "str", "Delivery channel ('email', 'sms', 'push')."),
            ("priority", "int", "Message priority (1-5, default 1)."),
        ],
        returns=("NotificationResult", "Result containing delivery status and ID."),
        raises=[
            ("UserNotFoundError", "If user_id doesn't exist."),
            ("InvalidChannelError", "If channel is not supported."),
        ],
        example='>>> result = send_notification("user_123", "Hello!", channel="sms")\n>>> print(result.id)\n"notif_abc"',
    )

    console.print(Syntax(generated, "python", theme="monokai"))

    # Check module documentation
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Module Documentation Check:[/bold]\n")

    sample_module = '''"""Sample module for demonstration.

This module contains utility functions for data processing.
"""

from typing import Optional

class DataProcessor:
    """Processes data items."""

    def process(self, item):
        return item

def transform(data: list) -> list:
    """Transform data items.

    Args:
        data: List of items to transform.

    Returns:
        Transformed list.
    """
    return data

def helper_function(x):
    # Internal helper, no docstring needed
    return x * 2

def undocumented_public_function(items, limit):
    return items[:limit]
'''

    console.print("[dim]Checking module:[/dim]")
    console.print(Syntax(sample_module, "python", theme="monokai", line_numbers=True))

    module_score = check_module_documentation(sample_module)

    console.print(f"\n[bold]Module Score:[/bold] [{('green' if module_score.is_passing else 'red')}]{module_score.score}/100[/]")

    if module_score.issues:
        console.print("\n[red]Issues found:[/red]")
        for issue in module_score.issues:
            console.print(f"  - {issue}")

    if module_score.suggestions:
        console.print("\n[yellow]Suggestions:[/yellow]")
        for suggestion in module_score.suggestions:
            console.print(f"  - {suggestion}")

    # Best practices
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Docstring Best Practices:[/bold]\n")

    best_practices = """
```python
def example_function(
    required_param: str,
    optional_param: int = 10,
    *,
    keyword_only: bool = False,
) -> ResultType:
    \"\"\"One-line summary that fits in 80 characters.

    Extended description if needed. Explains the "why" and
    any important context. Keep it focused and relevant.

    Args:
        required_param: Description of what this parameter is for.
            Can span multiple lines if needed.
        optional_param: Description with default mentioned.
        keyword_only: Parameters after * are keyword-only.

    Returns:
        Description of what is returned. For complex return types,
        describe the structure.

    Raises:
        SpecificError: When this specific condition occurs.
        AnotherError: When this other condition occurs.

    Example:
        >>> result = example_function("value")
        >>> print(result.status)
        "success"

    Note:
        Any additional information that doesn't fit elsewhere.
    \"\"\"
```
"""

    console.print(Markdown(best_practices))

    # Key takeaways
    console.print("\n[bold]Key Takeaways:[/bold]\n")

    takeaways = [
        "Every public function needs a docstring",
        "Start with a one-line summary that fits in 80 chars",
        "Document all parameters with types and descriptions",
        "Always document what a function returns",
        "Document exceptions that callers should handle",
        "Include at least one usage example",
        "Use type hints alongside docstrings",
    ]

    for takeaway in takeaways:
        console.print(f"  - {takeaway}")

    console.print("\n[bold green]Example completed successfully![/bold green]")


if __name__ == "__main__":
    main()
