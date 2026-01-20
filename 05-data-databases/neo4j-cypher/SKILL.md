---
name: querying-with-cypher
description: The Cypher query language for graph databases. Cypher is to Neo4j what SQL is to relational databases - a declarative pattern-matching language for querying and manipulating graph data. Use when writing or improving tests.
---

# Neo4J Cypher

## Quick Start
```python
from neo4j import GraphDatabase

def run_query(driver, query: str, params: dict = None):
    """Always use parameters for safety and query caching."""
    with driver.session() as session:
        result = session.run(query, params or {})
        return [record.data() for record in result]

# Usage - ALWAYS parameterize
run_query(driver, "MATCH (p:Person {name: $name}) RETURN p", {"name": "Alice"})
```


## Key Points
- Pattern Matching
- MATCH
- CREATE/MERGE

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples