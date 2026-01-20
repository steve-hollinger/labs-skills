# System Prompts

Learn prompt engineering for system prompts that guide AI behavior effectively. Master the art of crafting clear, well-structured prompts that produce consistent, high-quality AI responses.

## Learning Objectives

After completing this skill, you will be able to:
- Understand the four key components of effective system prompts
- Write system prompts for different use cases (coding, writing, analysis)
- Apply prompt engineering best practices
- Debug and improve underperforming prompts
- Create reusable prompt templates

## Prerequisites

- Python 3.11+
- UV package manager
- Basic understanding of large language models (LLMs)
- Familiarity with the CLAUDE.md Standards skill (recommended)

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

### The Four Components of System Prompts

Every effective system prompt contains four key components:

1. **Role**: Who is the AI? What expertise does it have?
2. **Context**: What situation is the AI operating in?
3. **Instructions**: What should the AI do?
4. **Constraints**: What should the AI avoid or limit?

```
ROLE:       You are an expert Python developer...
CONTEXT:    You are reviewing code for a fintech startup...
INSTRUCTIONS: Analyze the code for security issues...
CONSTRAINTS: Never suggest changes that break existing tests...
```

### Why System Prompts Matter

System prompts:
- Set consistent behavior across conversations
- Define expertise and personality
- Establish boundaries and safety guardrails
- Improve response quality and relevance

### Prompt Engineering vs. Prompt Writing

Prompt engineering is iterative and data-driven:
1. Write initial prompt
2. Test with varied inputs
3. Analyze failure cases
4. Refine and repeat

## Examples

### Example 1: Anatomy of a System Prompt

Dissect a well-structured system prompt to understand each component.

```bash
make example-1
```

### Example 2: Prompts for Different Use Cases

See how prompt structure changes for coding, writing, and analysis tasks.

```bash
make example-2
```

### Example 3: Prompt Debugging and Improvement

Learn techniques for diagnosing and fixing underperforming prompts.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Write a system prompt for a code reviewer
2. **Exercise 2**: Convert vague instructions to precise prompts
3. **Exercise 3**: Create a prompt template system

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Vague Role Definition
Don't: "You are helpful."
Do: "You are a senior backend engineer specializing in Python and PostgreSQL."

### Missing Constraints
Don't: Assume the AI knows what to avoid
Do: Explicitly list what not to do

### Overloading with Instructions
Don't: Include every possible scenario
Do: Focus on the primary use case with clear priorities

### Ignoring Edge Cases
Don't: Only test with ideal inputs
Do: Test with edge cases, errors, and adversarial inputs

## Further Reading

- [Official Documentation](https://docs.anthropic.com/claude/docs/system-prompts)
- Related skills in this repository:
  - [CLAUDE.md Standards](../claude-md-standards/)
  - [Component Documentation](../component-documentation/)
