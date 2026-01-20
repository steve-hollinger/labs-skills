---
name: localizing-ios-apps
description: This skill teaches iOS localization including String Catalogs, LocalizedStringKey, and removing hardcoded strings. Use when localizing apps or auditing hardcoded text.
---

# iOS Localization

## Quick Start
```swift
// Using String Catalogs (Xcode 15+)
struct AssistantView: View {
    var body: some View {
        VStack {
            // Key in Localizable.xcstrings
            Text("assistant.welcome")

            TextField("assistant.input.placeholder", text: $input)
        }
    }
}

// Programmatic localization
let title = String(localized: "assistant.title")
let formatted = String(localized: "points.earned.\(count)")
```

## Commands
```bash
make setup      # swift package resolve
make examples   # Run all examples
make example-1  # String Catalogs
make example-2  # LocalizedStringKey
make example-3  # Pluralization
make test       # swift test
```

## Key Points
- String Catalogs
- LocalizedStringKey
- Pluralization rules
- Hardcoded audit

## Common Mistakes
1. **Hardcoded strings** - All user-visible text should use localization keys
2. **Missing pluralization** - Use plural rules for counts

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples
