"""Tests for template management."""

import pytest

from four_layer_prompts.templates import (
    LayerTemplate,
    TemplateRegistry,
    create_default_registry,
)


class TestLayerTemplate:
    """Tests for LayerTemplate class."""

    def test_simple_render(self) -> None:
        """Test basic variable substitution."""
        template = LayerTemplate(template="Hello, $name!")
        result = template.render(name="World")

        assert result == "Hello, World!"

    def test_multiple_variables(self) -> None:
        """Test multiple variable substitution."""
        template = LayerTemplate(
            template="You are a $role specializing in $domain."
        )
        result = template.render(role="developer", domain="Python")

        assert result == "You are a developer specializing in Python."

    def test_safe_substitute(self) -> None:
        """Test that missing variables are left as-is."""
        template = LayerTemplate(template="Hello, $name! Your role is $role.")
        result = template.render(name="Alice")

        assert "Alice" in result
        assert "$role" in result  # Unsubstituted

    def test_required_variables(self) -> None:
        """Test extracting required variables."""
        template = LayerTemplate(
            template="User: $username, Level: $level, Topic: ${topic}"
        )
        required = template.required_variables()

        assert "username" in required
        assert "level" in required
        assert "topic" in required

    def test_validate_variables_missing(self) -> None:
        """Test validation with missing variables."""
        template = LayerTemplate(template="$a $b $c")
        missing = template.validate_variables(a="1", b="2")

        assert "c" in missing
        assert "a" not in missing
        assert "b" not in missing

    def test_validate_variables_complete(self) -> None:
        """Test validation with all variables provided."""
        template = LayerTemplate(template="$x $y")
        missing = template.validate_variables(x="1", y="2")

        assert len(missing) == 0

    def test_jinja_template(self) -> None:
        """Test Jinja2 template rendering."""
        template = LayerTemplate(
            template="Hello, {{ name }}!",
            use_jinja=True,
        )
        result = template.render(name="World")

        assert result == "Hello, World!"

    def test_jinja_conditionals(self) -> None:
        """Test Jinja2 conditionals."""
        template = LayerTemplate(
            template="{% if show_greeting %}Hello!{% endif %}",
            use_jinja=True,
        )

        assert template.render(show_greeting=True) == "Hello!"
        assert template.render(show_greeting=False) == ""

    def test_jinja_loops(self) -> None:
        """Test Jinja2 loops."""
        template = LayerTemplate(
            template="{% for item in items %}{{ item }} {% endfor %}",
            use_jinja=True,
        )
        result = template.render(items=["a", "b", "c"])

        assert result == "a b c "

    def test_template_metadata(self) -> None:
        """Test template with metadata."""
        template = LayerTemplate(
            template="Content",
            name="test_template",
            description="A test template",
        )

        assert template.name == "test_template"
        assert template.description == "A test template"


class TestTemplateRegistry:
    """Tests for TemplateRegistry class."""

    def test_register_and_get_system(self) -> None:
        """Test registering and retrieving system template."""
        registry = TemplateRegistry()
        registry.register_system("test", "System content")

        template = registry.get_system("test")

        assert template.render() == "System content"

    def test_register_layer_template(self) -> None:
        """Test registering LayerTemplate object."""
        registry = TemplateRegistry()
        template = LayerTemplate(template="$greeting, $name!")

        registry.register_system("greeting", template)
        result = registry.get_system("greeting").render(
            greeting="Hello",
            name="World"
        )

        assert result == "Hello, World!"

    def test_get_nonexistent_raises(self) -> None:
        """Test that getting nonexistent template raises KeyError."""
        registry = TemplateRegistry()

        with pytest.raises(KeyError):
            registry.get_system("nonexistent")

    def test_list_templates(self) -> None:
        """Test listing registered templates."""
        registry = TemplateRegistry()
        registry.register_system("sys1", "System 1")
        registry.register_system("sys2", "System 2")
        registry.register_context("ctx1", "Context 1")

        systems = registry.list_systems()
        contexts = registry.list_contexts()

        assert "sys1" in systems
        assert "sys2" in systems
        assert "ctx1" in contexts

    def test_has_template(self) -> None:
        """Test checking template existence."""
        registry = TemplateRegistry()
        registry.register_system("exists", "Content")

        assert registry.has_system("exists")
        assert not registry.has_system("not_exists")
        assert not registry.has_context("exists")  # Different category

    def test_all_layer_types(self) -> None:
        """Test all layer registration methods."""
        registry = TemplateRegistry()

        registry.register_system("s", "System")
        registry.register_context("c", "Context")
        registry.register_instruction("i", "Instruction")
        registry.register_constraint("r", "Constraint")

        assert registry.get_system("s").render() == "System"
        assert registry.get_context("c").render() == "Context"
        assert registry.get_instruction("i").render() == "Instruction"
        assert registry.get_constraint("r").render() == "Constraint"


class TestDefaultRegistry:
    """Tests for default registry creation."""

    def test_creates_registry(self) -> None:
        """Test that default registry is created."""
        registry = create_default_registry()

        assert isinstance(registry, TemplateRegistry)

    def test_has_default_systems(self) -> None:
        """Test default system templates."""
        registry = create_default_registry()

        assert registry.has_system("helpful_assistant")
        assert registry.has_system("expert")
        assert registry.has_system("code_reviewer")

    def test_has_default_contexts(self) -> None:
        """Test default context templates."""
        registry = create_default_registry()

        assert registry.has_context("document")
        assert registry.has_context("code")
        assert registry.has_context("conversation")

    def test_has_default_instructions(self) -> None:
        """Test default instruction templates."""
        registry = create_default_registry()

        assert registry.has_instruction("summarize")
        assert registry.has_instruction("analyze")
        assert registry.has_instruction("generate")

    def test_has_default_constraints(self) -> None:
        """Test default constraint templates."""
        registry = create_default_registry()

        assert registry.has_constraint("concise")
        assert registry.has_constraint("markdown")
        assert registry.has_constraint("json")

    def test_default_templates_render(self) -> None:
        """Test that default templates render correctly."""
        registry = create_default_registry()

        expert = registry.get_system("expert")
        result = expert.render(domain="Python", years="10")

        assert "Python" in result
        assert "10" in result
