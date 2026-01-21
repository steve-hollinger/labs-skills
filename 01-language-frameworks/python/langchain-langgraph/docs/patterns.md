# Common Patterns

This document covers practical patterns for building LLM applications with LangChain and LangGraph.

## Chain Patterns

### 1. Sequential Chain

Process data through multiple steps sequentially.

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

model = ChatOpenAI(model="gpt-4o-mini")

# Step 1: Extract key points
extract_prompt = ChatPromptTemplate.from_template(
    "Extract the key points from this text:\n\n{text}"
)
extract_chain = extract_prompt | model | StrOutputParser()

# Step 2: Summarize the key points
summarize_prompt = ChatPromptTemplate.from_template(
    "Summarize these key points in one paragraph:\n\n{key_points}"
)
summarize_chain = summarize_prompt | model | StrOutputParser()

# Combine into sequential chain
def extract_and_summarize(text: str) -> str:
    key_points = extract_chain.invoke({"text": text})
    summary = summarize_chain.invoke({"key_points": key_points})
    return summary
```

### 2. Parallel Chain

Execute multiple chains simultaneously.

```python
from langchain_core.runnables import RunnableParallel

# Define parallel operations
parallel_chain = RunnableParallel(
    summary=summarize_chain,
    sentiment=sentiment_chain,
    keywords=keyword_chain
)

# All three run in parallel
result = parallel_chain.invoke({"text": document})
# result = {"summary": "...", "sentiment": "...", "keywords": "..."}
```

### 3. Branching Chain

Route to different chains based on input.

```python
from langchain_core.runnables import RunnableBranch

# Define routing logic
branch_chain = RunnableBranch(
    (lambda x: x["type"] == "question", qa_chain),
    (lambda x: x["type"] == "summary", summarize_chain),
    default_chain  # Fallback
)

result = branch_chain.invoke({"type": "question", "text": "What is Python?"})
```

### 4. Retry Chain

Automatically retry on failure.

```python
from langchain_core.runnables import RunnableWithRetry

# Wrap chain with retry logic
chain_with_retry = chain.with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)
```

## Agent Patterns

### 1. ReAct Agent (Reasoning + Acting)

The standard agent pattern that thinks step-by-step.

```python
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Search results for: {query}"

@tool
def calculator(expression: str) -> str:
    """Calculate a math expression."""
    return str(eval(expression))

model = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(model, [search, calculator])

result = agent.invoke({
    "messages": [("user", "What is 25 * 4, and what is Python?")]
})
```

### 2. Multi-Tool Agent with Structured Input

Agent with tools that have complex inputs.

```python
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class DatabaseQueryInput(BaseModel):
    table: str = Field(description="Table name to query")
    columns: list[str] = Field(description="Columns to select")
    where: str | None = Field(default=None, description="WHERE clause")
    limit: int = Field(default=10, ge=1, le=100)

@tool(args_schema=DatabaseQueryInput)
def query_database(
    table: str,
    columns: list[str],
    where: str | None = None,
    limit: int = 10
) -> str:
    """Query the database with the given parameters."""
    query = f"SELECT {', '.join(columns)} FROM {table}"
    if where:
        query += f" WHERE {where}"
    query += f" LIMIT {limit}"
    return f"Executed: {query}"
```

### 3. Agent with Human-in-the-Loop

Pause for human approval before sensitive actions.

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

class State(TypedDict):
    messages: Annotated[list, add]
    pending_action: dict | None
    approved: bool

def check_approval(state: State) -> str:
    if state.get("pending_action") and not state.get("approved"):
        return "wait_for_approval"
    return "execute"

graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("wait_for_approval", lambda s: s)  # Pause point
graph.add_node("execute", execute_node)

graph.add_conditional_edges("agent", check_approval)

app = graph.compile(checkpointer=MemorySaver(), interrupt_before=["wait_for_approval"])
```

## LangGraph Workflow Patterns

### 1. Linear Pipeline

Simple sequential processing.

```python
from langgraph.graph import StateGraph, START, END

class PipelineState(TypedDict):
    input: str
    validated: bool
    processed: str
    output: str

def validate(state: PipelineState) -> dict:
    # Validate input
    return {"validated": True}

def process(state: PipelineState) -> dict:
    # Process the input
    return {"processed": state["input"].upper()}

def format_output(state: PipelineState) -> dict:
    return {"output": f"Result: {state['processed']}"}

graph = StateGraph(PipelineState)
graph.add_node("validate", validate)
graph.add_node("process", process)
graph.add_node("format", format_output)

graph.add_edge(START, "validate")
graph.add_edge("validate", "process")
graph.add_edge("process", "format")
graph.add_edge("format", END)

pipeline = graph.compile()
```

### 2. Conditional Branching

Route based on content or state.

```python
def route_by_type(state: State) -> str:
    content = state["input"].lower()
    if "code" in content:
        return "code_handler"
    elif "data" in content:
        return "data_handler"
    return "general_handler"

graph.add_conditional_edges(
    "classifier",
    route_by_type,
    {
        "code_handler": "code_node",
        "data_handler": "data_node",
        "general_handler": "general_node"
    }
)
```

### 3. Retry Loop

Retry with feedback until success.

```python
class RetryState(TypedDict):
    input: str
    attempts: int
    result: str | None
    error: str | None

def process_with_retry(state: RetryState) -> dict:
    try:
        result = do_something(state["input"])
        return {"result": result, "attempts": state["attempts"] + 1}
    except Exception as e:
        return {"error": str(e), "attempts": state["attempts"] + 1}

def should_retry(state: RetryState) -> str:
    if state.get("result"):
        return "success"
    if state["attempts"] >= 3:
        return "failure"
    return "retry"

graph.add_conditional_edges(
    "process",
    should_retry,
    {"success": END, "failure": "error_handler", "retry": "process"}
)
```

### 4. Parallel Processing with Join

Fan out to multiple nodes, then join results.

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated

def merge_results(old: dict, new: dict) -> dict:
    return {**old, **new}

class ParallelState(TypedDict):
    input: str
    results: Annotated[dict, merge_results]

def analysis_a(state: ParallelState) -> dict:
    return {"results": {"a": "Result from A"}}

def analysis_b(state: ParallelState) -> dict:
    return {"results": {"b": "Result from B"}}

def combine(state: ParallelState) -> dict:
    all_results = state["results"]
    return {"results": {"combined": f"A: {all_results['a']}, B: {all_results['b']}"}}

# Note: True parallel execution requires LangGraph's Send API
# This pattern shows the state management approach
```

### 5. Supervisor Pattern

One agent coordinates multiple specialized agents.

```python
class SupervisorState(TypedDict):
    messages: Annotated[list, add]
    next_agent: str
    final_answer: str | None

def supervisor(state: SupervisorState) -> dict:
    # Supervisor decides which agent to call
    response = supervisor_model.invoke(state["messages"])
    return {"next_agent": response.content}

def researcher(state: SupervisorState) -> dict:
    # Research agent
    return {"messages": [{"role": "assistant", "content": "Research results..."}]}

def writer(state: SupervisorState) -> dict:
    # Writer agent
    return {"messages": [{"role": "assistant", "content": "Written content..."}]}

def route_to_agent(state: SupervisorState) -> str:
    return state["next_agent"]

graph = StateGraph(SupervisorState)
graph.add_node("supervisor", supervisor)
graph.add_node("researcher", researcher)
graph.add_node("writer", writer)

graph.add_edge(START, "supervisor")
graph.add_conditional_edges(
    "supervisor",
    route_to_agent,
    {"researcher": "researcher", "writer": "writer", "done": END}
)
graph.add_edge("researcher", "supervisor")
graph.add_edge("writer", "supervisor")
```

## Memory and Persistence Patterns

### 1. Conversation Memory

Maintain chat history across turns.

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# Each thread maintains separate history
config = {"configurable": {"thread_id": "user-123"}}

# First message
app.invoke({"messages": [("user", "My name is Alice")]}, config)

# Second message - remembers the name
app.invoke({"messages": [("user", "What is my name?")]}, config)
```

### 2. Session State

Store custom state between interactions.

```python
class SessionState(TypedDict):
    messages: Annotated[list, add]
    user_preferences: dict
    context: dict

def update_preferences(state: SessionState) -> dict:
    # Extract and store user preferences
    preferences = extract_preferences(state["messages"])
    return {"user_preferences": {**state.get("user_preferences", {}), **preferences}}
```

### 3. Long-term Memory with External Store

Use external databases for persistent memory.

```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Vector store for semantic search over history
vectorstore = Chroma(
    embedding_function=OpenAIEmbeddings(),
    persist_directory="./memory_db"
)

def retrieve_relevant_memories(query: str) -> list[str]:
    docs = vectorstore.similarity_search(query, k=5)
    return [doc.page_content for doc in docs]

def store_memory(content: str, metadata: dict):
    vectorstore.add_texts([content], metadatas=[metadata])
```

## Error Handling Patterns

### 1. Graceful Degradation

```python
def safe_tool_call(state: State) -> dict:
    try:
        result = tool.invoke(state["input"])
        return {"result": result, "error": None}
    except Exception as e:
        # Return error info instead of crashing
        return {"result": None, "error": str(e)}
```

### 2. Fallback Chain

```python
from langchain_core.runnables import RunnableWithFallbacks

# Try GPT-4, fall back to GPT-3.5
chain_with_fallback = gpt4_chain.with_fallbacks([gpt35_chain])
```

### 3. Validation Node

```python
def validate_output(state: State) -> dict:
    output = state["output"]

    # Check for required fields
    if not output.get("answer"):
        return {"valid": False, "validation_error": "Missing answer"}

    # Check for hallucination markers
    if "I don't know" in output["answer"] and output.get("confidence", 0) > 0.8:
        return {"valid": False, "validation_error": "Confidence mismatch"}

    return {"valid": True, "validation_error": None}
```

## Streaming Patterns

### 1. Token Streaming

```python
async def stream_response(chain, input_data):
    """Stream tokens to client."""
    async for chunk in chain.astream(input_data):
        yield chunk
```

### 2. Event Streaming

```python
async def stream_events(app, input_data):
    """Stream graph events to client."""
    async for event in app.astream_events(input_data, version="v2"):
        if event["event"] == "on_chat_model_stream":
            yield event["data"]["chunk"].content
```

### 3. Progress Updates

```python
def stream_with_progress(app, input_data):
    """Stream with node progress updates."""
    for update in app.stream(input_data, stream_mode="updates"):
        node_name = list(update.keys())[0]
        yield {"type": "progress", "node": node_name}
        yield {"type": "data", "content": update[node_name]}
```
