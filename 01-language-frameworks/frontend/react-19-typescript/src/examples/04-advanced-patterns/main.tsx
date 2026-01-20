/**
 * Example 4: Advanced Patterns
 *
 * This example demonstrates advanced React patterns including:
 * - Compound components
 * - Render props
 * - Higher-order components
 * - Error boundaries
 * - Portals
 * - Performance optimization
 */

import React, {
  useState,
  useContext,
  createContext,
  useCallback,
  useMemo,
  memo,
  lazy,
  Suspense,
  createPortal,
  Component,
  ErrorInfo,
} from 'react'

console.log('=== Example 4: Advanced Patterns ===\n')

// ============================================
// 1. Compound Components
// ============================================

interface AccordionContextValue {
  openItems: Set<string>
  toggleItem: (id: string) => void
}

const AccordionContext = createContext<AccordionContextValue | null>(null)

function useAccordion() {
  const context = useContext(AccordionContext)
  if (!context) {
    throw new Error('useAccordion must be used within Accordion')
  }
  return context
}

interface AccordionProps {
  children: React.ReactNode
  allowMultiple?: boolean
}

function Accordion({ children, allowMultiple = false }: AccordionProps) {
  const [openItems, setOpenItems] = useState<Set<string>>(new Set())

  const toggleItem = useCallback(
    (id: string) => {
      setOpenItems((prev) => {
        const next = new Set(allowMultiple ? prev : [])
        if (prev.has(id)) {
          next.delete(id)
        } else {
          next.add(id)
        }
        return next
      })
    },
    [allowMultiple]
  )

  const value = useMemo(
    () => ({ openItems, toggleItem }),
    [openItems, toggleItem]
  )

  return (
    <AccordionContext.Provider value={value}>
      <div className="accordion">{children}</div>
    </AccordionContext.Provider>
  )
}

interface AccordionItemProps {
  id: string
  children: React.ReactNode
}

function AccordionItem({ id, children }: AccordionItemProps) {
  return (
    <div className="accordion-item" data-id={id}>
      {children}
    </div>
  )
}

interface AccordionTriggerProps {
  id: string
  children: React.ReactNode
}

function AccordionTrigger({ id, children }: AccordionTriggerProps) {
  const { openItems, toggleItem } = useAccordion()
  const isOpen = openItems.has(id)

  return (
    <button
      className="accordion-trigger"
      onClick={() => toggleItem(id)}
      aria-expanded={isOpen}
    >
      {children}
      <span>{isOpen ? '-' : '+'}</span>
    </button>
  )
}

interface AccordionContentProps {
  id: string
  children: React.ReactNode
}

function AccordionContent({ id, children }: AccordionContentProps) {
  const { openItems } = useAccordion()
  const isOpen = openItems.has(id)

  if (!isOpen) return null

  return <div className="accordion-content">{children}</div>
}

// Attach sub-components
Accordion.Item = AccordionItem
Accordion.Trigger = AccordionTrigger
Accordion.Content = AccordionContent

console.log('1. Compound Components:')
console.log('   - Components that work together')
console.log('   - Shared state via context')
console.log('   - Clean, declarative API')

// ============================================
// 2. Render Props Pattern
// ============================================

interface MousePosition {
  x: number
  y: number
}

interface MouseTrackerProps {
  render: (position: MousePosition) => React.ReactNode
}

function MouseTracker({ render }: MouseTrackerProps) {
  const [position, setPosition] = useState<MousePosition>({ x: 0, y: 0 })

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    setPosition({ x: e.clientX, y: e.clientY })
  }, [])

  return <div onMouseMove={handleMouseMove}>{render(position)}</div>
}

// Alternative: children as function
interface MouseTrackerChildrenProps {
  children: (position: MousePosition) => React.ReactNode
}

function MouseTrackerChildren({ children }: MouseTrackerChildrenProps) {
  const [position, setPosition] = useState<MousePosition>({ x: 0, y: 0 })

  return (
    <div onMouseMove={(e) => setPosition({ x: e.clientX, y: e.clientY })}>
      {children(position)}
    </div>
  )
}

console.log('2. Render Props:')
console.log('   - Pass rendering logic as function')
console.log('   - Flexible component reuse')
console.log('   - Children as function variant')

// ============================================
// 3. Higher-Order Components (HOC)
// ============================================

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
      return <div className="loading">Loading...</div>
    }
    return <WrappedComponent {...(props as P)} />
  }
}

// HOC with options
interface WithAuthOptions {
  redirectTo?: string
}

function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  options: WithAuthOptions = {}
) {
  return function WithAuthComponent(props: P & { isAuthenticated: boolean }) {
    const { isAuthenticated, ...rest } = props

    if (!isAuthenticated) {
      return <div>Please log in to view this content</div>
    }

    return <WrappedComponent {...(rest as P)} />
  }
}

// Example usage
interface UserProfileProps {
  userId: number
  userName: string
}

function UserProfile({ userId, userName }: UserProfileProps) {
  return (
    <div>
      <h3>{userName}</h3>
      <p>ID: {userId}</p>
    </div>
  )
}

const UserProfileWithLoading = withLoading(UserProfile)
const UserProfileWithAuth = withAuth(UserProfile)

console.log('3. Higher-Order Components:')
console.log('   - Wrap components to add functionality')
console.log('   - Type-safe with generics')
console.log('   - Composable patterns')

// ============================================
// 4. Error Boundaries
// ============================================

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
    this.props.onError?.(error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <details>
            <summary>Error details</summary>
            <pre>{this.state.error?.message}</pre>
          </details>
          <button onClick={() => this.setState({ hasError: false, error: null })}>
            Try again
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

// Hook to throw error for testing
function ErrorThrower({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error from ErrorThrower')
  }
  return <div>No error!</div>
}

console.log('4. Error Boundaries:')
console.log('   - Catch errors in component tree')
console.log('   - Display fallback UI')
console.log('   - Log errors for debugging')

// ============================================
// 5. Portals
// ============================================

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
}

function Modal({ isOpen, onClose, title, children }: ModalProps) {
  if (!isOpen) return null

  // Get or create portal container
  let container = document.getElementById('modal-root')
  if (!container) {
    container = document.createElement('div')
    container.id = 'modal-root'
    document.body.appendChild(container)
  }

  return createPortal(
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{title}</h2>
          <button onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>,
    container
  )
}

// Tooltip using portal
interface TooltipProps {
  content: string
  children: React.ReactElement
}

function Tooltip({ content, children }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [position, setPosition] = useState({ top: 0, left: 0 })

  const showTooltip = (e: React.MouseEvent) => {
    setPosition({ top: e.clientY + 10, left: e.clientX + 10 })
    setIsVisible(true)
  }

  const hideTooltip = () => setIsVisible(false)

  return (
    <>
      {React.cloneElement(children, {
        onMouseEnter: showTooltip,
        onMouseLeave: hideTooltip,
      })}
      {isVisible &&
        createPortal(
          <div
            className="tooltip"
            style={{ position: 'fixed', top: position.top, left: position.left }}
          >
            {content}
          </div>,
          document.body
        )}
    </>
  )
}

console.log('5. Portals:')
console.log('   - Render outside parent DOM')
console.log('   - Useful for modals, tooltips')
console.log('   - Events still bubble to React tree')

// ============================================
// 6. Performance Optimization
// ============================================

// Memoized component
interface ExpensiveItemProps {
  id: number
  name: string
  onClick: (id: number) => void
}

const ExpensiveItem = memo(function ExpensiveItem({
  id,
  name,
  onClick,
}: ExpensiveItemProps) {
  console.log(`Rendering ExpensiveItem ${id}`)
  return (
    <div onClick={() => onClick(id)}>
      {name}
    </div>
  )
})

// Custom comparison function
interface UserItemProps {
  user: { id: number; name: string; lastLogin: Date }
}

const UserItem = memo(
  function UserItem({ user }: UserItemProps) {
    return <div>{user.name}</div>
  },
  // Only re-render if id or name changes, ignore lastLogin
  (prevProps, nextProps) =>
    prevProps.user.id === nextProps.user.id &&
    prevProps.user.name === nextProps.user.name
)

// List with stable callbacks
function OptimizedList({ items }: { items: Array<{ id: number; name: string }> }) {
  const [selectedId, setSelectedId] = useState<number | null>(null)

  // Stable callback reference
  const handleClick = useCallback((id: number) => {
    setSelectedId(id)
  }, [])

  // Memoized filtered items
  const visibleItems = useMemo(
    () => items.filter((item) => item.name.length > 0),
    [items]
  )

  return (
    <div>
      {visibleItems.map((item) => (
        <ExpensiveItem
          key={item.id}
          id={item.id}
          name={item.name}
          onClick={handleClick}
        />
      ))}
      <p>Selected: {selectedId}</p>
    </div>
  )
}

console.log('6. Performance Optimization:')
console.log('   - memo() prevents unnecessary re-renders')
console.log('   - useCallback for stable function refs')
console.log('   - useMemo for expensive computations')

// ============================================
// 7. Code Splitting with Lazy
// ============================================

// Lazy load components
const LazyDashboard = lazy(() =>
  import('./Dashboard').catch(() => ({
    default: () => <div>Failed to load Dashboard</div>,
  }))
)

const LazySettings = lazy(() =>
  import('./Settings').catch(() => ({
    default: () => <div>Failed to load Settings</div>,
  }))
)

function AppWithLazyLoading({ route }: { route: 'dashboard' | 'settings' }) {
  return (
    <Suspense fallback={<div className="loading">Loading page...</div>}>
      {route === 'dashboard' ? <LazyDashboard /> : <LazySettings />}
    </Suspense>
  )
}

console.log('7. Code Splitting:')
console.log('   - lazy() for dynamic imports')
console.log('   - Suspense for loading states')
console.log('   - Smaller initial bundle')

// ============================================
// Demo
// ============================================

function AdvancedPatternsDemo() {
  const [showModal, setShowModal] = useState(false)
  const [throwError, setThrowError] = useState(false)

  return (
    <div>
      <h1>Advanced Patterns Demo</h1>

      {/* Compound Components */}
      <section>
        <h2>Accordion (Compound Components)</h2>
        <Accordion allowMultiple>
          <Accordion.Item id="1">
            <Accordion.Trigger id="1">What is React?</Accordion.Trigger>
            <Accordion.Content id="1">
              A JavaScript library for building user interfaces.
            </Accordion.Content>
          </Accordion.Item>
          <Accordion.Item id="2">
            <Accordion.Trigger id="2">What is TypeScript?</Accordion.Trigger>
            <Accordion.Content id="2">
              A typed superset of JavaScript.
            </Accordion.Content>
          </Accordion.Item>
        </Accordion>
      </section>

      {/* Render Props */}
      <section>
        <h2>Mouse Tracker (Render Props)</h2>
        <MouseTracker
          render={({ x, y }) => (
            <p>
              Mouse position: ({x}, {y})
            </p>
          )}
        />
      </section>

      {/* Error Boundary */}
      <section>
        <h2>Error Boundary</h2>
        <button onClick={() => setThrowError(!throwError)}>
          {throwError ? 'Clear Error' : 'Trigger Error'}
        </button>
        <ErrorBoundary fallback={<div>Caught an error!</div>}>
          <ErrorThrower shouldThrow={throwError} />
        </ErrorBoundary>
      </section>

      {/* Modal (Portal) */}
      <section>
        <h2>Modal (Portal)</h2>
        <button onClick={() => setShowModal(true)}>Open Modal</button>
        <Modal
          isOpen={showModal}
          onClose={() => setShowModal(false)}
          title="Example Modal"
        >
          <p>This is rendered in a portal!</p>
        </Modal>
      </section>

      {/* Tooltip */}
      <section>
        <h2>Tooltip (Portal)</h2>
        <Tooltip content="This is a tooltip!">
          <button>Hover me</button>
        </Tooltip>
      </section>
    </div>
  )
}

console.log('\nRun `make dev` to see advanced patterns in action')

/**
 * Key Takeaways:
 *
 * 1. Compound components share state via context
 * 2. Render props provide flexible rendering control
 * 3. HOCs add reusable functionality to components
 * 4. Error boundaries catch errors in the component tree
 * 5. Portals render outside the parent DOM hierarchy
 * 6. memo, useCallback, useMemo optimize performance
 * 7. lazy and Suspense enable code splitting
 */

export {
  Accordion,
  MouseTracker,
  withLoading,
  withAuth,
  ErrorBoundary,
  Modal,
  Tooltip,
  ExpensiveItem,
  OptimizedList,
  AdvancedPatternsDemo,
}
