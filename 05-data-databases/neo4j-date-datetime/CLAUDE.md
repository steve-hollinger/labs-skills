# CLAUDE.md - Neo4j DATE vs DATETIME

This skill teaches temporal data handling in Neo4j. Understanding when to use DATE versus DATETIME (and other temporal types) is critical for data modeling and query performance.

## Key Concepts

- **DATE**: Calendar date without time (year-month-day)
- **DATETIME**: Full timestamp with timezone (ISO 8601)
- **LOCALDATETIME**: Timestamp without timezone
- **TIME**: Time of day with timezone
- **LOCALTIME**: Time of day without timezone
- **Duration**: Time periods for date arithmetic

## Common Commands

```bash
make setup      # Install Python dependencies with UV
make examples   # Run all examples
make example-1  # Run DATE basics example
make example-2  # Run DATETIME/timezone example
make example-3  # Run duration/arithmetic example
make test       # Run pytest
make lint       # Run ruff and mypy
make clean      # Remove build artifacts
```

## Project Structure

```
neo4j-date-datetime/
├── README.md
├── CLAUDE.md
├── pyproject.toml
├── Makefile
├── examples/
│   ├── __init__.py
│   ├── example_1_date.py         # DATE basics
│   ├── example_2_datetime.py     # DATETIME and timezones
│   └── example_3_duration.py     # Duration operations
├── exercises/
│   ├── exercise_1_calendar.py    # Event calendar
│   ├── exercise_2_analytics.py   # Time-based analytics
│   ├── exercise_3_timezone.py    # Timezone handling
│   └── solutions/
├── tests/
│   └── test_temporal.py
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Choosing the Right Temporal Type

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

```cypher
// DATE - Calendar events, birthdays, deadlines
CREATE (t:Task {dueDate: date('2024-03-15')})

// DATETIME - Precise moments in time
CREATE (e:Event {timestamp: datetime('2024-03-15T14:30:00Z')})

// LOCALDATETIME - Local context, no timezone needed
CREATE (m:Meeting {scheduledAt: localdatetime('2024-03-15T14:30:00')})
```

### Pattern 2: Safe Date Parsing from User Input

```python
from datetime import date, datetime
from neo4j.time import Date, DateTime

def safe_parse_date(value: str) -> Date:
    """Parse date string to Neo4j Date."""
    try:
        # Try ISO format first
        d = datetime.fromisoformat(value)
        return Date(d.year, d.month, d.day)
    except ValueError:
        # Try common formats
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"]:
            try:
                d = datetime.strptime(value, fmt)
                return Date(d.year, d.month, d.day)
            except ValueError:
                continue
        raise ValueError(f"Cannot parse date: {value}")
```

### Pattern 3: Timezone-Safe DateTime Handling

```cypher
// Store in UTC
CREATE (e:Event {
    timestamp: datetime({
        year: 2024, month: 3, day: 15,
        hour: 14, minute: 30,
        timezone: 'UTC'
    })
})

// Query with timezone conversion for display
MATCH (e:Event)
RETURN e.timestamp AS utc,
       datetime({datetime: e.timestamp, timezone: 'America/New_York'}) AS eastern,
       datetime({datetime: e.timestamp, timezone: 'Europe/London'}) AS london
```

### Pattern 4: Date Range Queries with Indexes

```cypher
// Create index on temporal property
CREATE INDEX event_timestamp FOR (e:Event) ON (e.timestamp)

// Efficient range query (uses index)
MATCH (e:Event)
WHERE date('2024-01-01') <= date(e.timestamp) <= date('2024-12-31')
RETURN e

// Also efficient with datetime
MATCH (e:Event)
WHERE e.timestamp >= datetime('2024-01-01T00:00:00Z')
  AND e.timestamp < datetime('2025-01-01T00:00:00Z')
RETURN e
```

## Common Mistakes

1. **Storing dates as strings**
   - String comparison fails: '9' > '10' lexicographically
   - Use native temporal types for correct sorting/comparison
   - Strings can't use temporal functions

2. **Using DATETIME when DATE is sufficient**
   - Wastes storage space
   - Complicates queries (need to handle time component)
   - Can cause timezone confusion

3. **Ignoring timezone in DATETIME**
   - DATETIME without explicit timezone uses server timezone
   - Can cause bugs when server moves or changes timezone
   - Always store in UTC, convert for display

4. **Duration arithmetic pitfalls**
   - `duration({months: 1})` varies (28-31 days)
   - Mixing months/days with hours/seconds is tricky
   - Use consistent units within a duration

5. **Not indexing temporal properties**
   - Date range queries are common
   - Without index, requires full label scan
   - Create indexes for filtered temporal properties

## When Users Ask About...

### "How do I store a birthday?"
Use DATE - time is irrelevant for birthdays:
```cypher
CREATE (p:Person {name: 'Alice', birthDate: date('1990-05-15')})
```

### "How do I find events in the last 24 hours?"
Use datetime() and duration():
```cypher
MATCH (e:Event)
WHERE e.timestamp > datetime() - duration({hours: 24})
RETURN e
```

### "How do I convert between timezones?"
Use the timezone parameter in datetime():
```cypher
// Stored in UTC
MATCH (e:Event)
// Convert to Eastern Time for display
RETURN datetime({datetime: e.timestamp, timezone: 'America/New_York'}) AS localTime
```

### "How do I find all events on a specific date regardless of time?"
Truncate to date or use date():
```cypher
MATCH (e:Event)
WHERE date(e.timestamp) = date('2024-03-15')
RETURN e
```

### "How do I add days/months to a date?"
Use duration():
```cypher
// Add 30 days
RETURN date('2024-01-15') + duration({days: 30}) AS futureDate

// Add 1 month
RETURN date('2024-01-15') + duration({months: 1}) AS nextMonth
```

### "How do I calculate the difference between two dates?"
Use duration.between():
```cypher
WITH date('2024-01-01') AS start, date('2024-12-31') AS end
RETURN duration.between(start, end) AS diff,
       duration.inDays(start, end) AS daysDiff
```

## Testing Notes

- Tests require Neo4j running (use `make infra-up` from repo root)
- Temporal tests should use fixed dates, not `datetime()`, for reproducibility
- Test timezone handling with multiple explicit timezones
- Mark integration tests with `@pytest.mark.integration`

## Dependencies

Key dependencies in pyproject.toml:
- neo4j: Official Neo4j Python driver (includes temporal types)
- pytest: Testing framework
- pytz: Timezone definitions (optional, for advanced timezone handling)
