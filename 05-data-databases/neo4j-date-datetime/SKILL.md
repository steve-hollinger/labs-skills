---
name: handling-neo4j-dates
description: Temporal data handling in Neo4j. Understanding when to use DATE versus DATETIME (and other temporal types) is critical for data modeling and query performance. Use when writing or improving tests.
---

# Neo4J Date Datetime

## Quick Start
```python
# Decision tree for temporal type selection:
#
# Need time component?
#   NO  -> DATE (birthdays, holidays, deadlines)
#   YES -> Need timezone?
#           NO  -> LOCALDATETIME (local events, logs)
#           YES -> DATETIME (global events, APIs)
#
# Only time, no date?
#   Need timezone? -> TIME or LOCALTIME
```


## Key Points
- DATE
- DATETIME
- LOCALDATETIME

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples