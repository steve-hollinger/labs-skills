/**
 * React 19 + TypeScript Skill - Main App Component
 */

import React, { useState } from 'react'

interface Example {
  id: number
  title: string
  description: string
}

const examples: Example[] = [
  {
    id: 1,
    title: 'Component Basics',
    description: 'Typed components, props, and basic patterns',
  },
  {
    id: 2,
    title: 'Hooks Deep Dive',
    description: 'useState, useEffect, useReducer, and custom hooks',
  },
  {
    id: 3,
    title: 'React 19 Features',
    description: 'use(), Actions, useOptimistic, and more',
  },
  {
    id: 4,
    title: 'Advanced Patterns',
    description: 'Context, composition, and performance',
  },
]

function App() {
  const [selectedExample, setSelectedExample] = useState<number | null>(null)

  return (
    <div className="app">
      <header>
        <h1>React 19 + TypeScript</h1>
        <p>Modern React Development with Type Safety</p>
      </header>

      <main>
        <section>
          <h2>Examples</h2>
          <div className="example-grid">
            {examples.map((example) => (
              <div
                key={example.id}
                className={`example-card ${
                  selectedExample === example.id ? 'selected' : ''
                }`}
                onClick={() => setSelectedExample(example.id)}
              >
                <h3>Example {example.id}: {example.title}</h3>
                <p>{example.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2>Quick Start</h2>
          <pre>
{`# Install dependencies
make setup

# Start dev server
make dev

# Run examples
make examples

# Run tests
make test`}
          </pre>
        </section>

        <section>
          <h2>Key Features</h2>
          <ul>
            <li><strong>Type-Safe Components</strong> - Full TypeScript support for props and state</li>
            <li><strong>React 19 Hooks</strong> - use(), useActionState, useOptimistic</li>
            <li><strong>Custom Hooks</strong> - Reusable, typed hook patterns</li>
            <li><strong>Advanced Patterns</strong> - Compound components, render props, HOCs</li>
            <li><strong>Testing</strong> - Vitest with React Testing Library</li>
          </ul>
        </section>

        <section>
          <h2>Type Examples</h2>
          <pre>
{`// Typed component props
interface ButtonProps {
  label: string
  onClick: () => void
  variant?: 'primary' | 'secondary'
}

// Typed state
const [user, setUser] = useState<User | null>(null)

// Typed events
function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
  console.log(e.target.value)
}

// Custom hook with types
function useFetch<T>(url: string): { data: T | null; loading: boolean } {
  // ...
}`}
          </pre>
        </section>
      </main>

      <footer>
        <p>Run <code>make dev</code> to start developing</p>
      </footer>
    </div>
  )
}

export default App
