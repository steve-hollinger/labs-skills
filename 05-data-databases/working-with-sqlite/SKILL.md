---
name: working-with-sqlite
description: Use SQLite for simple services with file-based or in-memory databases, supporting Python, Node.js, and Go. Use when building prototypes, MVPs, or services with < 1,000 QPS and < 100 GB data.
tags: ['sqlite', 'database', 'python', 'nodejs', 'go', 'storage']
---

# Working with SQLite

## Quick Start

**Simple SQLite setup in 3 languages:**

```python
# Python (built-in sqlite3)
import sqlite3
conn = sqlite3.connect('/app/data/app.db')
conn.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)')
conn.commit()
```

```javascript
// Node.js (better-sqlite3)
const Database = require('better-sqlite3');
const db = new Database('/app/data/app.db');
db.exec('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)');
```

```go
// Go (database/sql + mattn/go-sqlite3)
import "database/sql"
import _ "github.com/mattn/go-sqlite3"

db, _ := sql.Open("sqlite3", "/app/data/app.db")
db.Exec("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)")
```

## Key Points

- **Use SQLite for simple services** - Best for < 1,000 QPS, < 100 GB data, read-heavy workloads
- **File location matters in containers** - `/tmp` is ephemeral (data lost), use mounted volumes or accept ephemeral storage for prototypes
- **SQLite is serverless** - No separate database process, no AWS credentials needed for local development
- **Works locally without AWS credentials** - Perfect for development and testing without cloud dependencies
- **Not suitable for multi-writer scenarios** - SQLite supports one writer at a time; use DynamoDB for concurrent writes

## Common Mistakes

1. **Using in-memory database in production** - `:memory:` database is lost when container restarts. Use file-based for persistence.
2. **Not initializing database schema on startup** - Container starts with empty database, causing "no such table" errors. Always run CREATE TABLE IF NOT EXISTS on startup.
3. **Storing .db file in wrong location** - `/tmp/app.db` disappears when container restarts. Use `/app/data/app.db` with volume mount or accept data loss.
4. **Treating SQLite like Postgres** - SQLite doesn't support concurrent writes. Use connection pooling carefully and handle "database is locked" errors.
5. **Not handling "database locked" errors** - Multiple goroutines/threads writing simultaneously can lock database. Retry with exponential backoff or use write-ahead logging (WAL mode).

## More Detail

- [docs/concepts.md](docs/concepts.md) - SQLite fundamentals, use cases, limitations
- [docs/patterns.md](docs/patterns.md) - Integration patterns for Python, Node.js, and Go
