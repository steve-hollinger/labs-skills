"""Example 3: Prompt Debugging and Improvement

This example demonstrates techniques for diagnosing and fixing
underperforming prompts through iterative refinement.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from system_prompts.models import SystemPrompt
from system_prompts.analyzer import analyze_prompt, analyze_text


# A problematic prompt that needs improvement
BAD_PROMPT = SystemPrompt(
    role="You are a helpful assistant.",
    context="",
    instructions="Help the user with their code.",
    constraints="Be nice.",
    name="Bad Example",
)

# An improved version after debugging
IMPROVED_PROMPT = SystemPrompt(
    role="""You are a senior software engineer with expertise in Python, JavaScript,
and cloud infrastructure. You have 10+ years of experience building production
systems and are known for clear, practical advice.""",

    context="""You are helping developers solve coding problems during their workday.
They may be debugging issues, designing solutions, or learning new concepts.
Time is valuable, so focus on actionable solutions.""",

    instructions="""When helping with code:

1. First, understand the problem:
   - What is the code supposed to do?
   - What is actually happening?
   - What error messages appear?

2. Provide solutions:
   - Give working code, not pseudocode
   - Include necessary imports
   - Add comments for complex logic
   - Handle edge cases and errors

3. Explain your reasoning:
   - Why this approach works
   - What alternatives exist
   - Potential pitfalls to watch for

Format responses with:
- Brief summary of the issue
- Working code solution
- Explanation of key points""",

    constraints="""- Don't guess if you're unsure - ask for clarification
- Don't use deprecated functions or insecure patterns
- Don't write overly complex solutions when simple ones work
- If there are multiple valid approaches, mention tradeoffs
- Always consider security implications in your suggestions""",

    name="Improved Example",
)


def main() -> None:
    """Run the prompt debugging example."""
    console = Console()

    console.print(Panel.fit(
        "[bold blue]Example 3: Prompt Debugging and Improvement[/bold blue]\n"
        "Learn techniques for diagnosing and fixing underperforming prompts.",
        title="System Prompts"
    ))

    # Show the problematic prompt
    console.print("\n[bold red]The Problematic Prompt:[/bold red]\n")
    console.print(Panel(
        BAD_PROMPT.render(),
        title="Before",
        border_style="red",
    ))

    # Analyze it
    bad_result = analyze_prompt(BAD_PROMPT)

    console.print("\n[bold]Analysis Results:[/bold]")
    _show_analysis(console, bad_result, "red")

    # Walk through the problems
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Identified Problems:[/bold]\n")

    problems = [
        {
            "issue": "Vague role: 'helpful assistant'",
            "impact": "AI doesn't know what expertise level to use",
            "fix": "Specify expertise areas and experience level",
        },
        {
            "issue": "No context provided",
            "impact": "AI can't tailor responses to the situation",
            "fix": "Add information about the user and environment",
        },
        {
            "issue": "Instructions too brief",
            "impact": "AI must guess at format and approach",
            "fix": "Add specific steps and output format",
        },
        {
            "issue": "Constraints are trivial",
            "impact": "No real guidance on what to avoid",
            "fix": "Add substantive constraints about behavior",
        },
    ]

    for i, prob in enumerate(problems, 1):
        console.print(f"[bold]{i}. {prob['issue']}[/bold]")
        console.print(f"   [red]Impact:[/red] {prob['impact']}")
        console.print(f"   [green]Fix:[/green] {prob['fix']}\n")

    # Show the improved version
    console.print("=" * 60)
    console.print("\n[bold green]The Improved Prompt:[/bold green]\n")
    console.print(Panel(
        IMPROVED_PROMPT.render(),
        title="After",
        border_style="green",
    ))

    # Analyze improved version
    good_result = analyze_prompt(IMPROVED_PROMPT)

    console.print("\n[bold]Analysis Results:[/bold]")
    _show_analysis(console, good_result, "green")

    # Show comparison
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Before vs After Comparison:[/bold]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Metric")
    table.add_column("Before", justify="right")
    table.add_column("After", justify="right")
    table.add_column("Change", justify="right")

    metrics = [
        ("Score", bad_result.score, good_result.score),
        ("Word Count", bad_result.word_count, good_result.word_count),
        ("Components", len(bad_result.components_found), len(good_result.components_found)),
        ("Issues", len(bad_result.issues), len(good_result.issues)),
    ]

    for name, before, after in metrics:
        change = after - before
        change_str = f"[green]+{change}[/green]" if change > 0 else f"[red]{change}[/red]"
        table.add_row(name, str(before), str(after), change_str)

    console.print(table)

    # Show debugging workflow
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Prompt Debugging Workflow:[/bold]\n")

    workflow = """
1. **Identify the symptom**
   - AI responses are too vague/generic
   - AI misses important considerations
   - AI uses wrong format or tone
   - AI asks too many clarifying questions

2. **Analyze the prompt**
   - Check for missing components
   - Look for vague language
   - Verify instructions are specific
   - Ensure constraints are meaningful

3. **Make targeted improvements**
   - Add missing components
   - Replace vague words with specifics
   - Add examples and format specs
   - Add constraints for observed issues

4. **Test with varied inputs**
   - Try edge cases
   - Test with ambiguous requests
   - Check error handling guidance
   - Verify tone and format

5. **Iterate**
   - Track improvements
   - Document what worked
   - Build on successful patterns
"""

    console.print(workflow)

    # Demonstrate analyzing raw text
    console.print("=" * 60)
    console.print("\n[bold]Analyzing Raw Prompt Text:[/bold]\n")

    raw_prompt = """You are a Python expert. Review code for bugs and issues.
Be thorough but not nitpicky. Focus on real problems.
Don't suggest changes that break tests.
When you find issues, explain how to fix them."""

    console.print("[dim]Raw text:[/dim]")
    console.print(Panel(raw_prompt, border_style="dim"))

    raw_result = analyze_text(raw_prompt)
    console.print(f"\n[bold]Analysis:[/bold] Score {raw_result.score}/100")
    console.print(f"Components detected: {[c.value for c in raw_result.components_found]}")

    if raw_result.issues:
        console.print("\n[yellow]Issues:[/yellow]")
        for issue in raw_result.issues[:3]:
            console.print(f"  - {issue}")

    console.print("\n[bold green]Example completed successfully![/bold green]")


def _show_analysis(console: Console, result, color: str) -> None:
    """Display analysis results with appropriate formatting."""
    table = Table(show_header=False)
    table.add_column("Metric", style="bold")
    table.add_column("Value")

    score_color = "green" if result.score >= 70 else "yellow" if result.score >= 50 else "red"

    table.add_row("Score", f"[{score_color}]{result.score}/100[/{score_color}]")
    table.add_row("Word Count", str(result.word_count))
    table.add_row("Components Found", f"{len(result.components_found)}/4")

    console.print(table)

    if result.issues:
        console.print(f"\n[{color}]Issues ({len(result.issues)}):[/{color}]")
        for issue in result.issues:
            console.print(f"  - {issue}")


if __name__ == "__main__":
    main()
