"""Fluent builder for constructing system prompts."""

from typing import Optional

from system_prompts.models import SystemPrompt


class PromptBuilder:
    """Fluent builder for creating system prompts.

    Example:
        prompt = (
            PromptBuilder()
            .with_role("senior Python developer")
            .with_expertise(["FastAPI", "PostgreSQL", "security"])
            .with_context("fintech startup", "payment processing")
            .with_task("review code for security issues")
            .with_output_format("markdown with severity ratings")
            .with_constraint("be constructive")
            .with_constraint("focus on security over style")
            .build()
        )
    """

    def __init__(self) -> None:
        """Initialize an empty prompt builder."""
        self._role_parts: list[str] = []
        self._context_parts: list[str] = []
        self._instruction_parts: list[str] = []
        self._constraint_parts: list[str] = []
        self._name: Optional[str] = None
        self._description: Optional[str] = None

    def with_name(self, name: str) -> "PromptBuilder":
        """Set the prompt name for identification."""
        self._name = name
        return self

    def with_description(self, description: str) -> "PromptBuilder":
        """Set a description of what this prompt is for."""
        self._description = description
        return self

    # Role methods
    def with_role(self, role: str) -> "PromptBuilder":
        """Set the primary role (e.g., 'senior Python developer')."""
        self._role_parts.insert(0, f"You are a {role}.")
        return self

    def with_expertise(self, areas: list[str]) -> "PromptBuilder":
        """Add areas of expertise to the role."""
        if len(areas) == 1:
            self._role_parts.append(f"You have deep expertise in {areas[0]}.")
        elif len(areas) == 2:
            self._role_parts.append(f"You have deep expertise in {areas[0]} and {areas[1]}.")
        else:
            formatted = ", ".join(areas[:-1]) + f", and {areas[-1]}"
            self._role_parts.append(f"You have deep expertise in {formatted}.")
        return self

    def with_experience(self, years: int, domain: str) -> "PromptBuilder":
        """Add years of experience in a domain."""
        self._role_parts.append(f"You have {years}+ years of experience in {domain}.")
        return self

    def with_personality(self, traits: list[str]) -> "PromptBuilder":
        """Add personality traits to the role."""
        formatted = " and ".join(traits)
        self._role_parts.append(f"You are {formatted}.")
        return self

    # Context methods
    def with_context(self, environment: str, purpose: str) -> "PromptBuilder":
        """Set the working context."""
        self._context_parts.append(f"You are working in a {environment} environment.")
        self._context_parts.append(f"The goal is to {purpose}.")
        return self

    def with_audience(self, audience: str, skill_level: str = "intermediate") -> "PromptBuilder":
        """Define the target audience."""
        self._context_parts.append(
            f"Your audience is {audience} with {skill_level} skill level."
        )
        return self

    def with_codebase_info(
        self,
        language: str,
        frameworks: Optional[list[str]] = None,
        notes: Optional[str] = None,
    ) -> "PromptBuilder":
        """Add information about the codebase context."""
        info = f"The codebase uses {language}"
        if frameworks:
            info += f" with {', '.join(frameworks)}"
        info += "."
        self._context_parts.append(info)
        if notes:
            self._context_parts.append(notes)
        return self

    # Instruction methods
    def with_task(self, task: str) -> "PromptBuilder":
        """Set the primary task."""
        self._instruction_parts.insert(0, f"Your task is to {task}.")
        return self

    def with_steps(self, steps: list[str]) -> "PromptBuilder":
        """Add numbered steps to follow."""
        formatted_steps = "\n".join(f"{i}. {step}" for i, step in enumerate(steps, 1))
        self._instruction_parts.append(f"Follow these steps:\n{formatted_steps}")
        return self

    def with_output_format(self, format_description: str) -> "PromptBuilder":
        """Specify the desired output format."""
        self._instruction_parts.append(f"Format your response as {format_description}.")
        return self

    def with_example(self, input_example: str, output_example: str) -> "PromptBuilder":
        """Add an input/output example."""
        example = f"Example:\nInput: {input_example}\nOutput: {output_example}"
        self._instruction_parts.append(example)
        return self

    # Constraint methods
    def with_constraint(self, constraint: str) -> "PromptBuilder":
        """Add a single constraint."""
        self._constraint_parts.append(f"- {constraint}")
        return self

    def with_constraints(self, constraints: list[str]) -> "PromptBuilder":
        """Add multiple constraints at once."""
        for constraint in constraints:
            self._constraint_parts.append(f"- {constraint}")
        return self

    def without(self, *things: str) -> "PromptBuilder":
        """Add things to avoid (convenience for negative constraints)."""
        for thing in things:
            self._constraint_parts.append(f"- Do not {thing}")
        return self

    def must_not(self, action: str) -> "PromptBuilder":
        """Add a 'must not' constraint."""
        self._constraint_parts.append(f"- You must not {action}")
        return self

    def build(self) -> SystemPrompt:
        """Build the final SystemPrompt.

        Returns:
            A SystemPrompt with all components assembled.

        Raises:
            ValueError: If no role is defined.
        """
        if not self._role_parts:
            raise ValueError("Role is required. Call with_role() before build().")

        return SystemPrompt(
            role=" ".join(self._role_parts),
            context=" ".join(self._context_parts) if self._context_parts else "",
            instructions=" ".join(self._instruction_parts) if self._instruction_parts else "",
            constraints="\n".join(self._constraint_parts) if self._constraint_parts else "",
            name=self._name,
            description=self._description,
        )

    def preview(self) -> str:
        """Preview the prompt without building.

        Returns:
            A preview of what build() would produce.
        """
        try:
            return self.build().render()
        except ValueError as e:
            return f"[Incomplete prompt: {e}]"


def quick_prompt(
    role: str,
    task: str,
    constraints: Optional[list[str]] = None,
) -> SystemPrompt:
    """Create a simple prompt quickly.

    Args:
        role: The AI role (e.g., "Python developer")
        task: The task to perform
        constraints: Optional list of constraints

    Returns:
        A basic SystemPrompt.
    """
    builder = PromptBuilder().with_role(role).with_task(task)

    if constraints:
        builder.with_constraints(constraints)

    return builder.build()
