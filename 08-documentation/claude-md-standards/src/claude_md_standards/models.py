"""Data models for CLAUDE.md parsing and validation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SectionType(Enum):
    """Types of sections commonly found in CLAUDE.md files."""

    OVERVIEW = "overview"
    COMMANDS = "commands"
    ARCHITECTURE = "architecture"
    PATTERNS = "patterns"
    MISTAKES = "mistakes"
    FAQ = "faq"
    TESTING = "testing"
    DEPENDENCIES = "dependencies"
    STRUCTURE = "structure"
    OTHER = "other"


class IssueSeverity(Enum):
    """Severity levels for validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Section:
    """A section within a CLAUDE.md file."""

    title: str
    content: str
    level: int  # Header level (1-6)
    section_type: SectionType = SectionType.OTHER
    line_number: int = 0

    @property
    def word_count(self) -> int:
        """Count words in the section content."""
        return len(self.content.split())

    @property
    def has_code_blocks(self) -> bool:
        """Check if section contains code blocks."""
        return "```" in self.content

    @property
    def is_actionable(self) -> bool:
        """Check if section contains actionable content."""
        actionable_indicators = [
            "```",  # Code blocks
            "make ",  # Makefile commands
            "run ",  # Run commands
            "- [ ]",  # Task lists
            "1. ",  # Numbered lists
            "Step ",  # Step instructions
        ]
        return any(indicator in self.content for indicator in actionable_indicators)


@dataclass
class ValidationIssue:
    """A single validation issue found in a CLAUDE.md file."""

    message: str
    severity: IssueSeverity
    line_number: Optional[int] = None
    section: Optional[str] = None
    suggestion: Optional[str] = None

    def __str__(self) -> str:
        location = f"Line {self.line_number}: " if self.line_number else ""
        section_info = f"[{self.section}] " if self.section else ""
        return f"{self.severity.value.upper()}: {location}{section_info}{self.message}"


@dataclass
class ValidationResult:
    """Result of validating a CLAUDE.md file."""

    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    score: int = 100  # Quality score 0-100

    @property
    def errors(self) -> list[ValidationIssue]:
        """Get only error-level issues."""
        return [i for i in self.issues if i.severity == IssueSeverity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        """Get only warning-level issues."""
        return [i for i in self.issues if i.severity == IssueSeverity.WARNING]

    def add_issue(
        self,
        message: str,
        severity: IssueSeverity,
        line_number: Optional[int] = None,
        section: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        """Add a validation issue."""
        self.issues.append(
            ValidationIssue(
                message=message,
                severity=severity,
                line_number=line_number,
                section=section,
                suggestion=suggestion,
            )
        )
        # Adjust score based on severity
        if severity == IssueSeverity.ERROR:
            self.score -= 20
        elif severity == IssueSeverity.WARNING:
            self.score -= 5
        self.score = max(0, self.score)

        # Update validity
        if severity == IssueSeverity.ERROR:
            self.is_valid = False


@dataclass
class ClaudeMdDocument:
    """Parsed representation of a CLAUDE.md file."""

    title: str
    sections: list[Section] = field(default_factory=list)
    raw_content: str = ""
    file_path: Optional[str] = None

    @property
    def section_titles(self) -> list[str]:
        """Get all section titles."""
        return [s.title for s in self.sections]

    @property
    def total_words(self) -> int:
        """Count total words in document."""
        return sum(s.word_count for s in self.sections)

    @property
    def total_lines(self) -> int:
        """Count total lines in document."""
        return len(self.raw_content.splitlines())

    def get_section(self, title: str) -> Optional[Section]:
        """Get a section by title (case-insensitive partial match)."""
        title_lower = title.lower()
        for section in self.sections:
            if title_lower in section.title.lower():
                return section
        return None

    def has_section(self, title: str) -> bool:
        """Check if document has a section with given title."""
        return self.get_section(title) is not None
