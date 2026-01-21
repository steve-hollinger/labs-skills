---
name: structuring-swiftui-apps
description: Structure SwiftUI apps with central action handlers, MVVM patterns, and view composition. Use when organizing view hierarchies or implementing action handling.
---

# SwiftUI Architecture

## Quick Start
```swift
// Central action handler pattern
struct AssistantView: View {
    @State private var handler = AssistantActionHandler()

    var body: some View {
        VStack {
            ChatView(onAction: handler.handle)
            InputBar(onSubmit: handler.handleSubmit)
        }
        .environment(handler)
    }
}

@Observable
final class AssistantActionHandler {
    func handle(_ action: AssistantAction) {
        switch action {
        case .sendMessage(let text): sendMessage(text)
        case .likeResponse(let id): trackLike(id)
        }
    }
}
```

## Key Points
- Central action handler
- View composition
- Environment injection
- MVVM separation

## Common Mistakes
1. **Scattered actions** - Centralize in one handler, not spread across views
2. **Deep prop drilling** - Use environment for widely-used dependencies

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
