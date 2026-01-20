"""Tests for prompt composer."""

import pytest

from four_layer_prompts.composer import (
    PromptComposer,
    compose_layers,
    compose_with_headers,
    ConditionalComposer,
)
from four_layer_prompts.templates import TemplateRegistry, LayerTemplate


class TestComposeLayers:
    """Tests for compose_layers function."""

    def test_basic_composition(self) -> None:
        """Test basic layer composition."""
        result = compose_layers(
            system="System",
            context="Context",
            instruction="Instruction",
            constraint="Constraint",
        )

        assert "System\n\nContext\n\nInstruction\n\nConstraint" == result

    def test_skips_empty_layers(self) -> None:
        """Test that empty layers are skipped."""
        result = compose_layers(
            system="System",
            context="",
            instruction="Instruction",
            constraint="",
        )

        assert result == "System\n\nInstruction"

    def test_custom_separator(self) -> None:
        """Test custom separator."""
        result = compose_layers(
            system="A",
            instruction="B",
            separator="\n---\n",
        )

        assert result == "A\n---\nB"

    def test_strips_whitespace(self) -> None:
        """Test that whitespace is stripped."""
        result = compose_layers(
            system="  System  ",
            instruction="  Instruction  ",
        )

        assert result == "System\n\nInstruction"

    def test_all_empty(self) -> None:
        """Test with all empty layers."""
        result = compose_layers()

        assert result == ""


class TestComposeWithHeaders:
    """Tests for compose_with_headers function."""

    def test_adds_headers(self) -> None:
        """Test that headers are added."""
        result = compose_with_headers(
            system="System content",
            context="Context content",
        )

        assert "## System" in result
        assert "## Context" in result
        assert "System content" in result
        assert "Context content" in result

    def test_skips_empty_with_headers(self) -> None:
        """Test that empty layers don't get headers."""
        result = compose_with_headers(
            system="System",
            context="",
            instruction="Instruction",
        )

        assert "## System" in result
        assert "## Instruction" in result
        assert "## Context" not in result

    def test_all_headers_present(self) -> None:
        """Test all headers when all layers provided."""
        result = compose_with_headers(
            system="S",
            context="C",
            instruction="I",
            constraint="R",
        )

        assert "## System" in result
        assert "## Context" in result
        assert "## Instruction" in result
        assert "## Constraints" in result


class TestPromptComposer:
    """Tests for PromptComposer class."""

    def test_compose_from_strings(self) -> None:
        """Test composing from string layers."""
        composer = PromptComposer()

        result = composer.compose_from_strings(
            system="System",
            instruction="Instruction",
        )

        assert "System" in result
        assert "Instruction" in result

    def test_compose_with_transforms(self) -> None:
        """Test composing with layer transforms."""
        def uppercase(s: str) -> str:
            return s.upper()

        composer = PromptComposer()
        composer.add_transform("system", uppercase)

        result = composer.compose_from_strings(
            system="system content",
            instruction="instruction",
        )

        assert "SYSTEM CONTENT" in result
        assert "instruction" in result  # Not transformed

    def test_compose_from_templates(self) -> None:
        """Test composing from templates."""
        registry = TemplateRegistry()
        registry.register_system("test", LayerTemplate(template="Role: $role"))
        registry.register_instruction("test", LayerTemplate(template="Do: $task"))

        composer = PromptComposer(registry=registry)

        result = composer.compose_from_templates(
            system_name="test",
            instruction_name="test",
            variables={"role": "assistant", "task": "help"},
        )

        assert "Role: assistant" in result
        assert "Do: help" in result

    def test_compose_hybrid(self) -> None:
        """Test hybrid composition."""
        registry = TemplateRegistry()
        registry.register_system("template", LayerTemplate(template="System: $type"))

        composer = PromptComposer(registry=registry)

        result = composer.compose_hybrid(
            system=("template", {"type": "test"}),  # Template
            instruction="Direct instruction",  # String
        )

        assert "System: test" in result
        assert "Direct instruction" in result

    def test_compose_no_registry_error(self) -> None:
        """Test that compose_from_templates requires registry."""
        composer = PromptComposer()

        with pytest.raises(ValueError, match="No registry"):
            composer.compose_from_templates(system_name="test")


class TestConditionalComposer:
    """Tests for ConditionalComposer class."""

    def test_default_layers(self) -> None:
        """Test default layer content."""
        composer = (
            ConditionalComposer()
            .default("system", "Default system")
            .default("instruction", "Default instruction")
        )

        result = composer.build()

        assert "Default system" in result
        assert "Default instruction" in result

    def test_conditional_true(self) -> None:
        """Test conditional when condition is True."""
        composer = (
            ConditionalComposer()
            .default("system", "Base")
            .when(lambda: True, "system", "Additional")
        )

        result = composer.build()

        assert "Base" in result
        assert "Additional" in result

    def test_conditional_false(self) -> None:
        """Test conditional when condition is False."""
        composer = (
            ConditionalComposer()
            .default("system", "Base")
            .when(lambda: False, "system", "Should not appear")
        )

        result = composer.build()

        assert "Base" in result
        assert "Should not appear" not in result

    def test_multiple_conditions(self) -> None:
        """Test multiple conditional layers."""
        flag_a = True
        flag_b = False

        composer = (
            ConditionalComposer()
            .default("instruction", "Task")
            .when(lambda: flag_a, "constraint", "Constraint A")
            .when(lambda: flag_b, "constraint", "Constraint B")
        )

        result = composer.build()

        assert "Constraint A" in result
        assert "Constraint B" not in result

    def test_conditional_empty_default(self) -> None:
        """Test conditional with no default."""
        composer = (
            ConditionalComposer()
            .when(lambda: True, "system", "Only if true")
        )

        result = composer.build()

        assert "Only if true" in result
