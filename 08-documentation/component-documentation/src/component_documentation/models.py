"""Data models for component documentation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any


class HttpMethod(Enum):
    """HTTP methods for API endpoints."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class SectionType(Enum):
    """Types of README sections."""

    TITLE = "title"
    DESCRIPTION = "description"
    BADGES = "badges"
    FEATURES = "features"
    INSTALLATION = "installation"
    QUICK_START = "quick_start"
    USAGE = "usage"
    API_REFERENCE = "api_reference"
    CONFIGURATION = "configuration"
    EXAMPLES = "examples"
    CONTRIBUTING = "contributing"
    LICENSE = "license"
    CUSTOM = "custom"


@dataclass
class ReadmeSection:
    """A section within a README file."""

    section_type: SectionType
    title: str
    content: str
    order: int = 0

    def render(self) -> str:
        """Render the section as markdown."""
        if self.section_type == SectionType.TITLE:
            return f"# {self.title}\n\n{self.content}"
        else:
            return f"## {self.title}\n\n{self.content}"


@dataclass
class ReadmeDocument:
    """A complete README document."""

    project_name: str
    sections: list[ReadmeSection] = field(default_factory=list)

    def render(self) -> str:
        """Render the complete README as markdown."""
        sorted_sections = sorted(self.sections, key=lambda s: s.order)
        return "\n\n".join(s.render() for s in sorted_sections)

    def add_section(
        self,
        section_type: SectionType,
        title: str,
        content: str,
        order: Optional[int] = None,
    ) -> None:
        """Add a section to the README."""
        if order is None:
            order = len(self.sections) * 10
        self.sections.append(
            ReadmeSection(
                section_type=section_type,
                title=title,
                content=content,
                order=order,
            )
        )

    def has_section(self, section_type: SectionType) -> bool:
        """Check if README has a specific section type."""
        return any(s.section_type == section_type for s in self.sections)

    @property
    def missing_essential_sections(self) -> list[SectionType]:
        """Get list of missing essential sections."""
        essential = [
            SectionType.TITLE,
            SectionType.INSTALLATION,
            SectionType.QUICK_START,
        ]
        return [s for s in essential if not self.has_section(s)]


@dataclass
class ApiParameter:
    """A parameter for an API endpoint."""

    name: str
    param_type: str
    required: bool
    description: str
    default: Optional[str] = None
    example: Optional[str] = None


@dataclass
class ApiResponse:
    """An API response definition."""

    status_code: int
    description: str
    example: Optional[dict[str, Any]] = None
    schema: Optional[dict[str, Any]] = None


@dataclass
class ApiEndpoint:
    """An API endpoint definition."""

    method: HttpMethod
    path: str
    summary: str
    description: str = ""
    parameters: list[ApiParameter] = field(default_factory=list)
    request_body: Optional[dict[str, Any]] = None
    responses: list[ApiResponse] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def render_markdown(self) -> str:
        """Render endpoint documentation as markdown."""
        lines = [
            f"### {self.summary}",
            "",
            f"`{self.method.value} {self.path}`",
            "",
        ]

        if self.description:
            lines.extend([self.description, ""])

        if self.parameters:
            lines.append("**Parameters**")
            lines.append("")
            lines.append("| Name | Type | Required | Description |")
            lines.append("|------|------|----------|-------------|")
            for param in self.parameters:
                required = "Yes" if param.required else "No"
                lines.append(
                    f"| {param.name} | {param.param_type} | {required} | {param.description} |"
                )
            lines.append("")

        if self.request_body:
            lines.append("**Request Body**")
            lines.append("```json")
            import json

            lines.append(json.dumps(self.request_body, indent=2))
            lines.append("```")
            lines.append("")

        if self.responses:
            lines.append("**Responses**")
            lines.append("")
            for response in self.responses:
                lines.append(f"**{response.status_code}** - {response.description}")
                if response.example:
                    lines.append("```json")
                    import json

                    lines.append(json.dumps(response.example, indent=2))
                    lines.append("```")
                lines.append("")

        return "\n".join(lines)


@dataclass
class ApiDocumentation:
    """Complete API documentation."""

    title: str
    description: str
    base_url: str
    version: str
    endpoints: list[ApiEndpoint] = field(default_factory=list)
    authentication: Optional[str] = None

    def render_markdown(self) -> str:
        """Render complete API documentation as markdown."""
        lines = [
            f"# {self.title}",
            "",
            self.description,
            "",
            f"**Base URL:** `{self.base_url}`",
            f"**Version:** {self.version}",
            "",
        ]

        if self.authentication:
            lines.extend([
                "## Authentication",
                "",
                self.authentication,
                "",
            ])

        lines.append("## Endpoints")
        lines.append("")

        for endpoint in self.endpoints:
            lines.append(endpoint.render_markdown())

        return "\n".join(lines)


@dataclass
class DocstringInfo:
    """Parsed information from a docstring."""

    summary: str
    description: str = ""
    args: dict[str, str] = field(default_factory=dict)
    returns: Optional[str] = None
    raises: dict[str, str] = field(default_factory=dict)
    examples: list[str] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """Check if docstring has all essential parts."""
        return bool(self.summary and (self.args or self.returns))

    @property
    def completeness_score(self) -> int:
        """Calculate completeness score (0-100)."""
        score = 0
        if self.summary:
            score += 30
        if self.description:
            score += 10
        if self.args:
            score += 20
        if self.returns:
            score += 20
        if self.raises:
            score += 10
        if self.examples:
            score += 10
        return score


@dataclass
class DocumentationScore:
    """Score for documentation quality."""

    score: int
    max_score: int = 100
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    @property
    def is_passing(self) -> bool:
        """Check if score meets minimum threshold."""
        return self.score >= 70

    @property
    def percentage(self) -> float:
        """Get score as percentage."""
        return (self.score / self.max_score) * 100

    def add_issue(self, issue: str, penalty: int = 10) -> None:
        """Add an issue and reduce score."""
        self.issues.append(issue)
        self.score = max(0, self.score - penalty)

    def add_suggestion(self, suggestion: str) -> None:
        """Add a suggestion without penalty."""
        self.suggestions.append(suggestion)
