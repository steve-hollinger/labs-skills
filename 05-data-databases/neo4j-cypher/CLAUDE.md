# CLAUDE.md - Neo4j Cypher Query Language

This skill teaches the Cypher query language for graph databases. Cypher is to Neo4j what SQL is to relational databases - a declarative pattern-matching language for querying and manipulating graph data.

## Key Concepts

- **Pattern Matching**: Cypher uses ASCII-art syntax `(node)-[rel]->(node)` to match graph patterns
- **MATCH**: Find existing patterns in the graph
- **CREATE/MERGE**: Add new nodes and relationships (MERGE is idempotent)
- **SET/REMOVE**: Modify properties on nodes and relationships
- **Aggregations**: COUNT, SUM, AVG, COLLECT work like SQL aggregates
- **Path Queries**: Variable-length patterns `[*1..3]` for multi-hop traversals

## Common Commands

```bash
make setup      # Install Python dependencies with UV
make examples   # Run all examples
make example-1  # Run basic CRUD example
make example-2  # Run pattern matching example
make example-3  # Run aggregations example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
neo4j-cypher/
├── README.md
├── CLAUDE.md
├── pyproject.toml
├── Makefile
├── examples/
│   ├── __init__.py
│   ├── example_1_crud.py       # Basic CRUD operations
│   ├── example_2_patterns.py   # Pattern matching
│   └── example_3_aggregations.py # Aggregations & paths
├── exercises/
│   ├── exercise_1_social.py    # Social network queries
│   ├── exercise_2_movies.py    # Movie database queries
│   ├── exercise_3_recommend.py # Recommendation queries
│   └── solutions/
│       ├── solution_1.py
│       ├── solution_2.py
│       └── solution_3.py
├── tests/
│   └── test_cypher.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Safe Query Execution with Parameters

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

### Pattern 2: Transaction Functions for Reliability

```python
def create_person(tx, name: str, age: int):
    """Transaction function - automatically handles retries."""
    query = """
    MERGE (p:Person {name: $name})
    ON CREATE SET p.age = $age, p.created = datetime()
    RETURN p
    """
    result = tx.run(query, name=name, age=age)
    return result.single()

# Execute in transaction
with driver.session() as session:
    person = session.execute_write(create_person, "Alice", 30)
```

### Pattern 3: Relationship Pattern Matching

```cypher
// Direct relationship
MATCH (a:Person)-[:KNOWS]->(b:Person)
RETURN a, b

// Variable-length path (1 to 3 hops)
MATCH path = (a:Person)-[:KNOWS*1..3]->(b:Person)
RETURN path

// Shortest path
MATCH path = shortestPath((a:Person)-[:KNOWS*]-(b:Person))
WHERE a.name = $start AND b.name = $end
RETURN path
```

## Common Mistakes

1. **Creating duplicates with CREATE instead of MERGE**
   - CREATE always creates new nodes/relationships
   - MERGE finds existing or creates if not found
   - Use MERGE for idempotent operations

2. **Forgetting relationship direction matters**
   - `(a)-[:KNOWS]->(b)` only matches one direction
   - `(a)-[:KNOWS]-(b)` matches both directions
   - Direction is often semantically important

3. **Cartesian products from unconnected patterns**
   - Multiple MATCH clauses without connection = cartesian product
   - This can be extremely slow
   - Connect patterns or use subqueries

4. **Not using indexes**
   - Create indexes on frequently queried properties
   - `CREATE INDEX FOR (p:Person) ON (p.name)`
   - Check query plans with `EXPLAIN` or `PROFILE`

5. **String interpolation instead of parameters**
   - Never interpolate user input into queries
   - Always use `$param` syntax with parameter dict
   - Parameters also enable query plan caching

## When Users Ask About...

### "How do I find friends of friends?"
Use variable-length paths:
```cypher
MATCH (person:Person {name: $name})-[:KNOWS*2]->(fof:Person)
WHERE person <> fof
RETURN DISTINCT fof
```

### "How do I count relationships?"
Use aggregation with COUNT:
```cypher
MATCH (p:Person)-[r:KNOWS]->()
RETURN p.name, COUNT(r) as friendCount
ORDER BY friendCount DESC
```

### "How do I delete nodes with relationships?"
Use DETACH DELETE:
```cypher
MATCH (p:Person {name: $name})
DETACH DELETE p  // Deletes node AND all its relationships
```

### "How do I update multiple properties?"
Use SET with map syntax:
```cypher
MATCH (p:Person {name: $name})
SET p += {age: 31, city: 'NYC', updated: datetime()}
```

### "Why is my query slow?"
Check the query plan:
```cypher
PROFILE MATCH (p:Person)-[:KNOWS*3]->(fof)
RETURN p, fof
```
Look for:
- Cartesian products (bad)
- Missing indexes (look for NodeByLabelScan)
- Unbounded variable-length paths

## Testing Notes

- Tests require Neo4j running (use `make infra-up` from repo root)
- Tests create and clean up their own data in a test database
- Use transaction rollback for test isolation
- Mark integration tests with `@pytest.mark.integration`

## Dependencies

Key dependencies in pyproject.toml:
- neo4j: Official Neo4j Python driver
- pytest: Testing framework
- pytest-asyncio: For async test support
