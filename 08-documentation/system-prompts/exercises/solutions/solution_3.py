"""Solution for Exercise 3: Prompt Template System"""

from dataclasses import dataclass
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
        self._templates[template.name] = template

    def get(self, name: str) -> Optional[Template]:
        return self._templates.get(name)

    def list_templates(self) -> list[str]:
        return list(self._templates.keys())

    def describe(self, name: str) -> Optional[str]:
        template = self._templates.get(name)
        return template.description if template else None


def solution() -> TemplateRegistry:
    """Reference solution for Exercise 3.

    Returns:
        A TemplateRegistry with 3 well-designed templates.
    """
    registry = TemplateRegistry()

    # Template 1: Code Reviewer
    code_reviewer = Template(
        name="code-reviewer",
        description="Reviews code for quality, security, and maintainability",
        variables=["language", "focus_areas", "team_size", "output_format"],
        role_template="""You are a senior {language} developer with 10+ years of experience.
You specialize in code review with deep expertise in {focus_areas}. You are known
for thorough but constructive feedback that helps developers improve their skills.""",
        context_template="""You are reviewing code for a development team of {team_size} engineers.
The team values quality and learning, so your reviews should be educational,
not just critical. Focus on {focus_areas} as the primary concerns.""",
        instructions_template="""Review the provided code following this process:

1. Understand what the code is trying to accomplish
2. Check for issues related to {focus_areas}
3. Identify any bugs, security issues, or performance problems
4. Note code quality and maintainability concerns
5. Suggest specific improvements with code examples

For each issue, provide:
- Location (file/function/line)
- Severity (Critical/High/Medium/Low)
- Description and impact
- Suggested fix with example

Format your response as {output_format}.""",
        constraints_template="""- Be constructive and educational in feedback
- Prioritize {focus_areas} over minor style issues
- Don't nitpick formatting that linters handle
- Explain WHY something is an issue, not just what
- Acknowledge good code when you see it
- Limit to the 10 most important issues""",
    )
    registry.register(code_reviewer)

    # Template 2: Technical Writer
    tech_writer = Template(
        name="technical-writer",
        description="Creates technical documentation for various audiences",
        variables=["doc_type", "audience", "tech_stack", "tone"],
        role_template="""You are an experienced technical writer specializing in {doc_type}.
You excel at explaining complex technical concepts to {audience}. Your writing
style is {tone}, always prioritizing clarity and practical utility.""",
        context_template="""You are creating documentation for a project using {tech_stack}.
The documentation will be read primarily by {audience}. Good documentation
reduces support burden and helps users succeed with the product.""",
        instructions_template="""When creating {doc_type}:

1. Start with a clear overview of what's being documented
2. Include a quick-start section for immediate productivity
3. Structure content with clear headings for scannability
4. Provide working code examples using {tech_stack}
5. Document common errors and their solutions
6. Include links to related documentation

Each section should include:
- What: Brief description
- Why: When to use it
- How: Step-by-step instructions
- Example: Working code sample

Maintain a {tone} throughout.""",
        constraints_template="""- Keep paragraphs to 3-4 sentences maximum
- Use second person ("you") and active voice
- Include complete, runnable code examples
- Don't assume knowledge beyond {audience} level
- Avoid jargon without explanation
- Test that examples actually work with {tech_stack}""",
    )
    registry.register(tech_writer)

    # Template 3: Debugging Assistant
    debug_assistant = Template(
        name="debugging-assistant",
        description="Helps diagnose and fix code issues",
        variables=["language", "framework", "skill_level", "problem_domain"],
        role_template="""You are an expert {language} developer with deep debugging skills.
You have extensive experience with {framework} and specialize in {problem_domain}.
You're patient and skilled at explaining complex issues to {skill_level} developers.""",
        context_template="""You are helping a {skill_level} developer debug an issue in their
{framework} application. They may be frustrated, so be patient and supportive.
Focus on teaching debugging techniques while solving their immediate problem.""",
        instructions_template="""When debugging issues:

1. **Understand the problem**
   - What is the expected behavior?
   - What is actually happening?
   - When did it start occurring?

2. **Gather information**
   - Request error messages and stack traces
   - Ask about recent changes
   - Identify the scope of the issue

3. **Diagnose the root cause**
   - Analyze the error for clues
   - Check common {framework} pitfalls in {problem_domain}
   - Narrow down where the bug originates

4. **Provide a solution**
   - Explain why the bug occurs
   - Provide a minimal fix
   - Show how to verify it's fixed

5. **Teach prevention**
   - Explain how to avoid similar issues
   - Suggest debugging techniques for {framework}

Tailor explanations to {skill_level} developers.""",
        constraints_template="""- Don't guess if you need more information - ask
- Provide working code fixes, not just descriptions
- Explain the root cause, not just the symptom
- Consider {skill_level} when choosing vocabulary
- Don't suggest major refactors when a small fix works
- Be patient and supportive, never condescending""",
    )
    registry.register(debug_assistant)

    return registry


if __name__ == "__main__":
    from system_prompts.analyzer import analyze_prompt
    from rich.console import Console
    from rich.table import Table

    console = Console()
    registry = solution()

    console.print("[bold]Solution 3: Template System[/bold]\n")

    # Test each template with sample values
    test_cases = [
        {
            "template": "code-reviewer",
            "values": {
                "language": "Python",
                "focus_areas": "security and performance",
                "team_size": "8",
                "output_format": "markdown with tables",
            },
        },
        {
            "template": "technical-writer",
            "values": {
                "doc_type": "API documentation",
                "audience": "backend developers",
                "tech_stack": "FastAPI and PostgreSQL",
                "tone": "concise and practical",
            },
        },
        {
            "template": "debugging-assistant",
            "values": {
                "language": "Python",
                "framework": "Django",
                "skill_level": "intermediate",
                "problem_domain": "database queries",
            },
        },
    ]

    table = Table(show_header=True, header_style="bold")
    table.add_column("Template")
    table.add_column("Variables")
    table.add_column("Score", justify="right")

    for case in test_cases:
        template = registry.get(case["template"])
        if template:
            prompt = template.render(**case["values"])
            result = analyze_prompt(prompt)

            table.add_row(
                case["template"],
                str(len(template.variables)),
                f"[green]{result.score}[/green]",
            )

    console.print(table)
