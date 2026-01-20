---
name: migrating-to-swift-6
description: This skill teaches Swift 6 concurrency migration including Sendable types, actors, and async/await patterns. Use when adopting strict concurrency or fixing Sendable warnings.
---

# Swift 6 Concurrency

## Quick Start
```swift
// Before: Completion handler
func fetchData(completion: @escaping (Data) -> Void) { ... }

// After: Async/await
func fetchData() async throws -> Data {
    let (data, _) = try await URLSession.shared.data(from: url)
    return data
}

// Actor for shared mutable state
actor DataStore {
    private var cache: [String: Data] = [:]
    func store(_ data: Data, for key: String) { cache[key] = data }
}
```

## Commands
```bash
make setup      # swift package resolve
make examples   # Run all examples
make example-1  # Basic async/await
make example-2  # Actors and isolation
make example-3  # Sendable patterns
make test       # swift test
```

## Key Points
- Sendable conformance
- Actor isolation
- @MainActor for UI
- Async/await migration

## Common Mistakes
1. **Missing Sendable** - Classes with mutable state need explicit handling; prefer structs or actors
2. **Blocking main actor** - Use `Task.detached` for CPU-intensive work

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
