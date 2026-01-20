---
name: handling-neo4j-dates
description: This skill teaches temporal data handling in Neo4j. Understanding when to use DATE versus DATETIME (and other temporal types) is critical for data modeling and query performance. Use when writing or improving tests.
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

## Commands
```bash
make setup      # Install Python dependencies with UV
make examples   # Run all examples
make example-1  # Run DATE basics example
make example-2  # Run DATETIME/timezone example
make example-3  # Run duration/arithmetic example
make test       # Run pytest
```

## Key Points
- DATE
- DATETIME
- LOCALDATETIME

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples