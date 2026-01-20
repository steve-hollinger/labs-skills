# React 19 + TypeScript Patterns

This document contains common patterns and best practices for React TypeScript development.

## Component Patterns

### Compound Components

Components that work together with implicit state sharing:

```typescript
interface TabsContextValue {
  activeTab: string
  setActiveTab: (tab: string) => void
}

const TabsContext = createContext<TabsContextValue | null>(null)

function useTabs() {
  const context = useContext(TabsContext)
  if (!context) throw new Error('useTabs must be used within Tabs')
  return context
}

interface TabsProps {
  defaultTab: string
  children: React.ReactNode
}

function Tabs({ defaultTab, children }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab)

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  )
}

interface TabProps {
  name: string
  children: React.ReactNode
}

function Tab({ name, children }: TabProps) {
  const { activeTab, setActiveTab } = useTabs()

  return (
    <button
      className={activeTab === name ? 'active' : ''}
      onClick={() => setActiveTab(name)}
    >
      {children}
    </button>
  )
}

interface TabPanelProps {
  name: string
  children: React.ReactNode
}

function TabPanel({ name, children }: TabPanelProps) {
  const { activeTab } = useTabs()
  if (activeTab !== name) return null
  return <div className="tab-panel">{children}</div>
}

// Attach sub-components
Tabs.Tab = Tab
Tabs.Panel = TabPanel

// Usage
function App() {
  return (
    <Tabs defaultTab="overview">
      <Tabs.Tab name="overview">Overview</Tabs.Tab>
      <Tabs.Tab name="details">Details</Tabs.Tab>

      <Tabs.Panel name="overview">
        <p>Overview content</p>
      </Tabs.Panel>
      <Tabs.Panel name="details">
        <p>Details content</p>
      </Tabs.Panel>
    </Tabs>
  )
}
```

### Render Props

Pass rendering logic as a function:

```typescript
interface MousePosition {
  x: number
  y: number
}

interface MouseTrackerProps {
  render: (position: MousePosition) => React.ReactNode
}

function MouseTracker({ render }: MouseTrackerProps) {
  const [position, setPosition] = useState<MousePosition>({ x: 0, y: 0 })

  useEffect(() => {
    const handleMove = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY })
    }

    window.addEventListener('mousemove', handleMove)
    return () => window.removeEventListener('mousemove', handleMove)
  }, [])

  return <>{render(position)}</>
}

// Usage
function App() {
  return (
    <MouseTracker
      render={({ x, y }) => (
        <p>Mouse at ({x}, {y})</p>
      )}
    />
  )
}
```

### Higher-Order Components (HOC)

Wrap components to add functionality:

```typescript
interface WithLoadingProps {
  loading: boolean
}

function withLoading<P extends object>(
  WrappedComponent: React.ComponentType<P>
) {
  return function WithLoadingComponent({
    loading,
    ...props
  }: P & WithLoadingProps) {
    if (loading) {
      return <div>Loading...</div>
    }
    return <WrappedComponent {...(props as P)} />
  }
}

// Usage
interface UserListProps {
  users: User[]
}

function UserList({ users }: UserListProps) {
  return (
    <ul>
      {users.map(u => <li key={u.id}>{u.name}</li>)}
    </ul>
  )
}

const UserListWithLoading = withLoading(UserList)

// In parent component
<UserListWithLoading loading={isLoading} users={users} />
```

### Custom Hook Patterns

#### useToggle

```typescript
function useToggle(initialValue = false): [boolean, () => void] {
  const [value, setValue] = useState(initialValue)
  const toggle = useCallback(() => setValue(v => !v), [])
  return [value, toggle]
}

// Usage
const [isOpen, toggleOpen] = useToggle(false)
```

#### useDebounce

```typescript
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debouncedValue
}

// Usage
const [searchTerm, setSearchTerm] = useState('')
const debouncedSearch = useDebounce(searchTerm, 300)
```

#### useLocalStorage

```typescript
function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((val: T) => T)) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch {
      return initialValue
    }
  })

  const setValue = (value: T | ((val: T) => T)) => {
    const valueToStore = value instanceof Function ? value(storedValue) : value
    setStoredValue(valueToStore)
    localStorage.setItem(key, JSON.stringify(valueToStore))
  }

  return [storedValue, setValue]
}

// Usage
const [theme, setTheme] = useLocalStorage<'light' | 'dark'>('theme', 'light')
```

#### useFetch

```typescript
interface FetchState<T> {
  data: T | null
  error: Error | null
  loading: boolean
}

function useFetch<T>(url: string): FetchState<T> {
  const [state, setState] = useState<FetchState<T>>({
    data: null,
    error: null,
    loading: true,
  })

  useEffect(() => {
    const controller = new AbortController()

    async function fetchData() {
      setState(s => ({ ...s, loading: true }))

      try {
        const response = await fetch(url, { signal: controller.signal })
        if (!response.ok) throw new Error('Fetch failed')
        const data = await response.json()
        setState({ data, error: null, loading: false })
      } catch (error) {
        if (error instanceof Error && error.name !== 'AbortError') {
          setState({ data: null, error, loading: false })
        }
      }
    }

    fetchData()
    return () => controller.abort()
  }, [url])

  return state
}

// Usage
const { data: users, loading, error } = useFetch<User[]>('/api/users')
```

## Form Patterns

### Controlled Form

```typescript
interface FormData {
  name: string
  email: string
  message: string
}

function ContactForm() {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    message: '',
  })

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    console.log(formData)
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        name="name"
        value={formData.name}
        onChange={handleChange}
      />
      <input
        name="email"
        type="email"
        value={formData.email}
        onChange={handleChange}
      />
      <textarea
        name="message"
        value={formData.message}
        onChange={handleChange}
      />
      <button type="submit">Send</button>
    </form>
  )
}
```

### Form with useReducer

```typescript
interface FormState {
  values: Record<string, string>
  errors: Record<string, string>
  touched: Record<string, boolean>
  isSubmitting: boolean
}

type FormAction =
  | { type: 'SET_VALUE'; field: string; value: string }
  | { type: 'SET_ERROR'; field: string; error: string }
  | { type: 'SET_TOUCHED'; field: string }
  | { type: 'SET_SUBMITTING'; isSubmitting: boolean }
  | { type: 'RESET' }

function formReducer(state: FormState, action: FormAction): FormState {
  switch (action.type) {
    case 'SET_VALUE':
      return {
        ...state,
        values: { ...state.values, [action.field]: action.value },
      }
    case 'SET_ERROR':
      return {
        ...state,
        errors: { ...state.errors, [action.field]: action.error },
      }
    case 'SET_TOUCHED':
      return {
        ...state,
        touched: { ...state.touched, [action.field]: true },
      }
    case 'SET_SUBMITTING':
      return { ...state, isSubmitting: action.isSubmitting }
    case 'RESET':
      return initialFormState
  }
}
```

## Error Handling Patterns

### Error Boundary

```typescript
interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback: React.ReactNode
}

class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback
    }
    return this.props.children
  }
}

// Usage
<ErrorBoundary fallback={<ErrorPage />}>
  <App />
</ErrorBoundary>
```

### Async Error Handling

```typescript
function useAsyncError() {
  const [, setError] = useState()
  return useCallback((error: Error) => {
    setError(() => {
      throw error
    })
  }, [])
}

// Usage in async component
function AsyncComponent() {
  const throwError = useAsyncError()

  useEffect(() => {
    fetchData().catch(throwError)
  }, [throwError])
}
```

## Performance Patterns

### Memoized Component

```typescript
interface ExpensiveListProps {
  items: Item[]
  onSelect: (item: Item) => void
}

const ExpensiveList = memo(function ExpensiveList({
  items,
  onSelect,
}: ExpensiveListProps) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id} onClick={() => onSelect(item)}>
          {item.name}
        </li>
      ))}
    </ul>
  )
})
```

### Virtualized List

```typescript
interface VirtualListProps<T> {
  items: T[]
  itemHeight: number
  windowHeight: number
  renderItem: (item: T, index: number) => React.ReactNode
}

function VirtualList<T>({
  items,
  itemHeight,
  windowHeight,
  renderItem,
}: VirtualListProps<T>) {
  const [scrollTop, setScrollTop] = useState(0)

  const startIndex = Math.floor(scrollTop / itemHeight)
  const endIndex = Math.min(
    startIndex + Math.ceil(windowHeight / itemHeight) + 1,
    items.length
  )

  const visibleItems = items.slice(startIndex, endIndex)
  const totalHeight = items.length * itemHeight
  const offsetY = startIndex * itemHeight

  return (
    <div
      style={{ height: windowHeight, overflow: 'auto' }}
      onScroll={e => setScrollTop(e.currentTarget.scrollTop)}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map((item, i) => renderItem(item, startIndex + i))}
        </div>
      </div>
    </div>
  )
}
```

### Code Splitting

```typescript
import { lazy, Suspense } from 'react'

// Lazy load components
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Settings = lazy(() => import('./pages/Settings'))

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  )
}
```
