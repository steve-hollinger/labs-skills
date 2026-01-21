# CLAUDE.md - AI Assistant Guidance

This repository contains Agent Skills for modern software development. Each skill follows [Anthropic's Agent Skills format](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) with a `SKILL.md` file that enables AI assistants to apply the skill effectively.

Skills use the official Anthropic Agent Skills format with `SKILL.md` files containing YAML frontmatter for name and description.

## Repository Purpose

Labs-skills is a collection of Agent Skills organized by category. AI assistants load these skills on-demand to gain domain-specific expertise.

## Skill Structure

All skills follow the minimal Agent Skills layout:
```
skill-name/
├── SKILL.md            # Agent skill definition (YAML frontmatter + guidance)
└── docs/
    ├── concepts.md     # Core concepts (loaded when referenced)
    └── patterns.md     # Code patterns (loaded when referenced)
```

## Category Overview

| ID | Category | Skills | Focus Area |
|----|----------|--------|------------|
| 01 | language-frameworks | 14 | Python, Go, Frontend core skills |
| 02 | architecture-design | 7 | Design patterns and architecture |
| 03 | testing | 7 | Testing frameworks and strategies |
| 04 | devops-deployment | 6 | Docker, CI/CD, FSD |
| 05 | data-databases | 7 | Storage, streaming, caching |
| 06 | ai-ml | 5 | LLM integration, search, evaluation |
| 07 | security | 5 | Auth, secrets, validation |
| 08 | documentation | 4 | Standards and practices |
| 09 | code-quality | 4 | Linting, typing, commits |
| 10 | mobile-dev | 8 | iOS/Swift, SwiftUI, concurrency |

## Working With Skills

### When a skill is triggered:
1. Read the skill's SKILL.md for specific guidance
2. Follow the Quick Start code patterns
3. Reference docs/concepts.md and docs/patterns.md for details
4. Note Common Mistakes to avoid pitfalls

### When creating or modifying skills:
1. Use templates from `shared/templates/`
2. Follow the SKILL.md format exactly
3. Keep SKILL.md concise (under 5k tokens)
4. Put detailed patterns in docs/patterns.md

## SKILL.md Format

Skills use Anthropic's official Agent Skills format:

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

**Format rules:**
- `name`: gerund form (verb-ing), lowercase with hyphens
- `description`: includes "Use when..." trigger phrase
- `More Detail`: links to docs/ files that Claude loads when needed

## Important Notes

- Each skill directory has its own SKILL.md with specific guidance
- Always read the skill's SKILL.md before helping with that skill
- SKILL.md files use YAML frontmatter with `name` (gerund form) and `description` (with "Use when..." trigger)
- docs/concepts.md and docs/patterns.md are loaded only when referenced
