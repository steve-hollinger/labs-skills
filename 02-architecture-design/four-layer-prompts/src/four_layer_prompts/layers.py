"""Prompt layer definitions and builders."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LayerType(Enum):
    """Types of prompt layers."""

    SYSTEM = "system"
    CONTEXT = "context"
    INSTRUCTION = "instruction"
    CONSTRAINT = "constraint"


@dataclass
class Layer:
    """Individual prompt layer with metadata.

    Attributes:
        layer_type: The type of this layer.
        content: The text content of the layer.
        metadata: Optional metadata for the layer.
    """

    layer_type: LayerType
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Return the layer content."""
        return self.content

    def with_prefix(self, prefix: str) -> "Layer":
        """Return a new layer with a prefix added.

        Args:
            prefix: Text to prepend to content.

        Returns:
            New Layer with prefixed content.
        """
        return Layer(
            layer_type=self.layer_type,
            content=f"{prefix}\n{self.content}",
            metadata=self.metadata,
        )


@dataclass
class PromptLayers:
    """Container for all four prompt layers.

    Attributes:
        system: The system layer defining AI identity.
        context: The context layer with background information.
        instruction: The instruction layer with the task.
        constraint: The constraint layer with output requirements.
    """

    system: str = ""
    context: str = ""
    instruction: str = ""
    constraint: str = ""

    def compose(self, separator: str = "\n\n") -> str:
        """Compose all layers into a single prompt.

        Args:
            separator: Text to place between layers.

        Returns:
            Combined prompt string.
        """
        layers = [self.system, self.context, self.instruction, self.constraint]
        return separator.join(layer for layer in layers if layer)

    def to_dict(self) -> dict[str, str]:
        """Convert layers to dictionary.

        Returns:
            Dictionary with layer names and contents.
        """
        return {
            "system": self.system,
            "context": self.context,
            "instruction": self.instruction,
            "constraint": self.constraint,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "PromptLayers":
        """Create PromptLayers from dictionary.

        Args:
            data: Dictionary with layer contents.

        Returns:
            New PromptLayers instance.
        """
        return cls(
            system=data.get("system", ""),
            context=data.get("context", ""),
            instruction=data.get("instruction", ""),
            constraint=data.get("constraint", ""),
        )


class PromptBuilder:
    """Fluent builder for constructing four-layer prompts."""

    def __init__(self) -> None:
        """Initialize an empty builder."""
        self._system: str = ""
        self._context: str = ""
        self._instruction: str = ""
        self._constraint: str = ""
        self._separator: str = "\n\n"

    def system(self, text: str) -> "PromptBuilder":
        """Set the system layer.

        Args:
            text: System layer content.

        Returns:
            Self for chaining.
        """
        self._system = text.strip()
        return self

    def context(self, text: str) -> "PromptBuilder":
        """Set the context layer.

        Args:
            text: Context layer content.

        Returns:
            Self for chaining.
        """
        self._context = text.strip()
        return self

    def instruction(self, text: str) -> "PromptBuilder":
        """Set the instruction layer.

        Args:
            text: Instruction layer content.

        Returns:
            Self for chaining.
        """
        self._instruction = text.strip()
        return self

    def constraint(self, text: str) -> "PromptBuilder":
        """Set the constraint layer.

        Args:
            text: Constraint layer content.

        Returns:
            Self for chaining.
        """
        self._constraint = text.strip()
        return self

    def separator(self, sep: str) -> "PromptBuilder":
        """Set the layer separator.

        Args:
            sep: Separator string between layers.

        Returns:
            Self for chaining.
        """
        self._separator = sep
        return self

    def append_to_system(self, text: str) -> "PromptBuilder":
        """Append text to the system layer.

        Args:
            text: Text to append.

        Returns:
            Self for chaining.
        """
        if self._system:
            self._system = f"{self._system}\n{text.strip()}"
        else:
            self._system = text.strip()
        return self

    def append_to_context(self, text: str) -> "PromptBuilder":
        """Append text to the context layer.

        Args:
            text: Text to append.

        Returns:
            Self for chaining.
        """
        if self._context:
            self._context = f"{self._context}\n{text.strip()}"
        else:
            self._context = text.strip()
        return self

    def append_to_constraint(self, text: str) -> "PromptBuilder":
        """Append text to the constraint layer.

        Args:
            text: Text to append.

        Returns:
            Self for chaining.
        """
        if self._constraint:
            self._constraint = f"{self._constraint}\n{text.strip()}"
        else:
            self._constraint = text.strip()
        return self

    def build(self) -> str:
        """Build the final prompt string.

        Returns:
            Composed prompt with all layers.
        """
        layers = [self._system, self._context, self._instruction, self._constraint]
        return self._separator.join(layer for layer in layers if layer)

    def build_layers(self) -> PromptLayers:
        """Build and return PromptLayers object.

        Returns:
            PromptLayers with all set layers.
        """
        return PromptLayers(
            system=self._system,
            context=self._context,
            instruction=self._instruction,
            constraint=self._constraint,
        )

    def reset(self) -> "PromptBuilder":
        """Reset the builder to empty state.

        Returns:
            Self for chaining.
        """
        self._system = ""
        self._context = ""
        self._instruction = ""
        self._constraint = ""
        return self

    def copy(self) -> "PromptBuilder":
        """Create a copy of this builder.

        Returns:
            New PromptBuilder with same values.
        """
        new_builder = PromptBuilder()
        new_builder._system = self._system
        new_builder._context = self._context
        new_builder._instruction = self._instruction
        new_builder._constraint = self._constraint
        new_builder._separator = self._separator
        return new_builder
