# React 19 + TypeScript

Master modern React development with TypeScript - building type-safe, performant applications using React 19's latest features including the new use() hook, Actions, and improved Server Components.

## Learning Objectives

After completing this skill, you will be able to:
- Build type-safe React components with TypeScript
- Use React 19's new features effectively
- Implement functional components with hooks
- Create custom hooks with proper typing
- Handle state and side effects correctly
- Work with Server Components basics
- Write maintainable, scalable React code

## Prerequisites

- TypeScript fundamentals
- Basic React knowledge (helpful but not required)
- Node.js 20+
- Understanding of ES modules

## Quick Start

```bash
# Install dependencies
make setup

# Start development server
make dev

# Run examples
make examples

# Run tests
make test
```

## Concepts

### React 19 Key Features

React 19 introduces several improvements:

```
React 19 Features:
┌─────────────────────────────────────────────────────────┐
│  use() Hook          - Consume promises and context     │
│  Actions             - Async transitions with forms     │
│  useActionState      - Form state management            │
│  useOptimistic       - Optimistic UI updates           │
│  ref as prop         - No more forwardRef needed       │
│  Document Metadata   - Native <title>, <meta> support  │
└─────────────────────────────────────────────────────────┘
```

### TypeScript with React

TypeScript enhances React development with:

```typescript
// Type-safe props
interface ButtonProps {
  label: string
  onClick: () => void
  variant?: 'primary' | 'secondary'
  disabled?: boolean
}

function Button({ label, onClick, variant = 'primary', disabled }: ButtonProps) {
  return (
    <button onClick={onClick} disabled={disabled} className={variant}>
      {label}
    </button>
  )
}
```

### Component Patterns

```typescript
// Function component with children
interface CardProps {
  title: string
  children: React.ReactNode
}

function Card({ title, children }: CardProps) {
  return (
    <div className="card">
      <h2>{title}</h2>
      {children}
    </div>
  )
}
```

### Hooks with TypeScript

```typescript
// useState with explicit type
const [user, setUser] = useState<User | null>(null)

// useReducer with typed actions
type Action = { type: 'increment' } | { type: 'set'; value: number }
const [state, dispatch] = useReducer(reducer, { count: 0 })

// Custom hook with return type
function useToggle(initial = false): [boolean, () => void] {
  const [value, setValue] = useState(initial)
  const toggle = useCallback(() => setValue(v => !v), [])
  return [value, toggle]
}
```

## Examples

### Example 1: Component Basics

Learn fundamental component patterns with TypeScript.

```bash
make example-1
```

### Example 2: Hooks Deep Dive

Master useState, useEffect, useReducer, and custom hooks.

```bash
make example-2
```

### Example 3: React 19 Features

Explore use(), Actions, and new React 19 capabilities.

```bash
make example-3
```

### Example 4: Advanced Patterns

Context, portals, error boundaries, and composition.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Build a Type-Safe Form - Create a form with validation and proper typing
2. **Exercise 2**: Custom Hook Library - Build reusable hooks with TypeScript
3. **Exercise 3**: State Management - Implement a shopping cart with useReducer

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Missing Key Prop in Lists

Always provide a stable key for list items:

```typescript
// Wrong
{items.map(item => <Item {...item} />)}

// Correct
{items.map(item => <Item key={item.id} {...item} />)}
```

### Incorrect Event Types

Use the correct React event types:

```typescript
// Wrong
function handleClick(e: Event) { ... }

// Correct
function handleClick(e: React.MouseEvent<HTMLButtonElement>) { ... }
```

### Not Typing Children Properly

Use ReactNode for children that can be anything:

```typescript
interface Props {
  children: React.ReactNode  // Accepts anything renderable
  // children: React.ReactElement  // Only accepts JSX elements
  // children: string  // Only accepts text
}
```

### Forgetting to Memoize Callbacks

Prevent unnecessary re-renders:

```typescript
// Can cause re-renders
const handleClick = () => { ... }

// Stable reference
const handleClick = useCallback(() => { ... }, [deps])
```

## Further Reading

- [React 19 Documentation](https://react.dev/)
- [TypeScript Handbook - React](https://www.typescriptlang.org/docs/handbook/react.html)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- Related skills in this repository:
  - [Vite 7](../vite-7/) - Build tooling for React projects
  - [Tailwind CSS 4](../tailwind-css-4/) - Style React components
