"""Tests for Component Documentation examples and core functionality."""

import pytest

from component_documentation.models import (
    ReadmeSection,
    ReadmeDocument,
    SectionType,
    ApiEndpoint,
    ApiParameter,
    ApiResponse,
    ApiDocumentation,
    HttpMethod,
    DocstringInfo,
    DocumentationScore,
)
from component_documentation.readme_builder import (
    ReadmeBuilder,
    generate_readme,
    validate_readme,
)
from component_documentation.api_docs import (
    document_endpoint,
    generate_api_docs,
    validate_api_docs,
    generate_error_reference,
)
from component_documentation.code_docs import (
    analyze_docstring,
    check_documentation,
    generate_docstring,
    check_module_documentation,
)


class TestReadmeModels:
    """Tests for README data models."""

    def test_readme_section_render(self) -> None:
        """Test rendering a README section."""
        section = ReadmeSection(
            section_type=SectionType.INSTALLATION,
            title="Installation",
            content="pip install my-package",
            order=10,
        )

        rendered = section.render()
        assert "## Installation" in rendered
        assert "pip install" in rendered

    def test_readme_section_title_render(self) -> None:
        """Test that title sections render as H1."""
        section = ReadmeSection(
            section_type=SectionType.TITLE,
            title="My Project",
            content="A great project",
            order=0,
        )

        rendered = section.render()
        assert "# My Project" in rendered
        assert "## " not in rendered

    def test_readme_document_render(self) -> None:
        """Test rendering a complete README."""
        doc = ReadmeDocument(project_name="test-project")
        doc.add_section(SectionType.TITLE, "Test Project", "Description", order=0)
        doc.add_section(SectionType.INSTALLATION, "Installation", "pip install test", order=10)

        rendered = doc.render()
        assert "# Test Project" in rendered
        assert "## Installation" in rendered

    def test_readme_document_missing_sections(self) -> None:
        """Test detecting missing essential sections."""
        doc = ReadmeDocument(project_name="test")
        doc.add_section(SectionType.TITLE, "Title", "Desc", order=0)

        missing = doc.missing_essential_sections
        assert SectionType.INSTALLATION in missing
        assert SectionType.QUICK_START in missing


class TestReadmeBuilder:
    """Tests for README builder."""

    def test_basic_readme_build(self) -> None:
        """Test building a basic README."""
        readme = (
            ReadmeBuilder("my-lib")
            .with_description("A library")
            .with_installation("pip install my-lib")
            .with_quick_start("import my_lib")
            .build()
        )

        rendered = readme.render()
        assert "my-lib" in rendered
        assert "pip install" in rendered

    def test_readme_with_features(self) -> None:
        """Test adding features to README."""
        readme = (
            ReadmeBuilder("my-lib")
            .with_description("A library")
            .with_features(["Fast", "Easy", "Tested"])
            .with_installation("pip install my-lib")
            .build()
        )

        rendered = readme.render()
        assert "- Fast" in rendered
        assert "- Easy" in rendered

    def test_readme_with_config(self) -> None:
        """Test adding configuration options."""
        readme = (
            ReadmeBuilder("my-lib")
            .with_description("A library")
            .with_config_option("timeout", "Request timeout", "30")
            .with_installation("pip install my-lib")
            .build()
        )

        rendered = readme.render()
        assert "timeout" in rendered
        assert "30" in rendered

    def test_generate_readme(self) -> None:
        """Test the generate_readme convenience function."""
        readme = generate_readme(
            project_name="test-lib",
            description="A test library",
            features=["Feature 1"],
            install_command="pip install test-lib",
            quick_start_code="import test_lib",
        )

        assert "# test-lib" in readme
        assert "pip install" in readme


class TestReadmeValidation:
    """Tests for README validation."""

    def test_validate_good_readme(self) -> None:
        """Test validating a well-structured README."""
        readme = """# My Project

A description of the project.

## Installation

```bash
pip install my-project
```

## Quick Start

```python
from my_project import main
main()
```

## Usage

More examples here.
"""
        score = validate_readme(readme)
        assert score.is_passing
        assert score.score >= 70

    def test_validate_missing_sections(self) -> None:
        """Test that missing sections are flagged."""
        readme = "# Title\n\nJust a title."

        score = validate_readme(readme)
        assert not score.is_passing
        assert len(score.issues) > 0


class TestApiDocs:
    """Tests for API documentation."""

    def test_document_endpoint(self) -> None:
        """Test creating an endpoint documentation."""
        endpoint = document_endpoint(
            method="GET",
            path="/users",
            summary="List users",
            parameters=[
                {"name": "limit", "type": "integer", "required": False, "description": "Max results"}
            ],
            responses=[
                {"status_code": 200, "description": "Success"}
            ],
        )

        assert endpoint.method == HttpMethod.GET
        assert endpoint.path == "/users"
        assert len(endpoint.parameters) == 1
        assert len(endpoint.responses) == 1

    def test_endpoint_render_markdown(self) -> None:
        """Test rendering endpoint as markdown."""
        endpoint = document_endpoint(
            method="POST",
            path="/tasks",
            summary="Create task",
            request_body={"title": "Test"},
            responses=[{"status_code": 201, "description": "Created"}],
        )

        markdown = endpoint.render_markdown()
        assert "POST /tasks" in markdown
        assert "201" in markdown

    def test_generate_api_docs(self) -> None:
        """Test generating complete API documentation."""
        endpoint = document_endpoint(
            method="GET",
            path="/health",
            summary="Health check",
            responses=[{"status_code": 200, "description": "OK"}],
        )

        docs = generate_api_docs(
            title="Test API",
            description="A test API",
            base_url="https://api.example.com",
            version="1.0.0",
            endpoints=[endpoint],
        )

        assert "# Test API" in docs
        assert "Health check" in docs

    def test_validate_api_docs(self) -> None:
        """Test API documentation validation."""
        endpoint = document_endpoint(
            method="GET",
            path="/test",
            summary="Test endpoint",
            responses=[
                {"status_code": 200, "description": "Success"},
                {"status_code": 404, "description": "Not found"},
            ],
        )

        docs = ApiDocumentation(
            title="Test API",
            description="Description",
            base_url="https://api.example.com",
            version="1.0.0",
            endpoints=[endpoint],
            authentication="API Key",
        )

        score = validate_api_docs(docs)
        assert score.is_passing

    def test_generate_error_reference(self) -> None:
        """Test error reference generation."""
        errors = [
            ("NOT_FOUND", 404, "Resource not found"),
            ("UNAUTHORIZED", 401, "Invalid credentials"),
        ]

        reference = generate_error_reference(errors)
        assert "NOT_FOUND" in reference
        assert "404" in reference


class TestCodeDocs:
    """Tests for code documentation utilities."""

    def test_analyze_docstring_full(self) -> None:
        """Test analyzing a complete docstring."""
        docstring = """Summary line.

        Extended description here.

        Args:
            param1: Description of param1.
            param2: Description of param2.

        Returns:
            Description of return value.

        Raises:
            ValueError: When value is invalid.

        Example:
            >>> func(1, 2)
            3
        """

        info = analyze_docstring(docstring)

        assert info.summary == "Summary line."
        assert "param1" in info.args
        assert info.returns is not None
        assert "ValueError" in info.raises
        assert len(info.examples) > 0

    def test_analyze_docstring_minimal(self) -> None:
        """Test analyzing a minimal docstring."""
        docstring = "Does something."

        info = analyze_docstring(docstring)

        assert info.summary == "Does something."
        assert len(info.args) == 0

    def test_analyze_docstring_empty(self) -> None:
        """Test analyzing an empty docstring."""
        info = analyze_docstring(None)

        assert info.summary == ""
        assert not info.is_complete

    def test_docstring_completeness_score(self) -> None:
        """Test completeness scoring."""
        full_info = DocstringInfo(
            summary="Summary",
            description="Description",
            args={"x": "param"},
            returns="Return value",
            raises={"ValueError": "error"},
            examples=[">>> code"],
        )

        assert full_info.completeness_score == 100
        assert full_info.is_complete

    def test_check_documentation(self) -> None:
        """Test checking function documentation."""

        def well_documented(x: int, y: int) -> int:
            """Add two numbers.

            Args:
                x: First number.
                y: Second number.

            Returns:
                Sum of x and y.
            """
            return x + y

        score = check_documentation(well_documented)
        assert score.is_passing

    def test_check_documentation_missing(self) -> None:
        """Test checking undocumented function."""

        def undocumented(x, y):
            return x + y

        score = check_documentation(undocumented)
        assert not score.is_passing
        assert len(score.issues) > 0

    def test_generate_docstring(self) -> None:
        """Test docstring generation."""
        docstring = generate_docstring(
            func_name="process",
            params=[("data", "list", "Data to process")],
            returns=("int", "Processed count"),
        )

        assert "Args:" in docstring
        assert "data:" in docstring
        assert "Returns:" in docstring

    def test_check_module_documentation(self) -> None:
        """Test module documentation checking."""
        source = '''"""Module docstring."""

def public_func(x: int) -> int:
    """Public function.

    Args:
        x: Input value.

    Returns:
        Processed value.
    """
    return x * 2

def _private_func(x):
    return x
'''

        score = check_module_documentation(source)
        assert score.is_passing


class TestDocumentationScore:
    """Tests for DocumentationScore model."""

    def test_score_calculation(self) -> None:
        """Test score penalty calculation."""
        score = DocumentationScore(score=100)

        score.add_issue("Error", penalty=20)
        assert score.score == 80

        score.add_issue("Another error", penalty=10)
        assert score.score == 70

    def test_score_minimum(self) -> None:
        """Test that score doesn't go below zero."""
        score = DocumentationScore(score=100)

        for _ in range(20):
            score.add_issue("Error", penalty=10)

        assert score.score == 0

    def test_suggestions_no_penalty(self) -> None:
        """Test that suggestions don't affect score."""
        score = DocumentationScore(score=100)

        score.add_suggestion("Consider adding X")
        assert score.score == 100
        assert len(score.suggestions) == 1


class TestSolutions:
    """Tests for exercise solutions."""

    def test_solution_1_readme_quality(self) -> None:
        """Test that Solution 1's README meets quality bar."""
        from component_documentation.exercises.solutions.solution_1 import solution

        readme = solution()
        score = validate_readme(readme)

        assert score.is_passing
        assert score.score >= 80

    def test_solution_2_api_quality(self) -> None:
        """Test that Solution 2's API docs meet quality bar."""
        from component_documentation.exercises.solutions.solution_2 import solution

        endpoints = solution()

        assert len(endpoints) >= 5

        docs = ApiDocumentation(
            title="Test",
            description="Test",
            base_url="https://test.com",
            version="1.0",
            endpoints=endpoints,
            authentication="Bearer token",
        )

        score = validate_api_docs(docs)
        assert score.is_passing

    def test_solution_3_code_quality(self) -> None:
        """Test that Solution 3's code documentation meets quality bar."""
        from component_documentation.exercises.solutions.solution_3 import solution

        documented = solution()
        score = check_module_documentation(documented)

        assert score.is_passing
        assert score.score >= 70
