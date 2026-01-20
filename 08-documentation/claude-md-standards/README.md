# CLAUDE.md Standards

Learn how to write effective CLAUDE.md files that provide AI assistants with the context and guidance they need to work effectively in your codebase.

## Learning Objectives

After completing this skill, you will be able to:
- Understand the purpose and structure of CLAUDE.md files
- Write clear, actionable AI guidance for different project types
- Distinguish between good and bad AI documentation practices
- Create CLAUDE.md templates for various project architectures

## Prerequisites

- Python 3.11+
- UV package manager
- Basic understanding of Markdown syntax
- Familiarity with software project structures

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Concepts

### What is CLAUDE.md?

CLAUDE.md is a special file that provides context and guidance to AI assistants working with your codebase. It acts as a "briefing document" that helps AI understand:
- What the project does and why it exists
- Key architectural decisions and patterns
- Common commands and workflows
- Important conventions and constraints

### Why CLAUDE.md Matters

Without proper context, AI assistants may:
- Suggest patterns that don't fit your architecture
- Miss important conventions in your codebase
- Struggle with project-specific terminology
- Make assumptions that don't apply to your situation

A well-written CLAUDE.md eliminates these issues by providing explicit guidance.

### The Hierarchy of CLAUDE.md Files

CLAUDE.md files can exist at multiple levels:
- **Repository root**: General guidance for the entire project
- **Subdirectories**: Specific guidance for modules, services, or packages
- **Nested contexts**: More specific files override more general ones

## Examples

### Example 1: Basic CLAUDE.md Structure

Learn the essential components every CLAUDE.md should have.

```bash
make example-1
```

### Example 2: Good vs Bad Guidance

Compare effective AI guidance with common anti-patterns.

```bash
make example-2
```

### Example 3: Project-Type Templates

Generate CLAUDE.md templates for different project types (web app, CLI tool, library).

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Write a CLAUDE.md for a simple Flask API
2. **Exercise 2**: Improve a poorly-written CLAUDE.md
3. **Exercise 3**: Create a CLAUDE.md hierarchy for a monorepo

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Too Vague
Don't write "Follow best practices." Instead, specify which practices and why.

### Too Verbose
A CLAUDE.md that's too long won't be fully absorbed. Keep it focused and scannable.

### Outdated Information
CLAUDE.md files must be maintained. Outdated guidance is worse than no guidance.

### Missing "Why"
Don't just list rules. Explain the reasoning so AI can make informed decisions.

## Further Reading

- [Official Documentation](https://docs.anthropic.com)
- Related skills in this repository:
  - [System Prompts](../system-prompts/)
  - [Component Documentation](../component-documentation/)
