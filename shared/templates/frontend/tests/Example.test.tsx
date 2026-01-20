import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { Example1 } from '../src/examples/Example1'
import { Example2 } from '../src/examples/Example2'
import { Example3 } from '../src/examples/Example3'

describe('Example1', () => {
  it('renders basic usage', () => {
    render(<Example1 />)
    expect(screen.getByText(/basic usage/i)).toBeInTheDocument()
  })
})

describe('Example2', () => {
  it('renders intermediate pattern', () => {
    render(<Example2 />)
    expect(screen.getByText(/intermediate/i)).toBeInTheDocument()
  })
})

describe('Example3', () => {
  it('renders advanced usage', () => {
    render(<Example3 />)
    expect(screen.getByText(/advanced/i)).toBeInTheDocument()
  })
})
