"""Exercise 2: Improve a Poorly-Written CLAUDE.md

Below is a CLAUDE.md file that has many problems. Your task is to
rewrite it to follow best practices while keeping the same general
information about the project.

Problems in the original:
1. Vague descriptions
2. Missing commands
3. No code examples
4. Generic troubleshooting
5. Aspirational content instead of actual state

Instructions:
1. Identify all the problems in BAD_CLAUDE_MD
2. Rewrite it as IMPROVED_CLAUDE_MD
3. Keep the same project context (payment service)
4. Make all guidance specific and actionable

Expected Output:
- A rewritten CLAUDE.md that scores 85+ on validation
- Every vague phrase replaced with specific guidance
- Code examples for patterns mentioned
- Actual troubleshooting for real errors
"""

BAD_CLAUDE_MD = """# CLAUDE.md

## About
This is the payment service. It handles payments.

## Getting Started
Set up the project and run it. Make sure you have the right dependencies.

## Architecture
We use a clean architecture approach. Services talk to repositories
which talk to the database. Follow best practices.

## Coding Standards
Write clean, maintainable code. Use proper naming conventions and
follow the style guide. Make sure your code is well-tested.

## Error Handling
Handle errors appropriately. Log them properly and return meaningful
error messages to users.

## Database
We use PostgreSQL. Make sure migrations are run correctly.

## Testing
Write comprehensive tests. We aim for good coverage. Tests should
be meaningful and actually test the functionality.

## Deployment
The service is deployed to Kubernetes. Follow the deployment process.

## Help
If you're stuck, ask a team member or check the documentation.
"""


def exercise() -> str:
    """Rewrite the BAD_CLAUDE_MD to follow best practices.

    Returns:
        The improved CLAUDE.md content as a string.
    """
    # TODO: Replace this with your improved version
    improved_claude_md = """# CLAUDE.md - Payment Service

    TODO: Rewrite this CLAUDE.md file to fix all the problems

    """

    return improved_claude_md


def analyze_original() -> None:
    """Analyze the original BAD_CLAUDE_MD."""
    from claude_md_standards.validator import validate_claude_md
    from rich.console import Console

    console = Console()
    console.print("[bold]Analysis of Original BAD_CLAUDE_MD:[/bold]\n")

    result = validate_claude_md(BAD_CLAUDE_MD)

    console.print(f"Score: [red]{result.score}/100[/red]")
    console.print(f"Valid: [red]{result.is_valid}[/red]")

    console.print("\n[bold]Issues found:[/bold]")
    for issue in result.issues:
        console.print(f"  - {issue}")


def validate_solution() -> None:
    """Validate your improved solution."""
    from claude_md_standards.validator import validate_claude_md
    from rich.console import Console

    console = Console()

    # Show original analysis
    analyze_original()

    # Validate improvement
    console.print("\n" + "=" * 50)
    console.print("\n[bold]Analysis of Your IMPROVED_CLAUDE_MD:[/bold]\n")

    content = exercise()
    result = validate_claude_md(content)

    console.print(f"Score: {result.score}/100")

    # Calculate improvement
    original_result = validate_claude_md(BAD_CLAUDE_MD)
    improvement = result.score - original_result.score

    if improvement > 0:
        console.print(f"[green]Improvement: +{improvement} points![/green]")
    else:
        console.print(f"[yellow]Improvement needed: {improvement} points[/yellow]")

    if result.score >= 85:
        console.print("\n[green]Excellent! Your improved CLAUDE.md meets the quality bar.[/green]")
    elif result.score >= 70:
        console.print("\n[yellow]Good progress! Keep improving.[/yellow]")
    else:
        console.print("\n[red]Keep working on it. See remaining issues below.[/red]")

    if result.issues:
        console.print("\n[bold]Remaining issues:[/bold]")
        for issue in result.issues:
            console.print(f"  - {issue}")


if __name__ == "__main__":
    validate_solution()
