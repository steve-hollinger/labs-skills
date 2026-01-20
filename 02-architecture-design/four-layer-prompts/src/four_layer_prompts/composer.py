"""Prompt composition utilities."""

from dataclasses import dataclass, field
from typing import Any, Callable

from four_layer_prompts.layers import PromptBuilder, PromptLayers
from four_layer_prompts.templates import TemplateRegistry, LayerTemplate


LayerTransform = Callable[[str], str]


@dataclass
class PromptComposer:
    """Advanced prompt composer with transformation support.

    Provides methods for composing prompts from templates and
    applying transformations to layers.
    """

    registry: TemplateRegistry | None = None
    _transforms: dict[str, list[LayerTransform]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize transform lists."""
        for layer in ["system", "context", "instruction", "constraint"]:
            if layer not in self._transforms:
                self._transforms[layer] = []

    def add_transform(self, layer: str, transform: LayerTransform) -> "PromptComposer":
        """Add a transformation function for a layer.

        Args:
            layer: Layer name to transform.
            transform: Function to apply to layer content.

        Returns:
            Self for chaining.
        """
        if layer not in self._transforms:
            self._transforms[layer] = []
        self._transforms[layer].append(transform)
        return self

    def _apply_transforms(self, layer: str, content: str) -> str:
        """Apply all transforms for a layer.

        Args:
            layer: Layer name.
            content: Initial content.

        Returns:
            Transformed content.
        """
        for transform in self._transforms.get(layer, []):
            content = transform(content)
        return content

    def compose_from_templates(
        self,
        system_name: str | None = None,
        context_name: str | None = None,
        instruction_name: str | None = None,
        constraint_name: str | None = None,
        variables: dict[str, Any] | None = None,
    ) -> str:
        """Compose a prompt from registered templates.

        Args:
            system_name: Name of system template to use.
            context_name: Name of context template to use.
            instruction_name: Name of instruction template to use.
            constraint_name: Name of constraint template to use.
            variables: Variables to substitute in templates.

        Returns:
            Composed prompt string.
        """
        if not self.registry:
            raise ValueError("No registry configured")

        vars_dict = variables or {}
        builder = PromptBuilder()

        if system_name and self.registry.has_system(system_name):
            system = self.registry.get_system(system_name).render(**vars_dict)
            system = self._apply_transforms("system", system)
            builder.system(system)

        if context_name and self.registry.has_context(context_name):
            context = self.registry.get_context(context_name).render(**vars_dict)
            context = self._apply_transforms("context", context)
            builder.context(context)

        if instruction_name and self.registry.has_instruction(instruction_name):
            instruction = self.registry.get_instruction(instruction_name).render(**vars_dict)
            instruction = self._apply_transforms("instruction", instruction)
            builder.instruction(instruction)

        if constraint_name and self.registry.has_constraint(constraint_name):
            constraint = self.registry.get_constraint(constraint_name).render(**vars_dict)
            constraint = self._apply_transforms("constraint", constraint)
            builder.constraint(constraint)

        return builder.build()

    def compose_from_strings(
        self,
        system: str = "",
        context: str = "",
        instruction: str = "",
        constraint: str = "",
    ) -> str:
        """Compose a prompt from string layers.

        Args:
            system: System layer content.
            context: Context layer content.
            instruction: Instruction layer content.
            constraint: Constraint layer content.

        Returns:
            Composed prompt string.
        """
        system = self._apply_transforms("system", system)
        context = self._apply_transforms("context", context)
        instruction = self._apply_transforms("instruction", instruction)
        constraint = self._apply_transforms("constraint", constraint)

        return (
            PromptBuilder()
            .system(system)
            .context(context)
            .instruction(instruction)
            .constraint(constraint)
            .build()
        )

    def compose_hybrid(
        self,
        system: str | tuple[str, dict[str, Any]] | None = None,
        context: str | tuple[str, dict[str, Any]] | None = None,
        instruction: str | tuple[str, dict[str, Any]] | None = None,
        constraint: str | tuple[str, dict[str, Any]] | None = None,
    ) -> str:
        """Compose prompt with mix of strings and template references.

        Each layer can be:
        - A string (used directly)
        - A tuple of (template_name, variables)
        - None (layer omitted)

        Args:
            system: System layer specification.
            context: Context layer specification.
            instruction: Instruction layer specification.
            constraint: Constraint layer specification.

        Returns:
            Composed prompt string.
        """
        def resolve_layer(
            spec: str | tuple[str, dict[str, Any]] | None,
            get_template: Callable[[str], LayerTemplate] | None,
        ) -> str:
            if spec is None:
                return ""
            if isinstance(spec, str):
                return spec
            if isinstance(spec, tuple) and get_template:
                name, vars_dict = spec
                return get_template(name).render(**vars_dict)
            return ""

        system_content = resolve_layer(
            system,
            self.registry.get_system if self.registry else None
        )
        context_content = resolve_layer(
            context,
            self.registry.get_context if self.registry else None
        )
        instruction_content = resolve_layer(
            instruction,
            self.registry.get_instruction if self.registry else None
        )
        constraint_content = resolve_layer(
            constraint,
            self.registry.get_constraint if self.registry else None
        )

        return self.compose_from_strings(
            system=system_content,
            context=context_content,
            instruction=instruction_content,
            constraint=constraint_content,
        )


def compose_layers(
    system: str = "",
    context: str = "",
    instruction: str = "",
    constraint: str = "",
    separator: str = "\n\n",
) -> str:
    """Simple function to compose four layers into a prompt.

    Args:
        system: System layer content.
        context: Context layer content.
        instruction: Instruction layer content.
        constraint: Constraint layer content.
        separator: Text between layers.

    Returns:
        Composed prompt string.
    """
    layers = [system, context, instruction, constraint]
    return separator.join(layer.strip() for layer in layers if layer.strip())


def compose_with_headers(
    system: str = "",
    context: str = "",
    instruction: str = "",
    constraint: str = "",
) -> str:
    """Compose layers with explicit section headers.

    Useful for debugging and clarity.

    Args:
        system: System layer content.
        context: Context layer content.
        instruction: Instruction layer content.
        constraint: Constraint layer content.

    Returns:
        Composed prompt with headers.
    """
    parts = []

    if system:
        parts.append(f"## System\n{system}")
    if context:
        parts.append(f"## Context\n{context}")
    if instruction:
        parts.append(f"## Instruction\n{instruction}")
    if constraint:
        parts.append(f"## Constraints\n{constraint}")

    return "\n\n".join(parts)


class ConditionalComposer:
    """Composer that builds prompts based on conditions."""

    def __init__(self) -> None:
        """Initialize empty composer."""
        self._conditions: list[tuple[Callable[[], bool], str, str]] = []
        self._default_layers: dict[str, str] = {}

    def when(
        self,
        condition: Callable[[], bool],
        layer: str,
        content: str,
    ) -> "ConditionalComposer":
        """Add conditional layer content.

        Args:
            condition: Function that returns True to include content.
            layer: Layer name (system, context, instruction, constraint).
            content: Content to include if condition is True.

        Returns:
            Self for chaining.
        """
        self._conditions.append((condition, layer, content))
        return self

    def default(self, layer: str, content: str) -> "ConditionalComposer":
        """Set default content for a layer.

        Args:
            layer: Layer name.
            content: Default content.

        Returns:
            Self for chaining.
        """
        self._default_layers[layer] = content
        return self

    def build(self) -> str:
        """Build prompt based on conditions.

        Returns:
            Composed prompt string.
        """
        layers = {
            "system": self._default_layers.get("system", ""),
            "context": self._default_layers.get("context", ""),
            "instruction": self._default_layers.get("instruction", ""),
            "constraint": self._default_layers.get("constraint", ""),
        }

        for condition, layer, content in self._conditions:
            if condition():
                if layers[layer]:
                    layers[layer] = f"{layers[layer]}\n{content}"
                else:
                    layers[layer] = content

        return compose_layers(**layers)
