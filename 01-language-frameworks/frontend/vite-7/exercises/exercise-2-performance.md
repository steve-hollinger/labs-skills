# Exercise 2: Build Performance Optimization

## Objective

Optimize a Vite project's build output for production performance, focusing on bundle size, loading speed, and caching efficiency.

## Scenario

You have a React application with the following issues:
- Large initial bundle (2MB+)
- Slow first load
- Poor cache utilization after updates
- No code splitting for routes

## Requirements

1. Reduce initial bundle size to under 200KB
2. Implement route-based code splitting
3. Optimize vendor chunks for long-term caching
4. Configure asset optimization
5. Add build analysis tooling

## Starting Point

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    // TODO: Add optimization configuration
  },
})
```

## Tasks

### Task 1: Analyze Current Bundle

Install and configure `rollup-plugin-visualizer` to understand your current bundle composition.

```bash
npm install -D rollup-plugin-visualizer
```

### Task 2: Configure Code Splitting

Implement manual chunks to separate:
- Framework code (React, React DOM)
- UI library code
- Utility libraries
- Application code

### Task 3: Dynamic Imports for Routes

Convert route components to use dynamic imports:

```typescript
// Before
import Dashboard from './pages/Dashboard'

// After
const Dashboard = lazy(() => import('./pages/Dashboard'))
```

### Task 4: Asset Optimization

Configure:
- Asset inlining threshold
- Image optimization
- CSS code splitting
- Font loading strategy

### Task 5: Configure Build Targets

Optimize for modern browsers while maintaining compatibility:
- Use `target: 'esnext'` for modern features
- Configure legacy browser support if needed

## Hints

1. Use `manualChunks` function for flexible chunk splitting
2. Consider separating frequently vs. rarely changing code
3. Dynamic imports create automatic code splitting points
4. The `chunkSizeWarningLimit` helps catch oversized chunks
5. CSS modules are automatically code-split with their JS

## Expected Metrics

After optimization:
- Initial JS bundle: < 200KB (gzipped)
- Largest chunk: < 150KB
- Vendor chunks should change rarely
- Route chunks load on-demand

## Analysis Commands

```bash
# Build with analysis
npm run build -- --mode production

# Check bundle sizes
npx vite-bundle-visualizer

# Test production build
npm run preview
```

## Validation Checklist

- [ ] Initial bundle under 200KB gzipped
- [ ] Vendor chunk separate from application code
- [ ] Routes load lazily
- [ ] No duplicate code across chunks
- [ ] Build analysis report generated
- [ ] All tests pass after optimization
