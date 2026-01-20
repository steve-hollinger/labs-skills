# Core Concepts

## Overview

Swift 6 introduces strict concurrency checking to eliminate data races at compile time. This document covers the key concepts you need to understand for migration.

## Concept 1: Sendable

### What It Is

`Sendable` is a protocol that marks types as safe to share across concurrency domains (actors, tasks, threads).

### Why It Matters

In Swift 6, the compiler checks that values crossing actor boundaries are `Sendable`. Non-Sendable types cause compile errors when passed between actors or tasks.

### How It Works

```swift
// Structs with Sendable properties are implicitly Sendable
struct UserData: Sendable {
    let id: String
    let name: String
}

// Classes need explicit conformance and must be:
// 1. Final
// 2. Have only immutable (let) stored properties of Sendable types
final class Config: Sendable {
    let apiKey: String
    let timeout: Int

    init(apiKey: String, timeout: Int) {
        self.apiKey = apiKey
        self.timeout = timeout
    }
}

// Enums with Sendable associated values are Sendable
enum Result<T: Sendable>: Sendable {
    case success(T)
    case failure(Error)
}
```

## Concept 2: Actors

### What It Is

Actors are reference types that protect their mutable state by ensuring only one task accesses it at a time.

### Why It Matters

Before actors, protecting shared state required manual synchronization (locks, queues) which is error-prone. Actors provide compiler-enforced isolation.

### How It Works

```swift
actor BankAccount {
    private var balance: Double = 0

    func deposit(_ amount: Double) {
        balance += amount  // Safe - actor ensures exclusive access
    }

    func withdraw(_ amount: Double) -> Bool {
        guard balance >= amount else { return false }
        balance -= amount
        return true
    }

    func getBalance() -> Double {
        balance
    }
}

// Usage requires await for cross-actor calls
let account = BankAccount()
await account.deposit(100)  // Crosses actor boundary
let success = await account.withdraw(50)
```

### Actor Isolation

- Code inside an actor is "isolated" to that actor
- External calls must use `await` (potential suspension point)
- Only `nonisolated` members can be called synchronously

```swift
actor DataStore {
    private var data: [String: String] = [:]

    // Isolated - requires await from outside
    func store(_ value: String, key: String) {
        data[key] = value
    }

    // Nonisolated - can be called without await
    nonisolated var description: String {
        "DataStore instance"
    }
}
```

## Concept 3: @MainActor

### What It Is

`@MainActor` is a global actor that represents the main thread. Code marked with `@MainActor` is guaranteed to run on the main thread.

### Why It Matters

UI updates must happen on the main thread. `@MainActor` provides compile-time guarantees that UI code runs on main.

### How It Works

```swift
// Entire class isolated to main actor
@MainActor
class ViewModel: ObservableObject {
    @Published var items: [Item] = []
    @Published var isLoading = false

    func loadItems() async {
        isLoading = true  // Safe - we're on @MainActor

        // This runs off main actor
        let fetched = await fetchFromNetwork()

        items = fetched  // Automatically back on main actor
        isLoading = false
    }
}

// Individual function
@MainActor
func updateUI() {
    // Guaranteed main thread
}
```

## Concept 4: Async/Await

### What It Is

`async/await` is structured concurrency syntax that makes asynchronous code read like synchronous code.

### Why It Matters

Replaces callback hell and completion handlers with linear, readable code. Also enables the compiler to reason about concurrency.

### How It Works

```swift
// Before: Completion handlers
func fetchUser(id: String, completion: @escaping (Result<User, Error>) -> Void) {
    URLSession.shared.dataTask(with: url) { data, _, error in
        // Parse and call completion
    }.resume()
}

// After: Async/await
func fetchUser(id: String) async throws -> User {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

// Parallel execution with async let
async let user = fetchUser(id: "1")
async let profile = fetchProfile(id: "1")
let result = try await (user, profile)  // Runs in parallel
```

## Summary

Key takeaways:

1. **Sendable** - Mark types as safe to share across concurrency boundaries
2. **Actors** - Protect mutable state with compiler-enforced isolation
3. **@MainActor** - Guarantee code runs on the main thread for UI
4. **Async/await** - Write asynchronous code that reads linearly
