/// Exercise 1: Convert Completion Handler to Async/Await
///
/// Convert the legacy ImageLoader.loadImage method from completion handlers
/// to async/await syntax.
///
/// Instructions:
/// 1. Add an async version of loadImage that uses URLSession's async API
/// 2. Add a bridge method using withCheckedThrowingContinuation
///
/// Run with: swift exercise1/main.swift
/// Check solution in: solutions/solution1/main.swift

import Foundation

class ImageLoader {
    enum ImageError: Error {
        case invalidURL
        case downloadFailed
        case invalidData
    }

    /// Legacy API - DO NOT MODIFY
    func loadImage(
        from urlString: String,
        completion: @escaping (Result<Data, ImageError>) -> Void
    ) {
        guard let url = URL(string: urlString) else {
            completion(.failure(.invalidURL))
            return
        }

        URLSession.shared.dataTask(with: url) { data, response, error in
            if error != nil {
                completion(.failure(.downloadFailed))
                return
            }
            guard let data = data, !data.isEmpty else {
                completion(.failure(.invalidData))
                return
            }
            completion(.success(data))
        }.resume()
    }

    // TODO: Add async version
    // func loadImage(from urlString: String) async throws -> Data

    // TODO: Add bridge method
    // func loadImageBridged(from urlString: String) async throws -> Data
}

// Test your implementation
func main() async {
    print("Exercise 1: Convert Completion Handler to Async/Await")
    print(String(repeating: "=", count: 50))

    let loader = ImageLoader()

    // Uncomment when you implement the async methods:
    // do {
    //     let data = try await loader.loadImage(from: "https://picsum.photos/200")
    //     print("Loaded \(data.count) bytes")
    // } catch {
    //     print("Error: \(error)")
    // }

    print("\nImplement the TODO methods and uncomment the test code!")
}

// Run main
Task {
    await main()
}
RunLoop.main.run(until: Date(timeIntervalSinceNow: 2))
