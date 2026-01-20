---
name: building-langchain-agents
description: This skill teaches LLM orchestration using LangChain and LangGraph - frameworks for building chains, agents, and graph-based AI workflows. Use when writing or improving tests.
---

# Langchain Langgraph

## Quick Start
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

## Commands
```bash
make setup      # Install dependencies with UV
make examples   # Run all examples
make example-1  # Run simple chain example
make example-2  # Run tool-using agent example
make example-3  # Run LangGraph workflow example
make example-4  # Run conversational agent example
```

## Key Points
- LCEL (LangChain Expression Language)
- Chains
- Agents

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples