/**
 * Example 2: Hooks Deep Dive
 *
 * This example demonstrates React hooks with TypeScript,
 * including useState, useEffect, useReducer, useContext, and custom hooks.
 */

import React, {
  useState,
  useEffect,
  useReducer,
  useContext,
  useCallback,
  useMemo,
  useRef,
  createContext,
} from 'react'

console.log('=== Example 2: Hooks Deep Dive ===\n')

// ============================================
// 1. useState with Types
// ============================================

interface User {
  id: number
  name: string
  email: string
}

function UseStateExample() {
  // Type inferred from initial value
  const [count, setCount] = useState(0)

  // Explicit type for complex state
  const [user, setUser] = useState<User | null>(null)

  // Array state
  const [items, setItems] = useState<string[]>([])

  // Object state with partial updates
  const updateUser = (updates: Partial<User>) => {
    setUser((prev) => (prev ? { ...prev, ...updates } : null))
  }

  // Functional update
  const increment = () => setCount((prev) => prev + 1)

  // Array operations
  const addItem = (item: string) => setItems((prev) => [...prev, item])
  const removeItem = (index: number) =>
    setItems((prev) => prev.filter((_, i) => i !== index))

  return { count, user, items, increment, updateUser, addItem, removeItem }
}

console.log('1. useState with TypeScript:')
console.log('   - Type inference for simple values')
console.log('   - Explicit types for complex/nullable state')
console.log('   - Functional updates for state derived from previous')

// ============================================
// 2. useEffect Patterns
// ============================================

function UseEffectExample({ userId }: { userId: number }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  // Effect with cleanup and abort controller
  useEffect(() => {
    const controller = new AbortController()

    async function fetchUser() {
      setLoading(true)
      setError(null)

      try {
        const response = await fetch(`/api/users/${userId}`, {
          signal: controller.signal,
        })
        if (!response.ok) throw new Error('Failed to fetch')
        const data: User = await response.json()
        setUser(data)
      } catch (err) {
        if (err instanceof Error && err.name !== 'AbortError') {
          setError(err)
        }
      } finally {
        setLoading(false)
      }
    }

    fetchUser()

    return () => controller.abort()
  }, [userId])

  return { user, loading, error }
}

console.log('2. useEffect patterns:')
console.log('   - Cleanup with AbortController')
console.log('   - Error handling for async operations')
console.log('   - Dependency array for re-running')

// ============================================
// 3. useReducer with Typed Actions
// ============================================

// State type
interface CounterState {
  count: number
  step: number
  history: number[]
}

// Discriminated union for actions
type CounterAction =
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'setStep'; payload: number }
  | { type: 'reset' }
  | { type: 'setCount'; payload: number }

const initialCounterState: CounterState = {
  count: 0,
  step: 1,
  history: [],
}

function counterReducer(state: CounterState, action: CounterAction): CounterState {
  switch (action.type) {
    case 'increment':
      return {
        ...state,
        count: state.count + state.step,
        history: [...state.history, state.count],
      }
    case 'decrement':
      return {
        ...state,
        count: state.count - state.step,
        history: [...state.history, state.count],
      }
    case 'setStep':
      return { ...state, step: action.payload }
    case 'setCount':
      return {
        ...state,
        count: action.payload,
        history: [...state.history, state.count],
      }
    case 'reset':
      return initialCounterState
  }
}

function UseReducerExample() {
  const [state, dispatch] = useReducer(counterReducer, initialCounterState)

  return (
    <div>
      <p>Count: {state.count}</p>
      <p>Step: {state.step}</p>
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
      <button onClick={() => dispatch({ type: 'setStep', payload: 5 })}>
        Set Step to 5
      </button>
      <button onClick={() => dispatch({ type: 'reset' })}>Reset</button>
    </div>
  )
}

console.log('3. useReducer with types:')
console.log('   - Discriminated union for type-safe actions')
console.log('   - Exhaustive switch handling')
console.log('   - Complex state transitions')

// ============================================
// 4. useContext with TypeScript
// ============================================

interface ThemeContextValue {
  theme: 'light' | 'dark'
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextValue | null>(null)

// Custom hook for type-safe context access
function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  const toggleTheme = useCallback(() => {
    setTheme((t) => (t === 'light' ? 'dark' : 'light'))
  }, [])

  const value = useMemo(() => ({ theme, toggleTheme }), [theme, toggleTheme])

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

function ThemedButton() {
  const { theme, toggleTheme } = useTheme()
  return (
    <button onClick={toggleTheme}>
      Current theme: {theme}. Click to toggle.
    </button>
  )
}

console.log('4. useContext with TypeScript:')
console.log('   - Typed context value')
console.log('   - Custom hook for safe access')
console.log('   - Memoized provider value')

// ============================================
// 5. useRef Patterns
// ============================================

function UseRefExample() {
  // DOM ref
  const inputRef = useRef<HTMLInputElement>(null)

  // Mutable value ref (doesn't trigger re-render)
  const renderCount = useRef(0)
  renderCount.current++

  // Store previous value
  const prevValue = useRef<string>('')

  const focusInput = () => {
    inputRef.current?.focus()
  }

  const selectAll = () => {
    inputRef.current?.select()
  }

  return (
    <div>
      <input ref={inputRef} type="text" />
      <button onClick={focusInput}>Focus</button>
      <button onClick={selectAll}>Select All</button>
      <p>Render count: {renderCount.current}</p>
    </div>
  )
}

console.log('5. useRef patterns:')
console.log('   - DOM element refs with correct types')
console.log('   - Mutable values that persist across renders')

// ============================================
// 6. Custom Hooks
// ============================================

// useToggle hook
function useToggle(initialValue = false): [boolean, () => void] {
  const [value, setValue] = useState(initialValue)
  const toggle = useCallback(() => setValue((v) => !v), [])
  return [value, toggle]
}

// useDebounce hook
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debouncedValue
}

// usePrevious hook
function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>()

  useEffect(() => {
    ref.current = value
  }, [value])

  return ref.current
}

// useLocalStorage hook
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

// useAsync hook
interface AsyncState<T> {
  data: T | null
  loading: boolean
  error: Error | null
}

function useAsync<T>(asyncFn: () => Promise<T>, deps: unknown[] = []): AsyncState<T> {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: true,
    error: null,
  })

  useEffect(() => {
    setState({ data: null, loading: true, error: null })

    asyncFn()
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((error) => setState({ data: null, loading: false, error }))
  }, deps)

  return state
}

console.log('6. Custom hooks:')
console.log('   - useToggle: Simple boolean toggle')
console.log('   - useDebounce: Delay value updates')
console.log('   - usePrevious: Track previous value')
console.log('   - useLocalStorage: Persist state')
console.log('   - useAsync: Handle async operations')

// ============================================
// 7. useMemo and useCallback
// ============================================

interface Item {
  id: number
  name: string
  category: string
}

function UseMemoCallbackExample({ items, filter }: { items: Item[]; filter: string }) {
  // Memoize expensive computation
  const filteredItems = useMemo(() => {
    console.log('Filtering items...')
    return items.filter((item) =>
      item.name.toLowerCase().includes(filter.toLowerCase())
    )
  }, [items, filter])

  // Memoize callback to prevent child re-renders
  const handleSelect = useCallback((item: Item) => {
    console.log('Selected:', item.name)
  }, [])

  // Memoize object to use as dependency
  const config = useMemo(
    () => ({
      showCategory: true,
      highlightFilter: filter,
    }),
    [filter]
  )

  return (
    <div>
      <p>Found {filteredItems.length} items</p>
      {filteredItems.map((item) => (
        <div key={item.id} onClick={() => handleSelect(item)}>
          {item.name}
          {config.showCategory && <span> ({item.category})</span>}
        </div>
      ))}
    </div>
  )
}

console.log('7. useMemo and useCallback:')
console.log('   - useMemo for expensive computations')
console.log('   - useCallback for stable function references')
console.log('   - Preventing unnecessary re-renders')

// ============================================
// Demo Component
// ============================================

function HooksDemo() {
  const [isOpen, toggleOpen] = useToggle(false)
  const [searchTerm, setSearchTerm] = useState('')
  const debouncedSearch = useDebounce(searchTerm, 300)

  return (
    <ThemeProvider>
      <div>
        <ThemedButton />

        <div>
          <button onClick={toggleOpen}>{isOpen ? 'Close' : 'Open'}</button>
          {isOpen && <div>Content is visible!</div>}
        </div>

        <div>
          <input
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search..."
          />
          <p>Debounced: {debouncedSearch}</p>
        </div>

        <UseReducerExample />
        <UseRefExample />
      </div>
    </ThemeProvider>
  )
}

console.log('\nDemo combines multiple hook patterns')

/**
 * Key Takeaways:
 *
 * 1. useState: Use explicit types for complex/nullable state
 * 2. useEffect: Always handle cleanup and async properly
 * 3. useReducer: Use discriminated unions for type-safe actions
 * 4. useContext: Create custom hooks for safe access
 * 5. useRef: Type based on element or value type
 * 6. Custom hooks: Encapsulate reusable stateful logic
 * 7. useMemo/useCallback: Optimize performance with correct deps
 */

export {
  UseStateExample,
  UseEffectExample,
  UseReducerExample,
  ThemeProvider,
  useTheme,
  UseRefExample,
  useToggle,
  useDebounce,
  usePrevious,
  useLocalStorage,
  useAsync,
  UseMemoCallbackExample,
  HooksDemo,
}
