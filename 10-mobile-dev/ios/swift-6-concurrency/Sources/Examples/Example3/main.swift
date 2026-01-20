/// Example 3: Sendable Patterns
///
/// Demonstrates making types safe to share across concurrency domains.

import Foundation
import Swift6Concurrency

print("Example 3: Sendable Patterns")
print(String(repeating: "=", count: 50))

// MARK: - Sendable Structs (Easy)

/// Structs with only Sendable properties are automatically Sendable
struct Message: Sendable {
    let id: UUID
    let text: String
    let timestamp: Date
}

// MARK: - Sendable Enums

/// Enums with Sendable associated values are Sendable
enum LoadingState<T: Sendable>: Sendable {
    case idle
    case loading
    case loaded(T)
    case failed(Error)
}

// Make Error conformance explicit for our error type
enum AppError: Error, Sendable {
    case networkError
    case decodingError
}

// MARK: - Sendable Classes (Harder)

/// Classes need explicit Sendable conformance
/// Option 1: Make it immutable with let properties
final class ImmutableConfig: Sendable {
    let apiKey: String
    let environment: String

    init(apiKey: String, environment: String) {
        self.apiKey = apiKey
        self.environment = environment
    }
}

/// Option 2: Use @unchecked Sendable with internal synchronization
final class SynchronizedCache: @unchecked Sendable {
    private let lock = NSLock()
    private var storage: [String: String] = [:]

    func set(_ value: String, for key: String) {
        lock.lock()
        defer { lock.unlock() }
        storage[key] = value
    }

    func get(_ key: String) -> String? {
        lock.lock()
        defer { lock.unlock() }
        return storage[key]
    }
}

// MARK: - Sendable Closures

/// @Sendable closures can be passed across actor boundaries
func processItems(
    items: [String],
    transform: @Sendable (String) -> String
) async -> [String] {
    await withTaskGroup(of: String.self) { group in
        for item in items {
            group.addTask {
                transform(item)
            }
        }

        var results: [String] = []
        for await result in group {
            results.append(result)
        }
        return results
    }
}

// MARK: - Non-Sendable Workarounds

/// When you have a non-Sendable type from a library
class LegacyProcessor {
    func process(_ input: String) -> String {
        "Processed: \(input)"
    }
}

/// Wrap it in an actor
actor ProcessorWrapper {
    private let processor = LegacyProcessor()

    func process(_ input: String) -> String {
        processor.process(input)
    }
}

// MARK: - Run Examples

print("\n1. Sendable structs in tasks:")
Task {
    let message = Message(id: UUID(), text: "Hello", timestamp: Date())

    // Safe to use in another task
    Task.detached {
        print("   Message: \(message.text) at \(message.timestamp)")
    }
}

print("\n2. Sendable closures:")
Task {
    let items = ["apple", "banana", "cherry"]

    // This closure is @Sendable - it captures nothing mutable
    let results = await processItems(items: items) { item in
        item.uppercased()
    }

    print("   Transformed: \(results)")
}

print("\n3. Loading state with generics:")
Task {
    var state: LoadingState<UserProfile> = .idle
    print("   Initial state: idle")

    state = .loading
    print("   Loading...")

    let profile = UserProfile(id: "1", name: "Alice", email: "alice@example.com")
    state = .loaded(profile)

    if case .loaded(let user) = state {
        print("   Loaded: \(user.name)")
    }
}

print("\n4. Wrapping non-Sendable types:")
Task {
    let wrapper = ProcessorWrapper()

    let result = await wrapper.process("input data")
    print("   \(result)")
}

print("\n5. Using library Sendable types:")
Task {
    let config = AppConfiguration(
        apiBaseURL: URL(string: "https://api.example.com")!,
        timeout: 30,
        maxRetries: 3
    )

    // Safe to pass to another task
    Task.detached {
        print("   Config: \(config.apiBaseURL) with \(config.timeout)s timeout")
    }
}

// Keep running for async tasks
RunLoop.main.run(until: Date(timeIntervalSinceNow: 1))
print("\nExample completed successfully!")
