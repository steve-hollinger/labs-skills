---
name: animating-swiftui-views
description: This skill teaches SwiftUI animation patterns including typewriter effects, rotating placeholders, and custom transitions. Use when adding text animations or view transitions.
---

# SwiftUI Animations

## Quick Start
```swift
// Typewriter text animation
struct TypewriterText: View {
    let fullText: String
    @State private var displayedText = ""

    var body: some View {
        Text(displayedText)
            .onAppear { animateText() }
    }

    private func animateText() {
        for (i, char) in fullText.enumerated() {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.03 * Double(i)) {
                displayedText += String(char)
            }
        }
    }
}
```

## Commands
```bash
make setup      # swift package resolve
make examples   # Run all examples
make example-1  # Typewriter animation
make example-2  # Rotating placeholders
make example-3  # Custom transitions
make test       # swift test
```

## Key Points
- Typewriter effects
- Rotating content
- withAnimation usage
- Custom transitions

## Common Mistakes
1. **Animation jank** - Use proper timing; avoid too-fast reveals
2. **Memory leaks** - Cancel timers/tasks when view disappears

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
