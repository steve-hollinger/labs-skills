# Common Patterns

## Overview

This document covers common patterns for working with temporal data in Neo4j, including best practices for storage, querying, and timezone handling.

## Pattern 1: Store in UTC, Display in Local

### When to Use

Whenever you work with global timestamps that may be displayed in different timezones.

### Implementation

```cypher
// Store event in UTC
CREATE (e:Event {
    name: 'Global Conference',
    // Always store as UTC
    timestamp: datetime({
        year: 2024, month: 3, day: 15,
        hour: 14, minute: 0,
        timezone: 'UTC'
    })
})

// Query and convert to user's timezone for display
MATCH (e:Event)
RETURN e.name,
       e.timestamp AS storedUtc,
       datetime({datetime: e.timestamp, timezone: 'America/New_York'}) AS eastern,
       datetime({datetime: e.timestamp, timezone: 'Asia/Tokyo'}) AS tokyo
```

```python
from neo4j import GraphDatabase
from datetime import datetime, timezone

def create_event(tx, name: str, local_time: datetime, user_timezone: str):
    """Create event, converting user's local time to UTC for storage."""
    # Convert to UTC before storing
    utc_time = local_time.astimezone(timezone.utc)

    tx.run("""
        CREATE (e:Event {
            name: $name,
            timestamp: datetime($timestamp)
        })
    """, name=name, timestamp=utc_time.isoformat())

def get_events_for_user(tx, user_timezone: str):
    """Get events converted to user's timezone."""
    result = tx.run("""
        MATCH (e:Event)
        RETURN e.name AS name,
               datetime({datetime: e.timestamp, timezone: $tz}) AS localTime
    """, tz=user_timezone)
    return list(result)
```

### Pitfalls to Avoid

- Don't assume server timezone is consistent
- Don't store local time without timezone context
- Document what timezone is used for storage

## Pattern 2: Date Range Queries

### When to Use

Filtering data by time periods (this week, last month, specific date range).

### Implementation

```cypher
// Events today
MATCH (e:Event)
WHERE date(e.timestamp) = date()
RETURN e

// Events this month
MATCH (e:Event)
WHERE e.timestamp >= datetime({year: 2024, month: 3, day: 1, timezone: 'UTC'})
  AND e.timestamp < datetime({year: 2024, month: 4, day: 1, timezone: 'UTC'})
RETURN e

// Events in last N days (parameterized)
MATCH (e:Event)
WHERE e.timestamp > datetime() - duration({days: $days})
RETURN e

// Events between two dates (inclusive)
MATCH (e:Event)
WHERE date($startDate) <= date(e.timestamp) <= date($endDate)
RETURN e
```

```python
def get_events_in_range(tx, start_date: str, end_date: str):
    """Get events within a date range (inclusive)."""
    result = tx.run("""
        MATCH (e:Event)
        WHERE date(e.timestamp) >= date($start)
          AND date(e.timestamp) <= date($end)
        RETURN e
        ORDER BY e.timestamp
    """, start=start_date, end=end_date)
    return list(result)

def get_recent_events(tx, days: int):
    """Get events from the last N days."""
    result = tx.run("""
        MATCH (e:Event)
        WHERE e.timestamp > datetime() - duration({days: $days})
        RETURN e
        ORDER BY e.timestamp DESC
    """, days=days)
    return list(result)
```

### Pitfalls to Avoid

- Use `<` for end of range, not `<=` when using datetime (avoids off-by-one)
- Index temporal properties used in WHERE clauses
- Be careful with timezone when comparing dates

## Pattern 3: Temporal Aggregations

### When to Use

Reporting by time periods (daily counts, monthly totals, hourly activity).

### Implementation

```cypher
// Count events per day
MATCH (e:Event)
WHERE e.timestamp >= datetime('2024-01-01T00:00:00Z')
  AND e.timestamp < datetime('2024-02-01T00:00:00Z')
RETURN date(e.timestamp) AS day, COUNT(e) AS eventCount
ORDER BY day

// Group by month
MATCH (e:Event)
RETURN e.timestamp.year AS year,
       e.timestamp.month AS month,
       COUNT(e) AS count
ORDER BY year, month

// Group by day of week (1=Monday, 7=Sunday)
MATCH (e:Event)
RETURN e.timestamp.dayOfWeek AS dayOfWeek, COUNT(e) AS count
ORDER BY dayOfWeek

// Hourly distribution
MATCH (e:Event)
RETURN e.timestamp.hour AS hour, COUNT(e) AS count
ORDER BY hour
```

### Pitfalls to Avoid

- Remember dayOfWeek starts at 1 (Monday), not 0
- Be aware of timezone when grouping by day
- Large date ranges may need pagination

## Pattern 4: Calculating Age/Duration

### When to Use

Finding age, tenure, elapsed time, or time until deadline.

### Implementation

```cypher
// Calculate age from birthdate
MATCH (p:Person)
RETURN p.name,
       p.birthDate,
       duration.between(p.birthDate, date()).years AS age

// Days until deadline
MATCH (t:Task)
WHERE t.dueDate >= date()
RETURN t.name,
       duration.inDays(date(), t.dueDate).days AS daysRemaining

// Employee tenure in years and months
MATCH (e:Employee)
WITH e, duration.between(e.hireDate, date()) AS tenure
RETURN e.name,
       tenure.years AS years,
       tenure.monthsOfYear AS months

// Time since last activity
MATCH (u:User)
RETURN u.name,
       duration.between(u.lastActive, datetime()) AS inactiveDuration,
       duration.inDays(u.lastActive, datetime()).days AS daysInactive
```

### Pitfalls to Avoid

- `duration.between()` returns a complex duration; use `duration.inDays()` for simple day count
- Duration components like `.years` and `.months` are NOT total; they're the respective component
- For total days between dates, use `duration.inDays(start, end).days`

## Pattern 5: Recurring Events

### When to Use

Modeling events that repeat (weekly meetings, monthly reports).

### Implementation

```cypher
// Create recurring event template
CREATE (r:RecurringEvent {
    name: 'Weekly Standup',
    dayOfWeek: 1,  // Monday
    time: time('09:00:00'),
    recurrence: 'weekly'
})

// Generate next occurrence
MATCH (r:RecurringEvent {name: 'Weekly Standup'})
WITH r, date() AS today
// Find next Monday
WITH r, today + duration({days: (7 - today.dayOfWeek + r.dayOfWeek) % 7}) AS nextDate
RETURN r.name,
       localdatetime({date: nextDate, time: r.time}) AS nextOccurrence

// Find all Mondays in a date range
WITH date('2024-01-01') AS start, date('2024-01-31') AS end
UNWIND range(0, duration.inDays(start, end).days) AS dayOffset
WITH start + duration({days: dayOffset}) AS d
WHERE d.dayOfWeek = 1  // Monday
RETURN d AS monday
```

### Pitfalls to Avoid

- Store recurrence rules, not individual events (for true recurring events)
- Consider edge cases (month end, leap years)
- Time zones can shift which day an event falls on

## Pattern 6: Business Days Calculation

### When to Use

Calculating deadlines or durations excluding weekends/holidays.

### Implementation

```cypher
// Count business days between dates (excluding weekends)
WITH date('2024-01-01') AS start, date('2024-01-31') AS end
WITH start, end, duration.inDays(start, end).days AS totalDays
UNWIND range(0, totalDays) AS dayOffset
WITH start + duration({days: dayOffset}) AS d
WHERE d.dayOfWeek <= 5  // Monday-Friday
RETURN COUNT(d) AS businessDays

// Find business day N days from now (excluding weekends)
WITH date() AS start, 10 AS businessDaysNeeded
WITH start, businessDaysNeeded, range(0, businessDaysNeeded * 2) AS possibleDays
UNWIND possibleDays AS dayOffset
WITH start + duration({days: dayOffset}) AS d, businessDaysNeeded
WHERE d.dayOfWeek <= 5
WITH d, businessDaysNeeded
ORDER BY d
LIMIT businessDaysNeeded
RETURN MAX(d) AS deadline
```

For holidays, you'd typically store them as nodes:
```cypher
// Create holidays
CREATE (:Holiday {date: date('2024-01-01'), name: 'New Year'})
CREATE (:Holiday {date: date('2024-07-04'), name: 'Independence Day'})

// Count business days excluding holidays
WITH date('2024-01-01') AS start, date('2024-01-31') AS end
MATCH (h:Holiday)
WHERE h.date >= start AND h.date <= end
WITH start, end, COLLECT(h.date) AS holidays
WITH start, end, holidays, duration.inDays(start, end).days AS totalDays
UNWIND range(0, totalDays) AS dayOffset
WITH start + duration({days: dayOffset}) AS d, holidays
WHERE d.dayOfWeek <= 5 AND NOT d IN holidays
RETURN COUNT(d) AS businessDays
```

## Anti-Pattern 1: Storing Dates as Strings

### What It Is

Using string properties instead of native temporal types.

### Why It's Bad

```cypher
// BAD - String storage
CREATE (e:Event {date: '2024-01-15'})

// These queries won't work correctly:
MATCH (e:Event) WHERE e.date > '2024-01-01'  // String comparison!
// '9' > '10' lexicographically, so '2024-09-01' > '2024-10-01'
```

### Better Approach

```cypher
// GOOD - Native DATE type
CREATE (e:Event {date: date('2024-01-15')})

// Correct comparison
MATCH (e:Event) WHERE e.date > date('2024-01-01')
```

## Anti-Pattern 2: Timezone Ignorance

### What It Is

Storing datetime without considering timezone implications.

### Why It's Bad

```cypher
// BAD - No explicit timezone
CREATE (e:Event {time: datetime('2024-01-15T14:30:00')})
// Uses server timezone - unpredictable!

// Later, on different server or after timezone change
MATCH (e:Event) RETURN e.time
// May return unexpected results
```

### Better Approach

```cypher
// GOOD - Always explicit timezone (preferably UTC)
CREATE (e:Event {time: datetime('2024-01-15T14:30:00Z')})

// Or with named timezone
CREATE (e:Event {time: datetime({
    year: 2024, month: 1, day: 15,
    hour: 14, minute: 30,
    timezone: 'America/New_York'
})})
```

## Anti-Pattern 3: Excessive Precision

### What It Is

Using DATETIME when DATE or LOCALDATETIME would suffice.

### Why It's Bad

```cypher
// BAD - Unnecessary precision and timezone complexity
CREATE (p:Person {birthDate: datetime('1990-05-15T00:00:00Z')})

// Now you have to handle:
// - Timezone conversion
// - Time component in comparisons
// - More storage space used
```

### Better Approach

```cypher
// GOOD - Appropriate type for the data
CREATE (p:Person {birthDate: date('1990-05-15')})

// Simple, clean queries
MATCH (p:Person) WHERE p.birthDate.year = 1990 RETURN p
```
