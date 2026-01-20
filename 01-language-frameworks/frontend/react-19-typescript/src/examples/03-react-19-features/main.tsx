/**
 * Example 3: React 19 Features
 *
 * This example demonstrates React 19's new features including:
 * - use() hook for promises and context
 * - Actions and useActionState
 * - useOptimistic for optimistic updates
 * - ref as a regular prop
 */

import React, {
  use,
  Suspense,
  useState,
  useOptimistic,
  createContext,
  useRef,
  useTransition,
} from 'react'

console.log('=== Example 3: React 19 Features ===\n')

// ============================================
// 1. use() Hook with Promises
// ============================================

interface Post {
  id: number
  title: string
  body: string
}

// Simulated API fetch
function fetchPost(id: number): Promise<Post> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        id,
        title: `Post ${id}`,
        body: `This is the content of post ${id}`,
      })
    }, 1000)
  })
}

// Component that uses a promise directly
function PostContent({ postPromise }: { postPromise: Promise<Post> }) {
  // use() unwraps the promise - component suspends until resolved
  const post = use(postPromise)

  return (
    <article>
      <h2>{post.title}</h2>
      <p>{post.body}</p>
    </article>
  )
}

function PostPage({ postId }: { postId: number }) {
  // Create promise in parent, pass to child
  const postPromise = fetchPost(postId)

  return (
    <Suspense fallback={<div>Loading post...</div>}>
      <PostContent postPromise={postPromise} />
    </Suspense>
  )
}

console.log('1. use() with Promises:')
console.log('   - Unwrap promises directly in components')
console.log('   - Works with Suspense for loading states')
console.log('   - Cleaner than useEffect + useState')

// ============================================
// 2. use() Hook with Context
// ============================================

interface UserContextValue {
  user: { name: string; role: string } | null
  login: (name: string) => void
  logout: () => void
}

const UserContext = createContext<UserContextValue | null>(null)

// Component using use() for context
function UserDisplay() {
  // use() can read context directly
  const userContext = use(UserContext)

  if (!userContext) {
    throw new Error('UserContext not found')
  }

  const { user } = userContext

  if (!user) {
    return <p>Not logged in</p>
  }

  return (
    <div>
      <p>Welcome, {user.name}!</p>
      <p>Role: {user.role}</p>
    </div>
  )
}

// Conditional context access
function ConditionalUserDisplay({ showUser }: { showUser: boolean }) {
  // use() can be called conditionally (unlike useContext)
  if (showUser) {
    const context = use(UserContext)
    return <p>User: {context?.user?.name}</p>
  }
  return <p>User hidden</p>
}

console.log('2. use() with Context:')
console.log('   - Alternative to useContext')
console.log('   - Can be called conditionally')
console.log('   - Works inside loops and conditions')

// ============================================
// 3. Actions and useActionState
// ============================================

interface FormState {
  message: string
  error: string | null
  success: boolean
}

// Server Action simulation
async function submitContactForm(
  prevState: FormState,
  formData: FormData
): Promise<FormState> {
  // Simulate API call
  await new Promise((resolve) => setTimeout(resolve, 1000))

  const name = formData.get('name') as string
  const email = formData.get('email') as string
  const message = formData.get('message') as string

  // Validation
  if (!name || !email || !message) {
    return {
      message: '',
      error: 'All fields are required',
      success: false,
    }
  }

  if (!email.includes('@')) {
    return {
      message: '',
      error: 'Invalid email address',
      success: false,
    }
  }

  // Success
  return {
    message: `Thanks ${name}! We'll contact you at ${email}.`,
    error: null,
    success: true,
  }
}

function ContactForm() {
  // Note: useActionState is the new name for useFormState
  // In React 19, it returns [state, formAction, isPending]
  const [state, formAction, isPending] = React.useActionState(
    submitContactForm,
    { message: '', error: null, success: false }
  )

  return (
    <form action={formAction}>
      <div>
        <label htmlFor="name">Name:</label>
        <input id="name" name="name" type="text" disabled={isPending} />
      </div>

      <div>
        <label htmlFor="email">Email:</label>
        <input id="email" name="email" type="email" disabled={isPending} />
      </div>

      <div>
        <label htmlFor="message">Message:</label>
        <textarea id="message" name="message" disabled={isPending} />
      </div>

      <button type="submit" disabled={isPending}>
        {isPending ? 'Sending...' : 'Send Message'}
      </button>

      {state.error && <p className="error">{state.error}</p>}
      {state.success && <p className="success">{state.message}</p>}
    </form>
  )
}

console.log('3. Actions and useActionState:')
console.log('   - Form action as async function')
console.log('   - Automatic pending state')
console.log('   - Progressive enhancement friendly')

// ============================================
// 4. useOptimistic for Optimistic Updates
// ============================================

interface Todo {
  id: string
  text: string
  completed: boolean
  pending?: boolean
}

// Simulated API
async function toggleTodoApi(id: string, completed: boolean): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 500))
  // Simulate occasional failure
  if (Math.random() < 0.1) {
    throw new Error('Failed to update todo')
  }
}

function TodoList({ initialTodos }: { initialTodos: Todo[] }) {
  const [todos, setTodos] = useState(initialTodos)

  // Optimistic state
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state: Todo[], { id, completed }: { id: string; completed: boolean }) =>
      state.map((todo) =>
        todo.id === id ? { ...todo, completed, pending: true } : todo
      )
  )

  async function handleToggle(id: string, completed: boolean) {
    // Update optimistically
    addOptimisticTodo({ id, completed })

    try {
      await toggleTodoApi(id, completed)
      // On success, update real state
      setTodos((prev) =>
        prev.map((todo) => (todo.id === id ? { ...todo, completed } : todo))
      )
    } catch {
      // On failure, state automatically reverts
      console.error('Failed to toggle todo')
    }
  }

  return (
    <ul>
      {optimisticTodos.map((todo) => (
        <li
          key={todo.id}
          style={{ opacity: todo.pending ? 0.5 : 1 }}
        >
          <input
            type="checkbox"
            checked={todo.completed}
            onChange={(e) => handleToggle(todo.id, e.target.checked)}
          />
          <span>{todo.text}</span>
          {todo.pending && <span> (saving...)</span>}
        </li>
      ))}
    </ul>
  )
}

console.log('4. useOptimistic:')
console.log('   - Instant UI feedback')
console.log('   - Automatic rollback on failure')
console.log('   - Better user experience')

// ============================================
// 5. ref as a Regular Prop (No forwardRef)
// ============================================

// In React 19, ref is a regular prop - no forwardRef needed!
interface CustomInputProps {
  ref?: React.Ref<HTMLInputElement>
  label: string
  placeholder?: string
}

function CustomInput({ ref, label, placeholder }: CustomInputProps) {
  return (
    <div className="custom-input">
      <label>{label}</label>
      <input ref={ref} placeholder={placeholder} />
    </div>
  )
}

function FormWithRef() {
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFocus = () => {
    inputRef.current?.focus()
  }

  return (
    <div>
      <CustomInput
        ref={inputRef}
        label="Username"
        placeholder="Enter username"
      />
      <button onClick={handleFocus}>Focus Input</button>
    </div>
  )
}

console.log('5. ref as Regular Prop:')
console.log('   - No more forwardRef needed')
console.log('   - Simpler component definitions')
console.log('   - Better TypeScript experience')

// ============================================
// 6. useTransition with Actions
// ============================================

function SearchWithTransition() {
  const [results, setResults] = useState<string[]>([])
  const [isPending, startTransition] = useTransition()

  async function search(term: string) {
    // Simulate search
    await new Promise((resolve) => setTimeout(resolve, 300))
    return ['Result 1', 'Result 2', 'Result 3'].filter((r) =>
      r.toLowerCase().includes(term.toLowerCase())
    )
  }

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const term = e.target.value

    startTransition(async () => {
      const results = await search(term)
      setResults(results)
    })
  }

  return (
    <div>
      <input onChange={handleSearch} placeholder="Search..." />
      {isPending && <span>Searching...</span>}
      <ul>
        {results.map((result, i) => (
          <li key={i}>{result}</li>
        ))}
      </ul>
    </div>
  )
}

console.log('6. useTransition with async:')
console.log('   - Non-blocking state updates')
console.log('   - Async functions in transitions')
console.log('   - Built-in pending state')

// ============================================
// 7. Document Metadata
// ============================================

function PageWithMetadata({ title }: { title: string }) {
  // React 19 supports document metadata components
  return (
    <div>
      {/* These components update document metadata */}
      <title>{title}</title>
      <meta name="description" content="A page description" />
      <link rel="canonical" href="https://example.com/page" />

      <h1>{title}</h1>
      <p>Page content here...</p>
    </div>
  )
}

console.log('7. Document Metadata:')
console.log('   - <title>, <meta>, <link> in components')
console.log('   - Automatic hoisting to <head>')
console.log('   - SSR friendly')

// ============================================
// Demo
// ============================================

function React19Demo() {
  const [postId, setPostId] = useState(1)

  return (
    <div>
      <h1>React 19 Features Demo</h1>

      <section>
        <h2>Post Viewer (use() with Promise)</h2>
        <button onClick={() => setPostId((id) => id + 1)}>Next Post</button>
        <PostPage postId={postId} />
      </section>

      <section>
        <h2>Contact Form (useActionState)</h2>
        <ContactForm />
      </section>

      <section>
        <h2>Todo List (useOptimistic)</h2>
        <TodoList
          initialTodos={[
            { id: '1', text: 'Learn React 19', completed: false },
            { id: '2', text: 'Build an app', completed: false },
            { id: '3', text: 'Deploy to production', completed: false },
          ]}
        />
      </section>

      <section>
        <h2>Custom Input (ref as prop)</h2>
        <FormWithRef />
      </section>

      <section>
        <h2>Search (useTransition)</h2>
        <SearchWithTransition />
      </section>
    </div>
  )
}

console.log('\nRun `make dev` to see React 19 features in action')

/**
 * Key Takeaways:
 *
 * 1. use() simplifies data fetching with Suspense
 * 2. use() can read context conditionally
 * 3. useActionState handles form state and pending automatically
 * 4. useOptimistic provides instant UI feedback
 * 5. ref is now a regular prop - no forwardRef needed
 * 6. useTransition works with async functions
 * 7. Document metadata components work everywhere
 */

export {
  PostContent,
  PostPage,
  UserDisplay,
  ContactForm,
  TodoList,
  CustomInput,
  FormWithRef,
  SearchWithTransition,
  React19Demo,
}
