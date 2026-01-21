# Vite 7 Concepts

This document covers the fundamental concepts you need to understand when working with Vite.

## How Vite Works

### Development Mode

During development, Vite takes a fundamentally different approach than traditional bundlers:

```
Traditional Bundler:
┌─────────────────────────────────────────────────────┐
│  All source files → Bundle → Dev Server → Browser  │
│  (Can take minutes for large projects)             │
└─────────────────────────────────────────────────────┘

Vite:
┌─────────────────────────────────────────────────────┐
│  Request → Transform single file → Serve           │
│  (Instant regardless of project size)              │
└─────────────────────────────────────────────────────┘
```

#### Native ES Modules

Modern browsers support ES modules natively. Vite leverages this by serving your source files directly:

```html
<!-- Vite transforms and serves this directly -->
<script type="module" src="/src/main.ts"></script>
```

The browser requests each module as needed, and Vite transforms and serves them on-demand.

#### Dependency Pre-Bundling

While your source code is served as ES modules, dependencies from `node_modules` are pre-bundled using esbuild:

1. **CommonJS to ESM**: Converts CommonJS modules to ES modules
2. **Many files to one**: Bundles packages with many internal modules (e.g., lodash)
3. **Caching**: Pre-bundled dependencies are cached in `node_modules/.vite`

```typescript
// This import triggers pre-bundling of lodash
import { debounce } from 'lodash-es'
```

### Production Mode

For production, Vite uses Rollup to create optimized bundles:

```
Source Files → Rollup → Optimized Bundle
                 ↓
         - Tree shaking
         - Code splitting
         - Minification
         - Asset optimization
```

## Configuration System

### The defineConfig Function

Always use `defineConfig` for type safety:

```typescript
import { defineConfig } from 'vite'

export default defineConfig({
  // Full TypeScript support and autocomplete
})
```

### Conditional Configuration

Use function syntax for mode-specific configuration:

```typescript
export default defineConfig(({ command, mode, isSsrBuild, isPreview }) => {
  // command: 'serve' | 'build'
  // mode: 'development' | 'production' | custom

  if (command === 'serve') {
    return {
      // Dev-specific config
    }
  } else {
    return {
      // Build-specific config
    }
  }
})
```

### Configuration Merging

Vite merges configuration from multiple sources:

1. Inline config (highest priority)
2. Config file (`vite.config.ts`)
3. Environment-specific files (`.env.production`)
4. Default configuration

## Module Resolution

### Import Aliases

Configure path aliases for cleaner imports:

```typescript
// vite.config.ts
export default defineConfig({
  resolve: {
    alias: {
      '@': '/src',
      '@components': '/src/components',
      '@utils': '/src/utils',
    },
  },
})
```

Remember to update `tsconfig.json` for TypeScript support:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"]
    }
  }
}
```

### Conditional Exports

Vite respects the `exports` field in package.json:

```json
{
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs"
    }
  }
}
```

## Hot Module Replacement (HMR)

### How HMR Works

When you modify a file:

1. Vite detects the change
2. Invalidates the module and its importers
3. Sends update to browser via WebSocket
4. Browser re-fetches changed modules
5. Application state is preserved (when possible)

### HMR API

For custom HMR behavior:

```typescript
if (import.meta.hot) {
  // Accept updates for this module
  import.meta.hot.accept()

  // Accept updates for a dependency
  import.meta.hot.accept('./dep.ts', (newModule) => {
    // Handle the updated module
  })

  // Clean up side effects
  import.meta.hot.dispose((data) => {
    // Save state for hot reload
    data.savedState = myState
  })

  // Restore state after reload
  if (import.meta.hot.data.savedState) {
    myState = import.meta.hot.data.savedState
  }
}
```

### Framework Integration

Frameworks like React handle HMR automatically via plugins:

```typescript
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    react({
      // Fast Refresh is enabled by default
    }),
  ],
})
```

## Environment Variables

### Loading Priority

1. `.env` - Loaded in all cases
2. `.env.local` - Loaded in all cases, ignored by git
3. `.env.[mode]` - Only loaded in specified mode
4. `.env.[mode].local` - Only loaded in specified mode, ignored by git

### Client-Side Access

Only `VITE_` prefixed variables are exposed to client code:

```bash
# .env
DB_PASSWORD=secret     # NOT exposed
VITE_API_URL=https://api.example.com  # Exposed
```

```typescript
// In browser code
console.log(import.meta.env.VITE_API_URL)  // Works
console.log(import.meta.env.DB_PASSWORD)   // undefined
```

### Type Safety

Create `env.d.ts` for TypeScript support:

```typescript
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_APP_TITLE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

## Asset Handling

### Static Assets

Assets in the `public` directory are served at root:

```
public/
  favicon.ico    → /favicon.ico
  images/
    logo.png     → /images/logo.png
```

### Imported Assets

Assets imported in code are processed:

```typescript
import imgUrl from './img.png'
// imgUrl will be '/assets/img.2d8efhg.png' after build

import workerUrl from './worker.js?worker'
// Imports as a Web Worker

import rawContent from './file.txt?raw'
// Imports as string

import jsonData from './data.json'
// Imports as parsed JSON
```

### Asset Inlining

Small assets are inlined as base64:

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    assetsInlineLimit: 4096,  // 4kb threshold
  },
})
```

## Build Optimization

### Code Splitting

Vite automatically splits code at:

- Dynamic imports
- Entry points
- CSS imported in JS

Manual control:

```typescript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          utils: ['lodash-es', 'date-fns'],
        },
      },
    },
  },
})
```

### Tree Shaking

Vite's Rollup build removes unused code:

```typescript
// Only `used` is included in bundle
import { used, unused } from './utils'
console.log(used())
```

Ensure you use ES module imports for tree shaking to work.

### CSS Code Splitting

CSS is automatically extracted and split alongside JS chunks:

```typescript
// This CSS will be in its own chunk
const Component = () => import('./Component.tsx')
```
