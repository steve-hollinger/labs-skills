"""Example 2: Prompts for Different Use Cases

This example demonstrates how prompt structure changes for different
use cases: coding assistance, technical writing, and data analysis.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from system_prompts.templates import (
    code_reviewer_template,
    technical_writer_template,
    coding_assistant_template,
    data_analyst_template,
)
from system_prompts.analyzer import analyze_prompt
from system_prompts.builder import PromptBuilder


def main() -> None:
    """Run the use case variations example."""
    console = Console()

    console.print(Panel.fit(
        "[bold blue]Example 2: Prompts for Different Use Cases[/bold blue]\n"
        "See how prompt structure adapts to different scenarios.",
        title="System Prompts"
    ))

    # Create prompts for different use cases
    use_cases = [
        {
            "name": "Code Reviewer",
            "description": "Reviews Python code for security and quality",
            "prompt": code_reviewer_template(
                language="Python",
                focus_areas="security vulnerabilities and performance",
                tone="constructive and educational",
            ),
            "color": "cyan",
        },
        {
            "name": "Technical Writer",
            "description": "Creates API documentation for developers",
            "prompt": technical_writer_template(
                doc_type="REST API documentation",
                audience="backend developers",
                style="concise with working examples",
            ),
            "color": "green",
        },
        {
            "name": "Coding Assistant",
            "description": "Helps developers write and debug code",
            "prompt": coding_assistant_template(
                language="Python",
                frameworks="FastAPI and SQLAlchemy",
                skill_level="intermediate",
            ),
            "color": "yellow",
        },
        {
            "name": "Data Analyst",
            "description": "Analyzes business metrics for insights",
            "prompt": data_analyst_template(
                data_type="user engagement metrics",
                tools="SQL and Python pandas",
            ),
            "color": "magenta",
        },
    ]

    # Show comparison table
    console.print("\n[bold]Use Case Comparison:[/bold]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Use Case")
    table.add_column("Words", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Focus Area")

    for case in use_cases:
        result = analyze_prompt(case["prompt"])
        focus = _identify_focus(case["prompt"])

        table.add_row(
            f"[{case['color']}]{case['name']}[/{case['color']}]",
            str(result.word_count),
            f"{result.score}/100",
            focus,
        )

    console.print(table)

    # Deep dive into each use case
    for case in use_cases:
        console.print(f"\n{'=' * 60}")
        console.print(f"\n[bold {case['color']}]{case['name']}[/bold {case['color']}]")
        console.print(f"[dim]{case['description']}[/dim]\n")

        prompt = case["prompt"]

        # Show key characteristics
        console.print("[bold]Role highlights:[/bold]")
        console.print(f"  {prompt.role[:200]}...")

        console.print("\n[bold]Key instructions:[/bold]")
        instructions = prompt.instructions.split("\n")[:5]
        for inst in instructions:
            if inst.strip():
                console.print(f"  {inst}")

        console.print("\n[bold]Important constraints:[/bold]")
        constraints = prompt.constraints.split("\n")[:3]
        for const in constraints:
            if const.strip():
                console.print(f"  {const}")

        # Analysis
        result = analyze_prompt(prompt)
        if result.issues:
            console.print(f"\n[yellow]Analysis notes ({len(result.issues)}):[/yellow]")
            for issue in result.issues[:2]:
                console.print(f"  - {issue.message}")

    # Show how to customize with PromptBuilder
    console.print(f"\n{'=' * 60}")
    console.print("\n[bold]Building Custom Prompts:[/bold]\n")

    custom_prompt = (
        PromptBuilder()
        .with_name("Custom Security Reviewer")
        .with_role("security engineer")
        .with_expertise(["penetration testing", "secure code review", "OWASP"])
        .with_experience(8, "application security")
        .with_context("healthcare startup", "reviewing code handling PHI data")
        .with_audience("development team", "mixed experience levels")
        .with_task("review code for HIPAA compliance issues")
        .with_steps([
            "Identify data handling patterns",
            "Check encryption at rest and in transit",
            "Verify access controls",
            "Review audit logging",
        ])
        .with_output_format("markdown with severity ratings")
        .with_constraint("Consider HIPAA requirements")
        .with_constraint("Don't suggest breaking existing functionality")
        .without("using deprecated security functions")
        .build()
    )

    console.print("[bold]Built with PromptBuilder:[/bold]\n")
    console.print(Panel(
        custom_prompt.render(),
        title="Custom Security Reviewer",
        border_style="cyan",
    ))

    result = analyze_prompt(custom_prompt)
    console.print(f"\n[bold]Quality Score:[/bold] {result.score}/100")

    # Summary
    console.print(f"\n{'=' * 60}")
    console.print("\n[bold]Key Insights:[/bold]\n")

    insights = [
        "Different use cases need different emphasis on components",
        "Code reviewers need detailed instructions on what to check",
        "Technical writers need format specifications",
        "Coding assistants need skill-level awareness",
        "Data analysts need to avoid overclaiming",
        "Use PromptBuilder for complex, customized prompts",
    ]

    for insight in insights:
        console.print(f"  - {insight}")

    console.print("\n[bold green]Example completed successfully![/bold green]")


def _identify_focus(prompt) -> str:
    """Identify the main focus area of a prompt."""
    content = prompt.render().lower()

    if "security" in content:
        return "Security"
    elif "document" in content:
        return "Documentation"
    elif "debug" in content or "code" in content:
        return "Coding"
    elif "data" in content or "analy" in content:
        return "Analysis"
    else:
        return "General"


if __name__ == "__main__":
    main()
