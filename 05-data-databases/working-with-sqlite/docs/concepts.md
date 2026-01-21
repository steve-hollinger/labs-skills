# Core Concepts

## What is SQLite?

**SQLite** is a self-contained, serverless, zero-configuration SQL database engine. Unlike traditional databases (PostgreSQL, MySQL), SQLite is embedded directly into your application.

**Key characteristics:**
- **Serverless** - No separate database process or daemon
- **File-based** - Entire database is a single file on disk
- **Zero configuration** - No installation or setup required
- **Cross-platform** - Works on any OS
- **Full SQL support** - Standard SQL syntax, transactions, indexes

**Architecture comparison:**

```
Traditional Database (PostgreSQL):
[Your App] --network--> [PostgreSQL Server] --> [Data Files]

SQLite:
[Your App + SQLite Library] --> [database.db file]
```

**Why this matters:**
- **No network latency** - Database calls are function calls, not network requests
- **Simpler deployment** - No database server to manage or monitor
- **Lower operational cost** - No RDS instance to pay for
- **Easier local development** - No Docker Compose database service needed

## SQLite vs DynamoDB vs PostgreSQL

### Decision Matrix

| Factor | SQLite | DynamoDB | PostgreSQL (RDS) |
|--------|--------|----------|------------------|
| **Setup complexity** | ⭐ (just a file) | ⭐⭐ (IAM, schema) | ⭐⭐⭐ (VPC, security groups) |
| **Query volume** | < 1,000 QPS | Unlimited | 10,000+ QPS |
| **Data size** | < 100 GB | Unlimited | 64 TB (max) |
| **Concurrent writes** | 1 writer | Unlimited | 100s-1000s |
| **Query language** | Full SQL | NoSQL (limited) | Full SQL |
| **Local development** | ✅ No AWS needed | ❌ Needs AWS/localstack | ❌ Needs Docker |
| **Cost (monthly)** | $0 | ~$10-100 (pay-per-use) | ~$50-500 (RDS instance) |
| **Backups** | Manual (file copy) | Automatic (PITR) | Automatic (snapshots) |
| **Read latency** | < 1 ms | 1-5 ms | 5-20 ms |
| **Write latency** | < 1 ms | 5-20 ms | 10-50 ms |

### When to Use SQLite

✅ **Use SQLite for:**
- Prototypes and MVPs (fast to implement)
- Services with < 1,000 requests/second
- Read-heavy workloads (analytics, reporting)
- Single-container applications (no horizontal scaling needed)
- Development and testing (no external dependencies)
- Services where data loss is acceptable (logs, caches, temporary data)
- Internal tools with < 10 concurrent users

✅ **SQLite is production-ready for:**
- Configuration databases
- Feature flag storage
- Local caching layers
- Embedded analytics
- Single-tenant SaaS applications (one DB per customer)

### When to Use DynamoDB

✅ **Use DynamoDB for:**
- High write throughput (> 100 writes/second)
- Multi-writer scenarios (multiple ECS tasks writing)
- Data size > 100 GB
- Need automatic backups and point-in-time recovery
- Global replication requirements
- Serverless architectures (Lambda + DynamoDB)

❌ **Don't use DynamoDB for:**
- Complex queries with JOINs (DynamoDB is NoSQL)
- Ad-hoc analytics (limited query capabilities)
- When you need SQL syntax
- When you want to avoid vendor lock-in

### When to Use PostgreSQL (RDS)

✅ **Use PostgreSQL for:**
- Complex relational data models
- Need for JOINs, foreign keys, constraints
- ACID transaction guarantees across tables
- Full-text search, JSON queries, advanced SQL features
- Data size > 100 GB with complex queries
- Need for database-level logic (stored procedures, triggers)

❌ **Don't use PostgreSQL for:**
- Simple key-value storage (overkill)
- Prototypes (slow setup, higher cost)
- Single-table CRUD operations (SQLite or DynamoDB is simpler)

### Graduation Path: SQLite → DynamoDB/PostgreSQL

**Start with SQLite:**
```python
# Day 1: Prototype with SQLite
conn = sqlite3.connect('/app/data/app.db')
conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)')
```

**Migrate to DynamoDB when:**
- SQLite database file exceeds 50 GB
- Seeing "database is locked" errors (write contention)
- Need to scale horizontally (multiple ECS tasks)
- Need automatic backups and disaster recovery

**Migration effort:**
- Update application code (SQLite → boto3)
- Create DynamoDB table via FSD YAML
- Run one-time data migration script
- Test in staging, deploy to production

**Migrate to PostgreSQL when:**
- Need complex JOINs across multiple tables
- Require foreign key constraints
- Need advanced SQL features (window functions, CTEs)
- Data integrity is critical (banking, healthcare)

## File-Based Persistence in Containers

### Container Filesystem is Ephemeral

**ECS Fargate containers are ephemeral** - when a task stops, all data in the container is lost.

```
Task Lifecycle:
START → [Container with empty filesystem] → STOP → [All data deleted]
```

**What triggers task restarts?**
- New deployment (code change)
- Health check failures
- Container crashes
- ECS maintenance (automatic restarts)
- Scaling down then up

### SQLite File Location Strategies

#### Strategy 1: Container-local (Ephemeral)

```python
# Store in container filesystem
db_path = '/app/data/app.db'
```

**Pros:**
- Simple, no additional infrastructure
- Fast (local disk I/O)
- Good for caches, temporary data, development

**Cons:**
- Data lost on every deployment or restart
- Each ECS task has separate database (no shared state)

**Use for:**
- Prototypes and demos
- Feature flag caches
- Session storage (with short TTL)
- Development/testing environments

#### Strategy 2: EFS Volume (Persistent)

```yaml
# FSD YAML with EFS dependency
dependencies:
  - type: aws_efs_file_system
    name: my-service-efs
    mountPoint: /mnt/efs
```

```python
# Store on EFS-mounted volume
db_path = '/mnt/efs/app.db'
```

**Pros:**
- Data persists across deployments and restarts
- Shared across multiple ECS tasks (read-only workloads)
- Automatic backups possible

**Cons:**
- Higher latency than local disk (network filesystem)
- Additional cost (~$0.30/GB/month)
- Concurrent writes cause "database is locked" errors

**Use for:**
- Production services with acceptable latency (100-500ms)
- Read-heavy workloads with single writer
- Services where data persistence is required

#### Strategy 3: In-Memory (Testing)

```python
# In-memory database (no persistence)
conn = sqlite3.connect(':memory:')
```

**Pros:**
- Fastest possible (RAM speed)
- Clean state for each test
- No disk I/O

**Cons:**
- Data lost when process exits
- Can't inspect database between test runs
- Memory usage grows with data size

**Use for:**
- Unit tests
- Integration tests
- Temporary scratch space

### Concurrency Considerations

**SQLite's concurrency model:**
- **Single writer, multiple readers** (default mode)
- Write operations are serialized (one at a time)
- Reads can happen concurrently with other reads
- Reads block writes, writes block everything

**Implications for ECS:**
- ✅ Single ECS task (desiredCount=1) + SQLite on EFS = Works fine
- ⚠️ Multiple ECS tasks (desiredCount>1) + SQLite on EFS = "database is locked" errors
- ✅ Multiple ECS tasks + separate SQLite files per task = Works, but no shared data

**If you need multiple writers:**
1. Use Write-Ahead Logging (WAL mode) - allows concurrent reads during writes
2. Use DynamoDB instead (unlimited concurrent writes)
3. Use PostgreSQL RDS (supports many concurrent writers)

## Limitations

### 1. Concurrent Writes

**Problem:**
```python
# Multiple goroutines/threads writing simultaneously
Thread 1: INSERT INTO users ...
Thread 2: INSERT INTO users ...  # "database is locked" error
```

**Solutions:**
- Enable WAL mode: `PRAGMA journal_mode=WAL;`
- Use connection pooling with single writer thread
- Retry with exponential backoff
- Migrate to DynamoDB/PostgreSQL

### 2. Database Size

**Practical limits:**
- **Maximum database size:** 281 TB (theoretical)
- **Recommended maximum:** 100 GB (performance degrades after)
- **Container storage:** ECS Fargate provides 20 GB ephemeral storage (default)

**If database exceeds limits:**
- Archive old data
- Partition into multiple databases
- Migrate to PostgreSQL or DynamoDB

### 3. Network Filesystem Performance

**SQLite on EFS is slower than local disk:**
- Local disk: < 1 ms per query
- EFS: 10-100 ms per query (network latency)

**Mitigation strategies:**
- Enable SQLite's memory-mapped I/O
- Use larger page size (PRAGMA page_size=8192)
- Cache frequently-read data in application memory
- Use EFS Provisioned Throughput mode

### 4. No Built-in Replication

**SQLite does not support:**
- Master-slave replication
- Multi-region replication
- Automatic failover

**If you need high availability:**
- Use DynamoDB (built-in replication)
- Use PostgreSQL RDS with Multi-AZ
- Implement application-level replication (complex)

## Testing with In-Memory Databases

### Why Use In-Memory Databases for Tests?

```python
# Production: file-based
conn = sqlite3.connect('/app/data/app.db')

# Tests: in-memory
conn = sqlite3.connect(':memory:')
```

**Benefits:**
- **Fast** - No disk I/O (10-100x faster tests)
- **Isolated** - Each test gets clean database
- **No cleanup** - Automatic teardown when connection closes
- **Parallel tests** - No file locking conflicts

### Pattern: Shared Schema, Separate Data

```python
# conftest.py (pytest)
import sqlite3
import pytest

@pytest.fixture
def db():
    """Provide in-memory database for each test"""
    conn = sqlite3.connect(':memory:')

    # Initialize schema
    conn.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()

    yield conn

    conn.close()

# test_users.py
def test_create_user(db):
    db.execute('INSERT INTO users (email) VALUES (?)', ('test@example.com',))
    db.commit()

    cursor = db.execute('SELECT email FROM users')
    assert cursor.fetchone()[0] == 'test@example.com'
```

### When NOT to Use In-Memory Tests

❌ **Don't use in-memory databases when:**
- Testing EFS-specific behavior
- Testing database migration scripts
- Performance testing (in-memory is unrealistically fast)
- Testing concurrent access patterns

✅ **Do use file-based test database when:**
- Need to inspect database between test runs
- Testing persistence behavior
- Debugging complex queries

## Summary

**SQLite is ideal for:**
- Prototypes and MVPs
- Services with < 1,000 QPS
- Read-heavy workloads
- Local development (no AWS credentials)
- Embedded databases in single-container apps

**Key limitations:**
- Single writer (concurrent writes cause locking)
- Recommended max size: 100 GB
- No built-in replication or high availability
- Slower on network filesystems (EFS)

**Migration triggers:**
- Database file > 50 GB
- Write contention ("database is locked")
- Need multi-region replication
- Query latency exceeds SLA

**Next:** See [patterns.md](patterns.md) for language-specific integration examples.
