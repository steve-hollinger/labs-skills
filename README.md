# Labs Skills

A collection of **69 Agent Skills** for modern software development, following [Anthropic's Agent Skills format](https://docs.anthropic.com/en/docs/claude-code/skills).

## Categories

| ID | Category | Skills | Focus Area |
|----|----------|--------|------------|
| 01 | language-frameworks | 16 | Python, Go, Frontend |
| 02 | architecture-design | 7 | Design patterns and architecture |
| 03 | testing | 7 | Testing frameworks and strategies |
| 04 | devops-deployment | 6 | Docker, CI/CD, FSD |
| 05 | data-databases | 8 | Storage, streaming, caching |
| 06 | ai-ml | 5 | LLM integration, search, evaluation |
| 07 | security | 5 | Auth, secrets, validation |
| 08 | documentation | 4 | Standards and practices |
| 09 | code-quality | 6 | Linting, typing, commits |
| 10 | mobile-dev | 8 | iOS/Swift, SwiftUI |

## Skill Structure

Each skill follows the minimal Agent Skills layout:

```
skill-name/
├── SKILL.md            # YAML frontmatter + guidance
└── docs/
    ├── concepts.md     # Core concepts
    └── patterns.md     # Code patterns
```

## Using with Claude Code

### Option 1: Clone as Project Skills

```bash
git clone https://github.com/steve-hollinger/labs-skills.git
cd labs-skills
claude  # Skills are discovered from nested directories
```

### Option 2: Copy Skills Manually

```bash
# Copy specific skills to your global skills directory
cp -r 01-language-frameworks/python/fastapi-basics ~/.claude/skills/

# Or to a project's local skills
cp -r 07-security/jwt-validation ./your-project/.claude/skills/
```

### Option 3: Symlink for Development

```bash
# Symlink entire categories
ln -s /path/to/labs-skills/01-language-frameworks ~/.claude/skills/language-frameworks
```

## SKILL.md Format

Skills use YAML frontmatter with a gerund-form name and trigger description:

```yaml
---
name: building-fastapi-services
description: Build REST APIs with FastAPI. Use when creating Python web services.
---

# FastAPI Basics

## Quick Start
(concise example code)

## Key Points
- Point 1
- Point 2

## Common Mistakes
1. **Mistake name** - Brief explanation

## More Detail
- [docs/concepts.md](docs/concepts.md)
- [docs/patterns.md](docs/patterns.md)
```

## License

MIT
