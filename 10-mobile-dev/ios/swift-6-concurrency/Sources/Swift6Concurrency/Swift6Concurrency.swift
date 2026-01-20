/// Swift6Concurrency - Core utilities for Swift 6 concurrency patterns
///
/// This module provides examples of Swift 6 concurrency patterns.

import Foundation

// MARK: - Sendable Types

/// A user profile that can be safely shared across concurrency domains
public struct UserProfile: Sendable {
    public let id: String
    public let name: String
    public let email: String

    public init(id: String, name: String, email: String) {
        self.id = id
        self.name = name
        self.email = email
    }
}

// MARK: - Actor Example

/// An actor that safely manages cached data
public actor DataStore {
    private var cache: [String: UserProfile] = [:]

    public init() {}

    public func fetchUser(id: String) async throws -> UserProfile {
        if let cached = cache[id] {
            return cached
        }

        // Simulate network request
        try await Task.sleep(nanoseconds: 100_000_000)
        let user = UserProfile(id: id, name: "User \(id)", email: "\(id)@example.com")
        cache[id] = user
        return user
    }

    public func store(_ user: UserProfile) {
        cache[user.id] = user
    }
}
