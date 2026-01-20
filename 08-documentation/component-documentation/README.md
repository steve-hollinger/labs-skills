# Component Documentation

Learn how to document software components effectively, including APIs, libraries, and modules. Master patterns for README files, API documentation, and inline code documentation that help users understand and use your code.

## Learning Objectives

After completing this skill, you will be able to:
- Write clear, comprehensive README files
- Document APIs with examples and error handling
- Create inline documentation that helps maintainers
- Apply documentation patterns for different component types
- Use automated tools to improve documentation quality

## Prerequisites

- Python 3.11+
- UV package manager
- Basic understanding of software components and APIs
- Familiarity with Markdown syntax

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

### What is Component Documentation?

Component documentation describes software modules, libraries, and services to help:
- **Users** understand how to use the component
- **Maintainers** understand how to modify it
- **Integrators** understand how to connect it with other systems

### The Documentation Pyramid

Documentation exists at multiple levels:

```
        /\
       /  \   API Reference (generated)
      /----\
     /      \  Tutorials & Guides
    /--------\
   /          \ README (entry point)
  /------------\
 / Inline Docs  \
/______________\_\
```

Each level serves different needs at different times in the user journey.

### README-Driven Development

Write the README first to:
- Clarify what you're building
- Design the user experience
- Identify gaps in your approach
- Create documentation naturally

## Examples

### Example 1: README Structure

Learn the essential sections every README should have.

```bash
make example-1
```

### Example 2: API Documentation

Document API endpoints, parameters, and responses effectively.

```bash
make example-2
```

### Example 3: Code Documentation

Write helpful docstrings, type hints, and inline comments.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Write a README for an existing code module
2. **Exercise 2**: Document an API with multiple endpoints
3. **Exercise 3**: Add documentation to undocumented code

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Documentation Without Examples
Always include working code examples. Show, don't just tell.

### Outdated Documentation
Documentation must be updated when code changes. Stale docs are worse than no docs.

### Assuming Too Much Knowledge
Write for someone who doesn't know your codebase. Explain context.

### Skipping Error Cases
Document what happens when things go wrong, not just the happy path.

## Further Reading

- [Write the Docs](https://www.writethedocs.org/)
- Related skills in this repository:
  - [CLAUDE.md Standards](../claude-md-standards/)
  - [System Prompts](../system-prompts/)
