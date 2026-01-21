#!/usr/bin/env python3
"""
Convert CLAUDE.md files to the official SKILL.md format with YAML frontmatter.

Usage:
    python convert-to-skill-format.py <path-to-skill-directory>
    python convert-to-skill-format.py --all  # Convert all skills
    python convert-to-skill-format.py --dry-run <path>  # Preview without writing
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional

# Gerund mappings for common skill name patterns
GERUND_MAPPINGS = {
    # Go skills
    "http-services": "building-http-services",
    "concurrency": "managing-go-concurrency",
    "mcp-server": "building-mcp-servers",
    "neo4j-driver": "using-neo4j-go-driver",
    "kafka-franz-go": "streaming-with-franz-go",
    # Python skills
    "fastapi-basics": "building-fastapi-services",
    "dynaconf-config": "configuring-with-dynaconf",
    "langchain-langgraph": "building-langchain-agents",
    "pydantic-v2": "validating-with-pydantic",
    "uv-package-manager": "managing-python-packages",
    # Frontend skills
    "react-19-typescript": "building-react-typescript-apps",
    "tailwind-css-4": "styling-with-tailwind",
    "vite-7": "building-with-vite",
    # Security skills
    "api-key-auth": "implementing-api-key-auth",
    "jwt-validation": "validating-jwt-tokens",
    "oauth-21-oidc": "implementing-oauth-oidc",
    "secrets-manager": "managing-aws-secrets",
    "token-masking": "masking-sensitive-tokens",
    # DevOps skills
    "docker-compose": "composing-docker-services",
    "docker-ecr": "building-docker-images",
    "fsd-dependencies": "defining-fsd-dependencies",
    "fsd-iam-policies": "creating-iam-policies",
    "fsd-yaml-config": "configuring-fsd-services",
    "github-actions": "automating-with-github-actions",
    # Data skills
    "dynamodb-schema": "designing-dynamodb-schemas",
    "dynamodb-streams-cdc": "streaming-dynamodb-changes",
    "kafka-event-streaming": "streaming-kafka-events",
    "neo4j-cypher": "querying-with-cypher",
    "neo4j-date-datetime": "handling-neo4j-dates",
    "s3-content-addressed": "storing-content-addressed-s3",
    "valkey-redis": "caching-with-valkey",
    # AI/ML skills
    "hybrid-search": "implementing-hybrid-search",
    "mcp-tool-schemas": "designing-mcp-tool-schemas",
    "openai-responses-api": "using-openai-responses-api",
    "opik-evaluation": "evaluating-with-opik",
    "sse-streaming": "streaming-server-sent-events",
    # Architecture skills
    "component-system": "building-component-systems",
    "dual-mode-streaming": "implementing-dual-mode-streaming",
    "episode-based-history": "managing-episode-history",
    "factory-pattern": "implementing-factory-patterns",
    "four-layer-prompts": "structuring-four-layer-prompts",
    "hybrid-authentication": "implementing-hybrid-auth",
    "tool-registry": "building-tool-registries",
    # Documentation skills
    "claude-md-standards": "writing-claude-md-files",
    "component-documentation": "documenting-components",
    "system-prompts": "crafting-system-prompts",
    # Code quality skills
    "commit-standards": "writing-commit-messages",
    "golangci-lint": "linting-go-code",
    "logging-constants": "defining-logging-constants",
    "bandit-security": "scanning-python-security",
    "mypy-type-checking": "type-checking-with-mypy",
    "ruff-linting": "linting-with-ruff",
    # Testing skills
    "race-detector": "detecting-go-race-conditions",
    "test-logger-init": "initializing-test-loggers",
    "testcontainers": "testing-with-containers",
    "testify-framework": "testing-with-testify",
    "aws-mocking-moto": "mocking-aws-with-moto",
    "pytest-asyncio": "testing-async-python",
    "pytest-markers": "organizing-pytest-markers",
}


def to_gerund_name(skill_name: str) -> str:
    """Convert skill name to gerund form."""
    if skill_name in GERUND_MAPPINGS:
        return GERUND_MAPPINGS[skill_name]

    # Fallback: create a reasonable gerund form
    # Add -ing to common patterns
    if skill_name.endswith("-api"):
        return f"using-{skill_name}"
    if skill_name.endswith("-config"):
        return f"configuring-{skill_name.replace('-config', '')}"
    if skill_name.endswith("-pattern"):
        return f"implementing-{skill_name.replace('-pattern', '-patterns')}"

    # Default: prefix with "using-"
    return f"using-{skill_name}"


def extract_description(content: str) -> str:
    """Extract the first paragraph after the title as description."""
    lines = content.split('\n')
    in_description = False
    description_lines = []

    for line in lines:
        if line.startswith('# CLAUDE.md'):
            in_description = True
            continue
        if in_description:
            if line.strip() == '':
                if description_lines:
                    break
                continue
            if line.startswith('#'):
                break
            description_lines.append(line.strip())

    description = ' '.join(description_lines)
    # Clean up and truncate if needed
    description = re.sub(r'\s+', ' ', description).strip()

    # Create "Use when..." trigger
    skill_type = detect_skill_type(content)
    trigger = generate_trigger(skill_type, content)

    return f"{description} {trigger}"


def detect_skill_type(content: str) -> str:
    """Detect what type of skill this is."""
    content_lower = content.lower()
    if 'jwt' in content_lower or 'auth' in content_lower:
        return 'auth'
    if 'docker' in content_lower or 'container' in content_lower:
        return 'container'
    if 'test' in content_lower:
        return 'testing'
    if 'api' in content_lower or 'http' in content_lower:
        return 'api'
    if 'database' in content_lower or 'dynamodb' in content_lower or 'neo4j' in content_lower:
        return 'database'
    if 'kafka' in content_lower or 'stream' in content_lower:
        return 'streaming'
    if 'lint' in content_lower or 'format' in content_lower:
        return 'quality'
    return 'general'


def generate_trigger(skill_type: str, content: str) -> str:
    """Generate 'Use when...' trigger based on skill type."""
    triggers = {
        'auth': 'Use when implementing authentication or verifying tokens.',
        'container': 'Use when building or deploying containerized applications.',
        'testing': 'Use when writing or improving tests.',
        'api': 'Use when building HTTP APIs or web services.',
        'database': 'Use when designing schemas or querying data.',
        'streaming': 'Use when implementing event streaming or real-time data.',
        'quality': 'Use when improving code quality or consistency.',
        'general': 'Use when working with this technology.',
    }
    return triggers.get(skill_type, triggers['general'])


def extract_section(content: str, header: str) -> Optional[str]:
    """Extract a section by header name."""
    pattern = rf'^## {header}\s*\n(.*?)(?=^## |\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else None


def extract_key_concepts(content: str) -> list[str]:
    """Extract key concepts as brief bullet points."""
    section = extract_section(content, 'Key Concepts')
    if not section:
        return []

    concepts = []
    for line in section.split('\n'):
        match = re.match(r'^- \*\*([^*]+)\*\*:', line)
        if match:
            concepts.append(match.group(1))

    return concepts[:3]  # Max 3 concepts


def extract_commands(content: str) -> Optional[str]:
    """Extract command section."""
    section = extract_section(content, 'Common Commands')
    if not section:
        return None

    # Find the code block
    match = re.search(r'```bash\n(.*?)```', section, re.DOTALL)
    if match:
        commands = match.group(1).strip()
        # Keep only essential commands (first 5-6 lines)
        lines = commands.split('\n')
        essential = []
        for line in lines[:6]:
            if line.strip():
                essential.append(line)
        return '\n'.join(essential)
    return None


def extract_one_pattern(content: str) -> Optional[str]:
    """Extract the first code pattern as a quick example."""
    section = extract_section(content, 'Code Patterns')
    if not section:
        return None

    # Find the first code block
    match = re.search(r'```(?:python|go|typescript|javascript)\n(.*?)```', section, re.DOTALL)
    if match:
        code = match.group(1).strip()
        # Truncate if too long (keep first ~15 lines)
        lines = code.split('\n')
        if len(lines) > 15:
            code = '\n'.join(lines[:15]) + '\n    # ... see docs/patterns.md for more'
        return code
    return None


def extract_code_language(content: str) -> str:
    """Detect the primary language of the skill."""
    if 'go.mod' in content or 'cmd/examples' in content:
        return 'go'
    if 'pyproject.toml' in content or 'PyJWT' in content or 'pytest' in content:
        return 'python'
    if 'package.json' in content or '.tsx' in content:
        return 'typescript'
    return 'bash'


def extract_common_mistakes(content: str) -> list[tuple[str, str]]:
    """Extract common mistakes as brief bullet points."""
    section = extract_section(content, 'Common Mistakes')
    if not section:
        return []

    mistakes = []
    current_mistake = None
    current_fix = None

    for line in section.split('\n'):
        # Match numbered mistake
        num_match = re.match(r'^\d+\.\s+\*\*([^*]+)\*\*', line)
        if num_match:
            if current_mistake and current_fix:
                mistakes.append((current_mistake, current_fix))
            current_mistake = num_match.group(1)
            current_fix = None
        # Match fix line
        fix_match = re.match(r'^\s+- (How to fix|Fix):\s*(.+)', line)
        if fix_match and current_mistake:
            current_fix = fix_match.group(2)

    # Add last one
    if current_mistake and current_fix:
        mistakes.append((current_mistake, current_fix))

    return mistakes[:3]  # Max 3 mistakes


def convert_claude_to_skill(claude_content: str, skill_name: str) -> str:
    """Convert CLAUDE.md content to SKILL.md format."""

    gerund_name = to_gerund_name(skill_name)
    description = extract_description(claude_content)
    key_concepts = extract_key_concepts(claude_content)
    commands = extract_commands(claude_content)
    pattern = extract_one_pattern(claude_content)
    language = extract_code_language(claude_content)
    mistakes = extract_common_mistakes(claude_content)

    # Build SKILL.md content
    lines = [
        '---',
        f'name: {gerund_name}',
        f'description: {description}',
        '---',
        '',
        f'# {skill_name.replace("-", " ").title()}',
        '',
    ]

    # Quick start with pattern
    if pattern:
        lines.extend([
            '## Quick Start',
            f'```{language}',
            pattern,
            '```',
            '',
        ])

    # Commands
    if commands:
        lines.extend([
            '## Commands',
            '```bash',
            commands,
            '```',
            '',
        ])

    # Key points
    if key_concepts:
        lines.append('## Key Points')
        for concept in key_concepts:
            lines.append(f'- {concept}')
        lines.append('')

    # Common mistakes
    if mistakes:
        lines.append('## Common Mistakes')
        for i, (mistake, fix) in enumerate(mistakes, 1):
            lines.append(f'{i}. **{mistake}** - {fix}')
        lines.append('')

    # Reference docs
    lines.extend([
        '## More Detail',
        '- [docs/concepts.md](docs/concepts.md) - Core concepts and theory',
        '- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples',
    ])

    return '\n'.join(lines)


def process_skill_directory(skill_path: Path, dry_run: bool = False) -> bool:
    """Process a single skill directory."""
    claude_md = skill_path / 'CLAUDE.md'
    skill_md = skill_path / 'SKILL.md'

    if not claude_md.exists():
        print(f"  Skipping {skill_path.name}: No CLAUDE.md found")
        return False

    # Read CLAUDE.md
    content = claude_md.read_text()
    skill_name = skill_path.name

    # Convert
    skill_content = convert_claude_to_skill(content, skill_name)

    if dry_run:
        print(f"\n{'='*60}")
        print(f"Would create: {skill_md}")
        print('='*60)
        print(skill_content)
        print('='*60)
        return True

    # Write SKILL.md
    skill_md.write_text(skill_content)
    print(f"  Created: {skill_md}")

    # Delete CLAUDE.md
    claude_md.unlink()
    print(f"  Deleted: {claude_md}")

    return True


def find_all_skills(base_path: Path) -> list[Path]:
    """Find all skill directories with CLAUDE.md files."""
    skills = []

    # Look in numbered category directories
    for category_dir in sorted(base_path.iterdir()):
        if not category_dir.is_dir():
            continue
        if not category_dir.name[0:2].isdigit():
            continue

        # Skills can be directly in category or nested by language
        for item in category_dir.rglob('CLAUDE.md'):
            skills.append(item.parent)

    return skills


def main():
    parser = argparse.ArgumentParser(description='Convert CLAUDE.md to SKILL.md format')
    parser.add_argument('path', nargs='?', help='Path to skill directory')
    parser.add_argument('--all', action='store_true', help='Convert all skills')
    parser.add_argument('--dry-run', action='store_true', help='Preview without writing')

    args = parser.parse_args()

    # Determine base path
    script_dir = Path(__file__).parent
    base_path = script_dir.parent.parent  # labs-skills/

    if args.all:
        skills = find_all_skills(base_path)
        print(f"Found {len(skills)} skills to convert")

        converted = 0
        for skill_path in skills:
            print(f"\nProcessing: {skill_path.relative_to(base_path)}")
            if process_skill_directory(skill_path, args.dry_run):
                converted += 1

        print(f"\n{'Would convert' if args.dry_run else 'Converted'}: {converted} skills")

    elif args.path:
        skill_path = Path(args.path).resolve()
        if not skill_path.exists():
            print(f"Error: Path does not exist: {skill_path}")
            sys.exit(1)
        process_skill_directory(skill_path, args.dry_run)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
