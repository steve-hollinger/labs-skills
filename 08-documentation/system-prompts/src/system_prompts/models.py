"""Data models for system prompts."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PromptComponent(Enum):
    """The four key components of a system prompt."""

    ROLE = "role"
    CONTEXT = "context"
    INSTRUCTIONS = "instructions"
    CONSTRAINTS = "constraints"


class IssueSeverity(Enum):
    """Severity levels for prompt analysis issues."""

    ERROR = "error"
    WARNING = "warning"
    SUGGESTION = "suggestion"


@dataclass
class SystemPrompt:
    """A structured system prompt with four components."""

    role: str
    context: str
    instructions: str
    constraints: str
    name: Optional[str] = None
    description: Optional[str] = None

    def render(self, separator: str = "\n\n") -> str:
        """Render the prompt as a single string.

        Args:
            separator: String to separate components.

        Returns:
            Complete prompt text.
        """
        sections = []

        if self.role:
            sections.append(f"ROLE:\n{self.role}")

        if self.context:
            sections.append(f"CONTEXT:\n{self.context}")

        if self.instructions:
            sections.append(f"INSTRUCTIONS:\n{self.instructions}")

        if self.constraints:
            sections.append(f"CONSTRAINTS:\n{self.constraints}")

        return separator.join(sections)

    def render_compact(self) -> str:
        """Render the prompt without section headers.

        Returns:
            Complete prompt text without explicit headers.
        """
        parts = [self.role, self.context, self.instructions, self.constraints]
        return "\n\n".join(p for p in parts if p)

    @property
    def word_count(self) -> int:
        """Count total words in the prompt."""
        return len(self.render().split())

    @property
    def component_counts(self) -> dict[PromptComponent, int]:
        """Count words in each component."""
        return {
            PromptComponent.ROLE: len(self.role.split()),
            PromptComponent.CONTEXT: len(self.context.split()),
            PromptComponent.INSTRUCTIONS: len(self.instructions.split()),
            PromptComponent.CONSTRAINTS: len(self.constraints.split()),
        }

    def has_component(self, component: PromptComponent) -> bool:
        """Check if a component has content."""
        content = getattr(self, component.value)
        return bool(content and content.strip())

    @property
    def missing_components(self) -> list[PromptComponent]:
        """Get list of missing or empty components."""
        return [c for c in PromptComponent if not self.has_component(c)]


@dataclass
class PromptIssue:
    """An issue found during prompt analysis."""

    message: str
    severity: IssueSeverity
    component: Optional[PromptComponent] = None
    suggestion: Optional[str] = None

    def __str__(self) -> str:
        comp = f"[{self.component.value}] " if self.component else ""
        return f"{self.severity.value.upper()}: {comp}{self.message}"


@dataclass
class AnalysisResult:
    """Result of analyzing a system prompt."""

    score: int  # 0-100 quality score
    issues: list[PromptIssue] = field(default_factory=list)
    components_found: list[PromptComponent] = field(default_factory=list)
    word_count: int = 0
    estimated_tokens: int = 0

    @property
    def is_good(self) -> bool:
        """Check if prompt meets minimum quality bar."""
        return self.score >= 70 and not any(
            i.severity == IssueSeverity.ERROR for i in self.issues
        )

    @property
    def errors(self) -> list[PromptIssue]:
        """Get only error-level issues."""
        return [i for i in self.issues if i.severity == IssueSeverity.ERROR]

    @property
    def warnings(self) -> list[PromptIssue]:
        """Get only warning-level issues."""
        return [i for i in self.issues if i.severity == IssueSeverity.WARNING]

    def add_issue(
        self,
        message: str,
        severity: IssueSeverity,
        component: Optional[PromptComponent] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        """Add an issue to the analysis result."""
        self.issues.append(
            PromptIssue(
                message=message,
                severity=severity,
                component=component,
                suggestion=suggestion,
            )
        )


@dataclass
class PromptTemplate:
    """A reusable prompt template with placeholders."""

    name: str
    description: str
    role_template: str
    context_template: str
    instructions_template: str
    constraints_template: str
    variables: list[str] = field(default_factory=list)

    def render(self, **kwargs: str) -> SystemPrompt:
        """Render the template with provided variables.

        Args:
            **kwargs: Variable values to substitute.

        Returns:
            A SystemPrompt with variables substituted.
        """

        def substitute(template: str) -> str:
            result = template
            for key, value in kwargs.items():
                result = result.replace(f"{{{key}}}", value)
            return result

        return SystemPrompt(
            role=substitute(self.role_template),
            context=substitute(self.context_template),
            instructions=substitute(self.instructions_template),
            constraints=substitute(self.constraints_template),
            name=self.name,
            description=self.description,
        )
