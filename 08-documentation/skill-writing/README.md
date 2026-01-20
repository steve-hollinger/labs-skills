# Skill Writing

Learn to create effective Agent Skills following Anthropic's official format.

## Overview

This skill teaches the structure and best practices for writing SKILL.md files that Claude can discover and use effectively.

## Structure

```
skill-writing/
├── SKILL.md           # Quick reference for writing skills
├── README.md          # This file
└── docs/
    ├── concepts.md    # Anthropic's official guidelines
    └── patterns.md    # Templates and examples
```

## Key Concepts

### YAML Frontmatter
- `name`: Gerund form (verb-ing), lowercase with hyphens, max 64 chars
- `description`: Starts with "This skill teaches...", includes "Use when...", max 1024 chars

### Body Structure
- Quick Start: Concise code example (5-10 lines)
- Key Points: 3-4 short phrases (2-3 words each)
- Common Mistakes: Critical errors only
- More Detail: Links to docs/

### Progressive Disclosure
1. Metadata (name + description) - Always loaded (~100 tokens)
2. SKILL.md body - When skill triggers (<500 lines)
3. Bundled resources - As needed by Claude

## Resources

- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
