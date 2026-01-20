/// Solution for Exercise 1: Convert Completion Handler to Async/Await

import Foundation

class ImageLoader {
    enum ImageError: Error {
        case invalidURL
        case downloadFailed
        case invalidData
    }

    /// Legacy API (unchanged)
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

    /// SOLUTION: Pure async implementation
    func loadImage(from urlString: String) async throws -> Data {
        guard let url = URL(string: urlString) else {
            throw ImageError.invalidURL
        }

        do {
            let (data, response) = try await URLSession.shared.data(from: url)

            guard let httpResponse = response as? HTTPURLResponse,
                  (200...299).contains(httpResponse.statusCode) else {
                throw ImageError.downloadFailed
            }

            guard !data.isEmpty else {
                throw ImageError.invalidData
            }

            return data
        } catch is ImageError {
            throw error
        } catch {
            throw ImageError.downloadFailed
        }
    }

    /// SOLUTION: Bridge method wrapping completion handler
    func loadImageBridged(from urlString: String) async throws -> Data {
        try await withCheckedThrowingContinuation { continuation in
            loadImage(from: urlString) { result in
                continuation.resume(with: result)
            }
        }
    }
}

func main() async {
    print("Solution 1: Async/Await Conversion")
    print(String(repeating: "=", count: 50))

    let loader = ImageLoader()

    print("\n1. Using async version:")
    do {
        let data = try await loader.loadImage(from: "https://picsum.photos/200")
        print("   Loaded \(data.count) bytes")
    } catch {
        print("   Error: \(error)")
    }

    print("\n2. Using bridged version:")
    do {
        let data = try await loader.loadImageBridged(from: "https://picsum.photos/200")
        print("   Loaded \(data.count) bytes")
    } catch {
        print("   Error: \(error)")
    }

    print("\nSolution completed!")
}

Task {
    await main()
}
RunLoop.main.run(until: Date(timeIntervalSinceNow: 5))
