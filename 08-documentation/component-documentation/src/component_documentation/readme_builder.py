"""README builder utilities."""

from typing import Optional
from component_documentation.models import (
    ReadmeDocument,
    ReadmeSection,
    SectionType,
    DocumentationScore,
)


class ReadmeBuilder:
    """Fluent builder for creating README documents.

    Example:
        readme = (
            ReadmeBuilder("my-library")
            .with_description("A useful library for doing things.")
            .with_badges(["pypi", "tests", "coverage"])
            .with_features(["Fast", "Easy to use", "Well documented"])
            .with_installation("pip install my-library")
            .with_quick_start('''
                from my_library import do_thing
                result = do_thing()
            ''')
            .build()
        )
    """

    def __init__(self, project_name: str) -> None:
        """Initialize the builder with a project name."""
        self._project_name = project_name
        self._description = ""
        self._badges: list[str] = []
        self._features: list[str] = []
        self._installation = ""
        self._quick_start = ""
        self._usage_sections: list[tuple[str, str]] = []
        self._configuration: list[tuple[str, str, str]] = []
        self._api_reference = ""
        self._contributing = ""
        self._license = ""
        self._custom_sections: list[tuple[str, str]] = []

    def with_description(self, description: str) -> "ReadmeBuilder":
        """Add a project description."""
        self._description = description
        return self

    def with_badges(self, badges: list[str]) -> "ReadmeBuilder":
        """Add badge names (pypi, tests, coverage, etc.)."""
        self._badges = badges
        return self

    def with_features(self, features: list[str]) -> "ReadmeBuilder":
        """Add feature list."""
        self._features = features
        return self

    def with_installation(self, install_command: str) -> "ReadmeBuilder":
        """Add installation instructions."""
        self._installation = install_command
        return self

    def with_quick_start(self, code: str) -> "ReadmeBuilder":
        """Add quick start code example."""
        self._quick_start = code.strip()
        return self

    def with_usage(self, title: str, code: str) -> "ReadmeBuilder":
        """Add a usage example section."""
        self._usage_sections.append((title, code.strip()))
        return self

    def with_config_option(
        self,
        name: str,
        description: str,
        default: str,
    ) -> "ReadmeBuilder":
        """Add a configuration option."""
        self._configuration.append((name, description, default))
        return self

    def with_api_reference(self, content: str) -> "ReadmeBuilder":
        """Add API reference content."""
        self._api_reference = content
        return self

    def with_contributing(self, content: str) -> "ReadmeBuilder":
        """Add contributing guidelines."""
        self._contributing = content
        return self

    def with_license(self, license_type: str) -> "ReadmeBuilder":
        """Add license information."""
        self._license = license_type
        return self

    def with_section(self, title: str, content: str) -> "ReadmeBuilder":
        """Add a custom section."""
        self._custom_sections.append((title, content))
        return self

    def build(self) -> ReadmeDocument:
        """Build the README document."""
        doc = ReadmeDocument(project_name=self._project_name)
        order = 0

        # Title and description
        title_content = self._description
        if self._badges:
            badge_line = " ".join(
                f"![{b}](https://img.shields.io/badge/{b}-blue)"
                for b in self._badges
            )
            title_content = f"{badge_line}\n\n{self._description}"

        doc.add_section(
            SectionType.TITLE,
            self._project_name,
            title_content,
            order=order,
        )
        order += 10

        # Features
        if self._features:
            feature_list = "\n".join(f"- {f}" for f in self._features)
            doc.add_section(
                SectionType.FEATURES,
                "Features",
                feature_list,
                order=order,
            )
            order += 10

        # Installation
        if self._installation:
            doc.add_section(
                SectionType.INSTALLATION,
                "Installation",
                f"```bash\n{self._installation}\n```",
                order=order,
            )
            order += 10

        # Quick Start
        if self._quick_start:
            doc.add_section(
                SectionType.QUICK_START,
                "Quick Start",
                f"```python\n{self._quick_start}\n```",
                order=order,
            )
            order += 10

        # Usage sections
        if self._usage_sections:
            usage_content = ""
            for title, code in self._usage_sections:
                usage_content += f"### {title}\n\n```python\n{code}\n```\n\n"
            doc.add_section(
                SectionType.USAGE,
                "Usage",
                usage_content.strip(),
                order=order,
            )
            order += 10

        # Configuration
        if self._configuration:
            table = "| Option | Description | Default |\n"
            table += "|--------|-------------|--------|\n"
            for name, desc, default in self._configuration:
                table += f"| `{name}` | {desc} | `{default}` |\n"
            doc.add_section(
                SectionType.CONFIGURATION,
                "Configuration",
                table,
                order=order,
            )
            order += 10

        # API Reference
        if self._api_reference:
            doc.add_section(
                SectionType.API_REFERENCE,
                "API Reference",
                self._api_reference,
                order=order,
            )
            order += 10

        # Custom sections
        for title, content in self._custom_sections:
            doc.add_section(
                SectionType.CUSTOM,
                title,
                content,
                order=order,
            )
            order += 10

        # Contributing
        if self._contributing:
            doc.add_section(
                SectionType.CONTRIBUTING,
                "Contributing",
                self._contributing,
                order=order,
            )
            order += 10

        # License
        if self._license:
            doc.add_section(
                SectionType.LICENSE,
                "License",
                f"This project is licensed under the {self._license} License.",
                order=order,
            )

        return doc


def generate_readme(
    project_name: str,
    description: str,
    features: list[str],
    install_command: str,
    quick_start_code: str,
    license_type: str = "MIT",
) -> str:
    """Generate a complete README from basic information.

    Args:
        project_name: Name of the project.
        description: One-line project description.
        features: List of key features.
        install_command: Command to install the package.
        quick_start_code: Example code for quick start.
        license_type: License type (default MIT).

    Returns:
        Complete README content as markdown string.
    """
    doc = (
        ReadmeBuilder(project_name)
        .with_description(description)
        .with_features(features)
        .with_installation(install_command)
        .with_quick_start(quick_start_code)
        .with_contributing("See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.")
        .with_license(license_type)
        .build()
    )

    return doc.render()


def validate_readme(content: str) -> DocumentationScore:
    """Validate a README for completeness and quality.

    Args:
        content: README content as string.

    Returns:
        DocumentationScore with issues and suggestions.
    """
    score = DocumentationScore(score=100)
    content_lower = content.lower()

    # Check for essential sections
    if "# " not in content:
        score.add_issue("Missing title/heading", penalty=20)

    if "install" not in content_lower:
        score.add_issue("Missing installation instructions", penalty=15)

    if "```" not in content:
        score.add_issue("No code examples found", penalty=15)

    if "quick start" not in content_lower and "getting started" not in content_lower:
        score.add_issue("Missing quick start section", penalty=10)

    if "usage" not in content_lower and "example" not in content_lower:
        score.add_issue("Missing usage examples", penalty=10)

    # Check for good practices
    if "license" not in content_lower:
        score.add_suggestion("Consider adding a License section")

    if "contributing" not in content_lower:
        score.add_suggestion("Consider adding a Contributing section")

    if "| " not in content:
        score.add_suggestion("Consider using tables for configuration options")

    # Check length
    word_count = len(content.split())
    if word_count < 100:
        score.add_issue("README is too short", penalty=10)
    elif word_count < 200:
        score.add_suggestion("Consider adding more detail to the README")

    return score
