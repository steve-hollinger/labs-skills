# React 19 + TypeScript Concepts

This document covers fundamental concepts for building React applications with TypeScript.

## React Component Model

### Function Components

React 19 uses function components exclusively. Class components are legacy:

```typescript
// Modern function component
interface GreetingProps {
  name: string
  enthusiastic?: boolean
}

function Greeting({ name, enthusiastic = false }: GreetingProps) {
  const exclamation = enthusiastic ? '!' : ''
  return <h1>Hello, {name}{exclamation}</h1>
}
```

### JSX and TypeScript

JSX is transformed into `React.createElement` calls. TypeScript validates:

- Element types exist
- Props match component interfaces
- Children are valid

```typescript
// TypeScript catches errors at compile time
<Button
  label="Click me"
  onClick={() => console.log('clicked')}
  // @ts-error: 'color' does not exist on ButtonProps
  color="red"
/>
```

## TypeScript Integration

### Typing Props

Define interfaces for component props:

```typescript
// Required and optional props
interface CardProps {
  title: string           // Required
  subtitle?: string       // Optional
  onClick?: () => void    // Optional callback
}

// Props with specific literal types
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger'
  size: 'sm' | 'md' | 'lg'
}

// Props with children
interface LayoutProps {
  children: React.ReactNode
  sidebar?: React.ReactNode
}
```

### Typing State

```typescript
// Simple state - type inferred
const [count, setCount] = useState(0)

// Complex state - explicit type
interface User {
  id: number
  name: string
  email: string
}

const [user, setUser] = useState<User | null>(null)

// Array state
const [items, setItems] = useState<string[]>([])

// Object state
const [form, setForm] = useState<Record<string, string>>({})
```

### Typing Events

React provides generic event types:

```typescript
// Mouse events
function handleClick(e: React.MouseEvent<HTMLButtonElement>) {
  console.log('Clicked at', e.clientX, e.clientY)
}

// Input events
function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
  console.log('Value:', e.target.value)
}

// Form events
function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
  e.preventDefault()
  const formData = new FormData(e.currentTarget)
}

// Keyboard events
function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
  if (e.key === 'Enter') {
    // Submit
  }
}
```

## Hooks

### useState

Manages component state:

```typescript
// Type inference
const [count, setCount] = useState(0)

// Explicit typing for complex types
const [user, setUser] = useState<User | null>(null)

// Functional updates
setCount(prev => prev + 1)
setUser(prev => prev ? { ...prev, name: 'New Name' } : null)

// Lazy initialization
const [expensiveState] = useState(() => computeExpensiveValue())
```

### useEffect

Handles side effects:

```typescript
// Run on every render
useEffect(() => {
  console.log('Rendered')
})

// Run once on mount
useEffect(() => {
  console.log('Mounted')
}, [])

// Run when dependencies change
useEffect(() => {
  console.log('Count changed:', count)
}, [count])

// Cleanup function
useEffect(() => {
  const subscription = subscribe()
  return () => subscription.unsubscribe()
}, [])

// Async effect pattern
useEffect(() => {
  const controller = new AbortController()

  async function fetchData() {
    try {
      const response = await fetch(url, { signal: controller.signal })
      const data = await response.json()
      setData(data)
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        setError(error)
      }
    }
  }

  fetchData()
  return () => controller.abort()
}, [url])
```

### useReducer

For complex state logic:

```typescript
// Define state and action types
interface State {
  count: number
  error: string | null
  loading: boolean
}

type Action =
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'setCount'; payload: number }
  | { type: 'setError'; payload: string }
  | { type: 'setLoading'; payload: boolean }

// Type-safe reducer
function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment':
      return { ...state, count: state.count + 1 }
    case 'decrement':
      return { ...state, count: state.count - 1 }
    case 'setCount':
      return { ...state, count: action.payload }
    case 'setError':
      return { ...state, error: action.payload }
    case 'setLoading':
      return { ...state, loading: action.payload }
  }
}

// Usage
const [state, dispatch] = useReducer(reducer, {
  count: 0,
  error: null,
  loading: false,
})
```

### useContext

Share state across components:

```typescript
// Create typed context
interface ThemeContext {
  theme: 'light' | 'dark'
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContext | null>(null)

// Custom hook for type-safe access
function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}

// Provider component
function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')
  const toggleTheme = () => setTheme(t => t === 'light' ? 'dark' : 'light')

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}
```

### useRef

Access DOM elements or persist values:

```typescript
// DOM ref
const inputRef = useRef<HTMLInputElement>(null)

function focusInput() {
  inputRef.current?.focus()
}

// Mutable ref (doesn't trigger re-render)
const renderCount = useRef(0)
renderCount.current++
```

### useMemo and useCallback

Optimize performance:

```typescript
// Memoize expensive computation
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data)
}, [data])

// Memoize callback to prevent re-renders
const handleClick = useCallback(() => {
  console.log('Clicked with', id)
}, [id])
```

## React 19 Features

### use() Hook

Consume promises and context:

```typescript
import { use, Suspense } from 'react'

// Read from a promise
function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise)
  return <div>{user.name}</div>
}

// Read from context (no need for useContext)
function ThemeButton() {
  const { theme } = use(ThemeContext)
  return <button className={theme}>Click</button>
}
```

### Actions and useActionState

Handle form submissions:

```typescript
import { useActionState } from 'react'

interface FormState {
  error: string | null
  success: boolean
}

async function submitForm(
  prevState: FormState,
  formData: FormData
): Promise<FormState> {
  const name = formData.get('name')

  if (!name) {
    return { error: 'Name is required', success: false }
  }

  await saveToDatabase({ name })
  return { error: null, success: true }
}

function Form() {
  const [state, formAction, isPending] = useActionState(
    submitForm,
    { error: null, success: false }
  )

  return (
    <form action={formAction}>
      <input name="name" />
      <button disabled={isPending}>
        {isPending ? 'Saving...' : 'Save'}
      </button>
      {state.error && <p className="error">{state.error}</p>}
    </form>
  )
}
```

### useOptimistic

Optimistic UI updates:

```typescript
import { useOptimistic } from 'react'

function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo: Todo) => [...state, newTodo]
  )

  async function addTodo(formData: FormData) {
    const newTodo = {
      id: crypto.randomUUID(),
      text: formData.get('text') as string,
      completed: false,
    }

    addOptimisticTodo(newTodo)
    await saveTodo(newTodo)
  }

  return (
    <form action={addTodo}>
      <input name="text" />
      <button>Add</button>
      <ul>
        {optimisticTodos.map(todo => (
          <li key={todo.id}>{todo.text}</li>
        ))}
      </ul>
    </form>
  )
}
```

### ref as Prop

In React 19, ref is a regular prop:

```typescript
// No need for forwardRef in React 19
function Input({ ref, ...props }: {
  ref?: React.Ref<HTMLInputElement>
  placeholder?: string
}) {
  return <input ref={ref} {...props} />
}

// Usage
function Form() {
  const inputRef = useRef<HTMLInputElement>(null)
  return <Input ref={inputRef} placeholder="Enter name" />
}
```

## Component Lifecycle

Understanding when effects run:

```
Mount:
1. Component renders
2. DOM updates
3. useLayoutEffect runs (blocking)
4. Browser paints
5. useEffect runs (non-blocking)

Update (state/props change):
1. Component re-renders
2. DOM updates
3. Cleanup functions run
4. useLayoutEffect runs
5. Browser paints
6. useEffect runs

Unmount:
1. Cleanup functions run
2. Component removed from DOM
```
