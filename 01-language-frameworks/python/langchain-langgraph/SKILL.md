---
name: building-langchain-agents
description: LLM orchestration using LangChain and LangGraph - frameworks for building chains, agents, and graph-based AI workflows. Use when writing or improving tests.
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


## Key Points
- LCEL (LangChain Expression Language)
- Chains
- Agents

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples