# Common Patterns

## Pattern 1: Python + FastAPI + SQLite (sqlite3)

**When to Use:** Simple CRUD operations, prototypes, Python services without heavy ORM needs.

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from contextlib import contextmanager
from typing import List

app = FastAPI()
DB_PATH = "/app/data/app.db"

class User(BaseModel):
    id: int | None = None
    email: str
    name: str

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
    finally:
        conn.close()

@app.on_event("startup")
def init_db():
    """Initialize database schema on startup"""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL
            )
        ''')
        conn.commit()
    print("Database initialized")

@app.get("/health")
def health_check():
    """Health check with database connectivity test"""
    try:
        with get_db() as conn:
            conn.execute("SELECT 1").fetchone()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503

@app.post("/users", response_model=User, status_code=201)
def create_user(user: User):
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "INSERT INTO users (email, name) VALUES (?, ?)",
                (user.email, user.name)
            )
            conn.commit()
            return User(id=cursor.lastrowid, email=user.email, name=user.name)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(row)

@app.get("/users", response_model=List[User])
def list_users(limit: int = 100):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM users LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: User):
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET email = ?, name = ? WHERE id = ?",
            (user.email, user.name, user_id)
        )
        conn.commit()
        if conn.total_changes == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return User(id=user_id, email=user.email, name=user.name)

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        if conn.total_changes == 0:
            raise HTTPException(status_code=404, detail="User not found")
```

**Pitfalls:**
- Not using context manager → connection leaks
- Not handling `sqlite3.IntegrityError` → cryptic 500 errors
- Fetching without LIMIT → memory exhaustion on large tables

---

## Pattern 2: Python + FastAPI + SQLAlchemy

**When to Use:** Need ORM features (relationships, migrations), complex data models.

```python
# database.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:////app/data/app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite specific
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

# Initialize tables
Base.metadata.create_all(bind=engine)
```

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, User
from pydantic import BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    email: str
    name: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str

    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(email=user.email, name=user.name)
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**Pitfalls:**
- Forgetting `check_same_thread=False` → cryptic threading errors
- Not calling `db.commit()` → changes not persisted
- Not handling session cleanup → connection leaks

---

## Pattern 3: Node.js + Express + better-sqlite3

**When to Use:** Node.js services, need synchronous database API (simpler than async).

```javascript
// app.js
const express = require('express');
const Database = require('better-sqlite3');

const app = express();
const PORT = 8000;
const DB_PATH = '/app/data/app.db';

app.use(express.json());

// Initialize database
const db = new Database(DB_PATH);

// Enable WAL mode for better concurrency
db.pragma('journal_mode = WAL');

// Initialize schema
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
  )
`);

// Prepared statements (reusable, more efficient)
const insertUser = db.prepare('INSERT INTO users (email, name) VALUES (?, ?)');
const getUserById = db.prepare('SELECT * FROM users WHERE id = ?');
const getAllUsers = db.prepare('SELECT * FROM users LIMIT ?');
const updateUser = db.prepare('UPDATE users SET email = ?, name = ? WHERE id = ?');
const deleteUser = db.prepare('DELETE FROM users WHERE id = ?');

// Health check
app.get('/health', (req, res) => {
  try {
    db.prepare('SELECT 1').get();
    res.json({ status: 'healthy', database: 'connected' });
  } catch (err) {
    res.status(503).json({ status: 'unhealthy', error: err.message });
  }
});

// Create user
app.post('/users', (req, res) => {
  const { email, name } = req.body;

  if (!email || !name) {
    return res.status(400).json({ error: 'Email and name are required' });
  }

  try {
    const result = insertUser.run(email, name);
    res.status(201).json({ id: result.lastInsertRowid, email, name });
  } catch (err) {
    if (err.code === 'SQLITE_CONSTRAINT') {
      return res.status(400).json({ error: 'Email already exists' });
    }
    res.status(500).json({ error: err.message });
  }
});

// Get user
app.get('/users/:id', (req, res) => {
  const user = getUserById.get(req.params.id);
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  res.json(user);
});

// List users
app.get('/users', (req, res) => {
  const limit = parseInt(req.query.limit) || 100;
  const users = getAllUsers.all(limit);
  res.json(users);
});

// Update user
app.put('/users/:id', (req, res) => {
  const { email, name } = req.body;
  const result = updateUser.run(email, name, req.params.id);

  if (result.changes === 0) {
    return res.status(404).json({ error: 'User not found' });
  }

  res.json({ id: parseInt(req.params.id), email, name });
});

// Delete user
app.delete('/users/:id', (req, res) => {
  const result = deleteUser.run(req.params.id);

  if (result.changes === 0) {
    return res.status(404).json({ error: 'User not found' });
  }

  res.status(204).send();
});

// Graceful shutdown
process.on('SIGTERM', () => {
  db.close();
  process.exit(0);
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
```

```json
// package.json
{
  "name": "my-service",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.2",
    "better-sqlite3": "^9.2.2"
  }
}
```

**Pitfalls:**
- Not using prepared statements → SQL injection risk, slower performance
- Not enabling WAL mode → "database is locked" errors under load
- Not handling SQLITE_CONSTRAINT error → generic 500 errors
- Not closing database on shutdown → file lock issues

---

## Pattern 4: Go + database/sql + mattn/go-sqlite3

**When to Use:** Go services, need standard database/sql interface.

```go
// main.go
package main

import (
    "database/sql"
    "encoding/json"
    "log"
    "net/http"
    "strconv"

    _ "github.com/mattn/go-sqlite3"
)

var db *sql.DB

type User struct {
    ID    int    `json:"id"`
    Email string `json:"email"`
    Name  string `json:"name"`
}

func main() {
    var err error
    db, err = sql.Open("sqlite3", "file:/app/data/app.db?cache=shared&mode=rwc")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    // Set connection pool settings
    db.SetMaxOpenConns(1) // SQLite supports single writer

    // Enable WAL mode for better concurrency
    if _, err := db.Exec("PRAGMA journal_mode=WAL"); err != nil {
        log.Fatal(err)
    }

    // Initialize schema
    if err := initSchema(); err != nil {
        log.Fatal(err)
    }

    http.HandleFunc("/health", handleHealth)
    http.HandleFunc("/users", handleUsers)
    http.HandleFunc("/users/", handleUser)

    log.Println("Server starting on :8000")
    log.Fatal(http.ListenAndServe(":8000", nil))
}

func initSchema() error {
    _, err := db.Exec(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        )
    `)
    return err
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    if err := db.Ping(); err != nil {
        w.WriteHeader(http.StatusServiceUnavailable)
        json.NewEncoder(w).Encode(map[string]string{
            "status": "unhealthy",
            "error":  err.Error(),
        })
        return
    }

    json.NewEncoder(w).Encode(map[string]string{
        "status":   "healthy",
        "database": "connected",
    })
}

func handleUsers(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    switch r.Method {
    case "POST":
        var user User
        if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
            http.Error(w, err.Error(), http.StatusBadRequest)
            return
        }

        result, err := db.Exec(
            "INSERT INTO users (email, name) VALUES (?, ?)",
            user.Email, user.Name,
        )
        if err != nil {
            http.Error(w, "Email already exists", http.StatusBadRequest)
            return
        }

        id, _ := result.LastInsertId()
        user.ID = int(id)
        w.WriteHeader(http.StatusCreated)
        json.NewEncoder(w).Encode(user)

    case "GET":
        rows, err := db.Query("SELECT id, email, name FROM users LIMIT 100")
        if err != nil {
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        }
        defer rows.Close()

        var users []User
        for rows.Next() {
            var user User
            if err := rows.Scan(&user.ID, &user.Email, &user.Name); err != nil {
                continue
            }
            users = append(users, user)
        }

        if users == nil {
            users = []User{}
        }
        json.NewEncoder(w).Encode(users)
    }
}

func handleUser(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    // Extract ID from path
    idStr := r.URL.Path[len("/users/"):]
    id, err := strconv.Atoi(idStr)
    if err != nil {
        http.Error(w, "Invalid user ID", http.StatusBadRequest)
        return
    }

    switch r.Method {
    case "GET":
        var user User
        err := db.QueryRow(
            "SELECT id, email, name FROM users WHERE id = ?", id,
        ).Scan(&user.ID, &user.Email, &user.Name)

        if err == sql.ErrNoRows {
            http.Error(w, "User not found", http.StatusNotFound)
            return
        } else if err != nil {
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        }

        json.NewEncoder(w).Encode(user)

    case "DELETE":
        result, err := db.Exec("DELETE FROM users WHERE id = ?", id)
        if err != nil {
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        }

        rowsAffected, _ := result.RowsAffected()
        if rowsAffected == 0 {
            http.Error(w, "User not found", http.StatusNotFound)
            return
        }

        w.WriteHeader(http.StatusNoContent)
    }
}
```

```go
// go.mod
module my-service

go 1.21

require github.com/mattn/go-sqlite3 v1.14.19
```

**Pitfalls:**
- Not setting `SetMaxOpenConns(1)` → "database is locked" errors
- Not deferring `rows.Close()` → connection leaks
- Not handling `sql.ErrNoRows` → generic 500 instead of 404
- Not enabling WAL mode → poor concurrency

---

## Pattern 5: Database Initialization on Startup

**When to Use:** Every production service (ensures schema exists before handling requests).

### Python (with migration versioning)

```python
# migrations.py
import sqlite3
from contextlib import contextmanager

DB_PATH = "/app/data/app.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def get_schema_version(conn):
    """Get current schema version"""
    try:
        cursor = conn.execute("SELECT version FROM schema_version LIMIT 1")
        row = cursor.fetchone()
        return row[0] if row else 0
    except sqlite3.OperationalError:
        return 0

def set_schema_version(conn, version):
    """Set schema version"""
    conn.execute("DELETE FROM schema_version")
    conn.execute("INSERT INTO schema_version (version) VALUES (?)", (version,))
    conn.commit()

def migrate_to_v1(conn):
    """Initial schema"""
    conn.execute('''
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

def migrate_to_v2(conn):
    """Add indexes"""
    conn.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    conn.commit()

def migrate_to_v3(conn):
    """Add new column"""
    conn.execute('ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1')
    conn.commit()

MIGRATIONS = {
    1: migrate_to_v1,
    2: migrate_to_v2,
    3: migrate_to_v3,
}

def run_migrations():
    """Run all pending migrations"""
    with get_db() as conn:
        current_version = get_schema_version(conn)
        target_version = max(MIGRATIONS.keys())

        if current_version >= target_version:
            print(f"Database schema is up to date (v{current_version})")
            return

        print(f"Migrating database from v{current_version} to v{target_version}")

        for version in range(current_version + 1, target_version + 1):
            if version in MIGRATIONS:
                print(f"Applying migration v{version}...")
                MIGRATIONS[version](conn)
                set_schema_version(conn, version)

        print("Migrations complete")

# main.py
from fastapi import FastAPI
from migrations import run_migrations

app = FastAPI()

@app.on_event("startup")
def startup():
    run_migrations()
```

### Node.js (simple version)

```javascript
// migrations.js
const Database = require('better-sqlite3');

function runMigrations(dbPath) {
  const db = new Database(dbPath);

  // Enable WAL mode
  db.pragma('journal_mode = WAL');

  // Create schema_version table
  db.exec(`
    CREATE TABLE IF NOT EXISTS schema_version (
      version INTEGER NOT NULL
    )
  `);

  // Get current version
  let currentVersion = 0;
  try {
    const row = db.prepare('SELECT version FROM schema_version').get();
    currentVersion = row ? row.version : 0;
  } catch (err) {
    // Table exists but is empty
  }

  const migrations = [
    // Migration 1: Initial schema
    (db) => {
      db.exec(`
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          email TEXT UNIQUE NOT NULL,
          name TEXT NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
      `);
    },
    // Migration 2: Add indexes
    (db) => {
      db.exec('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)');
    },
  ];

  // Run pending migrations
  for (let i = currentVersion; i < migrations.length; i++) {
    console.log(`Running migration ${i + 1}...`);
    migrations[i](db);

    // Update version
    db.prepare('DELETE FROM schema_version').run();
    db.prepare('INSERT INTO schema_version (version) VALUES (?)').run(i + 1);
  }

  console.log(`Database schema at version ${migrations.length}`);
  db.close();
}

module.exports = { runMigrations };
```

**Pitfalls:**
- Not version-tracking migrations → can't evolve schema safely
- Running migrations in application code instead of startup → race conditions
- Not using transactions → partial migrations leave database in broken state

---

## Pattern 6: Docker Volume for Persistence

**When to Use:** Need SQLite data to persist across container restarts (EFS or local development).

### docker-compose.yml (Local Development)

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data  # Mount local directory for SQLite database
    environment:
      - SERVICE_NAME=my-service
      - ENVIRONMENT=local
```

**Benefits:**
- Database persists across `docker-compose down` and `up`
- Can inspect SQLite file locally with `sqlite3 ./data/app.db`
- Fast iteration (no data loss between restarts)

### FSD YAML with EFS (Production)

```yaml
# my-service.yml
apiVersion: fsd/v1
kind: Service

metadata:
  name: my-service
  pack: my-pack

service:
  type: ecs
  port: 8000
  healthCheck:
    path: /health

  resources:
    cpu: 512
    memory: 1024

  # Mount EFS for persistent storage
  volumes:
    - name: efs-storage
      efs:
        fileSystemId: fs-12345678  # Reference to EFS dependency
        rootDirectory: /
      mountPath: /app/data

dependencies:
  - type: aws_efs_file_system
    name: my-service-efs
    encrypted: true
    performanceMode: generalPurpose
```

**Important considerations:**
- EFS adds network latency (10-100ms per query vs < 1ms local disk)
- Multiple ECS tasks writing to same SQLite file → "database is locked" errors
- Use WAL mode for better concurrency: `PRAGMA journal_mode=WAL`
- Consider DynamoDB if need true multi-writer support

---

## Pattern 7: In-Memory Database for Testing

**When to Use:** Unit tests, integration tests, fast test suites.

### Python (pytest)

```python
# conftest.py
import pytest
import sqlite3

@pytest.fixture
def db():
    """Provide in-memory database for each test"""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row

    # Initialize schema
    conn.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    conn.commit()

    yield conn

    conn.close()

# test_users.py
def test_create_user(db):
    cursor = db.execute(
        'INSERT INTO users (email, name) VALUES (?, ?)',
        ('test@example.com', 'Test User')
    )
    db.commit()

    assert cursor.lastrowid == 1

def test_duplicate_email(db):
    db.execute('INSERT INTO users (email, name) VALUES (?, ?)', ('a@b.com', 'User 1'))
    db.commit()

    with pytest.raises(sqlite3.IntegrityError):
        db.execute('INSERT INTO users (email, name) VALUES (?, ?)', ('a@b.com', 'User 2'))
        db.commit()
```

### Node.js (Jest)

```javascript
// db.test.js
const Database = require('better-sqlite3');

describe('User database', () => {
  let db;

  beforeEach(() => {
    // Create in-memory database for each test
    db = new Database(':memory:');

    // Initialize schema
    db.exec(`
      CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL
      )
    `);
  });

  afterEach(() => {
    db.close();
  });

  test('creates user', () => {
    const stmt = db.prepare('INSERT INTO users (email, name) VALUES (?, ?)');
    const result = stmt.run('test@example.com', 'Test User');

    expect(result.lastInsertRowid).toBe(1);
  });

  test('rejects duplicate email', () => {
    db.prepare('INSERT INTO users (email, name) VALUES (?, ?)').run('a@b.com', 'User 1');

    expect(() => {
      db.prepare('INSERT INTO users (email, name) VALUES (?, ?)').run('a@b.com', 'User 2');
    }).toThrow();
  });
});
```

**Benefits:**
- 10-100x faster than file-based tests
- Isolated (each test gets clean database)
- No cleanup needed (automatic)
- Can run tests in parallel

**Pitfalls:**
- In-memory is faster than production (don't use for performance tests)
- Can't inspect database between test runs
- Doesn't test EFS-specific behavior

---

## Summary

**Key patterns:**
1. **Python + sqlite3** - Simple, built-in, good for prototypes
2. **Python + SQLAlchemy** - ORM features, complex data models
3. **Node.js + better-sqlite3** - Synchronous API, prepared statements
4. **Go + database/sql** - Standard interface, connection pooling
5. **Database initialization** - Schema versioning, safe migrations
6. **Docker volumes** - Persistence in development and production
7. **In-memory testing** - Fast, isolated test suites

**Next steps:**
- See `deploying-your-first-service` for end-to-end deployment
- See `understanding-ecs-resources` for resource sizing
- See `dynamodb-schema` when ready to graduate from SQLite
