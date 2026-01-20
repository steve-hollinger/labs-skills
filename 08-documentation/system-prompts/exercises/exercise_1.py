"""Exercise 1: Write a System Prompt for a Code Reviewer

Your task is to write a system prompt for an AI that reviews Python
pull requests. The AI should focus on security, performance, and
maintainability.

Requirements:
1. Include all four components (role, context, instructions, constraints)
2. Role should establish expertise and experience level
3. Context should describe the working environment
4. Instructions should be specific with numbered steps
5. Constraints should include at least 5 meaningful limitations

Target:
- Quality score: 75+
- Word count: 150-400 words
- All four components present

Hints:
- Think about what expertise a good code reviewer needs
- Consider what context helps (language, team size, priorities)
- Instructions should cover what to check and how to report
- Constraints should prevent common reviewer mistakes
"""

from system_prompts.models import SystemPrompt


def exercise() -> SystemPrompt:
    """Create your code reviewer system prompt.

    Returns:
        A SystemPrompt for code review.
    """
    # TODO: Replace this with your implementation
    return SystemPrompt(
        role="TODO: Define the AI's role and expertise",
        context="TODO: Describe the working environment",
        instructions="TODO: Specify what the AI should do",
        constraints="TODO: List what the AI should avoid",
    )


def validate_solution() -> None:
    """Validate your solution."""
    from system_prompts.analyzer import analyze_prompt
    from rich.console import Console

    console = Console()
    prompt = exercise()
    result = analyze_prompt(prompt)

    console.print("\n[bold]Exercise 1: Code Reviewer Prompt[/bold]\n")
    console.print(f"Quality Score: {result.score}/100")
    console.print(f"Word Count: {result.word_count}")
    console.print(f"Components: {len(result.components_found)}/4")

    # Check requirements
    passed = []
    failed = []

    if result.score >= 75:
        passed.append("Score >= 75")
    else:
        failed.append(f"Score {result.score} < 75")

    if 150 <= result.word_count <= 400:
        passed.append("Word count in range")
    else:
        failed.append(f"Word count {result.word_count} not in 150-400")

    if len(result.components_found) == 4:
        passed.append("All 4 components present")
    else:
        failed.append(f"Only {len(result.components_found)} components")

    if prompt.constraints.count("\n") >= 4 or prompt.constraints.count("-") >= 5:
        passed.append("5+ constraints")
    else:
        failed.append("Fewer than 5 constraints")

    console.print("\n[green]Passed:[/green]")
    for p in passed:
        console.print(f"  + {p}")

    if failed:
        console.print("\n[red]Failed:[/red]")
        for f in failed:
            console.print(f"  - {f}")

    if result.issues:
        console.print("\n[yellow]Issues to address:[/yellow]")
        for issue in result.issues[:5]:
            console.print(f"  - {issue}")

    if not failed:
        console.print("\n[bold green]All requirements met![/bold green]")


if __name__ == "__main__":
    validate_solution()
