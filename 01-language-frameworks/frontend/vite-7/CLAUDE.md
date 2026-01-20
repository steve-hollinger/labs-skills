# CLAUDE.md - Vite 7

This skill teaches modern frontend build tooling with Vite 7, focusing on development workflow, configuration, and production optimization.

## Key Concepts

- **Native ESM Dev Server**: Vite serves source files over native ES modules, eliminating bundling during development
- **Hot Module Replacement (HMR)**: Instant updates without full page reload, preserving application state
- **Pre-bundling**: Dependencies are pre-bundled with esbuild for faster loading
- **Rollup-based Production Builds**: Optimized, tree-shaken bundles for production
- **Plugin System**: Universal plugin API that works in both dev and build modes
- **Environment Variables**: Type-safe env vars with `VITE_` prefix

## Common Commands

```bash
make setup      # Install dependencies
make dev        # Start dev server with HMR
make build      # Build for production
make preview    # Preview production build
make examples   # Run all examples
make example-1  # Run basic setup example
make example-2  # Run dev server example
make example-3  # Run build optimization example
make example-4  # Run plugin development example
make test       # Run Vitest tests
make lint       # Run ESLint and TypeScript checks
make clean      # Remove build artifacts
```

## Project Structure

```
vite-7/
├── src/
│   ├── main.ts
│   └── examples/
│       ├── 01-basic-setup/
│       ├── 02-dev-server-config/
│       ├── 03-build-optimization/
│       └── 04-custom-plugins/
├── exercises/
│   ├── exercise-1-multi-page/
│   ├── exercise-2-performance/
│   ├── exercise-3-custom-plugin/
│   └── solutions/
├── tests/
│   └── vite-config.test.ts
├── docs/
│   ├── concepts.md
│   └── patterns.md
├── vite.config.ts
├── tsconfig.json
└── package.json
```

## Code Patterns

### Pattern 1: Basic Configuration
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

### Pattern 2: Development Server with Proxy
```typescript
import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

### Pattern 3: Conditional Configuration
```typescript
import { defineConfig } from 'vite'

export default defineConfig(({ command, mode }) => {
  const isDev = command === 'serve'
  const isProd = mode === 'production'

  return {
    define: {
      __DEV__: isDev,
    },
    build: {
      sourcemap: isDev ? 'inline' : false,
    },
  }
})
```

### Pattern 4: Manual Chunk Splitting
```typescript
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          utils: ['lodash', 'date-fns'],
        },
      },
    },
  },
})
```

### Pattern 5: Custom Plugin
```typescript
import type { Plugin } from 'vite'

function myPlugin(): Plugin {
  return {
    name: 'my-plugin',

    // Transform hook - modify source code
    transform(code, id) {
      if (id.endsWith('.md')) {
        return `export default ${JSON.stringify(code)}`
      }
    },

    // Config hook - modify Vite config
    config() {
      return {
        define: {
          __PLUGIN_VERSION__: '"1.0.0"',
        },
      }
    },
  }
}
```

## Common Mistakes

1. **Forgetting to prefix environment variables with VITE_**
   - Only `VITE_*` variables are exposed to client code
   - Other variables are available in vite.config.ts but not in browser code

2. **Using Node.js APIs in browser code**
   - `fs`, `path`, `process` etc. are not available in browser
   - Use `import.meta.env` instead of `process.env`

3. **Not using defineConfig wrapper**
   - Loses TypeScript type inference and autocomplete
   - Always import and use `defineConfig`

4. **Incorrect import paths in config**
   - Config runs in Node.js, not browser
   - Use correct module resolution

5. **Modifying config without understanding modes**
   - `command` can be `'serve'` or `'build'`
   - `mode` defaults to `'development'` or `'production'`

## When Users Ask About...

### "How do I start a new project?"
Point them to `make setup` and the basic setup example. The template creates a minimal Vite + TypeScript project.

### "Why is my environment variable undefined?"
Check that:
1. Variable is prefixed with `VITE_`
2. Using `import.meta.env.VITE_*` not `process.env`
3. Dev server was restarted after adding new env vars

### "How do I add a framework (React/Vue)?"
Install the official plugin and add to config:
```typescript
import react from '@vitejs/plugin-react'
export default defineConfig({
  plugins: [react()],
})
```

### "How do I optimize my bundle size?"
1. Check bundle with `npx vite-bundle-visualizer`
2. Use manual chunks for vendor code
3. Enable tree shaking by using ES module imports
4. Consider dynamic imports for code splitting

### "How do I set up path aliases?"
Configure both vite.config.ts and tsconfig.json:
```typescript
// vite.config.ts
export default defineConfig({
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})
```

### "Why is HMR not working?"
Check that:
1. Module exports are not mixed (default + named)
2. File changes are within Vite's watch scope
3. Browser console for HMR errors

## Testing Notes

- Tests use Vitest (Vite-native test runner)
- Config tests verify correct configuration patterns
- Plugin tests check transform and hook behaviors
- Run specific tests: `npx vitest run -t "test name"`

## Dependencies

Key dependencies in package.json:
- vite@^7.0.0: Core build tool
- @vitejs/plugin-react@^5.0.0: React integration
- vitest@^3.0.0: Vite-native testing
- typescript@^5.6.0: TypeScript support
- @types/node@^22.0.0: Node.js type definitions
