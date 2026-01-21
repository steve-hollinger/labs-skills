# Common Patterns

## Pattern 1: Minimal API (Hello World with /health)

**When to Use:** Starting a new service, learning deployment basics, testing infrastructure.

### Python (FastAPI)

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Run: uvicorn main:app --host 0.0.0.0 --port 8000
```

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```txt
# requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
```

### Node.js (Express)

```javascript
// app.js
const express = require('express');
const app = express();
const PORT = 8000;

app.get('/', (req, res) => {
  res.json({ message: 'Hello World' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
```

```dockerfile
# Dockerfile
FROM node:20-slim

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY app.js .

# Run as non-root user
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:8000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Start application
CMD ["node", "app.js"]
```

```json
// package.json
{
  "name": "my-service",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.2"
  }
}
```

### Go

```go
// main.go
package main

import (
    "encoding/json"
    "log"
    "net/http"
)

func main() {
    http.HandleFunc("/", handleRoot)
    http.HandleFunc("/health", handleHealth)

    log.Println("Server starting on :8000")
    if err := http.ListenAndServe(":8000", nil); err != nil {
        log.Fatal(err)
    }
}

func handleRoot(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{
        "message": "Hello World",
    })
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{
        "status": "healthy",
    })
}
```

```dockerfile
# Dockerfile
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY main.go .
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

FROM alpine:latest

# Install curl for health check
RUN apk --no-cache add curl

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/main .

# Run as non-root user
RUN adduser -D -u 1000 appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["./main"]
```

**Pitfalls:**
- Missing `/health` endpoint → ECS health checks fail
- Not running as non-root user → ECS security policy rejects container
- Health check endpoint returns 500 or doesn't respond → infinite restart loop

---

## Pattern 2: API + SQLite Database

**When to Use:** Simple CRUD operations, prototypes, services with < 1,000 QPS.

### Python (FastAPI + SQLite)

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from contextlib import contextmanager

app = FastAPI()
DB_PATH = "/app/data/app.db"  # Use volume mount for persistence

class Item(BaseModel):
    id: int | None = None
    name: str
    description: str

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@app.on_event("startup")
def init_db():
    """Initialize database schema on startup"""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        """)
        conn.commit()

@app.get("/health")
def health_check():
    """Health check with database connectivity test"""
    try:
        with get_db() as conn:
            conn.execute("SELECT 1").fetchone()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503

@app.post("/items")
def create_item(item: Item):
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO items (name, description) VALUES (?, ?)",
            (item.name, item.description)
        )
        conn.commit()
        return {"id": cursor.lastrowid, **item.dict()}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Item not found")
        return dict(row)

@app.get("/items")
def list_items():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM items").fetchall()
        return [dict(row) for row in rows]
```

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install curl for health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Create data directory for SQLite
RUN mkdir -p /app/data && chmod 755 /app/data

# Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Node.js (Express + better-sqlite3)

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
db.exec(`
  CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
  )
`);

app.get('/health', (req, res) => {
  try {
    db.prepare('SELECT 1').get();
    res.json({ status: 'healthy', database: 'connected' });
  } catch (err) {
    res.status(503).json({ status: 'unhealthy', error: err.message });
  }
});

app.post('/items', (req, res) => {
  const { name, description } = req.body;
  const stmt = db.prepare('INSERT INTO items (name, description) VALUES (?, ?)');
  const result = stmt.run(name, description);
  res.json({ id: result.lastInsertRowid, name, description });
});

app.get('/items/:id', (req, res) => {
  const stmt = db.prepare('SELECT * FROM items WHERE id = ?');
  const item = stmt.get(req.params.id);
  if (!item) {
    return res.status(404).json({ error: 'Item not found' });
  }
  res.json(item);
});

app.get('/items', (req, res) => {
  const stmt = db.prepare('SELECT * FROM items');
  const items = stmt.all();
  res.json(items);
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
```

### Go (database/sql + mattn/go-sqlite3)

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

type Item struct {
    ID          int    `json:"id"`
    Name        string `json:"name"`
    Description string `json:"description"`
}

func main() {
    var err error
    db, err = sql.Open("sqlite3", "/app/data/app.db")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    // Initialize schema
    _, err = db.Exec(`
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    `)
    if err != nil {
        log.Fatal(err)
    }

    http.HandleFunc("/health", handleHealth)
    http.HandleFunc("/items", handleItems)

    log.Println("Server starting on :8000")
    log.Fatal(http.ListenAndServe(":8000", nil))
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    // Test database connection
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

func handleItems(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")

    switch r.Method {
    case "POST":
        var item Item
        if err := json.NewDecoder(r.Body).Decode(&item); err != nil {
            w.WriteHeader(http.StatusBadRequest)
            json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
            return
        }

        result, err := db.Exec("INSERT INTO items (name, description) VALUES (?, ?)",
            item.Name, item.Description)
        if err != nil {
            w.WriteHeader(http.StatusInternalServerError)
            json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
            return
        }

        id, _ := result.LastInsertId()
        item.ID = int(id)
        json.NewEncoder(w).Encode(item)

    case "GET":
        rows, err := db.Query("SELECT id, name, description FROM items")
        if err != nil {
            w.WriteHeader(http.StatusInternalServerError)
            json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
            return
        }
        defer rows.Close()

        var items []Item
        for rows.Next() {
            var item Item
            if err := rows.Scan(&item.ID, &item.Name, &item.Description); err != nil {
                continue
            }
            items = append(items, item)
        }
        json.NewEncoder(w).Encode(items)
    }
}
```

**Pitfalls:**
- Storing SQLite file in `/tmp` → Data lost on restart
- Not initializing schema on startup → "no such table" errors
- Not testing database connection in `/health` → Unhealthy app reports as healthy
- Using in-memory database (`:memory:`) in production → All data lost on restart

---

## Pattern 3: Local Development with docker-compose

**When to Use:** Before deploying to ECS, to catch configuration issues early.

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SERVICE_NAME=my-service
      - ENVIRONMENT=local
    volumes:
      - ./data:/app/data  # Persist SQLite database
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
```

**Local testing workflow:**

```bash
# Build and start
docker-compose up --build

# Test health endpoint
curl http://localhost:8000/health

# Test API
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Item", "description": "Testing locally"}'

# View logs
docker-compose logs -f

# Stop and clean up
docker-compose down
```

**Benefits:**
- Catches Dockerfile errors before pushing to ECR
- Tests health check configuration
- Validates environment variable setup
- Fast iteration (no AWS deployment wait time)

---

## Pattern 4: FSD YAML Configuration

**When to Use:** Deploying to ECS for the first time, configuring resources.

```yaml
# my-service.yml
apiVersion: fsd/v1
kind: Service

metadata:
  name: my-service
  pack: my-pack
  owner: platform-team

service:
  type: ecs
  port: 8000

  # Health check (must match application endpoint)
  healthCheck:
    path: /health
    interval: 30
    timeout: 5
    healthyThreshold: 2
    unhealthyThreshold: 3

  # Resource allocation
  resources:
    cpu: 512        # 0.5 vCPU (start small)
    memory: 1024    # 1 GB

  # Auto-scaling configuration
  autoScaling:
    minCount: 2     # High availability
    maxCount: 10
    targetCPU: 70   # Scale when CPU > 70%

  # Environment variables
  environment:
    SERVICE_NAME: my-service
    ENVIRONMENT: ${ENV}
    LOG_LEVEL: info

  # Secrets (AWS Secrets Manager)
  secrets:
    - name: API_KEY
      valueFrom: arn:aws:secretsmanager:us-east-1:123456789012:secret:my-api-key

# Dependencies (optional)
dependencies:
  - type: aws_dynamodb_table  # Example: If migrating from SQLite
    name: my-service-data
    attributes:
      - name: id
        type: S
    keySchema:
      - attributeName: id
        keyType: HASH
```

**Deploy with FSD CLI:**

```bash
# Staging deployment
fsd deploy my-service.yml --env staging

# Production deployment
fsd deploy my-service.yml --env prod

# View deployment status
fsd status my-service --env staging
```

---

## Pattern 5: GitHub Actions Deployment Workflow

**When to Use:** Automating deployments on every push to staging or main branch.

```yaml
# .github/workflows/deploy.yml
name: Deploy to ECS

on:
  push:
    branches:
      - staging
      - main

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: my-service
  SERVICE_NAME: my-service

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push image to Amazon ECR
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

      - name: Install FSD CLI
        run: |
          curl -fsSL https://fsd.fetch.com/install.sh | sh
          echo "$HOME/.fsd/bin" >> $GITHUB_PATH

      - name: Deploy to staging
        if: github.ref == 'refs/heads/staging'
        run: |
          fsd deploy ${{ env.SERVICE_NAME }}.yml --env staging

      - name: Deploy to production
        if: github.ref == 'refs/heads/main'
        run: |
          fsd deploy ${{ env.SERVICE_NAME }}.yml --env prod

      - name: Notify on failure
        if: failure()
        run: |
          echo "Deployment failed! Check logs."
```

**Required GitHub Secrets:**
- `AWS_ACCESS_KEY_ID` - IAM user with ECR and ECS permissions
- `AWS_SECRET_ACCESS_KEY` - IAM user secret key

**Workflow triggers:**
- Push to `staging` branch → Deploy to staging environment
- Push to `main` branch → Deploy to production environment

---

## Pattern 6: Troubleshooting Deployment Failures

**When to Use:** Deployment hangs, tasks fail, or service is unhealthy.

### Step 1: Check ECS Console

```bash
# Get service status
aws ecs describe-services \
  --cluster my-cluster \
  --services my-service \
  --region us-east-1

# Check task failure reason
aws ecs describe-tasks \
  --cluster my-cluster \
  --tasks <task-id> \
  --region us-east-1
```

**Common task stopped reasons:**
- `Essential container in task exited` → Application crashed (check logs)
- `Task failed ELB health checks` → `/health` endpoint not responding
- `OutOfMemoryError: Container killed` → Insufficient memory allocation
- `CannotPullContainerError` → ECR permissions or image not found

### Step 2: Check CloudWatch Logs

```bash
# View logs for specific task
aws logs tail /ecs/my-service --follow --region us-east-1

# Search for errors
aws logs filter-pattern /ecs/my-service --filter-pattern "ERROR" --region us-east-1
```

**Look for:**
- Application startup errors (missing environment variables, port conflicts)
- Health check failures (endpoint not implemented, returns 500)
- Database connection errors (SQLite file permissions)

### Step 3: Test Locally with docker-compose

```bash
# Run the exact same container locally
docker-compose up

# Test health endpoint
curl http://localhost:8000/health

# Check logs for errors
docker-compose logs
```

### Step 4: Verify Health Check Configuration

**Common mismatches:**

| FSD YAML | Application | Result |
|----------|-------------|--------|
| `path: /health` | `@app.get("/health")` | ✅ Works |
| `path: /health` | `@app.get("/healthz")` | ❌ Fails |
| `path: /health` | Missing endpoint | ❌ Fails |
| `port: 8000` | `app.listen(3000)` | ❌ Fails |

**Fix:** Ensure FSD YAML matches application configuration exactly.

### Step 5: Check IAM Permissions

```bash
# Test ECR access
aws ecr describe-repositories --region us-east-1

# Test Secrets Manager access (if using secrets)
aws secretsmanager get-secret-value \
  --secret-id my-api-key \
  --region us-east-1
```

**Common IAM issues:**
- Task execution role can't pull from ECR
- Task role can't read from Secrets Manager
- Missing permissions for CloudWatch Logs

### When to Escalate

Ask for help if:
- Deployment has been failing for > 30 minutes
- CloudWatch Logs show unfamiliar errors
- Health checks pass locally but fail in ECS
- FSD CLI returns cryptic errors
- No obvious mismatch between config and code

**Include in your request:**
- Service name and environment
- FSD YAML configuration
- CloudWatch Logs excerpt (last 50 lines)
- Task stopped reason from ECS
- What you've already tried

---

## Summary

**Core patterns for first deployment:**
1. Minimal API with `/health` → Foundation for all services
2. API + SQLite → Adds data persistence
3. docker-compose → Local testing before deployment
4. FSD YAML → Infrastructure configuration
5. GitHub Actions → Automated CI/CD pipeline
6. Troubleshooting → Debug deployment failures

**Next steps:**
- See `understanding-ecs-resources` for resource sizing
- See `working-with-sqlite` for database patterns
- See `troubleshooting-ecs-deployments` for advanced debugging
