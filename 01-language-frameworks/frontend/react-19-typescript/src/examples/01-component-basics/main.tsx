/**
 * Example 1: Component Basics
 *
 * This example demonstrates fundamental React component patterns with TypeScript,
 * including typed props, children, and basic component composition.
 */

import React from 'react'

console.log('=== Example 1: Component Basics ===\n')

// ============================================
// 1. Basic Typed Component
// ============================================

interface GreetingProps {
  name: string
  enthusiastic?: boolean
}

function Greeting({ name, enthusiastic = false }: GreetingProps) {
  const punctuation = enthusiastic ? '!' : '.'
  return (
    <h1>
      Hello, {name}{punctuation}
    </h1>
  )
}

console.log('1. Basic typed component:')
console.log('   Greeting component with required name and optional enthusiastic prop')

// ============================================
// 2. Component with Multiple Prop Types
// ============================================

interface UserCardProps {
  user: {
    id: number
    name: string
    email: string
    avatar?: string
  }
  showEmail?: boolean
  onEdit?: (userId: number) => void
}

function UserCard({ user, showEmail = true, onEdit }: UserCardProps) {
  return (
    <div className="user-card">
      {user.avatar && <img src={user.avatar} alt={user.name} />}
      <h3>{user.name}</h3>
      {showEmail && <p>{user.email}</p>}
      {onEdit && (
        <button onClick={() => onEdit(user.id)}>Edit</button>
      )}
    </div>
  )
}

console.log('2. Component with complex props:')
console.log('   UserCard with object prop, optional callback, and conditional rendering')

// ============================================
// 3. Component with Children
// ============================================

interface CardProps {
  title: string
  children: React.ReactNode
  footer?: React.ReactNode
}

function Card({ title, children, footer }: CardProps) {
  return (
    <div className="card">
      <div className="card-header">
        <h2>{title}</h2>
      </div>
      <div className="card-body">{children}</div>
      {footer && <div className="card-footer">{footer}</div>}
    </div>
  )
}

console.log('3. Component with children:')
console.log('   Card component accepts React.ReactNode for flexible children')

// ============================================
// 4. Generic Component
// ============================================

interface ListProps<T> {
  items: T[]
  renderItem: (item: T, index: number) => React.ReactNode
  keyExtractor: (item: T) => string | number
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={keyExtractor(item)}>{renderItem(item, index)}</li>
      ))}
    </ul>
  )
}

console.log('4. Generic component:')
console.log('   List<T> component works with any item type')

// ============================================
// 5. Component with Literal Types
// ============================================

interface ButtonProps {
  label: string
  variant: 'primary' | 'secondary' | 'danger'
  size: 'sm' | 'md' | 'lg'
  disabled?: boolean
  onClick?: () => void
}

function Button({
  label,
  variant,
  size,
  disabled = false,
  onClick,
}: ButtonProps) {
  const className = `btn btn-${variant} btn-${size}`
  return (
    <button className={className} disabled={disabled} onClick={onClick}>
      {label}
    </button>
  )
}

console.log('5. Component with literal types:')
console.log('   Button restricts variant to specific values')

// ============================================
// 6. Component with Default Props
// ============================================

interface AlertProps {
  message: string
  type?: 'info' | 'warning' | 'error' | 'success'
  dismissible?: boolean
  onDismiss?: () => void
}

function Alert({
  message,
  type = 'info',
  dismissible = false,
  onDismiss,
}: AlertProps) {
  return (
    <div className={`alert alert-${type}`} role="alert">
      <span>{message}</span>
      {dismissible && onDismiss && (
        <button onClick={onDismiss} aria-label="Dismiss">
          &times;
        </button>
      )}
    </div>
  )
}

console.log('6. Component with defaults:')
console.log('   Alert has sensible defaults for optional props')

// ============================================
// 7. Extending Native Element Props
// ============================================

interface CustomInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string
  error?: string
}

function CustomInput({ label, error, id, ...inputProps }: CustomInputProps) {
  const inputId = id || `input-${label.toLowerCase().replace(/\s+/g, '-')}`

  return (
    <div className="form-group">
      <label htmlFor={inputId}>{label}</label>
      <input id={inputId} {...inputProps} aria-invalid={!!error} />
      {error && <span className="error">{error}</span>}
    </div>
  )
}

console.log('7. Extending native props:')
console.log('   CustomInput extends HTMLInputElement attributes')

// ============================================
// 8. Discriminated Union Props
// ============================================

type NotificationProps =
  | { type: 'loading'; message: string }
  | { type: 'success'; message: string; onClose: () => void }
  | { type: 'error'; message: string; retry: () => void }

function Notification(props: NotificationProps) {
  switch (props.type) {
    case 'loading':
      return <div className="notification loading">{props.message}</div>
    case 'success':
      return (
        <div className="notification success">
          {props.message}
          <button onClick={props.onClose}>Close</button>
        </div>
      )
    case 'error':
      return (
        <div className="notification error">
          {props.message}
          <button onClick={props.retry}>Retry</button>
        </div>
      )
  }
}

console.log('8. Discriminated union props:')
console.log('   Notification has different props based on type')

// ============================================
// Demo Usage
// ============================================

function Demo() {
  const users = [
    { id: 1, name: 'Alice', email: 'alice@example.com' },
    { id: 2, name: 'Bob', email: 'bob@example.com' },
  ]

  return (
    <div>
      <Greeting name="Developer" enthusiastic />

      <Card title="Users">
        <List
          items={users}
          keyExtractor={(user) => user.id}
          renderItem={(user) => <UserCard user={user} />}
        />
      </Card>

      <Button label="Submit" variant="primary" size="md" />

      <Alert message="This is an info message" />

      <CustomInput
        label="Email"
        type="email"
        placeholder="Enter email"
        required
      />
    </div>
  )
}

console.log('\nDemo component combines all patterns')
console.log('Run `make dev` to see components in action')

/**
 * Key Takeaways:
 *
 * 1. Always define interfaces for component props
 * 2. Use optional properties (?) for non-required props
 * 3. Use React.ReactNode for children that can be anything
 * 4. Generic components provide type safety for any data type
 * 5. Literal types restrict props to specific values
 * 6. Extend native element types for custom form components
 * 7. Discriminated unions handle conditional props elegantly
 */

export {
  Greeting,
  UserCard,
  Card,
  List,
  Button,
  Alert,
  CustomInput,
  Notification,
  Demo,
}
