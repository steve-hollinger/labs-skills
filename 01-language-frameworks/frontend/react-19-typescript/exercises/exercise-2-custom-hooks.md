# Exercise 2: Custom Hook Library

## Objective

Build a library of reusable, type-safe custom hooks that can be used across React applications.

## Requirements

Create the following custom hooks with proper TypeScript types:

### 1. useLocalStorage<T>

Persist state to localStorage with type safety.

```typescript
const [value, setValue] = useLocalStorage<User>('user', defaultUser)
```

### 2. useFetch<T>

Fetch data from an API with loading, error, and data states.

```typescript
const { data, loading, error, refetch } = useFetch<User[]>('/api/users')
```

### 3. useDebounce<T>

Debounce a value change.

```typescript
const debouncedSearch = useDebounce(searchTerm, 300)
```

### 4. useMediaQuery

Check if a media query matches.

```typescript
const isMobile = useMediaQuery('(max-width: 768px)')
```

### 5. useClickOutside

Detect clicks outside a referenced element.

```typescript
const ref = useClickOutside<HTMLDivElement>(() => setIsOpen(false))
```

### 6. useInterval

Set up an interval that cleans up properly.

```typescript
useInterval(() => setCount(c => c + 1), 1000)
```

### 7. usePrevious<T>

Track the previous value of a variable.

```typescript
const previousCount = usePrevious(count)
```

## Tasks

### Task 1: Implement useLocalStorage

- Handle SSR (server-side rendering) gracefully
- Parse and stringify JSON automatically
- Handle errors when localStorage is unavailable
- Support function updates like useState

### Task 2: Implement useFetch

- Support generic return type
- Include loading and error states
- Provide a refetch function
- Handle race conditions with cleanup
- Support custom options (headers, etc.)

### Task 3: Implement useDebounce

- Accept value and delay parameters
- Return debounced value
- Clean up timeout on unmount
- Handle value changes correctly

### Task 4: Implement useMediaQuery

- Return boolean for match state
- Update on window resize
- Handle SSR gracefully
- Clean up event listeners

### Task 5: Implement useClickOutside

- Accept callback function
- Return ref to attach to element
- Handle event listeners properly
- Support any HTMLElement type

### Task 6: Implement useInterval

- Accept callback and delay
- Handle delay changes
- Support null delay to pause
- Clean up interval on unmount

### Task 7: Implement usePrevious

- Track previous value with useRef
- Update after each render
- Return undefined on first render

## Testing Requirements

For each hook, write tests that verify:
- Correct TypeScript types
- Expected behavior
- Edge cases (null, undefined, etc.)
- Cleanup on unmount

## Hints

1. Use generics for type-safe hooks
2. Consider SSR compatibility
3. Always clean up side effects
4. Use useCallback for function stability
5. Test with @testing-library/react-hooks

## Example Usage

```typescript
function UserProfile() {
  const [savedUser, setSavedUser] = useLocalStorage<User | null>('user', null)
  const { data: user, loading, error } = useFetch<User>('/api/user')
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search, 300)
  const isMobile = useMediaQuery('(max-width: 768px)')
  const previousSearch = usePrevious(search)

  const dropdownRef = useClickOutside<HTMLDivElement>(() => {
    // Close dropdown
  })

  useInterval(() => {
    // Poll for updates
  }, 5000)

  // Component implementation...
}
```

## Validation Checklist

- [ ] All hooks properly typed with generics
- [ ] No TypeScript errors
- [ ] SSR compatibility where applicable
- [ ] Proper cleanup in all hooks
- [ ] Tests pass for all hooks
