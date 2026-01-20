"""Tests for CLAUDE.md Standards examples and core functionality."""

import pytest

from claude_md_standards.models import (
    ClaudeMdDocument,
    Section,
    SectionType,
    ValidationResult,
    IssueSeverity,
)
from claude_md_standards.parser import (
    parse_claude_md,
    extract_code_blocks,
    extract_commands,
)
from claude_md_standards.validator import validate_claude_md, quick_check
from claude_md_standards.generator import (
    generate_claude_md,
    generate_web_api_template,
    ProjectConfig,
    ProjectType,
)


class TestParser:
    """Tests for CLAUDE.md parser."""

    def test_parse_basic_document(self) -> None:
        """Test parsing a basic CLAUDE.md document."""
        content = """# My Project

Overview of the project.

## Commands

```bash
make setup
make test
```

## Patterns

Some patterns here.
"""
        doc = parse_claude_md(content)

        assert doc.title == "My Project"
        assert len(doc.sections) == 3
        assert doc.sections[0].title == "My Project"
        assert doc.sections[1].title == "Commands"
        assert doc.sections[2].title == "Patterns"

    def test_parse_nested_headers(self) -> None:
        """Test parsing document with nested headers."""
        content = """# Root

## Section 1

### Subsection 1.1

Content

### Subsection 1.2

More content

## Section 2

Final content
"""
        doc = parse_claude_md(content)

        # Should have 5 sections (root + 2 sections + 2 subsections)
        assert len(doc.sections) == 5
        assert doc.sections[2].level == 3
        assert doc.sections[2].title == "Subsection 1.1"

    def test_detect_section_type_commands(self) -> None:
        """Test that command sections are detected."""
        content = """# Project

## Key Commands

```bash
make setup
make test
```
"""
        doc = parse_claude_md(content)
        commands_section = doc.get_section("Commands")

        assert commands_section is not None
        assert commands_section.section_type == SectionType.COMMANDS

    def test_detect_section_type_patterns(self) -> None:
        """Test that pattern sections are detected."""
        content = """# Project

## Code Patterns

```python
def example():
    pass
```
"""
        doc = parse_claude_md(content)
        patterns_section = doc.get_section("Patterns")

        assert patterns_section is not None
        assert patterns_section.section_type == SectionType.PATTERNS

    def test_extract_code_blocks(self) -> None:
        """Test extracting code blocks from content."""
        content = """
```python
def hello():
    print("hello")
```

Some text

```bash
make test
```
"""
        blocks = extract_code_blocks(content)

        assert len(blocks) == 2
        assert blocks[0][0] == "python"
        assert "def hello" in blocks[0][1]
        assert blocks[1][0] == "bash"
        assert "make test" in blocks[1][1]

    def test_extract_commands(self) -> None:
        """Test extracting shell commands."""
        content = """
```bash
# Setup
make setup
make test

# Deploy
./deploy.sh
```
"""
        commands = extract_commands(content)

        assert "make setup" in commands
        assert "make test" in commands
        assert "./deploy.sh" in commands
        # Comments should be excluded
        assert "# Setup" not in commands


class TestValidator:
    """Tests for CLAUDE.md validator."""

    def test_validate_good_document(self) -> None:
        """Test validation of a well-structured document."""
        content = """# CLAUDE.md - Test Project

A test project for validation.

## Overview

This project does important things. It handles X, Y, and Z
with high quality and reliability.

## Key Commands

```bash
make setup    # Install dependencies
make test     # Run tests
make build    # Build project
```

## Code Patterns

### Error Handling

```python
try:
    do_something()
except SpecificError as e:
    handle_error(e)
```

## Common Mistakes

1. **Forgetting to run tests**
   - Always run `make test` before committing
"""
        result = validate_claude_md(content)

        assert result.is_valid
        assert result.score >= 70

    def test_validate_missing_sections(self) -> None:
        """Test validation catches missing sections."""
        content = """# Project

Just some text without proper sections.
"""
        result = validate_claude_md(content)

        assert not result.is_valid
        assert result.score < 50
        assert len(result.errors) > 0

    def test_validate_vague_language(self) -> None:
        """Test validation catches vague language."""
        content = """# Project

## Overview

This is our project.

## Code Style

Follow best practices and write clean code.
Use appropriate patterns when necessary.

## Commands

```bash
make setup
```
"""
        result = validate_claude_md(content)

        # Should have warnings about vague language
        vague_warnings = [i for i in result.warnings if "vague" in i.message.lower()]
        assert len(vague_warnings) > 0

    def test_validate_commands_without_code_blocks(self) -> None:
        """Test validation catches commands section without code."""
        content = """# Project

## Overview

Good overview content here.

## Key Commands

Run make setup to install and make test to test.

## Patterns

```python
def example():
    pass
```
"""
        result = validate_claude_md(content)

        # Should flag commands section without code blocks
        command_issues = [i for i in result.issues if "Commands" in (i.section or "")]
        assert len(command_issues) > 0

    def test_quick_check(self) -> None:
        """Test quick validation check function."""
        good_content = """# Project

## Overview

Project overview.

## Commands

```bash
make test
```
"""
        is_valid, messages = quick_check(good_content)
        # May have warnings but should be valid
        assert isinstance(is_valid, bool)
        assert isinstance(messages, list)


class TestGenerator:
    """Tests for CLAUDE.md generator."""

    def test_generate_web_api_template(self) -> None:
        """Test generating a web API template."""
        content = generate_web_api_template(
            name="User Service",
            description="Handles user management",
            language="python",
            framework="FastAPI",
        )

        assert "User Service" in content
        assert "FastAPI" in content
        assert "make setup" in content
        assert "make test" in content

    def test_generate_cli_template(self) -> None:
        """Test generating a CLI tool template."""
        from claude_md_standards.generator import generate_cli_template

        content = generate_cli_template(
            name="Data Tool",
            description="CLI for data processing",
            language="python",
        )

        assert "Data Tool" in content
        assert "command-line" in content.lower()

    def test_generate_with_custom_config(self) -> None:
        """Test generating with custom configuration."""
        config = ProjectConfig(
            name="Custom Project",
            project_type=ProjectType.LIBRARY,
            description="A custom library",
            language="python",
            additional_sections={
                "Custom Section": "Custom content here"
            },
        )

        content = generate_claude_md(config)

        assert "Custom Project" in content
        assert "Custom Section" in content
        assert "Custom content here" in content

    def test_generate_go_template(self) -> None:
        """Test generating a Go project template."""
        content = generate_web_api_template(
            name="Go Service",
            description="A Go-based service",
            language="go",
        )

        assert "Go Service" in content
        assert "go.mod" in content or "golangci-lint" in content


class TestModels:
    """Tests for data models."""

    def test_section_word_count(self) -> None:
        """Test section word count calculation."""
        section = Section(
            title="Test",
            content="This is a test with some words.",
            level=2,
        )

        assert section.word_count == 7

    def test_section_has_code_blocks(self) -> None:
        """Test detection of code blocks in section."""
        with_code = Section(
            title="Test",
            content="```python\ncode\n```",
            level=2,
        )
        without_code = Section(
            title="Test",
            content="No code here",
            level=2,
        )

        assert with_code.has_code_blocks
        assert not without_code.has_code_blocks

    def test_section_is_actionable(self) -> None:
        """Test detection of actionable content."""
        actionable = Section(
            title="Test",
            content="Run `make test` to execute tests",
            level=2,
        )
        not_actionable = Section(
            title="Test",
            content="This is just descriptive text.",
            level=2,
        )

        assert actionable.is_actionable
        assert not not_actionable.is_actionable

    def test_validation_result_scoring(self) -> None:
        """Test validation result score calculation."""
        result = ValidationResult(is_valid=True)

        result.add_issue("Error", IssueSeverity.ERROR)
        assert result.score == 80
        assert not result.is_valid

        result.add_issue("Warning", IssueSeverity.WARNING)
        assert result.score == 75

    def test_document_get_section(self) -> None:
        """Test getting section by title."""
        doc = ClaudeMdDocument(
            title="Test",
            sections=[
                Section(title="Overview", content="...", level=2),
                Section(title="Key Commands", content="...", level=2),
            ],
        )

        assert doc.get_section("overview") is not None
        assert doc.get_section("commands") is not None
        assert doc.get_section("nonexistent") is None

    def test_document_has_section(self) -> None:
        """Test checking for section existence."""
        doc = ClaudeMdDocument(
            title="Test",
            sections=[
                Section(title="Overview", content="...", level=2),
            ],
        )

        assert doc.has_section("overview")
        assert not doc.has_section("patterns")


class TestExampleContent:
    """Tests for example content quality."""

    def test_example_1_content_is_valid(self) -> None:
        """Test that Example 1's content passes validation."""
        from claude_md_standards.examples.example_1 import GOOD_CLAUDE_MD

        result = validate_claude_md(GOOD_CLAUDE_MD)
        assert result.is_valid
        assert result.score >= 70

    def test_example_2_bad_content_fails(self) -> None:
        """Test that Example 2's bad content fails validation."""
        from claude_md_standards.examples.example_2 import BAD_CLAUDE_MD

        result = validate_claude_md(BAD_CLAUDE_MD)
        assert result.score < 60

    def test_example_2_good_content_passes(self) -> None:
        """Test that Example 2's good content passes validation."""
        from claude_md_standards.examples.example_2 import GOOD_CLAUDE_MD

        result = validate_claude_md(GOOD_CLAUDE_MD)
        assert result.is_valid
        assert result.score >= 70


class TestSolutions:
    """Tests for exercise solutions."""

    def test_solution_1_quality(self) -> None:
        """Test that Solution 1 meets quality bar."""
        from claude_md_standards.exercises.solutions.solution_1 import solution

        result = validate_claude_md(solution())
        assert result.is_valid
        assert result.score >= 80

    def test_solution_2_quality(self) -> None:
        """Test that Solution 2 meets quality bar."""
        from claude_md_standards.exercises.solutions.solution_2 import solution

        result = validate_claude_md(solution())
        assert result.is_valid
        assert result.score >= 80

    def test_solution_3_hierarchy_quality(self) -> None:
        """Test that Solution 3's hierarchy meets quality bar."""
        from claude_md_standards.exercises.solutions.solution_3 import (
            root_claude_md,
            services_claude_md,
            user_service_claude_md,
        )

        total_score = 0
        for content_fn in [root_claude_md, services_claude_md, user_service_claude_md]:
            result = validate_claude_md(content_fn())
            assert result.is_valid
            total_score += result.score

        # Average should be at least 75
        assert total_score / 3 >= 75
