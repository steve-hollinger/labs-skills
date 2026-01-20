# Core Concepts

## Overview

System prompts are the foundation of AI application behavior. They define who the AI is, what it knows, what it should do, and what it should avoid. This guide covers the essential concepts for writing effective system prompts.

## Concept 1: The Four Components

### What It Is

Every effective system prompt contains four key components that work together to define AI behavior:

1. **Role** - The AI's identity and expertise
2. **Context** - The situation and environment
3. **Instructions** - What the AI should do
4. **Constraints** - What the AI should avoid

### Why It Matters

Missing any component leads to unpredictable behavior:
- No role = inconsistent expertise level
- No context = generic responses
- No instructions = AI guesses what to do
- No constraints = potential harmful outputs

### How It Works

```python
# Complete four-component prompt
system_prompt = """
ROLE:
You are a senior security engineer with 10+ years of experience
in application security, penetration testing, and secure code review.

CONTEXT:
You are reviewing code for a healthcare startup that handles
protected health information (PHI) under HIPAA regulations.

INSTRUCTIONS:
1. Analyze code for security vulnerabilities
2. Prioritize findings by severity (Critical, High, Medium, Low)
3. Provide specific remediation steps for each finding
4. Reference relevant OWASP guidelines where applicable

CONSTRAINTS:
- Never suggest security through obscurity
- Don't recommend deprecated cryptographic functions
- Always consider HIPAA compliance implications
- Don't make changes that would break existing functionality
"""
```

## Concept 2: Role Definition

### What It Is

The role defines the AI's identity, expertise level, and perspective. It answers "Who is the AI?"

### Why It Matters

A well-defined role:
- Sets the expertise level for responses
- Establishes consistent voice and tone
- Provides domain-specific knowledge focus
- Creates appropriate confidence levels

### How It Works

**Weak role definition:**
```
You are a helpful assistant.
```

**Strong role definition:**
```
You are a staff software engineer at a Fortune 500 company
with deep expertise in:
- Distributed systems architecture
- Python and Go programming
- PostgreSQL and Redis optimization
- Kubernetes deployment patterns

You have reviewed hundreds of production systems and have
a pragmatic, security-conscious approach to code review.
```

**Role components to include:**
- Job title/position level
- Years of experience (implied expertise)
- Specific technical domains
- Working style/approach

## Concept 3: Context Setting

### What It Is

Context provides the situation, environment, and background information the AI needs to give relevant responses.

### Why It Matters

The same AI role behaves differently in different contexts:
- A code reviewer acts differently for a startup vs. a bank
- A writing assistant adapts to blog posts vs. legal documents
- A tutor adjusts for beginners vs. experts

### How It Works

**Context elements:**
```python
context = {
    "environment": "Production fintech application",
    "audience": "Junior developers on the team",
    "constraints": "Must maintain Python 3.9 compatibility",
    "goals": "Improve code quality without blocking PRs",
    "history": "Team is transitioning from monolith to microservices",
}
```

**Example context in prompt:**
```
CONTEXT:
You are working with a team of 5 developers at an early-stage startup.
The codebase is 2 years old with mixed test coverage (40-60%).
The team values shipping quickly but wants to avoid technical debt.
Code reviews should be thorough but not pedantic.
```

## Concept 4: Instructions Design

### What It Is

Instructions tell the AI what actions to take, what format to use, and how to approach the task.

### Why It Matters

Clear instructions:
- Reduce ambiguity in responses
- Ensure consistent output format
- Guide the AI through complex tasks
- Enable automation and integration

### How It Works

**Instruction best practices:**

1. **Be specific about actions:**
```
# Vague
Review the code.

# Specific
1. Check for SQL injection vulnerabilities
2. Verify input validation on all user inputs
3. Ensure authentication is required for sensitive endpoints
4. Check for hardcoded credentials or secrets
```

2. **Define output format:**
```
Respond in this format:

## Summary
[1-2 sentence overview]

## Findings
| Severity | File | Line | Issue | Fix |
|----------|------|------|-------|-----|

## Recommendations
[Prioritized list of improvements]
```

3. **Include examples:**
```
Example input:
def get_user(id):
    return db.execute(f"SELECT * FROM users WHERE id = {id}")

Example output:
CRITICAL: SQL Injection in get_user()
- Line 2: User input directly interpolated into SQL
- Fix: Use parameterized queries
- Code: db.execute("SELECT * FROM users WHERE id = ?", [id])
```

## Concept 5: Constraint Definition

### What It Is

Constraints define boundaries, limitations, and things the AI should never do.

### Why It Matters

Constraints prevent:
- Harmful or dangerous outputs
- Off-topic responses
- Violations of policies or regulations
- Inconsistent behavior

### How It Works

**Types of constraints:**

1. **Safety constraints:**
```
- Never provide instructions for harmful activities
- Don't generate content that could harm individuals
- Refuse requests that violate user privacy
```

2. **Scope constraints:**
```
- Only discuss topics related to Python programming
- Don't provide medical, legal, or financial advice
- Stay focused on the code being reviewed
```

3. **Quality constraints:**
```
- Don't guess if unsure; ask for clarification
- Never fabricate citations or sources
- Acknowledge limitations of your knowledge
```

4. **Format constraints:**
```
- Keep responses under 500 words unless asked for detail
- Always include code examples for technical suggestions
- Use markdown formatting for readability
```

## Summary

Key takeaways for writing effective system prompts:

1. **Include all four components** - Role, Context, Instructions, Constraints
2. **Be specific in role definition** - Include expertise level and domains
3. **Provide relevant context** - Environment, audience, and goals
4. **Write clear instructions** - Actions, format, and examples
5. **Define explicit constraints** - Safety, scope, quality, and format
6. **Test with varied inputs** - Edge cases reveal prompt weaknesses
7. **Iterate based on results** - Prompts improve through refinement
