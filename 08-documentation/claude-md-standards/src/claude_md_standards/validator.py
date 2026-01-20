"""Validator for CLAUDE.md files."""

import re
from typing import Optional

from claude_md_standards.models import (
    ClaudeMdDocument,
    IssueSeverity,
    SectionType,
    ValidationResult,
)
from claude_md_standards.parser import parse_claude_md


# Recommended sections for a complete CLAUDE.md
RECOMMENDED_SECTIONS = {
    "essential": [
        ("overview", "Overview or purpose section"),
        ("command", "Commands section"),
    ],
    "recommended": [
        ("pattern", "Code patterns section"),
        ("mistake", "Common mistakes section"),
    ],
    "optional": [
        ("architecture", "Architecture decisions"),
        ("faq", "FAQ or troubleshooting"),
        ("testing", "Testing notes"),
    ],
}

# Vague phrases that should be replaced with specific guidance
VAGUE_PHRASES = [
    (r"\bfollow best practices\b", "Specify which practices"),
    (r"\bwrite clean code\b", "Define what 'clean' means in this context"),
    (r"\buse appropriate\b", "Specify what is appropriate"),
    (r"\bas needed\b", "Define when it's needed"),
    (r"\bwhen necessary\b", "Define what makes it necessary"),
    (r"\bproperly\b", "Define what 'properly' means"),
    (r"\bcorrectly\b", "Show the correct way with an example"),
    (r"\bgood practice\b", "Specify the practice"),
    (r"\bshould be obvious\b", "Explain it explicitly"),
    (r"\bcommon sense\b", "Document the expected behavior"),
]


def validate_claude_md(
    content: str,
    strict: bool = False,
    min_sections: int = 3,
) -> ValidationResult:
    """Validate a CLAUDE.md file for quality and completeness.

    Args:
        content: The raw markdown content of the CLAUDE.md file.
        strict: If True, treat warnings as errors.
        min_sections: Minimum number of sections required.

    Returns:
        ValidationResult with any issues found.
    """
    result = ValidationResult(is_valid=True)

    # Parse the document
    doc = parse_claude_md(content)

    # Check for minimum content
    if doc.total_lines < 10:
        result.add_issue(
            message="Document is too short (less than 10 lines)",
            severity=IssueSeverity.ERROR,
            suggestion="Add more sections covering commands, patterns, and common mistakes",
        )

    if doc.total_words < 50:
        result.add_issue(
            message="Document has too few words (less than 50)",
            severity=IssueSeverity.WARNING,
            suggestion="Expand sections with more detailed explanations",
        )

    # Check for minimum sections
    if len(doc.sections) < min_sections:
        result.add_issue(
            message=f"Document has fewer than {min_sections} sections",
            severity=IssueSeverity.ERROR if strict else IssueSeverity.WARNING,
            suggestion="Add sections for overview, commands, and patterns at minimum",
        )

    # Check for essential sections
    _validate_required_sections(doc, result)

    # Check for vague language
    _validate_vague_language(doc, result)

    # Check section quality
    _validate_section_quality(doc, result)

    # Check for code examples
    _validate_code_examples(doc, result)

    # Bonus points for good practices
    _validate_bonus_features(doc, result)

    return result


def _validate_required_sections(doc: ClaudeMdDocument, result: ValidationResult) -> None:
    """Check for required and recommended sections."""
    section_titles_lower = [s.title.lower() for s in doc.sections]
    all_content_lower = doc.raw_content.lower()

    # Check essential sections
    for keyword, description in RECOMMENDED_SECTIONS["essential"]:
        found = any(keyword in title for title in section_titles_lower)
        if not found:
            # Also check if content exists even without proper header
            if keyword in all_content_lower:
                result.add_issue(
                    message=f"Missing section header for {description}",
                    severity=IssueSeverity.WARNING,
                    suggestion=f"Add a dedicated '## {description}' section",
                )
            else:
                result.add_issue(
                    message=f"Missing essential section: {description}",
                    severity=IssueSeverity.ERROR,
                    suggestion=f"Add a '## {description}' section",
                )

    # Check recommended sections (warnings only)
    for keyword, description in RECOMMENDED_SECTIONS["recommended"]:
        found = any(keyword in title for title in section_titles_lower)
        if not found:
            result.add_issue(
                message=f"Consider adding: {description}",
                severity=IssueSeverity.INFO,
                suggestion=f"A '{description}' section helps AI avoid common pitfalls",
            )


def _validate_vague_language(doc: ClaudeMdDocument, result: ValidationResult) -> None:
    """Check for vague phrases that should be more specific."""
    for section in doc.sections:
        for pattern, suggestion in VAGUE_PHRASES:
            if re.search(pattern, section.content, re.IGNORECASE):
                result.add_issue(
                    message=f"Vague language found: '{pattern.strip(chr(92)).strip('b')}'",
                    severity=IssueSeverity.WARNING,
                    section=section.title,
                    line_number=section.line_number,
                    suggestion=suggestion,
                )


def _validate_section_quality(doc: ClaudeMdDocument, result: ValidationResult) -> None:
    """Check quality of individual sections."""
    for section in doc.sections:
        # Skip short sections that are headers for subsections
        if section.level > 2:
            continue

        # Check for empty or near-empty sections
        if section.word_count < 10:
            result.add_issue(
                message=f"Section '{section.title}' is too brief",
                severity=IssueSeverity.WARNING,
                section=section.title,
                line_number=section.line_number,
                suggestion="Expand with specific details, examples, or code",
            )

        # Command sections should have code blocks
        if section.section_type == SectionType.COMMANDS:
            if not section.has_code_blocks:
                result.add_issue(
                    message=f"Commands section '{section.title}' has no code blocks",
                    severity=IssueSeverity.ERROR,
                    section=section.title,
                    line_number=section.line_number,
                    suggestion="Add bash code blocks with actual commands",
                )

        # Pattern sections should have examples
        if section.section_type == SectionType.PATTERNS:
            if not section.has_code_blocks:
                result.add_issue(
                    message=f"Patterns section '{section.title}' has no code examples",
                    severity=IssueSeverity.WARNING,
                    section=section.title,
                    line_number=section.line_number,
                    suggestion="Add code examples showing the pattern implementation",
                )


def _validate_code_examples(doc: ClaudeMdDocument, result: ValidationResult) -> None:
    """Check that document has sufficient code examples."""
    total_code_blocks = doc.raw_content.count("```")
    if total_code_blocks < 2:
        result.add_issue(
            message="Document has few or no code examples",
            severity=IssueSeverity.WARNING,
            suggestion="Add code blocks showing commands and patterns",
        )


def _validate_bonus_features(doc: ClaudeMdDocument, result: ValidationResult) -> None:
    """Award bonus points for best practices."""
    # Check for "When users ask" section (great for AI guidance)
    if doc.has_section("when user") or doc.has_section("faq") or doc.has_section("ask about"):
        result.score = min(100, result.score + 5)

    # Check for project structure section
    if doc.has_section("structure") or doc.has_section("layout"):
        result.score = min(100, result.score + 5)

    # Check for architecture decisions
    if doc.has_section("architecture") or doc.has_section("decision"):
        result.score = min(100, result.score + 5)


def quick_check(content: str) -> tuple[bool, list[str]]:
    """Perform a quick validation check.

    Args:
        content: The raw markdown content.

    Returns:
        Tuple of (is_valid, list of issue messages).
    """
    result = validate_claude_md(content, strict=False)
    messages = [str(issue) for issue in result.issues]
    return result.is_valid, messages
