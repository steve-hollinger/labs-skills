"""Exercise 2: Convert Vague Instructions to Precise Prompts

Below are vague, ineffective prompt snippets. Your task is to rewrite
each one to be specific, actionable, and useful.

For each snippet:
1. Identify what's wrong with it
2. Rewrite it to be specific and actionable
3. Ensure the rewritten version would score well in analysis

Target:
- Each rewrite should improve the score by at least 20 points
- Remove all vague language
- Add specific, measurable criteria
"""

from dataclasses import dataclass
from system_prompts.analyzer import analyze_text


@dataclass
class VagueSnippet:
    """A vague snippet that needs improvement."""

    category: str
    original: str
    problem: str


VAGUE_SNIPPETS = [
    VagueSnippet(
        category="Role",
        original="You are a helpful assistant.",
        problem="No expertise defined, no personality, generic",
    ),
    VagueSnippet(
        category="Instructions",
        original="Review the code and provide feedback.",
        problem="No specifics on what to look for or how to format feedback",
    ),
    VagueSnippet(
        category="Constraints",
        original="Be appropriate and follow best practices.",
        problem="'Appropriate' and 'best practices' are undefined",
    ),
    VagueSnippet(
        category="Context",
        original="You're helping with a project.",
        problem="No details about project type, team, or goals",
    ),
    VagueSnippet(
        category="Output Format",
        original="Provide a good response.",
        problem="'Good' is subjective, no structure defined",
    ),
]


def exercise() -> dict[str, str]:
    """Rewrite each vague snippet to be specific and actionable.

    Returns:
        Dictionary mapping category to your improved version.
    """
    # TODO: Replace these with your improved versions
    return {
        "Role": "TODO: Rewrite the Role snippet",
        "Instructions": "TODO: Rewrite the Instructions snippet",
        "Constraints": "TODO: Rewrite the Constraints snippet",
        "Context": "TODO: Rewrite the Context snippet",
        "Output Format": "TODO: Rewrite the Output Format snippet",
    }


def validate_solution() -> None:
    """Validate your rewrites."""
    from rich.console import Console
    from rich.table import Table

    console = Console()
    rewrites = exercise()

    console.print("\n[bold]Exercise 2: Vague to Precise[/bold]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Category")
    table.add_column("Original Score", justify="right")
    table.add_column("Your Score", justify="right")
    table.add_column("Improvement", justify="right")

    total_improvement = 0
    all_improved = True

    for snippet in VAGUE_SNIPPETS:
        original_result = analyze_text(snippet.original)
        rewrite = rewrites.get(snippet.category, "")
        rewrite_result = analyze_text(rewrite)

        improvement = rewrite_result.score - original_result.score
        total_improvement += improvement

        if improvement < 20:
            all_improved = False

        imp_color = "green" if improvement >= 20 else "yellow" if improvement > 0 else "red"

        table.add_row(
            snippet.category,
            str(original_result.score),
            str(rewrite_result.score),
            f"[{imp_color}]+{improvement}[/{imp_color}]" if improvement > 0 else f"[red]{improvement}[/red]",
        )

    console.print(table)
    console.print(f"\n[bold]Total Improvement:[/bold] +{total_improvement} points")

    # Show details for each
    console.print("\n[bold]Details:[/bold]\n")

    for snippet in VAGUE_SNIPPETS:
        rewrite = rewrites.get(snippet.category, "")

        console.print(f"[cyan]{snippet.category}[/cyan]")
        console.print(f"[dim]Original:[/dim] {snippet.original}")
        console.print(f"[dim]Problem:[/dim] {snippet.problem}")
        console.print(f"[green]Your rewrite:[/green] {rewrite[:100]}...")
        console.print()

    if all_improved:
        console.print("[bold green]All snippets improved by 20+ points![/bold green]")
    else:
        console.print("[yellow]Some snippets need more improvement (target: +20 each)[/yellow]")


if __name__ == "__main__":
    validate_solution()
