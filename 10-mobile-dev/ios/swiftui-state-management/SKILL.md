---
name: managing-swiftui-state
description: Manage SwiftUI state with @State, @FocusState, @Observable, and atomic state patterns. Use when managing view state, keyboard focus, or refactoring state architecture.
---

# SwiftUI State Management

## Quick Start
```swift
// Keyboard focus with @FocusState
struct ChatInputView: View {
    @State private var message = ""
    @FocusState private var isInputFocused: Bool

    var body: some View {
        TextField("Message", text: $message)
            .focused($isInputFocused)
            .onAppear { isInputFocused = true }
    }
}

// Atomic state with @Observable
@Observable
final class ConversationState {
    var messages: [Message] = []
    var responseId: String?
    var isLoading = false
}
```

## Key Points
- @State for view-local
- @FocusState for keyboard
- @Observable for shared
- Atomic state patterns

## Common Mistakes
1. **State in wrong place** - Use @State for view-local, @Observable for shared
2. **Missing @FocusState** - Keyboard handling requires @FocusState

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
