# CLAUDE.md - React 19 + TypeScript

This skill teaches modern React development with TypeScript, covering React 19 features, component patterns, hooks, and type-safe application architecture.

## Key Concepts

- **Functional Components**: Modern React uses function components exclusively
- **Hooks**: useState, useEffect, useReducer, useContext, and custom hooks
- **TypeScript Integration**: Type-safe props, state, and events
- **React 19 Features**: use(), Actions, useActionState, useOptimistic
- **Component Composition**: Patterns for building reusable UI
- **Performance**: Memoization, lazy loading, and optimization

## Common Commands

```bash
make setup      # Install dependencies
make dev        # Start dev server with HMR
make build      # Build for production
make examples   # Run all examples
make example-1  # Run component basics example
make example-2  # Run hooks example
make example-3  # Run React 19 features example
make example-4  # Run advanced patterns example
make test       # Run Vitest tests
make lint       # Run ESLint and TypeScript checks
make clean      # Remove build artifacts
```

## Project Structure

```
react-19-typescript/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── components/
│   │   ├── Button.tsx
│   │   └── Card.tsx
│   └── examples/
│       ├── 01-component-basics/
│       ├── 02-hooks-deep-dive/
│       ├── 03-react-19-features/
│       └── 04-advanced-patterns/
├── exercises/
│   ├── exercise-1-type-safe-form/
│   ├── exercise-2-custom-hooks/
│   ├── exercise-3-state-management/
│   └── solutions/
├── tests/
│   └── components.test.tsx
├── docs/
│   ├── concepts.md
│   └── patterns.md
├── vite.config.ts
├── tsconfig.json
└── package.json
```

## Code Patterns

### Pattern 1: Typed Function Component
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

### Pattern 2: useState with Types
```typescript
interface User {
  id: number
  name: string
  email: string
}

function UserProfile() {
  // Explicit type for complex state
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true) // Type inferred

  // Update with proper typing
  const updateName = (name: string) => {
    setUser(prev => prev ? { ...prev, name } : null)
  }
}
```

### Pattern 3: useReducer with Discriminated Unions
```typescript
type State = { count: number; loading: boolean }

type Action =
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'set'; payload: number }
  | { type: 'setLoading'; payload: boolean }

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment':
      return { ...state, count: state.count + 1 }
    case 'decrement':
      return { ...state, count: state.count - 1 }
    case 'set':
      return { ...state, count: action.payload }
    case 'setLoading':
      return { ...state, loading: action.payload }
  }
}
```

### Pattern 4: Custom Hook
```typescript
function useFetch<T>(url: string) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()

    fetch(url, { signal: controller.signal })
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))

    return () => controller.abort()
  }, [url])

  return { data, error, loading }
}
```

### Pattern 5: Event Handlers
```typescript
function Form() {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value)
  }

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    console.log('Clicked at', e.clientX, e.clientY)
  }
}
```

### Pattern 6: React 19 use() Hook
```typescript
import { use, Suspense } from 'react'

function UserData({ userPromise }: { userPromise: Promise<User> }) {
  // use() unwraps the promise - component suspends until resolved
  const user = use(userPromise)

  return <div>{user.name}</div>
}

// Parent component
function App() {
  const userPromise = fetchUser(1)

  return (
    <Suspense fallback={<Loading />}>
      <UserData userPromise={userPromise} />
    </Suspense>
  )
}
```

## Common Mistakes

1. **Not typing component props**
   - Always define an interface for props
   - Use optional properties with `?` for optional props

2. **Using `any` type**
   - Avoid `any`; use `unknown` if type is truly unknown
   - Define proper types for API responses

3. **Incorrect event types**
   - Use `React.ChangeEvent<HTMLInputElement>` not `Event`
   - Use `React.FormEvent<HTMLFormElement>` for form submit

4. **Missing dependency arrays**
   - Always include dependencies in useEffect/useCallback/useMemo
   - Use ESLint plugin for exhaustive-deps rule

5. **Not handling null/undefined**
   - Check for null before accessing properties
   - Use optional chaining `?.` and nullish coalescing `??`

## When Users Ask About...

### "How do I type a component that accepts children?"
```typescript
interface Props {
  children: React.ReactNode
}
// or use React.PropsWithChildren<OtherProps>
```

### "How do I type a ref?"
```typescript
const inputRef = useRef<HTMLInputElement>(null)
// In React 19, ref is a regular prop:
function Input({ ref }: { ref: React.Ref<HTMLInputElement> }) {
  return <input ref={ref} />
}
```

### "How do I share state between components?"
Use Context with proper typing:
```typescript
const UserContext = createContext<User | null>(null)
// or useReducer for complex state
```

### "What's the difference between type and interface?"
- Use `interface` for component props (can be extended)
- Use `type` for unions, primitives, and complex types
- Both work for most cases; team consistency matters more

### "How do I handle async operations?"
- In React 19, use `use()` hook with Suspense
- Or use custom hooks with useState/useEffect
- Consider React Query/TanStack Query for data fetching

## Testing Notes

- Tests use Vitest with React Testing Library
- Use `@testing-library/react` for rendering
- Use `@testing-library/user-event` for interactions
- Mock modules with `vi.mock()`

## Dependencies

Key dependencies in package.json:
- react@^19.0.0: Core library
- react-dom@^19.0.0: DOM rendering
- typescript@^5.7.0: TypeScript compiler
- @types/react@^19.0.0: React type definitions
- vitest@^2.1.0: Testing framework
- @testing-library/react@^16.0.0: Testing utilities
