---
name: networking-with-async-await
description: This skill teaches modern iOS networking with async/await URLSession, response handling, and DTO mapping. Use when implementing API clients or handling network responses.
---

# iOS Networking

## Quick Start
```swift
// Async URLSession networking
final class ChatHistoryClient {
    func fetchHistory() async throws -> [ChatHistory] {
        let url = URL(string: "\(baseURL)/history")!
        let (data, response) = try await URLSession.shared.data(from: url)

        guard let http = response as? HTTPURLResponse,
              (200...299).contains(http.statusCode) else {
            throw NetworkError.invalidResponse
        }

        let dto = try JSONDecoder().decode(HistoryDTO.self, from: data)
        return dto.items.map { $0.toDomain() }
    }
}
```

## Commands
```bash
make setup      # swift package resolve
make examples   # Run all examples
make example-1  # Async URLSession
make example-2  # Response handling
make example-3  # DTO mapping
make test       # swift test
```

## Key Points
- Async URLSession
- Response validation
- DTO mapping
- Error handling

## Common Mistakes
1. **Missing status check** - Always validate HTTP status before decoding
2. **Tight coupling** - Map DTOs to domain models; don't use DTOs in views

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
