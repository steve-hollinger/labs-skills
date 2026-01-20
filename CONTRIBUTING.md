# Contributing to Labs Skills

Thank you for your interest in contributing! This guide explains how to add new skills or improve existing ones.

## Adding a New Skill

### 1. Choose the Right Category

| Category | When to Use |
|----------|-------------|
| 01-language-frameworks | Language-specific libraries and frameworks |
| 02-architecture-design | Design patterns and architectural decisions |
| 03-testing | Testing tools and strategies |
| 04-devops-deployment | Infrastructure and deployment |
| 05-data-databases | Data storage, streaming, caching |
| 06-ai-ml | AI/ML, LLM integration |
| 07-security | Security practices |
| 08-documentation | Documentation standards |
| 09-code-quality | Linting, typing, code standards |
| 10-mobile-dev | iOS/Swift, mobile development |

### 2. Create the Skill Structure

```
skill-name/
├── SKILL.md            # Required - YAML frontmatter + guidance
└── docs/
    ├── concepts.md     # Required - Core concepts
    └── patterns.md     # Required - Code patterns
```

That's it. No Makefile, no src/, no tests/, no exercises/.

### 3. SKILL.md Format

```yaml
---
name: building-something-cool
description: Build something cool with X. Use when Y.
---

# Skill Title

## Quick Start
```language
// Minimal working example (10-20 lines)
```

## Key Points
- Most important concept
- Second most important
- Third most important

## Common Mistakes
1. **Mistake name** - How to avoid it
2. **Another mistake** - How to avoid it

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts
- [docs/patterns.md](docs/patterns.md) - Code patterns
```

**Format rules:**
- `name`: gerund form (verb-ing), lowercase with hyphens
- `description`: includes "Use when..." trigger phrase
- Quick Start: minimal, working code example
- Key Points: 3-5 bullet points max
- Common Mistakes: 2-3 most frequent issues

### 4. docs/concepts.md

Explain the core concepts in depth:
- What the technology is and why it exists
- Key terminology
- How it works conceptually
- When to use it vs alternatives

### 5. docs/patterns.md

Provide reusable code patterns:
- Common implementation patterns
- Best practices with code examples
- Integration patterns
- Error handling patterns

## Improving Existing Skills

### Fixing Issues
1. Edit the relevant file (SKILL.md, concepts.md, or patterns.md)
2. Keep changes focused and minimal
3. Verify markdown renders correctly

### Adding Content
- Add concepts to docs/concepts.md
- Add patterns to docs/patterns.md
- Keep SKILL.md concise (under 100 lines)

## Pull Request Checklist

Before submitting:

- [ ] SKILL.md has valid YAML frontmatter
- [ ] `name` is gerund form (e.g., `building-apis`)
- [ ] `description` includes "Use when..." trigger
- [ ] Quick Start has working code example
- [ ] docs/concepts.md exists and is complete
- [ ] docs/patterns.md exists and is complete
- [ ] No extra files (no Makefile, src/, tests/, etc.)

## Questions?

Open an issue for:
- Clarification on where a skill belongs
- Feedback on skill design
- Suggestions for new skills
