# Core Concepts

## Overview

Cypher is a declarative graph query language that uses ASCII-art patterns to represent nodes and relationships. This guide covers the fundamental concepts you need to master Cypher queries.

## Concept 1: Graph Data Model

### What It Is

Neo4j stores data as a property graph consisting of:
- **Nodes**: Entities (like rows in a table, but more flexible)
- **Relationships**: Connections between nodes (always directed, always typed)
- **Properties**: Key-value pairs on nodes and relationships
- **Labels**: Categories for nodes (like table names)

### Why It Matters

Understanding the data model is essential because:
- Graph queries follow relationships directly (no joins needed)
- Schema is flexible - nodes of the same label can have different properties
- Relationships are first-class citizens, not foreign keys

### How It Works

```
Visual representation:

    (Person)           [:WORKS_AT]          (Company)
   name: "Alice"  ------------------>    name: "Acme"
   age: 30            since: 2020         industry: "Tech"
```

In Cypher:
```cypher
// Create this pattern
CREATE (alice:Person {name: 'Alice', age: 30})
CREATE (acme:Company {name: 'Acme', industry: 'Tech'})
CREATE (alice)-[:WORKS_AT {since: 2020}]->(acme)
```

## Concept 2: Pattern Matching with MATCH

### What It Is

MATCH finds patterns in your graph using ASCII-art syntax. It's the foundation of most Cypher queries.

### Why It Matters

Pattern matching is how you:
- Query existing data
- Specify what nodes/relationships to update or delete
- Navigate complex graph structures

### How It Works

Basic patterns:
```cypher
// Match all Person nodes
MATCH (p:Person)
RETURN p

// Match with property filter
MATCH (p:Person {name: 'Alice'})
RETURN p

// Match relationships
MATCH (p:Person)-[r:WORKS_AT]->(c:Company)
RETURN p.name, c.name, r.since

// Match any relationship type
MATCH (p:Person)-[r]->(c:Company)
RETURN type(r), r

// Match either direction
MATCH (a:Person)-[:KNOWS]-(b:Person)
RETURN a, b
```

Pattern elements:
```
(variable:Label {property: value})  -- Node
-[variable:TYPE {property: value}]-> -- Relationship (directed)
-[variable:TYPE]-                    -- Relationship (undirected)
```

## Concept 3: Creating Data with CREATE and MERGE

### What It Is

- **CREATE**: Always creates new nodes/relationships
- **MERGE**: Finds existing or creates if not found (idempotent)

### Why It Matters

Understanding when to use each prevents:
- Duplicate data from repeated CREATE operations
- Unexpected matches when you wanted to create

### How It Works

CREATE - Use for guaranteed new data:
```cypher
// Creates new node every time
CREATE (p:Person {name: 'Alice'})
RETURN p

// Create relationship between existing nodes
MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'})
CREATE (a)-[:KNOWS {since: date()}]->(b)
```

MERGE - Use for idempotent operations:
```cypher
// Finds or creates
MERGE (p:Person {name: 'Alice'})
RETURN p

// With conditional SET
MERGE (p:Person {name: 'Alice'})
ON CREATE SET p.created = datetime()
ON MATCH SET p.lastSeen = datetime()
RETURN p

// MERGE relationship (must MATCH nodes first)
MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'})
MERGE (a)-[:KNOWS]->(b)
```

**Important**: MERGE matches on the ENTIRE pattern. Be careful:
```cypher
// This merges based on name only - other properties ignored for matching
MERGE (p:Person {name: 'Alice'})
SET p.age = 30  // Use SET for additional properties
```

## Concept 4: Updating and Deleting

### What It Is

- **SET**: Add or update properties
- **REMOVE**: Remove properties or labels
- **DELETE**: Remove nodes and relationships
- **DETACH DELETE**: Delete nodes along with all their relationships

### Why It Matters

Graph databases require explicit relationship handling when deleting nodes. You cannot delete a node that has relationships.

### How It Works

SET operations:
```cypher
// Update single property
MATCH (p:Person {name: 'Alice'})
SET p.age = 31

// Update multiple properties
MATCH (p:Person {name: 'Alice'})
SET p.age = 31, p.city = 'NYC'

// Update from map (merge properties)
MATCH (p:Person {name: 'Alice'})
SET p += {age: 31, city: 'NYC'}

// Replace all properties
MATCH (p:Person {name: 'Alice'})
SET p = {name: 'Alice', age: 31}  // All other properties removed!
```

REMOVE operations:
```cypher
// Remove property
MATCH (p:Person {name: 'Alice'})
REMOVE p.age

// Remove label
MATCH (p:Person:Employee {name: 'Alice'})
REMOVE p:Employee
```

DELETE operations:
```cypher
// Delete relationship
MATCH (a:Person)-[r:KNOWS]->(b:Person)
WHERE a.name = 'Alice' AND b.name = 'Bob'
DELETE r

// Delete node (must have no relationships!)
MATCH (p:Person {name: 'Orphan'})
DELETE p

// Delete node and all its relationships
MATCH (p:Person {name: 'Alice'})
DETACH DELETE p
```

## Concept 5: Aggregations

### What It Is

Aggregation functions (COUNT, SUM, AVG, MIN, MAX, COLLECT) summarize data across multiple records.

### Why It Matters

Aggregations let you:
- Count relationships
- Calculate statistics
- Group results
- Build collections from query results

### How It Works

```cypher
// Count nodes
MATCH (p:Person)
RETURN COUNT(p) as personCount

// Count relationships per person
MATCH (p:Person)-[r:KNOWS]->()
RETURN p.name, COUNT(r) as friendCount
ORDER BY friendCount DESC

// Aggregate with COLLECT (returns list)
MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
RETURN p.name, COLLECT(m.title) as movies

// Multiple aggregations
MATCH (p:Person)-[r:KNOWS]->(friend:Person)
RETURN p.name,
       COUNT(friend) as friendCount,
       AVG(friend.age) as avgFriendAge,
       COLLECT(friend.name) as friendNames
```

**Grouping**: Non-aggregated return columns become the grouping key (like SQL GROUP BY):
```cypher
// Groups by p.name automatically
MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
RETURN p.name, COUNT(m) as movieCount
```

## Concept 6: Path Queries

### What It Is

Path queries find connections through variable numbers of relationships, enabling powerful graph traversals.

### Why It Matters

Variable-length paths let you:
- Find connections at any depth (friends of friends of friends...)
- Calculate shortest paths
- Detect cycles and patterns

### How It Works

```cypher
// Variable-length path (1 to 3 hops)
MATCH path = (a:Person)-[:KNOWS*1..3]->(b:Person)
WHERE a.name = 'Alice'
RETURN path

// Exactly 2 hops (friends of friends)
MATCH (a:Person)-[:KNOWS*2]->(fof:Person)
WHERE a.name = 'Alice' AND a <> fof
RETURN DISTINCT fof.name

// Any length (careful - can be slow!)
MATCH path = (a:Person)-[:KNOWS*]->(b:Person)
WHERE a.name = 'Alice' AND b.name = 'Bob'
RETURN path

// Shortest path
MATCH path = shortestPath(
  (a:Person {name: 'Alice'})-[:KNOWS*]-(b:Person {name: 'Bob'})
)
RETURN path, length(path)

// All shortest paths
MATCH path = allShortestPaths(
  (a:Person {name: 'Alice'})-[:KNOWS*]-(b:Person {name: 'Bob'})
)
RETURN path
```

Path functions:
```cypher
MATCH path = (a)-[:KNOWS*]->(b)
RETURN
  nodes(path),        // List of nodes in path
  relationships(path), // List of relationships
  length(path)        // Number of relationships
```

## Summary

Key takeaways:

1. **Property Graph Model**: Nodes, relationships, properties, labels - more flexible than relational
2. **MATCH**: Pattern matching is the heart of Cypher - learn the ASCII-art syntax well
3. **CREATE vs MERGE**: CREATE always creates; MERGE is idempotent - use appropriately
4. **SET/REMOVE/DELETE**: Explicit property and relationship handling; use DETACH DELETE for nodes with relationships
5. **Aggregations**: COUNT, COLLECT, AVG, etc. with implicit grouping
6. **Paths**: Variable-length patterns enable powerful graph traversals
