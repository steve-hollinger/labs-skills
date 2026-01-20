# CLAUDE.md - {{SKILL_NAME}}

This skill teaches [brief description].

## Key Concepts

- **Concept 1**: Brief explanation
- **Concept 2**: Brief explanation
- **Concept 3**: Brief explanation

## Common Commands

```bash
make setup      # Install dependencies
make dev        # Start dev server
make examples   # Build and preview examples
make test       # Run vitest
make lint       # Run eslint and tsc
make build      # Production build
make clean      # Remove build artifacts
```

## Project Structure

```
{{SKILL_NAME}}/
├── src/
│   ├── examples/
│   │   ├── Example1.tsx
│   │   ├── Example2.tsx
│   │   └── Example3.tsx
│   ├── components/
│   ├── hooks/
│   └── utils/
├── exercises/
│   ├── exercise1/
│   └── solutions/
├── tests/
│   └── *.test.tsx
└── docs/
    ├── concepts.md
    └── patterns.md
```

## Code Patterns

### Pattern 1: Basic Pattern
```typescript
// Example implementation
```

### Pattern 2: Common Pattern
```typescript
// Example implementation
```

## Common Mistakes

1. **Mistake description**
   - Why it happens
   - How to fix it

2. **Another mistake**
   - Why it happens
   - How to fix it

## When Users Ask About...

### "How do I get started?"
Point them to `make setup && make dev` and the README.md.

### "Why isn't X working?"
Check common mistakes above, verify Node version and dependencies.

### "What's the best practice for Y?"
Refer to docs/patterns.md for recommended approaches.

## Testing Notes

- Tests use Vitest with React Testing Library
- Run specific tests: `npm test -- --filter "test name"`
- Check coverage: `make coverage`

## Dependencies

Key dependencies in package.json:
- dependency1: purpose
- dependency2: purpose
