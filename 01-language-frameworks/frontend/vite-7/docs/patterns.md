# Vite 7 Patterns

This document contains common patterns and best practices for Vite projects.

## Configuration Patterns

### Multi-Environment Configuration

Handle different environments with a clean pattern:

```typescript
// vite.config.ts
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  // Load env file based on mode
  const env = loadEnv(mode, process.cwd(), '')

  return {
    define: {
      __APP_ENV__: JSON.stringify(env.APP_ENV),
    },
    server: {
      port: parseInt(env.VITE_PORT) || 3000,
    },
  }
})
```

### Multi-Page Application

Configure multiple entry points:

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        admin: resolve(__dirname, 'admin/index.html'),
        login: resolve(__dirname, 'login/index.html'),
      },
    },
  },
})
```

### Library Mode

Build a library for distribution:

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import { resolve } from 'path'
import dts from 'vite-plugin-dts'

export default defineConfig({
  plugins: [dts()],
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      name: 'MyLib',
      fileName: (format) => `my-lib.${format}.js`,
    },
    rollupOptions: {
      external: ['react', 'react-dom'],
      output: {
        globals: {
          react: 'React',
          'react-dom': 'ReactDOM',
        },
      },
    },
  },
})
```

## Server Patterns

### API Proxy with Rewriting

Route API calls to a backend server:

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      // Simple proxy
      '/api': 'http://localhost:8080',

      // With path rewriting
      '/api/v1': {
        target: 'http://api.example.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/v1/, ''),
      },

      // WebSocket proxy
      '/socket.io': {
        target: 'ws://localhost:8080',
        ws: true,
      },

      // With custom handler
      '/fallback': {
        target: 'http://localhost:8080',
        bypass(req, res, options) {
          if (req.headers.accept?.includes('text/html')) {
            return '/index.html'
          }
        },
      },
    },
  },
})
```

### HTTPS Development Server

Enable HTTPS for local development:

```typescript
// vite.config.ts
import basicSsl from '@vitejs/plugin-basic-ssl'

export default defineConfig({
  plugins: [basicSsl()],
  server: {
    https: true,
    port: 443,
  },
})
```

### Custom Middleware

Add server middleware for development:

```typescript
// vite.config.ts
import type { Plugin } from 'vite'

function apiMockPlugin(): Plugin {
  return {
    name: 'api-mock',
    configureServer(server) {
      server.middlewares.use('/api/users', (req, res) => {
        res.setHeader('Content-Type', 'application/json')
        res.end(JSON.stringify([{ id: 1, name: 'John' }]))
      })
    },
  }
}

export default defineConfig({
  plugins: [apiMockPlugin()],
})
```

## Plugin Patterns

### Transform Plugin

Transform file content during build:

```typescript
import type { Plugin } from 'vite'

function markdownPlugin(): Plugin {
  return {
    name: 'vite-plugin-markdown',

    transform(code, id) {
      if (!id.endsWith('.md')) return null

      // Transform markdown to a module
      const html = parseMarkdown(code)
      return {
        code: `export default ${JSON.stringify(html)}`,
        map: null,
      }
    },
  }
}
```

### Virtual Module Plugin

Create virtual modules that don't exist on disk:

```typescript
import type { Plugin } from 'vite'

function virtualModulePlugin(): Plugin {
  const virtualModuleId = 'virtual:my-module'
  const resolvedVirtualModuleId = '\0' + virtualModuleId

  return {
    name: 'my-virtual-module',

    resolveId(id) {
      if (id === virtualModuleId) {
        return resolvedVirtualModuleId
      }
    },

    load(id) {
      if (id === resolvedVirtualModuleId) {
        return `export const msg = "from virtual module"`
      }
    },
  }
}

// Usage in code:
// import { msg } from 'virtual:my-module'
```

### Build Hook Plugin

Modify output during build:

```typescript
import type { Plugin } from 'vite'

function buildInfoPlugin(): Plugin {
  return {
    name: 'build-info',
    apply: 'build', // Only run during build

    generateBundle(options, bundle) {
      // Add build info to manifest
      this.emitFile({
        type: 'asset',
        fileName: 'build-info.json',
        source: JSON.stringify({
          timestamp: new Date().toISOString(),
          files: Object.keys(bundle),
        }),
      })
    },
  }
}
```

## Performance Patterns

### Dependency Pre-Bundling Optimization

Control what gets pre-bundled:

```typescript
// vite.config.ts
export default defineConfig({
  optimizeDeps: {
    // Force include (for dynamic imports)
    include: ['lodash-es', 'axios'],

    // Exclude from pre-bundling
    exclude: ['@my-org/internal-lib'],

    // Custom esbuild options
    esbuildOptions: {
      target: 'esnext',
    },
  },
})
```

### Chunk Size Warning

Configure chunk size limits:

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    chunkSizeWarningLimit: 500, // KB

    rollupOptions: {
      output: {
        // Control chunk names
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
      },
    },
  },
})
```

### Dynamic Import with Preload

Preload critical dynamic imports:

```typescript
// In your code
const AdminModule = () => import(
  /* webpackPreload: true */
  './AdminModule'
)

// Vite automatically generates preload hints
// <link rel="modulepreload" href="/assets/AdminModule-abc123.js">
```

## Testing Patterns

### Vitest Configuration

Configure Vitest within vite.config.ts:

```typescript
/// <reference types="vitest" />
import { defineConfig } from 'vite'

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules', 'tests'],
    },

    // Setup files
    setupFiles: ['./tests/setup.ts'],

    // Include patterns
    include: ['**/*.{test,spec}.{js,ts,jsx,tsx}'],
  },
})
```

### Mock Modules

Mock dependencies in tests:

```typescript
// tests/setup.ts
import { vi } from 'vitest'

// Mock environment variables
vi.stubEnv('VITE_API_URL', 'http://test-api.com')

// Mock modules
vi.mock('@/api', () => ({
  fetchUser: vi.fn().mockResolvedValue({ id: 1, name: 'Test' }),
}))
```

## Error Handling Patterns

### Graceful Plugin Errors

Handle errors in plugins gracefully:

```typescript
function safePlugin(): Plugin {
  return {
    name: 'safe-plugin',

    transform(code, id) {
      try {
        return transformCode(code)
      } catch (error) {
        this.error({
          message: `Failed to transform ${id}`,
          stack: error.stack,
        })
      }
    },
  }
}
```

### Build Error Overlay

Customize error display during development:

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    hmr: {
      overlay: true, // Show error overlay (default)
    },
  },
})
```

## SSR Patterns

### Server-Side Rendering Setup

Basic SSR configuration:

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    ssr: true,
    rollupOptions: {
      input: '/src/entry-server.ts',
    },
  },
  ssr: {
    // Externalize dependencies for SSR
    external: ['react', 'react-dom'],

    // Force bundle these for SSR
    noExternal: ['@my-org/ui-lib'],
  },
})
```

### SSR Entry Point

Create a proper SSR entry:

```typescript
// src/entry-server.ts
import { renderToString } from 'react-dom/server'
import App from './App'

export function render(url: string) {
  const html = renderToString(<App url={url} />)
  return { html }
}
```
