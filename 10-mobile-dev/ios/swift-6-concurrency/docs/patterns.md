# Common Patterns

## Overview

This document covers common patterns for migrating to Swift 6 concurrency.

## Pattern 1: Converting Completion Handlers

### When to Use

When modernizing legacy APIs that use completion handlers.

### Implementation

```swift
// Legacy API with completion handler
func fetchData(completion: @escaping (Result<Data, Error>) -> Void) {
    URLSession.shared.dataTask(with: url) { data, response, error in
        if let error = error {
            completion(.failure(error))
        } else {
            completion(.success(data ?? Data()))
        }
    }.resume()
}

// Modern async version
func fetchData() async throws -> Data {
    let (data, _) = try await URLSession.shared.data(from: url)
    return data
}

// Bridge for compatibility
func fetchDataAsync() async throws -> Data {
    try await withCheckedThrowingContinuation { continuation in
        fetchData { result in
            continuation.resume(with: result)
        }
    }
}
```

### Pitfalls to Avoid

- Don't call `continuation.resume` more than once
- Always call `resume` exactly once (use throwing version for errors)
- Don't mix completion handlers and async in new code

## Pattern 2: Actor-Protected Cache

### When to Use

When you need thread-safe caching with request deduplication.

### Implementation

```swift
actor Cache<Key: Hashable & Sendable, Value: Sendable> {
    private var storage: [Key: Value] = [:]
    private var pending: [Key: Task<Value, Error>] = [:]

    func get(
        _ key: Key,
        fetch: @Sendable () async throws -> Value
    ) async throws -> Value {
        // Return cached value
        if let cached = storage[key] {
            return cached
        }

        // Deduplicate concurrent requests
        if let task = pending[key] {
            return try await task.value
        }

        // Create fetch task
        let task = Task { try await fetch() }
        pending[key] = task

        do {
            let value = try await task.value
            storage[key] = value
            pending[key] = nil
            return value
        } catch {
            pending[key] = nil
            throw error
        }
    }

    func invalidate(_ key: Key) {
        storage[key] = nil
    }
}
```

### Example

```swift
let userCache = Cache<String, User>()

// Multiple concurrent calls for same user deduplicate
async let user1 = userCache.get("user-123") {
    try await api.fetchUser("user-123")
}
async let user2 = userCache.get("user-123") {
    try await api.fetchUser("user-123")  // Won't actually run
}
```

### Pitfalls to Avoid

- Don't store non-Sendable values in actor cache
- Remember actor methods are re-entrant after await

## Pattern 3: MainActor ViewModel

### When to Use

For ViewModels that drive SwiftUI or UIKit views.

### Implementation

```swift
@MainActor
final class ItemListViewModel: ObservableObject {
    @Published private(set) var items: [Item] = []
    @Published private(set) var isLoading = false
    @Published private(set) var error: Error?

    private let repository: ItemRepository

    init(repository: ItemRepository) {
        self.repository = repository
    }

    func loadItems() async {
        guard !isLoading else { return }

        isLoading = true
        error = nil

        do {
            items = try await repository.fetchAll()
        } catch {
            self.error = error
        }

        isLoading = false
    }

    func refresh() async {
        items = []
        await loadItems()
    }
}
```

### Example

```swift
struct ItemListView: View {
    @StateObject private var viewModel = ItemListViewModel(
        repository: ItemRepository()
    )

    var body: some View {
        List(viewModel.items) { item in
            Text(item.name)
        }
        .task {
            await viewModel.loadItems()
        }
    }
}
```

### Pitfalls to Avoid

- Don't perform heavy computation on `@MainActor`
- Use `Task.detached` for CPU-intensive work

## Pattern 4: Sendable Wrapper for Non-Sendable Types

### When to Use

When working with non-Sendable types from libraries.

### Implementation

```swift
// Non-Sendable library type
class LegacyNetworkClient {
    func fetch(url: URL, completion: @escaping (Data?) -> Void) {
        // ...
    }
}

// Sendable wrapper using actor
actor NetworkClientWrapper {
    private let client = LegacyNetworkClient()

    func fetch(url: URL) async -> Data? {
        await withCheckedContinuation { continuation in
            client.fetch(url: url) { data in
                continuation.resume(returning: data)
            }
        }
    }
}

// Alternative: @unchecked Sendable with internal synchronization
final class SynchronizedClient: @unchecked Sendable {
    private let queue = DispatchQueue(label: "client-queue")
    private let client = LegacyNetworkClient()

    func fetch(url: URL) async -> Data? {
        await withCheckedContinuation { continuation in
            queue.async {
                self.client.fetch(url: url) { data in
                    continuation.resume(returning: data)
                }
            }
        }
    }
}
```

### Pitfalls to Avoid

- Only use `@unchecked Sendable` when you've verified thread safety
- Prefer actor wrapper when possible

## Anti-Patterns

### Anti-Pattern 1: Capturing Non-Sendable in Tasks

```swift
// BAD: Capturing mutable class in task
class Counter {
    var count = 0
}

let counter = Counter()
Task {
    counter.count += 1  // Data race!
}

// GOOD: Use actor instead
actor SafeCounter {
    var count = 0
    func increment() { count += 1 }
}
```

### Anti-Pattern 2: Blocking Main Actor

```swift
// BAD: Heavy work on main actor
@MainActor
func processLargeFile() {
    let data = heavyComputation()  // Blocks UI!
    updateUI(with: data)
}

// GOOD: Offload heavy work
@MainActor
func processLargeFile() async {
    let data = await Task.detached {
        heavyComputation()  // Runs on background
    }.value
    updateUI(with: data)
}
```

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Modernizing completion handlers | withCheckedContinuation |
| Thread-safe cache | Actor with deduplication |
| UI-driving logic | @MainActor ViewModel |
| Legacy non-Sendable types | Actor wrapper |
| CPU-intensive work | Task.detached |
| Multiple parallel requests | async let or TaskGroup |
