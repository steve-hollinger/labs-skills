# Neo4j Cypher Query Language

Learn the Cypher query language for working with graph databases in Neo4j. Master pattern matching, data manipulation, and complex traversals.

## Learning Objectives

After completing this skill, you will be able to:
- Write Cypher queries to create, read, update, and delete graph data
- Use MATCH patterns to traverse relationships and find connected data
- Apply CREATE, MERGE, and SET for data manipulation
- Write aggregation queries with GROUP BY equivalents
- Navigate complex paths with variable-length relationships
- Optimize queries using indexes and query planning

## Prerequisites

- Docker (for running Neo4j locally)
- Basic understanding of graph concepts (nodes, relationships)
- Python 3.11+ (for running examples)
- Neo4j shared infrastructure: `make infra-up` from repository root

## Quick Start

```bash
# Ensure Neo4j is running (from repository root)
cd /path/to/labs-skills
make infra-up

# Install dependencies
cd 05-data-databases/neo4j-cypher
make setup

# Run examples
make examples

# Run tests
make test
```

## Neo4j Connection Details

When using the shared infrastructure:
- **Bolt URL**: bolt://localhost:7687
- **HTTP URL**: http://localhost:7474
- **Username**: neo4j
- **Password**: password

## Concepts

### Nodes and Labels

Nodes are the primary entities in a graph. Labels categorize nodes.

```cypher
// Create a node with a label
CREATE (p:Person {name: 'Alice', age: 30})

// Find nodes by label
MATCH (p:Person) RETURN p

// Nodes can have multiple labels
CREATE (e:Person:Employee {name: 'Bob'})
```

### Relationships

Relationships connect nodes and have types and directions.

```cypher
// Create a relationship
MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'})
CREATE (a)-[:KNOWS {since: 2020}]->(b)

// Query relationships
MATCH (a:Person)-[r:KNOWS]->(b:Person)
RETURN a.name, r.since, b.name
```

### Properties

Both nodes and relationships can have properties (key-value pairs).

```cypher
// Set properties
MATCH (p:Person {name: 'Alice'})
SET p.email = 'alice@example.com'

// Remove properties
MATCH (p:Person {name: 'Alice'})
REMOVE p.email
```

### MERGE - Create If Not Exists

MERGE combines MATCH and CREATE - it finds or creates data.

```cypher
// Create if not exists
MERGE (p:Person {name: 'Charlie'})
ON CREATE SET p.created = datetime()
ON MATCH SET p.lastSeen = datetime()
```

## Examples

### Example 1: Basic CRUD Operations

Learn fundamental create, read, update, delete operations.

```bash
make example-1
```

### Example 2: Pattern Matching and Relationships

Master complex pattern matching with multiple relationships.

```bash
make example-2
```

### Example 3: Aggregations and Path Queries

Work with aggregations, collections, and variable-length paths.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Social Network - Create a friends network and query connections
2. **Exercise 2**: Movie Database - Build and query a movie-actor-director graph
3. **Exercise 3**: Recommendation Engine - Find recommendations using graph traversals

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Using CREATE Instead of MERGE

```cypher
// BAD - Creates duplicates on re-run
CREATE (p:Person {name: 'Alice'})

// GOOD - Idempotent operation
MERGE (p:Person {name: 'Alice'})
```

### Forgetting Relationship Direction

```cypher
// This won't find relationships in the opposite direction
MATCH (a)-[:KNOWS]->(b) RETURN a, b

// Use undirected if direction doesn't matter
MATCH (a)-[:KNOWS]-(b) RETURN a, b
```

### Cartesian Products from Multiple MATCH

```cypher
// BAD - Creates cartesian product (slow!)
MATCH (a:Person)
MATCH (b:Movie)
RETURN a, b

// GOOD - Use pattern or WHERE clause
MATCH (a:Person)-[:ACTED_IN]->(b:Movie)
RETURN a, b
```

### Not Using Parameters

```cypher
// BAD - String interpolation (SQL injection risk, no query caching)
MATCH (p:Person {name: 'Alice'}) RETURN p

// GOOD - Use parameters
MATCH (p:Person {name: $name}) RETURN p
// Pass parameters: {name: 'Alice'}
```

## Further Reading

- [Official Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [Neo4j GraphAcademy](https://graphacademy.neo4j.com/)
- Related skills in this repository:
  - [Neo4j DATE vs DATETIME](../neo4j-date-datetime/)
  - [Neo4j Driver (Go)](../../01-language-frameworks/go/neo4j-driver/)
