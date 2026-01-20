"""Exercise 3: Create a Prompt Template System

Build a reusable prompt template system that can generate prompts
for different scenarios. Your system should:

1. Define a base template structure
2. Allow customization through variables
3. Validate that required variables are provided
4. Generate complete, well-structured prompts

Requirements:
- Create at least 3 templates (you choose the use cases)
- Each template should have at least 4 variables
- Generated prompts should score 70+ on analysis
- Include a function to list all available templates

Bonus:
- Add template composition (one template extending another)
- Add variable validation (e.g., language must be a known language)
"""

from dataclasses import dataclass, field
from typing import Optional

from system_prompts.models import SystemPrompt


@dataclass
class Template:
    """A reusable prompt template."""

    name: str
    description: str
    variables: list[str]
    role_template: str
    context_template: str
    instructions_template: str
    constraints_template: str

    def render(self, **kwargs: str) -> SystemPrompt:
        """Render the template with provided variables."""
        # Check for missing variables
        missing = [v for v in self.variables if v not in kwargs]
        if missing:
            raise ValueError(f"Missing required variables: {missing}")

        def substitute(template: str) -> str:
            result = template
            for key, value in kwargs.items():
                result = result.replace(f"{{{key}}}", str(value))
            return result

        return SystemPrompt(
            role=substitute(self.role_template),
            context=substitute(self.context_template),
            instructions=substitute(self.instructions_template),
            constraints=substitute(self.constraints_template),
            name=f"{self.name} (generated)",
        )


class TemplateRegistry:
    """Registry of available prompt templates."""

    def __init__(self) -> None:
        self._templates: dict[str, Template] = {}

    def register(self, template: Template) -> None:
        """Register a template."""
        self._templates[template.name] = template

    def get(self, name: str) -> Optional[Template]:
        """Get a template by name."""
        return self._templates.get(name)

    def list_templates(self) -> list[str]:
        """List all available template names."""
        return list(self._templates.keys())

    def describe(self, name: str) -> Optional[str]:
        """Get description for a template."""
        template = self._templates.get(name)
        return template.description if template else None


def exercise() -> TemplateRegistry:
    """Create your template registry with at least 3 templates.

    Returns:
        A TemplateRegistry populated with your templates.
    """
    registry = TemplateRegistry()

    # TODO: Create and register at least 3 templates
    # Example structure:
    #
    # template1 = Template(
    #     name="code-reviewer",
    #     description="Reviews code for quality issues",
    #     variables=["language", "focus_areas", "team_context", "output_format"],
    #     role_template="You are a senior {language} developer...",
    #     context_template="You are reviewing code for {team_context}...",
    #     instructions_template="Focus on {focus_areas}...",
    #     constraints_template="Format as {output_format}...",
    # )
    # registry.register(template1)

    return registry


def validate_solution() -> None:
    """Validate your template registry."""
    from system_prompts.analyzer import analyze_prompt
    from rich.console import Console
    from rich.table import Table

    console = Console()
    registry = exercise()

    console.print("\n[bold]Exercise 3: Prompt Template System[/bold]\n")

    templates = registry.list_templates()
    console.print(f"[bold]Templates registered:[/bold] {len(templates)}")

    if len(templates) < 3:
        console.print("[red]Need at least 3 templates![/red]")
        return

    # Test each template
    table = Table(show_header=True, header_style="bold")
    table.add_column("Template")
    table.add_column("Variables")
    table.add_column("Generated Score", justify="right")

    all_pass = True

    for name in templates:
        template = registry.get(name)
        if not template:
            continue

        console.print(f"\n[cyan]Testing: {name}[/cyan]")
        console.print(f"[dim]{template.description}[/dim]")
        console.print(f"Variables: {template.variables}")

        # Try to generate with sample values
        sample_values = {var: f"sample_{var}" for var in template.variables}

        try:
            prompt = template.render(**sample_values)
            result = analyze_prompt(prompt)

            score_color = "green" if result.score >= 70 else "red"
            table.add_row(
                name,
                str(len(template.variables)),
                f"[{score_color}]{result.score}[/{score_color}]",
            )

            if result.score < 70:
                all_pass = False
                console.print(f"[red]Score {result.score} < 70[/red]")

        except Exception as e:
            table.add_row(name, str(len(template.variables)), f"[red]Error: {e}[/red]")
            all_pass = False

    console.print("\n")
    console.print(table)

    # Check requirements
    console.print("\n[bold]Requirements:[/bold]")

    if len(templates) >= 3:
        console.print("[green]+ At least 3 templates[/green]")
    else:
        console.print(f"[red]- Only {len(templates)} templates (need 3)[/red]")

    min_vars = min(len(registry.get(t).variables) for t in templates if registry.get(t))
    if min_vars >= 4:
        console.print("[green]+ All templates have 4+ variables[/green]")
    else:
        console.print(f"[red]- Some templates have < 4 variables[/red]")

    if all_pass:
        console.print("[green]+ All generated prompts score 70+[/green]")
        console.print("\n[bold green]All requirements met![/bold green]")
    else:
        console.print("[red]- Some prompts score below 70[/red]")


if __name__ == "__main__":
    validate_solution()
