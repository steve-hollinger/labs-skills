"""Tests for prompt layers."""

import pytest

from four_layer_prompts.layers import (
    Layer,
    LayerType,
    PromptLayers,
    PromptBuilder,
)


class TestLayer:
    """Tests for Layer class."""

    def test_layer_creation(self) -> None:
        """Test basic layer creation."""
        layer = Layer(
            layer_type=LayerType.SYSTEM,
            content="You are a helpful assistant.",
        )

        assert layer.layer_type == LayerType.SYSTEM
        assert layer.content == "You are a helpful assistant."

    def test_layer_str(self) -> None:
        """Test layer string representation."""
        layer = Layer(LayerType.INSTRUCTION, "Do something")
        assert str(layer) == "Do something"

    def test_layer_with_metadata(self) -> None:
        """Test layer with metadata."""
        layer = Layer(
            LayerType.CONTEXT,
            "Context content",
            metadata={"source": "user", "priority": 1},
        )

        assert layer.metadata["source"] == "user"
        assert layer.metadata["priority"] == 1

    def test_layer_with_prefix(self) -> None:
        """Test adding prefix to layer."""
        layer = Layer(LayerType.SYSTEM, "Original content")
        new_layer = layer.with_prefix("PREFIX:")

        assert new_layer.content == "PREFIX:\nOriginal content"
        assert layer.content == "Original content"  # Original unchanged


class TestPromptLayers:
    """Tests for PromptLayers class."""

    def test_basic_composition(self) -> None:
        """Test basic layer composition."""
        layers = PromptLayers(
            system="System layer",
            context="Context layer",
            instruction="Instruction layer",
            constraint="Constraint layer",
        )

        result = layers.compose()

        assert "System layer" in result
        assert "Context layer" in result
        assert "Instruction layer" in result
        assert "Constraint layer" in result

    def test_compose_with_separator(self) -> None:
        """Test composition with custom separator."""
        layers = PromptLayers(
            system="A",
            context="B",
            instruction="C",
            constraint="D",
        )

        result = layers.compose(separator="\n---\n")

        assert "A\n---\nB\n---\nC\n---\nD" == result

    def test_compose_skips_empty(self) -> None:
        """Test that empty layers are skipped."""
        layers = PromptLayers(
            system="System",
            context="",
            instruction="Instruction",
            constraint="",
        )

        result = layers.compose()

        assert result == "System\n\nInstruction"

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        layers = PromptLayers(
            system="S",
            context="C",
            instruction="I",
            constraint="R",
        )

        d = layers.to_dict()

        assert d["system"] == "S"
        assert d["context"] == "C"
        assert d["instruction"] == "I"
        assert d["constraint"] == "R"

    def test_from_dict(self) -> None:
        """Test creation from dictionary."""
        d = {
            "system": "System",
            "context": "Context",
            "instruction": "Instruction",
            "constraint": "Constraint",
        }

        layers = PromptLayers.from_dict(d)

        assert layers.system == "System"
        assert layers.context == "Context"

    def test_from_dict_partial(self) -> None:
        """Test creation from partial dictionary."""
        d = {"system": "System only"}

        layers = PromptLayers.from_dict(d)

        assert layers.system == "System only"
        assert layers.context == ""


class TestPromptBuilder:
    """Tests for PromptBuilder class."""

    def test_fluent_building(self) -> None:
        """Test fluent builder pattern."""
        prompt = (
            PromptBuilder()
            .system("System")
            .context("Context")
            .instruction("Instruction")
            .constraint("Constraint")
            .build()
        )

        assert "System\n\nContext\n\nInstruction\n\nConstraint" == prompt

    def test_strips_whitespace(self) -> None:
        """Test that layers are stripped of whitespace."""
        prompt = (
            PromptBuilder()
            .system("  System  ")
            .instruction("  Instruction  ")
            .build()
        )

        assert prompt == "System\n\nInstruction"

    def test_custom_separator(self) -> None:
        """Test builder with custom separator."""
        prompt = (
            PromptBuilder()
            .system("A")
            .instruction("B")
            .separator("\n---\n")
            .build()
        )

        assert prompt == "A\n---\nB"

    def test_append_to_system(self) -> None:
        """Test appending to system layer."""
        prompt = (
            PromptBuilder()
            .system("Base system")
            .append_to_system("Additional info")
            .build()
        )

        assert "Base system\nAdditional info" == prompt

    def test_append_to_empty(self) -> None:
        """Test appending to empty layer."""
        prompt = (
            PromptBuilder()
            .append_to_system("Content")
            .build()
        )

        assert prompt == "Content"

    def test_build_layers(self) -> None:
        """Test building PromptLayers object."""
        layers = (
            PromptBuilder()
            .system("S")
            .context("C")
            .build_layers()
        )

        assert isinstance(layers, PromptLayers)
        assert layers.system == "S"
        assert layers.context == "C"

    def test_reset(self) -> None:
        """Test resetting builder."""
        builder = (
            PromptBuilder()
            .system("System")
            .context("Context")
        )

        builder.reset()
        prompt = builder.build()

        assert prompt == ""

    def test_copy(self) -> None:
        """Test copying builder."""
        original = (
            PromptBuilder()
            .system("System")
            .context("Context")
        )

        copy = original.copy()
        copy.instruction("New instruction")

        # Original unchanged
        assert "instruction" not in original.build().lower()
        # Copy has new content
        assert "New instruction" in copy.build()

    def test_skips_empty_layers(self) -> None:
        """Test that empty layers don't create extra separators."""
        prompt = (
            PromptBuilder()
            .system("System")
            .context("")  # Empty
            .instruction("Instruction")
            .build()
        )

        assert prompt == "System\n\nInstruction"
        assert "\n\n\n" not in prompt  # No triple newlines
