---
name: building-chat-history
description: This skill teaches chat history implementation including session management, conversation persistence, and resume functionality. Use when implementing conversation history or chat restoration.
---

# iOS Chat History

## Quick Start
```swift
// Session management with ConversationState
@Observable
final class ConversationState {
    var sessionId: String?
    var messages: [Message] = []
    var canResume: Bool { sessionId != nil }

    func startNewSession() {
        sessionId = UUID().uuidString
        messages = []
    }

    func resume(from history: ChatHistory) {
        sessionId = history.sessionId
        messages = history.messages.map { $0.toDomain() }
    }
}
```

## Commands
```bash
make setup      # swift package resolve
make examples   # Run all examples
make example-1  # Session management
make example-2  # History network layer
make example-3  # Resume functionality
make test       # swift test
```

## Key Points
- Session management
- ConversationState
- History persistence
- Resume chat flow

## Common Mistakes
1. **Losing session** - Persist sessionId across view lifecycle
2. **Stale history** - Refresh history list when returning to view

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
