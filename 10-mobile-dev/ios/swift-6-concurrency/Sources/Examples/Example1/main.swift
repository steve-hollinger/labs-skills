/// Example 1: Basic Async/Await Migration
///
/// Demonstrates converting completion handler code to async/await.

import Foundation
import Swift6Concurrency

print("Example 1: Basic Async/Await Migration")
print(String(repeating: "=", count: 50))

// MARK: - Before: Completion Handlers

/// Old pattern with completion handlers (nested callbacks)
func fetchUserDataLegacy(
    userId: String,
    completion: @escaping (Result<String, Error>) -> Void
) {
    // Simulate first API call
    DispatchQueue.global().asyncAfter(deadline: .now() + 0.1) {
        let userData = "User: \(userId)"

        // Simulate second API call (nested)
        DispatchQueue.global().asyncAfter(deadline: .now() + 0.1) {
            let enrichedData = "\(userData) - enriched"
            completion(.success(enrichedData))
        }
    }
}

// MARK: - After: Async/Await

/// New pattern with async/await (linear and readable)
func fetchUserData(userId: String) async throws -> String {
    // First "API call"
    try await Task.sleep(nanoseconds: 100_000_000)
    let userData = "User: \(userId)"

    // Second "API call" (no nesting!)
    try await Task.sleep(nanoseconds: 100_000_000)
    let enrichedData = "\(userData) - enriched"

    return enrichedData
}

// MARK: - Bridging Old to New

/// Using withCheckedContinuation to bridge callback to async
func fetchUserDataBridged(userId: String) async throws -> String {
    try await withCheckedThrowingContinuation { continuation in
        fetchUserDataLegacy(userId: userId) { result in
            continuation.resume(with: result)
        }
    }
}

// MARK: - Run Examples

print("\n1. Using new async/await pattern:")
Task {
    do {
        let result = try await fetchUserData(userId: "123")
        print("   Result: \(result)")
    } catch {
        print("   Error: \(error)")
    }
}

print("\n2. Bridging legacy code to async:")
Task {
    do {
        let result = try await fetchUserDataBridged(userId: "456")
        print("   Result: \(result)")
    } catch {
        print("   Error: \(error)")
    }
}

print("\n3. Parallel fetches with async let:")
Task {
    async let user1 = fetchUserData(userId: "A")
    async let user2 = fetchUserData(userId: "B")
    async let user3 = fetchUserData(userId: "C")

    do {
        let results = try await [user1, user2, user3]
        print("   All users fetched: \(results.count) results")
        for result in results {
            print("   - \(result)")
        }
    } catch {
        print("   Error: \(error)")
    }
}

// Keep the program running for async tasks
RunLoop.main.run(until: Date(timeIntervalSinceNow: 2))
print("\nExample completed successfully!")
