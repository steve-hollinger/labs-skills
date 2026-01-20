"""Parser for CLAUDE.md files."""

import re
from typing import Optional

from claude_md_standards.models import ClaudeMdDocument, Section, SectionType


def _detect_section_type(title: str, content: str) -> SectionType:
    """Detect the type of section based on title and content."""
    title_lower = title.lower()

    # Map common title patterns to section types
    type_patterns = {
        SectionType.OVERVIEW: ["overview", "about", "introduction", "purpose", "description"],
        SectionType.COMMANDS: ["command", "usage", "how to", "quick start", "getting started"],
        SectionType.ARCHITECTURE: ["architecture", "design", "structure", "decisions", "adr"],
        SectionType.PATTERNS: ["pattern", "convention", "style", "code pattern", "best practice"],
        SectionType.MISTAKES: ["mistake", "error", "pitfall", "avoid", "anti-pattern", "don't"],
        SectionType.FAQ: ["faq", "question", "when user", "ask about", "troubleshoot"],
        SectionType.TESTING: ["test", "coverage", "verification", "quality"],
        SectionType.DEPENDENCIES: ["depend", "requirement", "prerequisite", "install"],
        SectionType.STRUCTURE: ["structure", "layout", "organization", "directory"],
    }

    for section_type, patterns in type_patterns.items():
        for pattern in patterns:
            if pattern in title_lower:
                return section_type

    # Check content for hints if title doesn't match
    if "```bash" in content and ("make " in content or "npm " in content):
        return SectionType.COMMANDS
    if "```" in content and ("def " in content or "func " in content or "class " in content):
        return SectionType.PATTERNS

    return SectionType.OTHER


def parse_claude_md(content: str, file_path: Optional[str] = None) -> ClaudeMdDocument:
    """Parse a CLAUDE.md file into a structured document.

    Args:
        content: The raw markdown content of the CLAUDE.md file.
        file_path: Optional path to the file for reference.

    Returns:
        A ClaudeMdDocument containing parsed sections.
    """
    lines = content.split("\n")
    sections: list[Section] = []
    current_section: Optional[dict[str, any]] = None  # type: ignore[valid-type]
    document_title = "CLAUDE.md"

    # Regular expression for markdown headers
    header_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

    for line_num, line in enumerate(lines, start=1):
        header_match = header_pattern.match(line)

        if header_match:
            # Save previous section if exists
            if current_section:
                section_content = "\n".join(current_section["lines"]).strip()
                sections.append(
                    Section(
                        title=current_section["title"],
                        content=section_content,
                        level=current_section["level"],
                        section_type=_detect_section_type(
                            current_section["title"], section_content
                        ),
                        line_number=current_section["line_number"],
                    )
                )

            level = len(header_match.group(1))
            title = header_match.group(2).strip()

            # First H1 is the document title
            if level == 1 and not sections and document_title == "CLAUDE.md":
                document_title = title

            current_section = {
                "title": title,
                "level": level,
                "line_number": line_num,
                "lines": [],
            }
        elif current_section:
            current_section["lines"].append(line)

    # Don't forget the last section
    if current_section:
        section_content = "\n".join(current_section["lines"]).strip()
        sections.append(
            Section(
                title=current_section["title"],
                content=section_content,
                level=current_section["level"],
                section_type=_detect_section_type(current_section["title"], section_content),
                line_number=current_section["line_number"],
            )
        )

    return ClaudeMdDocument(
        title=document_title,
        sections=sections,
        raw_content=content,
        file_path=file_path,
    )


def extract_code_blocks(content: str) -> list[tuple[str, str]]:
    """Extract code blocks from markdown content.

    Args:
        content: Markdown content containing code blocks.

    Returns:
        List of tuples (language, code) for each code block.
    """
    pattern = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)
    matches = pattern.findall(content)
    return [(lang or "text", code.strip()) for lang, code in matches]


def extract_commands(content: str) -> list[str]:
    """Extract shell commands from markdown content.

    Args:
        content: Markdown content containing commands.

    Returns:
        List of command strings.
    """
    commands = []

    # Extract from bash code blocks
    code_blocks = extract_code_blocks(content)
    for lang, code in code_blocks:
        if lang in ("bash", "shell", "sh", ""):
            for line in code.split("\n"):
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith("#"):
                    # Remove common prefixes
                    if line.startswith("$ "):
                        line = line[2:]
                    commands.append(line)

    return commands
