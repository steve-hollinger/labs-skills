# Core Concepts

This document explains the fundamental concepts in LangChain and LangGraph.

## LangChain Core Concepts

### 1. Runnables and LCEL

LangChain Expression Language (LCEL) is the declarative way to compose LangChain components.

#### The Pipe Operator

Components are composed using the pipe operator (`|`):

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Each component is a "Runnable"
prompt = ChatPromptTemplate.from_template("Tell me about {topic}")
model = ChatOpenAI(model="gpt-4o-mini")
parser = StrOutputParser()

# Compose into a chain
chain = prompt | model | parser

# Invoke the chain
result = chain.invoke({"topic": "Python"})
```

#### Runnable Interface

All components implement the Runnable interface:

- `invoke(input)` - Synchronous execution
- `ainvoke(input)` - Async execution
- `stream(input)` - Streaming output
- `astream(input)` - Async streaming
- `batch(inputs)` - Process multiple inputs
- `abatch(inputs)` - Async batch processing

### 2. Prompts

Prompts are templates for generating model inputs.

#### ChatPromptTemplate

```python
from langchain_core.prompts import ChatPromptTemplate

# From messages
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role}."),
    ("user", "{question}")
])

# With placeholders for message history
from langchain_core.prompts import MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}")
])
```

#### PromptTemplate (for completion models)

```python
from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template(
    "Summarize the following text:\n\n{text}\n\nSummary:"
)
```

### 3. Models

LangChain supports various LLM providers.

#### Chat Models

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# OpenAI
openai_model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=1000
)

# Anthropic
anthropic_model = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0.7
)
```

#### Model Configuration

```python
# Bind specific arguments
model_with_tools = model.bind(
    tools=[tool1, tool2],
    tool_choice="auto"
)

# Configure for JSON output
model_json = model.bind(
    response_format={"type": "json_object"}
)
```

### 4. Output Parsers

Output parsers transform model output into structured data.

#### String Parser

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
# Returns the content as a string
```

#### JSON Parser

```python
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

parser = JsonOutputParser(pydantic_object=Person)
```

#### Structured Output (Recommended)

```python
from pydantic import BaseModel

class Analysis(BaseModel):
    sentiment: str
    confidence: float
    keywords: list[str]

# Use with_structured_output for reliable parsing
structured_model = model.with_structured_output(Analysis)
result: Analysis = structured_model.invoke("Analyze: Great product!")
```

### 5. Tools

Tools are functions that agents can use.

#### Defining Tools

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# Simple tool
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"Weather in {city}: 72F, sunny"

# Tool with schema
class SearchInput(BaseModel):
    query: str = Field(description="Search query")
    num_results: int = Field(default=5, ge=1, le=20)

@tool(args_schema=SearchInput)
def search(query: str, num_results: int = 5) -> str:
    """Search the web for information."""
    return f"Found {num_results} results for: {query}"
```

#### Tool Best Practices

1. **Always include docstrings** - The LLM uses them to decide when to use the tool
2. **Use type hints** - Helps generate accurate schemas
3. **Use Pydantic schemas** - For complex inputs with validation
4. **Handle errors gracefully** - Return error messages rather than raising

## LangGraph Concepts

### 1. State

State is the data that flows through your graph, defined as a TypedDict.

```python
from typing import TypedDict, Annotated
from operator import add

class AgentState(TypedDict):
    # Simple field - overwritten each update
    current_step: str

    # Accumulating field - appends each update
    messages: Annotated[list, add]

    # Optional field
    error: str | None
```

#### Reducers

Annotated fields use reducer functions to combine updates:

```python
from operator import add

# add reducer: new = old + new (for lists, concatenates)
messages: Annotated[list, add]

# Custom reducer
def last_value(old, new):
    return new if new is not None else old

last_response: Annotated[str | None, last_value]
```

### 2. Nodes

Nodes are functions that receive state and return updates.

```python
def process_node(state: AgentState) -> dict:
    """Process the current state."""
    # Return only the fields you want to update
    return {
        "current_step": "processed",
        "messages": [{"role": "assistant", "content": "Done!"}]
    }
```

#### Node Types

1. **Regular nodes** - Transform state
2. **Tool nodes** - Execute tool calls
3. **Conditional nodes** - Route based on state

### 3. Edges

Edges define how nodes connect.

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(AgentState)

# Add nodes
graph.add_node("process", process_node)
graph.add_node("analyze", analyze_node)

# Regular edges
graph.add_edge(START, "process")
graph.add_edge("process", "analyze")
graph.add_edge("analyze", END)
```

#### Conditional Edges

```python
def route_decision(state: AgentState) -> str:
    if state.get("error"):
        return "handle_error"
    if state["current_step"] == "needs_review":
        return "review"
    return "complete"

graph.add_conditional_edges(
    "analyze",
    route_decision,
    {
        "handle_error": "error_handler",
        "review": "review_node",
        "complete": END
    }
)
```

### 4. Checkpointing

Checkpointing enables persistence and memory.

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

# In-memory (for development)
memory = MemorySaver()

# SQLite (for persistence)
# checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

app = graph.compile(checkpointer=memory)

# Use thread_id for conversation isolation
config = {"configurable": {"thread_id": "user-123"}}
result = app.invoke({"messages": ["Hello"]}, config)

# Later, same thread continues the conversation
result = app.invoke({"messages": ["Tell me more"]}, config)
```

### 5. Streaming

LangGraph supports multiple streaming modes.

```python
# Stream state updates
for update in app.stream({"messages": ["Hello"]}):
    print(update)

# Stream specific values
for event in app.stream({"messages": ["Hello"]}, stream_mode="values"):
    print(event)

# Async streaming
async for chunk in app.astream({"messages": ["Hello"]}):
    print(chunk)
```

## Putting It Together

### Simple Agent Pattern

```python
from typing import TypedDict, Annotated
from operator import add
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

class State(TypedDict):
    messages: Annotated[list, add]

@tool
def calculator(expression: str) -> str:
    """Calculate a math expression."""
    return str(eval(expression))

model = ChatOpenAI(model="gpt-4o-mini").bind_tools([calculator])

def call_model(state: State) -> dict:
    response = model.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: State) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

graph = StateGraph(State)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode([calculator]))
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

app = graph.compile()
```

This pattern creates a ReAct-style agent that:
1. Calls the model
2. If tool calls are needed, executes them
3. Returns tool results to the model
4. Repeats until no more tool calls
