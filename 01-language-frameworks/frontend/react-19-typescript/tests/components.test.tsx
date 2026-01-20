/**
 * React Component Tests
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React, { useState } from 'react'

// ============================================
// Component Examples for Testing
// ============================================

interface ButtonProps {
  label: string
  onClick?: () => void
  disabled?: boolean
}

function Button({ label, onClick, disabled = false }: ButtonProps) {
  return (
    <button onClick={onClick} disabled={disabled}>
      {label}
    </button>
  )
}

interface CounterProps {
  initialCount?: number
}

function Counter({ initialCount = 0 }: CounterProps) {
  const [count, setCount] = useState(initialCount)

  return (
    <div>
      <span data-testid="count">{count}</span>
      <button onClick={() => setCount(c => c + 1)}>Increment</button>
      <button onClick={() => setCount(c => c - 1)}>Decrement</button>
      <button onClick={() => setCount(0)}>Reset</button>
    </div>
  )
}

interface FormProps {
  onSubmit: (data: { name: string; email: string }) => void
}

function SimpleForm({ onSubmit }: FormProps) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({ name, email })
  }

  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="name">Name</label>
      <input
        id="name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />

      <label htmlFor="email">Email</label>
      <input
        id="email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <button type="submit">Submit</button>
    </form>
  )
}

// ============================================
// Tests
// ============================================

describe('Button Component', () => {
  it('renders with label', () => {
    render(<Button label="Click me" />)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', async () => {
    const handleClick = vi.fn()
    render(<Button label="Click me" onClick={handleClick} />)

    await userEvent.click(screen.getByText('Click me'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('does not call onClick when disabled', async () => {
    const handleClick = vi.fn()
    render(<Button label="Click me" onClick={handleClick} disabled />)

    const button = screen.getByText('Click me')
    expect(button).toBeDisabled()

    await userEvent.click(button)
    expect(handleClick).not.toHaveBeenCalled()
  })
})

describe('Counter Component', () => {
  it('renders with initial count', () => {
    render(<Counter initialCount={5} />)
    expect(screen.getByTestId('count')).toHaveTextContent('5')
  })

  it('increments count when increment button is clicked', async () => {
    render(<Counter />)

    await userEvent.click(screen.getByText('Increment'))
    expect(screen.getByTestId('count')).toHaveTextContent('1')
  })

  it('decrements count when decrement button is clicked', async () => {
    render(<Counter initialCount={5} />)

    await userEvent.click(screen.getByText('Decrement'))
    expect(screen.getByTestId('count')).toHaveTextContent('4')
  })

  it('resets count when reset button is clicked', async () => {
    render(<Counter initialCount={10} />)

    await userEvent.click(screen.getByText('Increment'))
    await userEvent.click(screen.getByText('Reset'))

    expect(screen.getByTestId('count')).toHaveTextContent('0')
  })
})

describe('SimpleForm Component', () => {
  it('renders form fields', () => {
    render(<SimpleForm onSubmit={vi.fn()} />)

    expect(screen.getByLabelText('Name')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Submit' })).toBeInTheDocument()
  })

  it('updates input values when typing', async () => {
    render(<SimpleForm onSubmit={vi.fn()} />)

    const nameInput = screen.getByLabelText('Name')
    const emailInput = screen.getByLabelText('Email')

    await userEvent.type(nameInput, 'John Doe')
    await userEvent.type(emailInput, 'john@example.com')

    expect(nameInput).toHaveValue('John Doe')
    expect(emailInput).toHaveValue('john@example.com')
  })

  it('calls onSubmit with form data', async () => {
    const handleSubmit = vi.fn()
    render(<SimpleForm onSubmit={handleSubmit} />)

    await userEvent.type(screen.getByLabelText('Name'), 'John Doe')
    await userEvent.type(screen.getByLabelText('Email'), 'john@example.com')
    await userEvent.click(screen.getByRole('button', { name: 'Submit' }))

    expect(handleSubmit).toHaveBeenCalledWith({
      name: 'John Doe',
      email: 'john@example.com',
    })
  })
})

describe('Async Component Tests', () => {
  function AsyncComponent() {
    const [data, setData] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)

    const loadData = async () => {
      setLoading(true)
      await new Promise((resolve) => setTimeout(resolve, 100))
      setData('Loaded data')
      setLoading(false)
    }

    return (
      <div>
        {loading && <span>Loading...</span>}
        {data && <span data-testid="data">{data}</span>}
        <button onClick={loadData}>Load Data</button>
      </div>
    )
  }

  it('shows loading state and then data', async () => {
    render(<AsyncComponent />)

    await userEvent.click(screen.getByText('Load Data'))

    // Should show loading
    expect(screen.getByText('Loading...')).toBeInTheDocument()

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByTestId('data')).toHaveTextContent('Loaded data')
    })

    // Loading should be gone
    expect(screen.queryByText('Loading...')).not.toBeInTheDocument()
  })
})

describe('TypeScript Type Tests', () => {
  // These tests verify TypeScript catches type errors at compile time

  it('enforces prop types', () => {
    // This would cause a TypeScript error if uncommented:
    // @ts-expect-error - label is required
    // render(<Button />)

    // This is correct
    render(<Button label="Test" />)
    expect(screen.getByText('Test')).toBeInTheDocument()
  })

  it('allows optional props', () => {
    // onClick and disabled are optional
    render(<Button label="Test" />)
    render(<Button label="Test" onClick={() => {}} />)
    render(<Button label="Test" disabled />)

    expect(screen.getAllByText('Test')).toHaveLength(3)
  })
})

describe('Event Handler Types', () => {
  function InputWithEvents() {
    const [value, setValue] = useState('')
    const [focused, setFocused] = useState(false)

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setValue(e.target.value)
    }

    const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
      setFocused(true)
    }

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setFocused(false)
    }

    return (
      <div>
        <input
          value={value}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          data-testid="input"
        />
        <span data-testid="value">{value}</span>
        <span data-testid="focused">{focused ? 'focused' : 'not focused'}</span>
      </div>
    )
  }

  it('handles change events correctly', async () => {
    render(<InputWithEvents />)

    const input = screen.getByTestId('input')
    await userEvent.type(input, 'Hello')

    expect(screen.getByTestId('value')).toHaveTextContent('Hello')
  })

  it('handles focus and blur events', async () => {
    render(<InputWithEvents />)

    const input = screen.getByTestId('input')

    await userEvent.click(input)
    expect(screen.getByTestId('focused')).toHaveTextContent('focused')

    await userEvent.tab()
    expect(screen.getByTestId('focused')).toHaveTextContent('not focused')
  })
})
