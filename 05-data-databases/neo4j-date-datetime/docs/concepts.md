# Core Concepts

## Overview

Neo4j provides rich temporal type support that goes beyond simple date strings. Understanding these types and when to use each is essential for building robust applications that handle time-based data correctly.

## Concept 1: Neo4j Temporal Types

### What They Are

Neo4j supports six temporal types:

| Type | Components | Timezone | Example |
|------|------------|----------|---------|
| DATE | year, month, day | No | `2024-01-15` |
| TIME | hour, minute, second, nanosecond | Yes | `14:30:00Z` |
| LOCALTIME | hour, minute, second, nanosecond | No | `14:30:00` |
| DATETIME | full date + time | Yes | `2024-01-15T14:30:00Z` |
| LOCALDATETIME | full date + time | No | `2024-01-15T14:30:00` |
| Duration | period of time | N/A | `P1Y2M3D` |

### Why They Matter

- **Type Safety**: Temporal types enforce valid date/time values
- **Correct Comparisons**: `date('2024-01-02') > date('2024-01-01')` works correctly
- **Built-in Functions**: Access to temporal functions (extract year, add days, etc.)
- **Indexing**: Temporal properties can be indexed for efficient range queries

### How They Work

```cypher
// Creating temporal values
RETURN date('2024-01-15') AS d,
       time('14:30:00') AS t,
       datetime('2024-01-15T14:30:00Z') AS dt,
       localdatetime('2024-01-15T14:30:00') AS ldt

// From components
RETURN date({year: 2024, month: 1, day: 15}) AS d,
       datetime({
           year: 2024, month: 1, day: 15,
           hour: 14, minute: 30, second: 0,
           timezone: 'UTC'
       }) AS dt

// Current values
RETURN date() AS today,
       datetime() AS now,
       time() AS currentTime
```

## Concept 2: DATE - Calendar Dates

### What It Is

DATE represents a calendar date without time information. It stores year, month, and day.

### Why It Matters

Use DATE when:
- Time of day is irrelevant (birthdays, holidays, deadlines)
- You want simpler queries without time handling
- Storage efficiency matters (DATE uses less space than DATETIME)
- You need predictable comparisons (no timezone complications)

### How It Works

```cypher
// Creating dates
CREATE (p:Person {
    birthDate: date('1990-05-15'),
    hireDate: date({year: 2020, month: 3, day: 1}),
    registrationDate: date()  // Today
})

// Querying dates
MATCH (p:Person)
WHERE p.birthDate.year = 1990
RETURN p

// Date comparisons
MATCH (p:Person)
WHERE p.hireDate > date('2019-01-01')
  AND p.hireDate < date('2021-01-01')
RETURN p

// Extracting components
MATCH (p:Person)
RETURN p.name,
       p.birthDate.year AS birthYear,
       p.birthDate.month AS birthMonth,
       p.birthDate.day AS birthDay
```

## Concept 3: DATETIME - Precise Timestamps

### What It Is

DATETIME represents a specific instant in time with timezone information. It's the most precise temporal type for recording when events occurred.

### Why It Matters

Use DATETIME when:
- You need to record exact moments (audit logs, events)
- Time zone matters (global applications, APIs)
- You need to compare times across different locations
- Precision to nanoseconds is required

### How It Works

```cypher
// Creating datetime values
CREATE (e:Event {
    // With timezone offset
    created: datetime('2024-01-15T14:30:00+05:30'),
    // With named timezone
    scheduled: datetime({
        year: 2024, month: 1, day: 15,
        hour: 14, minute: 30,
        timezone: 'America/New_York'
    }),
    // Current time
    logged: datetime()
})

// Querying with datetime
MATCH (e:Event)
WHERE e.created > datetime('2024-01-01T00:00:00Z')
RETURN e

// Timezone conversion
MATCH (e:Event)
RETURN e.created AS original,
       datetime({datetime: e.created, timezone: 'UTC'}) AS utc,
       datetime({datetime: e.created, timezone: 'Europe/London'}) AS london
```

## Concept 4: LOCALDATETIME vs DATETIME

### What It Is

LOCALDATETIME is like DATETIME but without timezone information. It represents "wall clock time" at an unspecified location.

### Why It Matters

The choice between LOCALDATETIME and DATETIME depends on your use case:

| Scenario | Recommended Type |
|----------|-----------------|
| User's local schedule | LOCALDATETIME |
| Global event timestamp | DATETIME |
| Audit log | DATETIME (UTC) |
| Recurring local event | LOCALDATETIME |
| API timestamps | DATETIME |

### How It Works

```cypher
// LOCALDATETIME - no timezone
CREATE (m:Meeting {
    // "3 PM on January 15" - timezone undefined
    scheduledTime: localdatetime('2024-01-15T15:00:00')
})

// DATETIME - timezone explicit
CREATE (e:GlobalEvent {
    // "3 PM UTC on January 15" - precise instant
    time: datetime('2024-01-15T15:00:00Z')
})

// Converting between them
MATCH (m:Meeting)
// Add timezone to local datetime
RETURN datetime({
    datetime: m.scheduledTime,
    timezone: 'America/New_York'
}) AS withTimezone
```

## Concept 5: Duration and Date Arithmetic

### What It Is

Duration represents a period of time that can be added to or subtracted from temporal values.

### Why It Matters

Durations enable:
- Date calculations (deadline + 30 days)
- Age calculations
- Time-based filtering (events in last 7 days)
- Scheduling logic

### How It Works

```cypher
// Creating durations
RETURN duration({days: 30}) AS thirtyDays,
       duration({months: 1}) AS oneMonth,
       duration({hours: 24}) AS oneDay,
       duration('P1Y2M3D') AS isoFormat  // 1 year, 2 months, 3 days

// Adding duration to dates
RETURN date('2024-01-15') + duration({days: 30}) AS futureDate,
       date('2024-01-15') - duration({months: 1}) AS pastDate

// Duration between dates
WITH date('2024-01-01') AS start, date('2024-12-31') AS end
RETURN duration.between(start, end) AS diff,
       duration.inDays(start, end).days AS daysBetween

// Common pattern: events in last N days
MATCH (e:Event)
WHERE e.created > datetime() - duration({days: 7})
RETURN e
```

## Concept 6: Temporal Indexing

### What It Is

Creating indexes on temporal properties to speed up range queries.

### Why It Matters

Date range queries are extremely common:
- "Events this month"
- "Orders in the last 24 hours"
- "Users who signed up after date X"

Without indexes, these queries scan all nodes with that label.

### How It Works

```cypher
// Create index on date property
CREATE INDEX person_birthdate FOR (p:Person) ON (p.birthDate)

// Create index on datetime property
CREATE INDEX event_created FOR (e:Event) ON (e.created)

// Composite index for multiple temporal queries
CREATE INDEX event_type_date FOR (e:Event) ON (e.type, e.created)

// Range query uses index
MATCH (e:Event)
WHERE e.created >= datetime('2024-01-01T00:00:00Z')
  AND e.created < datetime('2024-02-01T00:00:00Z')
RETURN e

// Verify index usage with EXPLAIN
EXPLAIN MATCH (e:Event)
WHERE e.created > datetime('2024-01-01T00:00:00Z')
RETURN e
// Should show NodeIndexSeek, not NodeByLabelScan
```

## Summary

Key takeaways:

1. **Use DATE** for calendar dates when time doesn't matter (birthdays, deadlines)
2. **Use DATETIME** for precise timestamps with timezone (events, audit logs)
3. **Use LOCALDATETIME** for local "wall clock" time when timezone is implicit
4. **Store in UTC** when using DATETIME, convert for display
5. **Use Duration** for date arithmetic, not manual calculations
6. **Create indexes** on temporal properties used in range queries
7. **Avoid strings** for dates - use native temporal types
