# Common Patterns

## Overview

This document covers common Cypher query patterns and best practices for working with Neo4j.

## Pattern 1: Safe Driver Usage

### When to Use

Always when connecting to Neo4j from application code.

### Implementation

```python
from neo4j import GraphDatabase
from contextlib import contextmanager

class Neo4jConnection:
    """Thread-safe Neo4j connection manager."""

    def __init__(self, uri: str, user: str, password: str):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    @contextmanager
    def session(self, database: str = "neo4j"):
        session = self._driver.session(database=database)
        try:
            yield session
        finally:
            session.close()

    def run_query(self, query: str, params: dict = None):
        """Execute a read query and return results."""
        with self.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]

# Usage
conn = Neo4jConnection("bolt://localhost:7687", "neo4j", "password")
try:
    results = conn.run_query(
        "MATCH (p:Person {name: $name}) RETURN p",
        {"name": "Alice"}
    )
finally:
    conn.close()
```

### Pitfalls to Avoid

- Never interpolate strings into queries (injection risk, no query caching)
- Always close drivers and sessions
- Don't create multiple drivers to the same database

## Pattern 2: Transaction Functions

### When to Use

For write operations that need automatic retry on transient failures.

### Implementation

```python
def create_person_with_company(tx, person_name: str, company_name: str):
    """Transaction function - automatically retried on failure."""
    query = """
    MERGE (p:Person {name: $person_name})
    MERGE (c:Company {name: $company_name})
    MERGE (p)-[:WORKS_AT {since: date()}]->(c)
    RETURN p, c
    """
    result = tx.run(query, person_name=person_name, company_name=company_name)
    record = result.single()
    return {
        "person": record["p"],
        "company": record["c"]
    }

# Execute write transaction
with driver.session() as session:
    result = session.execute_write(
        create_person_with_company,
        "Alice",
        "Acme Corp"
    )

# For read-only operations
def find_person(tx, name: str):
    result = tx.run("MATCH (p:Person {name: $name}) RETURN p", name=name)
    record = result.single()
    return record["p"] if record else None

with driver.session() as session:
    person = session.execute_read(find_person, "Alice")
```

### Pitfalls to Avoid

- Don't do non-idempotent operations in transaction functions (they may retry)
- Don't hold transactions open longer than necessary
- Use `execute_read` for read-only queries (enables routing to read replicas)

## Pattern 3: Idempotent Data Loading

### When to Use

When loading data that might be re-run (ETL, seed scripts, migrations).

### Implementation

```cypher
// Load data idempotently with MERGE
UNWIND $batch AS row
MERGE (p:Person {id: row.id})
ON CREATE SET
    p.name = row.name,
    p.email = row.email,
    p.created = datetime()
ON MATCH SET
    p.name = row.name,
    p.email = row.email,
    p.updated = datetime()
```

```python
def load_people_batch(tx, people: list[dict]):
    """Load people in batch, handling duplicates gracefully."""
    query = """
    UNWIND $batch AS row
    MERGE (p:Person {id: row.id})
    ON CREATE SET p += row, p.created = datetime()
    ON MATCH SET p += row, p.updated = datetime()
    RETURN count(p) as loaded
    """
    result = tx.run(query, batch=people)
    return result.single()["loaded"]

# Usage
people = [
    {"id": "1", "name": "Alice", "email": "alice@example.com"},
    {"id": "2", "name": "Bob", "email": "bob@example.com"},
]
with driver.session() as session:
    count = session.execute_write(load_people_batch, people)
```

### Pitfalls to Avoid

- MERGE on too many properties can be slow (only MERGE on unique identifiers)
- Don't use CREATE in seed scripts (creates duplicates on re-run)
- For relationships, MERGE on unique constraint or use natural key

## Pattern 4: Pagination with SKIP and LIMIT

### When to Use

When returning large result sets that need pagination.

### Implementation

```cypher
// Offset-based pagination
MATCH (p:Person)
RETURN p
ORDER BY p.name
SKIP $offset
LIMIT $limit

// Cursor-based pagination (more efficient for deep pagination)
MATCH (p:Person)
WHERE p.name > $lastSeenName
RETURN p
ORDER BY p.name
LIMIT $limit
```

```python
def get_people_page(tx, offset: int, limit: int):
    """Get a page of people with total count."""
    count_query = "MATCH (p:Person) RETURN count(p) as total"
    data_query = """
    MATCH (p:Person)
    RETURN p
    ORDER BY p.name
    SKIP $offset
    LIMIT $limit
    """

    total = tx.run(count_query).single()["total"]
    records = tx.run(data_query, offset=offset, limit=limit)

    return {
        "total": total,
        "data": [r["p"] for r in records],
        "offset": offset,
        "limit": limit
    }
```

### Pitfalls to Avoid

- Deep pagination with SKIP is slow (O(n))
- Use cursor-based pagination for large datasets
- Always include ORDER BY for consistent pagination

## Pattern 5: Conditional Query Building

### When to Use

When query filters are optional or dynamic.

### Implementation

```python
def search_people(tx, name: str = None, age_min: int = None, age_max: int = None):
    """Search with optional filters."""
    conditions = []
    params = {}

    if name:
        conditions.append("p.name CONTAINS $name")
        params["name"] = name

    if age_min is not None:
        conditions.append("p.age >= $age_min")
        params["age_min"] = age_min

    if age_max is not None:
        conditions.append("p.age <= $age_max")
        params["age_max"] = age_max

    where_clause = " AND ".join(conditions) if conditions else "true"

    query = f"""
    MATCH (p:Person)
    WHERE {where_clause}
    RETURN p
    ORDER BY p.name
    """

    return [r["p"] for r in tx.run(query, **params)]
```

Alternative using Cypher's CASE:
```cypher
MATCH (p:Person)
WHERE ($name IS NULL OR p.name CONTAINS $name)
  AND ($age_min IS NULL OR p.age >= $age_min)
  AND ($age_max IS NULL OR p.age <= $age_max)
RETURN p
```

### Pitfalls to Avoid

- Don't concatenate user input directly into queries
- Test generated queries with EXPLAIN to verify efficiency
- Consider creating indexes for commonly filtered properties

## Anti-Pattern 1: Cartesian Products

### What It Is

Unintentionally creating cross-products between unrelated patterns.

### Why It's Bad

```cypher
// BAD - This creates a cartesian product!
MATCH (p:Person)
MATCH (m:Movie)
RETURN p, m
// If you have 1000 persons and 1000 movies = 1,000,000 rows!
```

### Better Approach

```cypher
// GOOD - Connected pattern
MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
RETURN p, m

// GOOD - If you need all combinations, be explicit
MATCH (p:Person), (m:Movie)
WHERE p.name = 'Alice'  // Filter to reduce combinations
RETURN p, m

// GOOD - Use subqueries for independent patterns
MATCH (p:Person {name: 'Alice'})
CALL {
    MATCH (m:Movie)
    RETURN m LIMIT 10
}
RETURN p, m
```

## Anti-Pattern 2: Unbounded Variable-Length Paths

### What It Is

Using `*` without bounds in path patterns.

### Why It's Bad

```cypher
// BAD - Explores entire graph!
MATCH path = (a)-[*]->(b)
RETURN path

// Can hang or crash on large graphs
```

### Better Approach

```cypher
// GOOD - Set reasonable bounds
MATCH path = (a)-[*1..5]->(b)
RETURN path

// GOOD - Use shortestPath for specific endpoints
MATCH path = shortestPath((a:Person {name: 'Alice'})-[*]-(b:Person {name: 'Bob'}))
RETURN path

// GOOD - Limit results
MATCH path = (a:Person {name: 'Alice'})-[:KNOWS*1..10]->(b)
RETURN path
LIMIT 100
```

## Anti-Pattern 3: Missing Indexes

### What It Is

Querying properties that aren't indexed.

### Why It's Bad

```cypher
// Without index, this scans ALL Person nodes
MATCH (p:Person {email: 'alice@example.com'})
RETURN p
```

### Better Approach

```cypher
// Create index for frequently queried properties
CREATE INDEX person_email FOR (p:Person) ON (p.email)

// Create composite index for multi-property queries
CREATE INDEX person_name_age FOR (p:Person) ON (p.name, p.age)

// Create unique constraint (also creates index)
CREATE CONSTRAINT person_id_unique FOR (p:Person) REQUIRE p.id IS UNIQUE

// Verify indexes are used
EXPLAIN MATCH (p:Person {email: 'alice@example.com'}) RETURN p
// Should show "NodeIndexSeek" not "NodeByLabelScan"
```

## Pattern 6: Graph Algorithms with GDS

### When to Use

For complex analytics like PageRank, community detection, pathfinding at scale.

### Implementation

```cypher
// First, create a graph projection
CALL gds.graph.project(
    'myGraph',
    'Person',
    'KNOWS'
)

// Run PageRank
CALL gds.pageRank.stream('myGraph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC

// Community detection
CALL gds.louvain.stream('myGraph')
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).name AS name, communityId

// Clean up projection when done
CALL gds.graph.drop('myGraph')
```

### Pitfalls to Avoid

- GDS requires separate installation (Neo4j Graph Data Science library)
- Graph projections consume memory - drop when done
- Start with small subgraphs to test algorithms
