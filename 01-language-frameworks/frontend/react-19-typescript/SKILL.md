---
name: building-react-typescript-apps
description: This skill teaches modern React development with TypeScript, covering React 19 features, component patterns, hooks, and type-safe application architecture. Use when writing or improving tests.
---

# React 19 Typescript

## Quick Start
```typescript
interface GreetingProps {
  name: string
  age?: number
}

function Greeting({ name, age }: GreetingProps) {
  return (
    <div>
      <h1>Hello, {name}!</h1>
      {age && <p>You are {age} years old.</p>}
    </div>
  )
}
```

## Commands
```bash
make setup      # Install dependencies
make dev        # Start dev server with HMR
make build      # Build for production
make examples   # Run all examples
make example-1  # Run component basics example
make example-2  # Run hooks example
```

## Key Points
- Functional Components
- Hooks
- TypeScript Integration

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples