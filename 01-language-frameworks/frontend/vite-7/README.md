# Vite 7

Master modern frontend build tooling with Vite 7 - the lightning-fast build tool that revolutionizes frontend development with instant server start and blazing-fast HMR.

## Learning Objectives

After completing this skill, you will be able to:
- Set up and configure Vite projects from scratch
- Understand and customize the Vite development server
- Leverage Hot Module Replacement (HMR) effectively
- Configure build optimization for production
- Use and create Vite plugins
- Integrate Vite with various frameworks (React, Vue, etc.)

## Prerequisites

- Node.js 20+
- npm or pnpm package manager
- Basic understanding of JavaScript/TypeScript
- Familiarity with module systems (ES modules)

## Quick Start

```bash
# Install dependencies
make setup

# Start development server
make dev

# Run examples
make examples

# Run tests
make test

# Build for production
make build
```

## Concepts

### Why Vite?

Vite addresses the slow feedback loop in traditional bundlers by leveraging native ES modules in the browser during development. Key benefits:

- **Instant Server Start**: No bundling required during development
- **Lightning Fast HMR**: Updates in milliseconds, not seconds
- **Optimized Builds**: Pre-configured Rollup for production
- **Universal Plugin API**: Extends both dev and build

### Development vs Production

```
Development:                    Production:
┌─────────────────────┐        ┌─────────────────────┐
│  Native ES Modules  │        │   Rollup Bundling   │
│  (No bundling)      │        │   (Optimized)       │
│                     │        │                     │
│  Fast server start  │        │  Tree shaking       │
│  Instant HMR        │        │  Code splitting     │
│  On-demand loading  │        │  Minification       │
└─────────────────────┘        └─────────────────────┘
```

### Vite Configuration

The `vite.config.ts` file is the heart of your Vite project:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
```

### Environment Variables

Vite handles environment variables with the `VITE_` prefix:

```typescript
// .env
VITE_API_URL=https://api.example.com

// Usage in code
const apiUrl = import.meta.env.VITE_API_URL
```

## Examples

### Example 1: Basic Vite Setup

Demonstrates creating a Vite project from scratch with basic configuration.

```bash
make example-1
```

### Example 2: Custom Dev Server

Configure the development server with proxies, CORS, and HTTPS.

```bash
make example-2
```

### Example 3: Build Optimization

Advanced build configuration with code splitting, chunk optimization, and asset handling.

```bash
make example-3
```

### Example 4: Plugin Development

Create custom Vite plugins for development and build transformations.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Configure Multi-Page Application - Set up Vite for a multi-page app with shared dependencies
2. **Exercise 2**: Build Performance Optimization - Optimize bundle size and loading performance
3. **Exercise 3**: Custom Plugin Creation - Create a plugin that transforms markdown to HTML components

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Importing Node.js Built-ins in Browser Code

Vite is browser-first. Node.js APIs require polyfills:

```typescript
// Wrong - will fail in browser
import fs from 'fs'

// Correct - use browser-compatible alternatives or configure polyfills
import { fetchData } from './api'
```

### Missing VITE_ Prefix for Environment Variables

Only variables with `VITE_` prefix are exposed to client code:

```bash
# Not exposed to client
API_SECRET=secret123

# Exposed to client
VITE_API_URL=https://api.example.com
```

### Not Using defineConfig

Always wrap configuration for better TypeScript support:

```typescript
// Wrong - no type safety
export default {
  plugins: []
}

// Correct - full type safety and autocomplete
import { defineConfig } from 'vite'
export default defineConfig({
  plugins: []
})
```

## Further Reading

- [Official Vite Documentation](https://vitejs.dev/)
- [Vite Plugin API](https://vitejs.dev/guide/api-plugin.html)
- [Rollup Documentation](https://rollupjs.org/) (for build customization)
- Related skills in this repository:
  - [React 19 + TypeScript](../react-19-typescript/) - Build React apps with Vite
  - [Tailwind CSS 4](../tailwind-css-4/) - Style Vite projects with Tailwind
