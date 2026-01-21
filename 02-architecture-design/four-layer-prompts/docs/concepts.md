# Four-Layer Prompt Architecture Concepts

## Overview

The Four-Layer Prompt Architecture is a design pattern for structuring prompts that provides clear separation of concerns, making prompts more maintainable, testable, and reusable. This approach treats prompts as composable components rather than monolithic text blocks.

## The Four Layers

### Layer 1: System Layer

The System Layer establishes the AI's fundamental identity, capabilities, and behavioral parameters. It answers the question: "Who is this AI?"

**Purpose:**
- Define the AI's role and expertise
- Set personality and communication style
- Establish global behavioral boundaries
- Specify knowledge domains

**Characteristics:**
- Relatively static across conversations
- Concise but comprehensive (50-200 tokens)
- Defines capabilities without specific tasks
- Sets the tone for all interactions

**Example:**
```python
system_layer = """
You are an expert software architect with 15 years of experience.
You specialize in distributed systems, microservices, and cloud architecture.
You communicate technical concepts clearly and provide practical, actionable advice.
You always consider scalability, maintainability, and security in your recommendations.
"""
```

### Layer 2: Context Layer

The Context Layer provides the situational information, data, and background needed to understand and complete the task. It answers: "What do I need to know?"

**Purpose:**
- Supply relevant data and documents
- Provide environmental information
- Share conversation history or user preferences
- Include domain-specific knowledge

**Characteristics:**
- Dynamic and situation-specific
- Can be quite long (variable tokens)
- Contains the "raw material" for the task
- May include structured data (JSON, tables)

**Example:**
```python
context_layer = """
Project Context:
- Application: E-commerce platform
- Current architecture: Monolithic Django application
- Traffic: 10,000 requests/minute peak
- Pain points: Slow deployments, scaling issues

Technical Stack:
- Python 3.11, Django 4.2
- PostgreSQL 15
- Redis for caching
- AWS infrastructure

Recent Issues:
1. Black Friday outage due to database connection limits
2. 45-minute deployment windows causing customer impact
3. Unable to scale checkout independently from catalog
"""
```

### Layer 3: Instruction Layer

The Instruction Layer contains the specific task, action, or question. It answers: "What should I do?"

**Purpose:**
- Define the exact task to perform
- Specify desired outcomes
- Outline steps if needed
- Set task-specific parameters

**Characteristics:**
- Clear and unambiguous
- Task-focused without format details
- Moderate length (50-150 tokens)
- Action-oriented language

**Example:**
```python
instruction_layer = """
Analyze the current architecture and propose a migration strategy to microservices.
Your analysis should:
1. Identify service boundaries based on business domains
2. Prioritize which services to extract first
3. Recommend a phased migration approach
4. Address the specific pain points mentioned
5. Estimate high-level effort for each phase
"""
```

### Layer 4: Constraint Layer

The Constraint Layer specifies output requirements, limitations, and guardrails. It answers: "How should I present this?"

**Purpose:**
- Define output format
- Set length and scope limits
- Specify what to include/exclude
- Establish quality requirements

**Characteristics:**
- Focused on output, not process
- Clear, measurable requirements
- Enforces consistency
- Concise (30-100 tokens)

**Example:**
```python
constraint_layer = """
Output Requirements:
- Format as a structured proposal with clear sections
- Include a visual diagram description for architecture
- Limit total response to 1000 words
- Use bullet points for recommendations
- Do not include specific code implementations
- Provide rough effort estimates in person-weeks
"""
```

## Layer Interactions

### Sequential Processing

The layers work together in a sequential, building manner:

```
System (Identity) -> Context (Knowledge) -> Instruction (Task) -> Constraint (Output)
```

Each layer builds on the previous, creating a coherent prompt:
1. System establishes "who" is responding
2. Context provides "what" they need to know
3. Instruction specifies "what to do"
4. Constraint defines "how to present"

### Layer Override Pattern

Later layers can refine or override earlier layer implications:

```python
# System implies detailed technical responses
system = "You are a senior software engineer with deep expertise..."

# Context suggests user needs
context = "The user is a junior developer learning Python..."

# Constraint overrides default complexity
constraint = "Explain in simple terms, avoiding jargon. Use analogies."
```

### Conditional Layer Inclusion

Not all prompts need all layers at full detail:

```python
def build_prompt(task_type: str) -> str:
    layers = [base_system]

    if task_type == "analysis":
        layers.append(detailed_context)
        layers.append(analysis_instruction)
        layers.append(analysis_constraints)
    elif task_type == "quick_question":
        # Minimal context for quick responses
        layers.append(quick_instruction)
        layers.append(brief_constraints)

    return compose_layers(layers)
```

## Design Principles

### 1. Single Responsibility

Each layer should have one clear purpose:
- Don't mix identity with instructions
- Don't embed format requirements in context
- Keep task definitions separate from output format

### 2. Explicit Over Implicit

Make expectations explicit:

```python
# Implicit (bad)
instruction = "Write about the product."

# Explicit (good)
instruction = """
Write a product description that:
1. Highlights the top 3 features
2. Addresses the target customer's pain points
3. Includes a call-to-action
"""
```

### 3. Composability

Design layers to be mixed and matched:

```python
# Reusable system layers
TECHNICAL_WRITER_SYSTEM = "..."
CODE_REVIEWER_SYSTEM = "..."

# Reusable constraint layers
MARKDOWN_OUTPUT = "Format output as markdown..."
JSON_OUTPUT = "Return valid JSON..."

# Compose as needed
prompt = compose(
    TECHNICAL_WRITER_SYSTEM,
    api_context,
    documentation_instruction,
    MARKDOWN_OUTPUT
)
```

### 4. Testability

Each layer should be independently testable:

```python
def test_system_layer_contains_role():
    assert "technical writer" in SYSTEM_LAYER.lower()

def test_constraint_specifies_format():
    assert "markdown" in CONSTRAINT_LAYER.lower() or "json" in CONSTRAINT_LAYER.lower()
```

## Anti-Patterns

### Monolithic Prompts

```python
# Bad: Everything mixed together
prompt = """
You are an expert. Here is some data: {data}.
Write a report. Use markdown. Keep it brief.
"""

# Good: Separated layers
prompt = compose(system, context.format(data=data), instruction, constraint)
```

### Implicit Context

```python
# Bad: Assumes context
instruction = "Fix the bug."

# Good: Explicit context
context = "The following code has a null pointer exception on line 15: {code}"
instruction = "Identify the root cause and provide a fix."
```

### Contradictory Layers

```python
# Bad: Layers contradict
system = "You are verbose and thorough."
constraint = "Keep response under 50 words."

# Good: Consistent layers
system = "You are concise and precise."
constraint = "Keep response under 50 words."
```

## Migration Strategy

### From Monolithic Prompts

1. **Identify the identity**: Extract system layer elements
2. **Separate data**: Pull out context information
3. **Isolate the task**: Define clear instruction
4. **Extract format**: Create constraint layer
5. **Test and iterate**: Validate each layer independently

### Example Migration

Before:
```python
prompt = f"""
You're a helpful assistant. The user asked: {question}
Answer helpfully and concisely. Use markdown.
Here's some relevant info: {context}
"""
```

After:
```python
system = "You are a knowledgeable, helpful assistant."
context = f"Relevant information:\n{context}"
instruction = f"Answer the following question: {question}"
constraint = "Respond concisely using markdown formatting."

prompt = compose(system, context, instruction, constraint)
```
