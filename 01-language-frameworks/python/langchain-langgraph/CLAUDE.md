# CLAUDE.md - LangChain & LangGraph

This skill teaches LLM orchestration using LangChain and LangGraph - frameworks for building chains, agents, and graph-based AI workflows.

## Key Concepts

- **LCEL (LangChain Expression Language)**: Modern composition syntax using pipe operator (`|`)
- **Chains**: Sequential processing pipelines (prompt -> model -> parser)
- **Agents**: LLM-powered decision makers that use tools
- **Tools**: Functions that agents can call to interact with external systems
- **LangGraph**: Graph-based framework for stateful, multi-step workflows
- **State**: TypedDict defining the data flowing through a graph
- **Checkpointing**: Persistence mechanism for conversation memory

## Common Commands

```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run simple chain example
make example-2  # Run tool-using agent example
make example-3  # Run LangGraph workflow example
make example-4  # Run conversational agent example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
langchain-langgraph/
├── src/langchain_langgraph/
│   ├── __init__.py
│   └── examples/
│       ├── example_1_simple_chain.py
│       ├── example_2_tool_agent.py
│       ├── example_3_langgraph_workflow.py
│       └── example_4_memory_agent.py
├── exercises/
│   ├── exercise_1_summarization_chain.py
│   ├── exercise_2_custom_tool_agent.py
│   ├── exercise_3_document_pipeline.py
│   └── solutions/
├── tests/
│   ├── test_examples.py
│   └── conftest.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: LCEL Chain
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role}."),
    ("user", "{input}")
])
model = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

chain = prompt | model | parser
result = chain.invoke({"role": "assistant", "input": "Hello"})
```

### Pattern 2: Tool Definition
```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(description="Search query")
    limit: int = Field(default=5, description="Max results")

@tool(args_schema=SearchInput)
def search(query: str, limit: int = 5) -> str:
    """Search for information about a topic."""
    # Implementation here
    return f"Results for {query}"
```

### Pattern 3: LangGraph State and Nodes
```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from operator import add

class State(TypedDict):
    messages: Annotated[list, add]  # Messages accumulate
    current_step: str

def process_node(state: State) -> dict:
    return {"messages": ["Processed"], "current_step": "next"}

graph = StateGraph(State)
graph.add_node("process", process_node)
graph.add_edge(START, "process")
graph.add_edge("process", END)
app = graph.compile()
```

### Pattern 4: Conditional Routing
```python
def route_decision(state: State) -> str:
    """Decide next node based on state."""
    if state.get("needs_review"):
        return "review"
    return "complete"

graph.add_conditional_edges(
    "analyze",
    route_decision,
    {"review": "review_node", "complete": END}
)
```

### Pattern 5: Streaming Responses
```python
async def stream_response(chain, input_data):
    async for chunk in chain.astream(input_data):
        yield chunk
```

## Common Mistakes

1. **Using deprecated imports**
   - Old: `from langchain.chat_models import ChatOpenAI`
   - New: `from langchain_openai import ChatOpenAI`
   - Old: `from langchain.agents import initialize_agent`
   - New: `from langgraph.prebuilt import create_react_agent`

2. **Not using TypedDict for LangGraph state**
   - Always define state schema with TypedDict
   - Use Annotated with reducer functions for accumulating fields

3. **Forgetting to compile the graph**
   - Call `graph.compile()` before invoking
   - Add checkpointer for persistence: `graph.compile(checkpointer=memory)`

4. **Not handling async properly**
   - Use `ainvoke()` and `astream()` for async operations
   - Don't mix sync and async calls incorrectly

5. **Missing tool docstrings**
   - Tools MUST have docstrings - LLM uses them for tool selection
   - Use Pydantic schemas for complex tool arguments

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make example-1` and the README.md. Example 1 shows the simplest chain pattern.

### "What's the difference between LangChain and LangGraph?"
- LangChain: Building blocks (chains, prompts, models, tools)
- LangGraph: Graph-based orchestration for complex workflows
- Use both together: LangChain components inside LangGraph nodes

### "How do I add memory to my agent?"
Use LangGraph with checkpointing:
```python
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
app = graph.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "user-123"}}
```

### "Why isn't my tool being called?"
1. Check the tool has a docstring describing what it does
2. Verify the tool is passed to the agent
3. Check the prompt mentions the tool capability
4. Look at LangSmith traces for debugging

### "How do I debug LangChain?"
1. Enable verbose mode: `chain.invoke(..., config={"verbose": True})`
2. Use LangSmith for tracing (set `LANGCHAIN_TRACING_V2=true`)
3. Add callbacks for logging

### "What model should I use?"
- GPT-4o: Best reasoning, tool use
- GPT-4o-mini: Good balance of cost/quality
- Claude 3.5 Sonnet: Great for coding tasks
- Local models: Use with Ollama or vLLM

## Testing Notes

- Tests use pytest with async support
- Mock LLM calls for unit tests to avoid API costs
- Use `pytest-asyncio` for async tests
- Integration tests may need real API keys

## Dependencies

Key dependencies in pyproject.toml:
- langchain-core: Core abstractions and LCEL
- langchain-openai: OpenAI integrations
- langgraph: Graph-based workflows
- langchain-community: Community integrations
- pydantic>=2.0: Data validation for tools and state

## Environment Variables

```bash
OPENAI_API_KEY=sk-...          # Required for OpenAI models
LANGCHAIN_TRACING_V2=true      # Enable LangSmith tracing
LANGCHAIN_API_KEY=ls-...       # LangSmith API key
LANGCHAIN_PROJECT=my-project   # LangSmith project name
```
