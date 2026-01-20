# Swift 6 Concurrency

A hands-on skill for migrating Swift code to Swift 6's strict concurrency model.

## Prerequisites

- Xcode 16+ (Swift 6)
- macOS 14+
- Understanding of completion handlers and GCD

## Quick Start

```bash
# Install dependencies
make setup

# Run examples
make examples

# Run tests
make test
```

## Project Structure

```
swift-6-concurrency/
├── Package.swift              # Swift 6 language mode
├── SKILL.md                   # AI assistant guidance
├── Makefile                   # Build commands
├── Sources/
│   ├── Swift6Concurrency/     # Main module
│   │   ├── Swift6Concurrency.swift
│   │   ├── DataStore.swift    # Actor example
│   │   └── NetworkClient.swift # Async/await example
│   └── Examples/              # Runnable examples
│       ├── Example1/          # Basic async/await
│       ├── Example2/          # Actor isolation
│       └── Example3/          # Sendable patterns
├── Tests/
│   └── Swift6ConcurrencyTests/
├── docs/
│   ├── concepts.md            # Concurrency concepts
│   └── patterns.md            # Migration patterns
└── exercises/
    ├── exercise_1.md          # Convert completion handlers
    └── solutions/
```

## Learning Path

1. **Read** `SKILL.md` for quick overview
2. **Run** examples with `make examples`
3. **Study** `docs/concepts.md` for theory
4. **Practice** migration patterns in `exercises/`
5. **Verify** understanding with `make test`

## Examples

### Example 1: Basic Async/Await
Convert completion handlers to async/await pattern.

### Example 2: Actor Isolation
Protect shared mutable state with actors.

### Example 3: Sendable Patterns
Make types safe to share across concurrency domains.

## Key Concepts

- **Async/Await**: Structured way to write asynchronous code
- **Actors**: Reference types with isolated mutable state
- **Sendable**: Protocol marking types safe to share
- **@MainActor**: Ensures code runs on main thread

## Resources

- [Swift Concurrency](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/)
- [WWDC 2024: Migrate to Swift 6](https://developer.apple.com/videos/play/wwdc2024/10169/)
- [SE-0302: Sendable and @Sendable](https://github.com/apple/swift-evolution/blob/main/proposals/0302-concurrent-value-and-concurrent-closures.md)
