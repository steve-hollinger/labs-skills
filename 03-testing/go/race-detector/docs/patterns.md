# Common Patterns - Race Detector

## Overview

This document covers common patterns for preventing race conditions and best practices for using the race detector.

## Pattern 1: Mutex Guard

### When to Use

Use mutex guards when you need to protect a group of related operations on shared data.

### Implementation

```go
type SafeStore struct {
    mu    sync.Mutex
    items map[string]Item
}

func (s *SafeStore) Get(key string) (Item, bool) {
    s.mu.Lock()
    defer s.mu.Unlock()
    item, ok := s.items[key]
    return item, ok
}

func (s *SafeStore) Set(key string, item Item) {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.items[key] = item
}

func (s *SafeStore) Delete(key string) {
    s.mu.Lock()
    defer s.mu.Unlock()
    delete(s.items, key)
}
```

### Example

```go
store := &SafeStore{items: make(map[string]Item)}

// Safe concurrent access
var wg sync.WaitGroup
for i := 0; i < 100; i++ {
    wg.Add(1)
    go func(id int) {
        defer wg.Done()
        store.Set(fmt.Sprintf("key%d", id), Item{ID: id})
    }(i)
}
wg.Wait()
```

### Pitfalls to Avoid

- Forgetting to unlock (always use defer)
- Holding locks too long (copy data out, then process)
- Nested locks without consistent ordering (can deadlock)

## Pattern 2: Read-Write Mutex

### When to Use

Use RWMutex when reads are much more frequent than writes.

### Implementation

```go
type Cache struct {
    mu    sync.RWMutex
    data  map[string]string
}

// Multiple readers can hold the lock simultaneously
func (c *Cache) Get(key string) (string, bool) {
    c.mu.RLock()
    defer c.mu.RUnlock()
    val, ok := c.data[key]
    return val, ok
}

// Writers get exclusive access
func (c *Cache) Set(key, value string) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.data[key] = value
}
```

### Pitfalls to Avoid

- Using RWMutex when writes are frequent (worse performance than Mutex)
- Upgrading read lock to write lock (not supported, will deadlock)

## Pattern 3: Atomic Operations

### When to Use

Use atomic operations for simple counters, flags, and pointer swaps.

### Implementation

```go
type Metrics struct {
    requestCount  int64
    errorCount    int64
    lastTimestamp int64
}

func (m *Metrics) RecordRequest() {
    atomic.AddInt64(&m.requestCount, 1)
    atomic.StoreInt64(&m.lastTimestamp, time.Now().UnixNano())
}

func (m *Metrics) RecordError() {
    atomic.AddInt64(&m.errorCount, 1)
}

func (m *Metrics) GetStats() (requests, errors int64) {
    return atomic.LoadInt64(&m.requestCount),
           atomic.LoadInt64(&m.errorCount)
}
```

### When to Prefer Atomic

```go
// Good for atomic: single value operations
atomic.AddInt64(&counter, 1)
atomic.LoadInt64(&value)
atomic.StoreInt64(&value, newVal)
atomic.CompareAndSwapInt64(&value, old, new)

// Bad for atomic: multiple related values
// Use mutex instead when you need to update multiple values atomically
```

## Pattern 4: Channel-Based State

### When to Use

Use channels when state management involves complex logic or when you want to avoid mutexes entirely.

### Implementation

```go
type Counter struct {
    inc   chan struct{}
    get   chan chan int
    stop  chan struct{}
}

func NewCounter() *Counter {
    c := &Counter{
        inc:  make(chan struct{}),
        get:  make(chan chan int),
        stop: make(chan struct{}),
    }
    go c.run()
    return c
}

func (c *Counter) run() {
    var count int
    for {
        select {
        case <-c.inc:
            count++
        case reply := <-c.get:
            reply <- count
        case <-c.stop:
            return
        }
    }
}

func (c *Counter) Inc() {
    c.inc <- struct{}{}
}

func (c *Counter) Get() int {
    reply := make(chan int)
    c.get <- reply
    return <-reply
}
```

### Pitfalls to Avoid

- Channel operations can be slower than mutexes
- Deadlock if channel is full and no receiver
- Resource leak if goroutine isn't properly stopped

## Pattern 5: sync.Once for Initialization

### When to Use

Use sync.Once for one-time initialization of shared resources.

### Implementation

```go
type Database struct {
    conn *sql.DB
    once sync.Once
    err  error
}

func (db *Database) Connect(dsn string) error {
    db.once.Do(func() {
        db.conn, db.err = sql.Open("postgres", dsn)
        if db.err == nil {
            db.err = db.conn.Ping()
        }
    })
    return db.err
}

func (db *Database) Query(q string) (*sql.Rows, error) {
    if db.conn == nil {
        return nil, errors.New("not connected")
    }
    return db.conn.Query(q)
}
```

### Example: Singleton Pattern

```go
var (
    instance *Config
    once     sync.Once
)

func GetConfig() *Config {
    once.Do(func() {
        instance = &Config{
            loaded: true,
            values: loadFromFile(),
        }
    })
    return instance
}
```

## Pattern 6: sync.Map for Concurrent Maps

### When to Use

Use sync.Map when:
- Keys are mostly written once but read many times
- Multiple goroutines read, write, and overwrite disjoint sets of keys

### Implementation

```go
type SessionStore struct {
    sessions sync.Map
}

func (s *SessionStore) Set(id string, session *Session) {
    s.sessions.Store(id, session)
}

func (s *SessionStore) Get(id string) (*Session, bool) {
    v, ok := s.sessions.Load(id)
    if !ok {
        return nil, false
    }
    return v.(*Session), true
}

func (s *SessionStore) Delete(id string) {
    s.sessions.Delete(id)
}

func (s *SessionStore) Count() int {
    count := 0
    s.sessions.Range(func(_, _ interface{}) bool {
        count++
        return true
    })
    return count
}
```

### When NOT to Use sync.Map

- When a regular map with mutex would suffice
- When you need to iterate frequently
- When type safety is important (sync.Map uses interface{})

## Anti-Patterns

### Anti-Pattern 1: Unlocking Without Lock

```go
// Bad: may unlock an unlocked mutex
func (s *Store) Get(key string) Item {
    defer s.mu.Unlock() // Might panic!
    s.mu.Lock()
    return s.items[key]
}

// Good: Lock then defer Unlock
func (s *Store) Get(key string) Item {
    s.mu.Lock()
    defer s.mu.Unlock()
    return s.items[key]
}
```

### Anti-Pattern 2: Lock Copying

```go
// Bad: mutex is copied
func process(s SafeStore) { // Value copy!
    s.mu.Lock()
    // ...
}

// Good: use pointer
func process(s *SafeStore) {
    s.mu.Lock()
    // ...
}
```

### Anti-Pattern 3: Goroutine Leak

```go
// Bad: goroutine may leak
func fetch(ctx context.Context) <-chan Result {
    ch := make(chan Result)
    go func() {
        result := expensiveOperation()
        ch <- result // May block forever if ctx cancelled
    }()
    return ch
}

// Good: respect context cancellation
func fetch(ctx context.Context) <-chan Result {
    ch := make(chan Result, 1) // Buffered
    go func() {
        result := expensiveOperation()
        select {
        case ch <- result:
        case <-ctx.Done():
        }
    }()
    return ch
}
```

### Anti-Pattern 4: Check-Then-Act Race

```go
// Bad: TOCTOU race
if cache.Contains(key) {
    return cache.Get(key) // Key might be deleted between calls!
}

// Good: atomic operation
value, ok := cache.Get(key)
if ok {
    return value
}
```

## Testing for Races

### Best Practices

```go
func TestConcurrentAccess(t *testing.T) {
    store := NewStore()
    var wg sync.WaitGroup

    // Run many concurrent operations
    for i := 0; i < 100; i++ {
        wg.Add(2)
        go func(id int) {
            defer wg.Done()
            store.Set(fmt.Sprintf("key%d", id), id)
        }(i)
        go func(id int) {
            defer wg.Done()
            store.Get(fmt.Sprintf("key%d", id))
        }(i)
    }

    wg.Wait()
}
```

### Running Race Tests

```bash
# Basic race detection
go test -race ./...

# Increase detection probability
go test -race -count=10 ./...

# With timeout for infinite loops
go test -race -timeout=30s ./...
```
