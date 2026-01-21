# CLAUDE.md - Repository Guidance

This repository contains 68 Agent Skills for Claude Code, organized by category.

## Repository Structure

```
labs-skills/
├── 01-language-frameworks/   # Python, Go, Frontend
├── 02-architecture-design/   # Design patterns
├── 03-testing/               # Testing strategies
├── 04-devops-deployment/     # Docker, CI/CD, FSD
├── 05-data-databases/        # Storage, streaming
├── 06-ai-ml/                 # LLM integration
├── 07-security/              # Auth, secrets
├── 08-documentation/         # Standards
├── 09-code-quality/          # Linting, typing
├── 10-mobile-dev/            # iOS/Swift
└── shared/templates/         # Skill templates
```

## Skill Structure

Each skill follows the minimal Agent Skills format:

```
skill-name/
├── SKILL.md            # YAML frontmatter + guidance
└── docs/
    ├── concepts.md     # Core concepts
    └── patterns.md     # Code patterns
```

## When Adding a New Skill

1. Create the skill directory with SKILL.md and docs/
2. Follow the format in `08-documentation/skill-writing/`
3. **Update the Skill Index in README.md**
4. Update CONTRIBUTING.md if process changes

## Key Files

- `README.md` - Overview and **Skill Index**
- `CONTRIBUTING.md` - How to add/modify skills
- `08-documentation/skill-writing/` - Skill creation guide

## Common Tasks

### Find a skill by topic
```bash
grep -r "description:" --include="SKILL.md" | grep -i "kafka"
```

### List all skills
```bash
find . -name "SKILL.md" -not -path "./shared/*" | wc -l
```

### Validate SKILL.md format
- Has YAML frontmatter with `name` and `description`
- `name` is gerund form (verb-ing)
- `description` includes "Use when..."
