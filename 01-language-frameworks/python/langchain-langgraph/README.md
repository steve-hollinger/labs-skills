# LangChain & LangGraph

Master LLM orchestration with LangChain and LangGraph - the leading frameworks for building sophisticated AI applications with chains, agents, tools, and graph-based workflows.

## Learning Objectives

After completing this skill, you will be able to:
- Build LLM chains for sequential processing
- Create agents that use tools to accomplish tasks
- Design graph-based workflows with LangGraph
- Implement state management and memory persistence
- Handle streaming responses and callbacks
- Debug and trace LLM applications

## Prerequisites

- Python 3.11+
- UV package manager
- Basic understanding of LLMs and prompt engineering
- OpenAI API key (or other LLM provider)
- [Pydantic v2](../pydantic-v2/) skill recommended

## Quick Start

```bash
# Install dependencies
make setup

# Set your API key
export OPENAI_API_KEY=your-key-here

# Run examples
make examples

# Run tests
make test
```

## Concepts

### Chains

Chains are sequences of calls to LLMs or other components. They process input through multiple steps.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Create a simple chain using LCEL (LangChain Expression Language)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{input}")
])

model = ChatOpenAI(model="gpt-4o-mini")
output_parser = StrOutputParser()

chain = prompt | model | output_parser
response = chain.invoke({"input": "What is LangChain?"})
```

### Agents and Tools

Agents use LLMs to decide which actions to take. Tools are functions the agent can call.

```python
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

@tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression."""
    return str(eval(expression))

model = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(model, [calculate])

result = agent.invoke({"messages": [("user", "What is 25 * 4?")]})
```

### LangGraph Workflows

LangGraph enables building stateful, multi-step applications as graphs.

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    messages: list
    next_step: str

def process_input(state: State) -> State:
    # Process and return updated state
    return {"messages": state["messages"] + ["processed"], "next_step": "analyze"}

def analyze(state: State) -> State:
    return {"messages": state["messages"] + ["analyzed"], "next_step": "end"}

# Build the graph
workflow = StateGraph(State)
workflow.add_node("process", process_input)
workflow.add_node("analyze", analyze)
workflow.add_edge(START, "process")
workflow.add_edge("process", "analyze")
workflow.add_edge("analyze", END)

app = workflow.compile()
result = app.invoke({"messages": [], "next_step": "start"})
```

### Memory and Persistence

Maintain conversation history and state across interactions.

```python
from langgraph.checkpoint.memory import MemorySaver

# Add checkpointing for persistence
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Thread-based conversations
config = {"configurable": {"thread_id": "user-123"}}
result = app.invoke({"messages": ["Hello"]}, config)
```

## Examples

### Example 1: Simple Chain

Build a basic chain that processes user input through a prompt template and model.

```bash
make example-1
```

### Example 2: Tool-Using Agent

Create an agent with custom tools for web search and calculation.

```bash
make example-2
```

### Example 3: LangGraph Workflow

Build a multi-step workflow with conditional routing and state management.

```bash
make example-3
```

### Example 4: Conversational Agent with Memory

Implement a chatbot with persistent memory across sessions.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Build a Chain - Create a summarization chain that processes long text
2. **Exercise 2**: Custom Tool Agent - Build an agent with tools for a specific domain
3. **Exercise 3**: Workflow Graph - Design a document processing pipeline with LangGraph

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Architecture Patterns

### LCEL (LangChain Expression Language)

The modern way to compose LangChain components:

```python
# Pipe operator (|) for composition
chain = prompt | model | output_parser

# Parallel execution with RunnableParallel
from langchain_core.runnables import RunnableParallel
parallel = RunnableParallel(
    summary=summarize_chain,
    translation=translate_chain
)
```

### Graph-Based Workflows

Use LangGraph for complex, stateful applications:

```python
# Conditional routing
def should_continue(state):
    return "continue" if state["attempts"] < 3 else "end"

workflow.add_conditional_edges("check", should_continue, {
    "continue": "retry",
    "end": END
})
```

## Common Mistakes

### Using Deprecated APIs

LangChain evolves quickly. Use the modern imports:

```python
# Old (deprecated)
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent

# New (current)
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
```

### Not Handling Streaming

For better UX, stream responses:

```python
# Wrong - blocks until complete
response = chain.invoke({"input": "..."})

# Better - stream tokens
async for chunk in chain.astream({"input": "..."}):
    print(chunk, end="", flush=True)
```

### Ignoring State Management

Always use TypedDict for LangGraph state:

```python
# Wrong - untyped state leads to bugs
def node(state):
    return {"unknown_field": "value"}

# Correct - typed state catches errors
class State(TypedDict):
    messages: list
    context: str

def node(state: State) -> State:
    return {"messages": state["messages"] + ["new"]}
```

## Further Reading

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangSmith for Tracing](https://smith.langchain.com/)
- Related skills in this repository:
  - [Pydantic v2](../pydantic-v2/) - Data validation for structured outputs
  - [OpenAI Responses API](../../../06-ai-ml/openai-responses-api/) - Direct OpenAI integration
  - [SSE Streaming](../../../06-ai-ml/sse-streaming/) - Streaming responses to clients
