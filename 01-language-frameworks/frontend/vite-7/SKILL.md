---
name: building-with-vite
description: This skill teaches modern frontend build tooling with Vite 7, focusing on development workflow, configuration, and production optimization. Use when writing or improving tests.
---

# Vite 7

## Quick Start
```typescript
import { defineConfig } from 'vite'

export default defineConfig({
  root: './src',
  build: {
    outDir: '../dist',
    emptyOutDir: true,
  },
})
```

## Commands
```bash
make setup      # Install dependencies
make dev        # Start dev server with HMR
make build      # Build for production
make preview    # Preview production build
make examples   # Run all examples
make example-1  # Run basic setup example
```

## Key Points
- Native ESM Dev Server
- Hot Module Replacement (HMR)
- Pre-bundling

## More Detail
- [docs/concepts.md](docs/concepts.md) - Core concepts and theory
- [docs/patterns.md](docs/patterns.md) - Full code patterns and examples