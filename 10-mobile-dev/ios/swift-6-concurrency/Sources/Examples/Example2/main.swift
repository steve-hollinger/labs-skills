/// Example 2: Actor Isolation
///
/// Demonstrates using actors to protect shared mutable state.

import Foundation
import Swift6Concurrency

print("Example 2: Actor Isolation")
print(String(repeating: "=", count: 50))

// MARK: - Problem: Data Races with Classes

/// This class has potential data races (BAD in Swift 6)
final class UnsafeCounter {
    var count = 0

    func increment() {
        count += 1  // Data race if called from multiple threads!
    }
}

// MARK: - Solution: Actor

/// Actor safely protects mutable state
actor SafeCounter {
    private var count = 0

    func increment() {
        count += 1  // Safe! Actor guarantees serial access
    }

    func getCount() -> Int {
        count
    }
}

// MARK: - Custom Actor Example

/// A cache actor that deduplicates requests
actor RequestCache {
    private var cache: [String: String] = [:]
    private var inFlight: [String: Task<String, Error>] = [:]

    func fetch(key: String) async throws -> String {
        // Return cached value
        if let cached = cache[key] {
            print("   Cache hit for '\(key)'")
            return cached
        }

        // Deduplicate in-flight requests
        if let existing = inFlight[key] {
            print("   Joining existing request for '\(key)'")
            return try await existing.value
        }

        // Start new request
        print("   Starting new request for '\(key)'")
        let task = Task {
            try await Task.sleep(nanoseconds: 200_000_000)
            return "Value for \(key)"
        }

        inFlight[key] = task

        do {
            let value = try await task.value
            cache[key] = value
            inFlight[key] = nil
            return value
        } catch {
            inFlight[key] = nil
            throw error
        }
    }
}

// MARK: - Run Examples

print("\n1. Safe counter with actor:")
Task {
    let counter = SafeCounter()

    // Multiple concurrent increments are safe
    await withTaskGroup(of: Void.self) { group in
        for _ in 0..<100 {
            group.addTask {
                await counter.increment()
            }
        }
    }

    let finalCount = await counter.getCount()
    print("   Final count: \(finalCount) (expected: 100)")
}

print("\n2. Request deduplication with actor:")
Task {
    let cache = RequestCache()

    // Launch multiple concurrent requests for same key
    async let result1 = cache.fetch(key: "user-123")
    async let result2 = cache.fetch(key: "user-123")
    async let result3 = cache.fetch(key: "user-456")

    let results = try await [result1, result2, result3]
    print("   Results: \(results)")
}

print("\n3. Using the DataStore actor from library:")
Task {
    let store = DataStore()

    // Concurrent fetches are safe
    async let user1 = store.fetchUser(id: "alice")
    async let user2 = store.fetchUser(id: "bob")
    async let user3 = store.fetchUser(id: "alice")  // Will use cache

    let users = try await [user1, user2, user3]
    print("   Fetched \(users.count) users")
    for user in users {
        print("   - \(user.name) (\(user.email))")
    }
}

// Keep running for async tasks
RunLoop.main.run(until: Date(timeIntervalSinceNow: 2))
print("\nExample completed successfully!")
