"""Template management for prompt layers."""

from dataclasses import dataclass, field
from string import Template
from typing import Any, Protocol

from jinja2 import Environment, BaseLoader


class TemplateRenderer(Protocol):
    """Protocol for template renderers."""

    def render(self, **kwargs: Any) -> str:
        """Render the template with given variables."""
        ...


@dataclass
class LayerTemplate:
    """Template for a prompt layer with variable substitution.

    Supports both simple string.Template and Jinja2 templates.

    Attributes:
        template: The template string.
        name: Optional name for the template.
        description: Optional description.
        use_jinja: If True, use Jinja2 for rendering.
    """

    template: str
    name: str = ""
    description: str = ""
    use_jinja: bool = False
    _jinja_env: Environment = field(default_factory=lambda: Environment(loader=BaseLoader()))

    def render(self, **kwargs: Any) -> str:
        """Render the template with provided variables.

        Args:
            **kwargs: Variables to substitute in template.

        Returns:
            Rendered template string.
        """
        if self.use_jinja:
            jinja_template = self._jinja_env.from_string(self.template)
            return jinja_template.render(**kwargs)

        # Use standard string.Template
        return Template(self.template).safe_substitute(**kwargs)

    def required_variables(self) -> set[str]:
        """Extract required variable names from template.

        Returns:
            Set of variable names found in template.
        """
        if self.use_jinja:
            # Parse Jinja2 template for variables
            from jinja2 import meta

            ast = self._jinja_env.parse(self.template)
            return meta.find_undeclared_variables(ast)

        # Parse string.Template
        # Format: $var or ${var}
        import re

        pattern = r"\$\{?(\w+)\}?"
        matches = re.findall(pattern, self.template)
        return set(matches)

    def validate_variables(self, **kwargs: Any) -> list[str]:
        """Check if all required variables are provided.

        Args:
            **kwargs: Variables to check.

        Returns:
            List of missing variable names.
        """
        required = self.required_variables()
        provided = set(kwargs.keys())
        return list(required - provided)


class TemplateRegistry:
    """Registry for managing prompt layer templates.

    Organizes templates by layer type for easy retrieval and reuse.
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._systems: dict[str, LayerTemplate] = {}
        self._contexts: dict[str, LayerTemplate] = {}
        self._instructions: dict[str, LayerTemplate] = {}
        self._constraints: dict[str, LayerTemplate] = {}

    def register_system(self, name: str, template: str | LayerTemplate) -> None:
        """Register a system layer template.

        Args:
            name: Unique name for the template.
            template: Template string or LayerTemplate object.
        """
        if isinstance(template, str):
            template = LayerTemplate(template=template, name=name)
        self._systems[name] = template

    def register_context(self, name: str, template: str | LayerTemplate) -> None:
        """Register a context layer template.

        Args:
            name: Unique name for the template.
            template: Template string or LayerTemplate object.
        """
        if isinstance(template, str):
            template = LayerTemplate(template=template, name=name)
        self._contexts[name] = template

    def register_instruction(self, name: str, template: str | LayerTemplate) -> None:
        """Register an instruction layer template.

        Args:
            name: Unique name for the template.
            template: Template string or LayerTemplate object.
        """
        if isinstance(template, str):
            template = LayerTemplate(template=template, name=name)
        self._instructions[name] = template

    def register_constraint(self, name: str, template: str | LayerTemplate) -> None:
        """Register a constraint layer template.

        Args:
            name: Unique name for the template.
            template: Template string or LayerTemplate object.
        """
        if isinstance(template, str):
            template = LayerTemplate(template=template, name=name)
        self._constraints[name] = template

    def get_system(self, name: str) -> LayerTemplate:
        """Get a system layer template.

        Args:
            name: Template name.

        Returns:
            The requested template.

        Raises:
            KeyError: If template not found.
        """
        return self._systems[name]

    def get_context(self, name: str) -> LayerTemplate:
        """Get a context layer template.

        Args:
            name: Template name.

        Returns:
            The requested template.

        Raises:
            KeyError: If template not found.
        """
        return self._contexts[name]

    def get_instruction(self, name: str) -> LayerTemplate:
        """Get an instruction layer template.

        Args:
            name: Template name.

        Returns:
            The requested template.

        Raises:
            KeyError: If template not found.
        """
        return self._instructions[name]

    def get_constraint(self, name: str) -> LayerTemplate:
        """Get a constraint layer template.

        Args:
            name: Template name.

        Returns:
            The requested template.

        Raises:
            KeyError: If template not found.
        """
        return self._constraints[name]

    def list_systems(self) -> list[str]:
        """List all registered system template names."""
        return list(self._systems.keys())

    def list_contexts(self) -> list[str]:
        """List all registered context template names."""
        return list(self._contexts.keys())

    def list_instructions(self) -> list[str]:
        """List all registered instruction template names."""
        return list(self._instructions.keys())

    def list_constraints(self) -> list[str]:
        """List all registered constraint template names."""
        return list(self._constraints.keys())

    def has_system(self, name: str) -> bool:
        """Check if a system template exists."""
        return name in self._systems

    def has_context(self, name: str) -> bool:
        """Check if a context template exists."""
        return name in self._contexts

    def has_instruction(self, name: str) -> bool:
        """Check if an instruction template exists."""
        return name in self._instructions

    def has_constraint(self, name: str) -> bool:
        """Check if a constraint template exists."""
        return name in self._constraints


def create_default_registry() -> TemplateRegistry:
    """Create a registry with common default templates.

    Returns:
        TemplateRegistry with default templates.
    """
    registry = TemplateRegistry()

    # Default system templates
    registry.register_system(
        "helpful_assistant",
        "You are a helpful AI assistant."
    )
    registry.register_system(
        "expert",
        "You are an expert $domain specialist with $years years of experience."
    )
    registry.register_system(
        "code_reviewer",
        """You are a senior software engineer conducting code reviews.
You focus on code quality, security, performance, and maintainability.
You provide constructive feedback with specific suggestions."""
    )

    # Default context templates
    registry.register_context(
        "document",
        "Document to analyze:\n$document"
    )
    registry.register_context(
        "code",
        "Code to review:\n```$language\n$code\n```"
    )
    registry.register_context(
        "conversation",
        "Previous conversation:\n$history\n\nCurrent message: $message"
    )

    # Default instruction templates
    registry.register_instruction(
        "summarize",
        "Summarize the key points from the provided content."
    )
    registry.register_instruction(
        "analyze",
        "Analyze the provided content and identify:\n$aspects"
    )
    registry.register_instruction(
        "generate",
        "Generate $content_type based on the provided context."
    )

    # Default constraint templates
    registry.register_constraint(
        "concise",
        "Keep your response concise and to the point.\nMaximum length: $max_words words."
    )
    registry.register_constraint(
        "markdown",
        "Format your response using markdown.\nUse headers, bullet points, and code blocks as appropriate."
    )
    registry.register_constraint(
        "json",
        "Return your response as valid JSON matching this schema:\n$schema"
    )

    return registry
