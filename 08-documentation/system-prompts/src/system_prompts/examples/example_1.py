"""Example 1: Anatomy of a System Prompt

This example dissects a well-structured system prompt to understand
each of the four key components: Role, Context, Instructions, and Constraints.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from system_prompts.models import SystemPrompt, PromptComponent
from system_prompts.analyzer import analyze_prompt


# A well-structured example prompt
EXAMPLE_PROMPT = SystemPrompt(
    role="""You are a senior Python developer with 10+ years of experience
in web application security. You have conducted hundreds of security
audits and are an expert in OWASP Top 10 vulnerabilities. You are known
for being thorough but constructive in your feedback.""",

    context="""You are performing a security review for a fintech startup
that handles payment processing. The application is built with FastAPI
and uses PostgreSQL for data storage. The company must comply with
PCI-DSS requirements. The development team is small (5 developers)
and appreciates detailed explanations that help them learn.""",

    instructions="""Analyze the provided code for security vulnerabilities.

For each vulnerability found:
1. Identify the type (e.g., SQL Injection, XSS, Authentication Bypass)
2. Locate it precisely (file, function, line number)
3. Assess the severity (Critical/High/Medium/Low) based on:
   - Exploitability: How easy is it to exploit?
   - Impact: What's the worst case outcome?
4. Explain how an attacker could exploit it
5. Provide a specific fix with code example
6. Reference relevant OWASP guidelines

After reviewing all code, provide:
- Executive summary (2-3 sentences)
- Prioritized list of fixes
- Overall security posture assessment""",

    constraints="""- Never suggest "security through obscurity" solutions
- Don't recommend deprecated cryptographic functions (MD5, SHA1)
- Always consider PCI-DSS compliance implications
- Don't suggest changes that break existing functionality without warning
- If you're uncertain about a finding, say so rather than guess
- Don't overwhelm with trivial issues - focus on real security risks
- Acknowledge secure code patterns when you see them""",

    name="Security Code Reviewer",
    description="Reviews Python code for security vulnerabilities",
)


def main() -> None:
    """Run the prompt anatomy example."""
    console = Console()

    console.print(Panel.fit(
        "[bold blue]Example 1: Anatomy of a System Prompt[/bold blue]\n"
        "Dissecting the four key components of an effective prompt.",
        title="System Prompts"
    ))

    # Show each component
    components = [
        (PromptComponent.ROLE, EXAMPLE_PROMPT.role, "cyan"),
        (PromptComponent.CONTEXT, EXAMPLE_PROMPT.context, "green"),
        (PromptComponent.INSTRUCTIONS, EXAMPLE_PROMPT.instructions, "yellow"),
        (PromptComponent.CONSTRAINTS, EXAMPLE_PROMPT.constraints, "red"),
    ]

    for component, content, color in components:
        console.print(f"\n[bold {color}]Component: {component.value.upper()}[/bold {color}]")
        console.print(f"[dim]Purpose: {_get_component_purpose(component)}[/dim]\n")
        console.print(Panel(
            content,
            title=component.value.title(),
            border_style=color,
        ))

        # Show word count and key elements
        word_count = len(content.split())
        console.print(f"[dim]Word count: {word_count}[/dim]")

    # Show the complete rendered prompt
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Complete Rendered Prompt:[/bold]\n")
    console.print(Syntax(
        EXAMPLE_PROMPT.render(),
        "text",
        theme="monokai",
        word_wrap=True,
    ))

    # Analyze the prompt
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Prompt Analysis:[/bold]\n")

    result = analyze_prompt(EXAMPLE_PROMPT)

    # Summary table
    table = Table(show_header=True, header_style="bold")
    table.add_column("Metric")
    table.add_column("Value", justify="right")

    table.add_row("Quality Score", f"[green]{result.score}/100[/green]")
    table.add_row("Word Count", str(result.word_count))
    table.add_row("Estimated Tokens", str(result.estimated_tokens))
    table.add_row("Components Found", f"{len(result.components_found)}/4")
    table.add_row("Issues", str(len(result.issues)))

    console.print(table)

    if result.issues:
        console.print("\n[yellow]Issues found:[/yellow]")
        for issue in result.issues:
            console.print(f"  - {issue}")
    else:
        console.print("\n[green]No issues found![/green]")

    # Key takeaways
    console.print("\n" + "=" * 60)
    console.print("\n[bold]Key Takeaways:[/bold]\n")

    takeaways = [
        "[cyan]ROLE[/cyan]: Define expertise, experience level, and personality",
        "[green]CONTEXT[/green]: Provide situation, environment, and audience info",
        "[yellow]INSTRUCTIONS[/yellow]: Specify actions, steps, and output format",
        "[red]CONSTRAINTS[/red]: List what to avoid and quality requirements",
        "All four components work together for predictable AI behavior",
    ]
    for takeaway in takeaways:
        console.print(f"  - {takeaway}")

    console.print("\n[bold green]Example completed successfully![/bold green]")


def _get_component_purpose(component: PromptComponent) -> str:
    """Get a description of what each component does."""
    purposes = {
        PromptComponent.ROLE: "Establishes the AI's identity, expertise, and personality",
        PromptComponent.CONTEXT: "Provides situational information and environment details",
        PromptComponent.INSTRUCTIONS: "Defines what the AI should do and how",
        PromptComponent.CONSTRAINTS: "Sets boundaries on what the AI should avoid",
    }
    return purposes.get(component, "")


if __name__ == "__main__":
    main()
