# Contributing to Labs Skills

Thank you for your interest in contributing! This guide explains how to add new skills or improve existing ones.

## Quick Start: Use the Skill-Writing Skill

The easiest way to create a new skill is to use our **skill-writing skill**:

```
08-documentation/skill-writing/
├── SKILL.md           # Guidelines and quick reference
└── docs/
    ├── concepts.md    # Anthropic's official guidelines
    └── patterns.md    # Templates and examples
```

This skill contains Anthropic's official best practices for writing Agent Skills.

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

### 3. SKILL.md Format

````yaml
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
- docs/concepts.md - Core concepts
- docs/patterns.md - Code patterns
````

**Format rules:**
- `name`: gerund form (verb-ing), lowercase with hyphens
- `description`: includes "Use when..." trigger phrase
- Quick Start: minimal, working code example
- Key Points: 3-5 bullet points max
- Common Mistakes: 2-3 most frequent issues

### 4. docs/concepts.md

Explain core concepts in depth. Include these sections:

- **What is [Technology]?** - Brief description, what problem it solves
- **Key Terminology** - Define important terms
- **How It Works** - Mental model for understanding
- **When to Use** - Good use cases and when to avoid

### 5. docs/patterns.md

Provide reusable code patterns. For each pattern include:

- **Pattern Name** - Descriptive title
- **When to Use** - Scenario description
- **Implementation** - Complete, working code example
- **Pitfalls** - Common mistakes to avoid

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
