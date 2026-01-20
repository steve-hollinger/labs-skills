# Neo4j DATE vs DATETIME

Learn how to work with temporal data types in Neo4j. Understand the differences between DATE, DATETIME, TIME, and temporal duration operations.

## Learning Objectives

After completing this skill, you will be able to:
- Choose the appropriate temporal type for your data (DATE, DATETIME, TIME, LOCALDATETIME)
- Create and parse temporal values in Cypher
- Perform temporal comparisons and filtering
- Use duration operations for date arithmetic
- Handle timezone-aware datetime values
- Index and query temporal properties efficiently

## Prerequisites

- [Neo4j Cypher](../neo4j-cypher/) skill completed
- Docker (for running Neo4j locally)
- Python 3.11+
- Neo4j shared infrastructure: `make infra-up` from repository root

## Quick Start

```bash
# Ensure Neo4j is running (from repository root)
cd /path/to/labs-skills
make infra-up

# Install dependencies
cd 05-data-databases/neo4j-date-datetime
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

### Temporal Types Overview

Neo4j provides four main temporal types:

| Type | Description | Example | Use Case |
|------|-------------|---------|----------|
| DATE | Date only (no time) | `2024-01-15` | Birthdays, holidays |
| TIME | Time only (with timezone) | `14:30:00+00:00` | Opening hours, schedules |
| DATETIME | Full timestamp with timezone | `2024-01-15T14:30:00Z` | Events, audit logs |
| LOCALDATETIME | Timestamp without timezone | `2024-01-15T14:30:00` | Local events |

### DATE vs DATETIME - When to Use Each

```cypher
// DATE - When time doesn't matter
CREATE (p:Person {
    name: 'Alice',
    birthDate: date('1990-05-15'),      // Just the date
    hireDate: date()                     // Today's date
})

// DATETIME - When you need precise timestamps
CREATE (e:Event {
    name: 'Meeting',
    startTime: datetime('2024-01-15T14:30:00Z'),  // Full timestamp
    created: datetime()                            // Now
})

// LOCALDATETIME - When timezone doesn't matter
CREATE (l:LocalEvent {
    name: 'Lunch',
    time: localdatetime('2024-01-15T12:00:00')
})
```

### Creating Temporal Values

```cypher
// Current values
RETURN date() AS today,
       datetime() AS now,
       time() AS currentTime,
       localdatetime() AS localNow

// From strings
RETURN date('2024-01-15') AS d,
       datetime('2024-01-15T14:30:00Z') AS dt,
       datetime('2024-01-15T14:30:00+05:30') AS dtWithTz

// From components
RETURN date({year: 2024, month: 1, day: 15}) AS d,
       datetime({year: 2024, month: 1, day: 15, hour: 14, minute: 30}) AS dt
```

### Temporal Comparisons

```cypher
// Filter by date
MATCH (e:Event)
WHERE e.date > date('2024-01-01')
RETURN e

// Filter by date range
MATCH (e:Event)
WHERE date('2024-01-01') <= e.date <= date('2024-12-31')
RETURN e

// Recent events (last 7 days)
MATCH (e:Event)
WHERE e.created > datetime() - duration({days: 7})
RETURN e
```

## Examples

### Example 1: DATE Basics

Learn when and how to use DATE for calendar-based data.

```bash
make example-1
```

### Example 2: DATETIME and Timezones

Work with precise timestamps and timezone handling.

```bash
make example-2
```

### Example 3: Duration and Date Arithmetic

Perform calculations with durations and temporal values.

```bash
make example-3
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Event Calendar - Manage events with proper date/time handling
2. **Exercise 2**: Time-Based Analytics - Query data with temporal filtering
3. **Exercise 3**: Timezone Conversion - Handle multi-timezone scenarios

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Using String Comparisons for Dates

```cypher
// BAD - String comparison doesn't work correctly for dates
WHERE e.dateStr > '2024-01-15'

// GOOD - Use proper temporal types
WHERE e.date > date('2024-01-15')
```

### Ignoring Timezones

```cypher
// BAD - Comparing datetime with different timezones without consideration
WHERE e.time = datetime('2024-01-15T14:30:00Z')

// GOOD - Be explicit about timezone handling
WHERE e.time = datetime('2024-01-15T14:30:00Z')
   OR e.time = datetime('2024-01-15T09:30:00-05:00')  // Same instant
```

### Using DATETIME When DATE is Sufficient

```cypher
// BAD - Storing unnecessary precision
CREATE (p:Person {birthDate: datetime('1990-05-15T00:00:00Z')})

// GOOD - Use DATE when time doesn't matter
CREATE (p:Person {birthDate: date('1990-05-15')})
```

### Duration Arithmetic with Wrong Units

```cypher
// BAD - months and days don't mix predictably
duration({months: 1, days: 30})  // Confusing!

// GOOD - Be consistent with units
duration({days: 60})  // Clear intention
duration({months: 2}) // Or this
```

## Further Reading

- [Neo4j Temporal Documentation](https://neo4j.com/docs/cypher-manual/current/values-and-types/temporal/)
- [ISO 8601 Date/Time Format](https://en.wikipedia.org/wiki/ISO_8601)
- Related skills in this repository:
  - [Neo4j Cypher](../neo4j-cypher/)
  - [Neo4j Driver (Go)](../../01-language-frameworks/go/neo4j-driver/)
