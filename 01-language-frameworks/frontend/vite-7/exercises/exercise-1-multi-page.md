# Exercise 1: Configure Multi-Page Application

## Objective

Configure Vite to build a multi-page application (MPA) with shared dependencies and separate entry points.

## Requirements

1. Create a Vite configuration that supports multiple HTML entry points:
   - `index.html` - Main landing page
   - `admin/index.html` - Admin dashboard
   - `login/index.html` - Authentication page

2. Configure shared dependencies to be bundled once (not duplicated in each page).

3. Set up path aliases that work across all pages.

4. Configure the dev server to handle all routes correctly.

## Starting Point

```typescript
// vite.config.ts
import { defineConfig } from 'vite'

export default defineConfig({
  // TODO: Configure multi-page setup
})
```

## Project Structure

```
project/
├── index.html
├── admin/
│   └── index.html
├── login/
│   └── index.html
├── src/
│   ├── main.ts
│   ├── admin/
│   │   └── main.ts
│   ├── login/
│   │   └── main.ts
│   └── shared/
│       ├── utils.ts
│       └── api.ts
└── vite.config.ts
```

## Tasks

### Task 1: Configure Entry Points

Modify `vite.config.ts` to define multiple input entries using Rollup's input option.

### Task 2: Set Up Shared Chunks

Configure `manualChunks` to ensure shared code is bundled once and reused across pages.

### Task 3: Add Path Aliases

Configure path aliases so imports like `@shared/utils` work in all pages.

### Task 4: Dev Server Configuration

Ensure the development server correctly serves all HTML files and handles navigation.

## Hints

1. Use `rollupOptions.input` to define multiple entry points
2. The `resolve` function from `path` helps with absolute paths
3. `manualChunks` can be a function for dynamic chunk assignment
4. Consider using `appType: 'mpa'` for multi-page applications

## Expected Output

When you run `npm run build`, you should see:

```
dist/
├── index.html
├── admin/
│   └── index.html
├── login/
│   └── index.html
└── assets/
    ├── main-[hash].js
    ├── admin-[hash].js
    ├── login-[hash].js
    └── shared-[hash].js    # Shared code only bundled once
```

## Validation

1. Run `npm run build` - should complete without errors
2. Run `npm run preview` - all pages should load correctly
3. Check that shared code is not duplicated in each page bundle
4. Verify path aliases work in all entry points
