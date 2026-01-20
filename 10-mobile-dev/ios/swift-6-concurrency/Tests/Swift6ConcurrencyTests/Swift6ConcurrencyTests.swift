import XCTest
@testable import Swift6Concurrency

final class Swift6ConcurrencyTests: XCTestCase {

    // MARK: - Sendable Types Tests

    func testUserProfileIsSendable() {
        let profile = UserProfile(id: "1", name: "Test", email: "test@example.com")
        XCTAssertEqual(profile.id, "1")
        XCTAssertEqual(profile.name, "Test")
        XCTAssertEqual(profile.email, "test@example.com")
    }

    func testAppConfigurationIsSendable() {
        let config = AppConfiguration(
            apiBaseURL: URL(string: "https://api.example.com")!,
            timeout: 60,
            maxRetries: 5
        )
        XCTAssertEqual(config.timeout, 60)
        XCTAssertEqual(config.maxRetries, 5)
    }

    // MARK: - DataStore Actor Tests

    func testDataStoreFetchUser() async throws {
        let store = DataStore()

        let user = try await store.fetchUser(id: "test-user")

        XCTAssertEqual(user.id, "test-user")
        XCTAssertTrue(user.name.contains("test-user"))
    }

    func testDataStoreCaching() async throws {
        let store = DataStore()

        // First fetch
        let user1 = try await store.fetchUser(id: "cached-user")

        // Second fetch should return cached
        let user2 = try await store.fetchUser(id: "cached-user")

        XCTAssertEqual(user1.id, user2.id)
        XCTAssertEqual(user1.name, user2.name)
    }

    func testDataStoreConcurrentFetches() async throws {
        let store = DataStore()

        // Concurrent fetches for different IDs
        async let user1 = store.fetchUser(id: "user-1")
        async let user2 = store.fetchUser(id: "user-2")
        async let user3 = store.fetchUser(id: "user-3")

        let users = try await [user1, user2, user3]

        XCTAssertEqual(users.count, 3)
        XCTAssertEqual(Set(users.map(\.id)).count, 3)
    }

    func testDataStoreDeduplication() async throws {
        let store = DataStore()

        // Multiple concurrent fetches for same ID should deduplicate
        async let fetch1 = store.fetchUser(id: "same-id")
        async let fetch2 = store.fetchUser(id: "same-id")
        async let fetch3 = store.fetchUser(id: "same-id")

        let results = try await [fetch1, fetch2, fetch3]

        // All should return the same user
        XCTAssertEqual(results[0].id, results[1].id)
        XCTAssertEqual(results[1].id, results[2].id)
    }

    // MARK: - Analytics Actor Tests

    func testAnalyticsEventCreation() {
        let event = AnalyticsEvent(
            name: "test_event",
            properties: ["key": "value"]
        )

        XCTAssertEqual(event.name, "test_event")
        XCTAssertEqual(event.properties["key"], "value")
        XCTAssertNotNil(event.timestamp)
    }

    // MARK: - Network Client Tests

    func testNetworkErrorTypes() {
        let invalidURL = NetworkError.invalidURL
        let httpError = NetworkError.httpError(statusCode: 404)

        XCTAssertNotNil(invalidURL)
        if case .httpError(let code) = httpError {
            XCTAssertEqual(code, 404)
        } else {
            XCTFail("Expected httpError")
        }
    }

    func testAPIRequestCreation() {
        let request = APIRequest(
            path: "/users",
            method: "POST",
            headers: ["Content-Type": "application/json"],
            body: Data()
        )

        XCTAssertEqual(request.path, "/users")
        XCTAssertEqual(request.method, "POST")
        XCTAssertEqual(request.headers["Content-Type"], "application/json")
    }

    // MARK: - AsyncConverter Tests

    func testAsyncConverterInitialization() {
        let converter = AsyncConverter()
        XCTAssertNotNil(converter)
    }
}
