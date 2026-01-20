# CLAUDE.md - Tailwind CSS 4

This skill teaches utility-first CSS with Tailwind CSS 4, covering responsive design, dark mode, component patterns, and production optimization.

## Key Concepts

- **Utility Classes**: Pre-built, single-purpose CSS classes
- **Responsive Design**: Mobile-first breakpoint prefixes (sm, md, lg, xl, 2xl)
- **State Variants**: Hover, focus, active, disabled, and other state modifiers
- **Dark Mode**: Built-in dark mode support with `dark:` prefix
- **Customization**: Extend the default theme via configuration
- **Component Patterns**: Reusable UI patterns built with utilities

## Common Commands

```bash
make setup      # Install dependencies
make dev        # Start dev server with HMR
make build      # Build for production
make examples   # Run all examples
make example-1  # Run layout fundamentals example
make example-2  # Run component patterns example
make example-3  # Run responsive design example
make example-4  # Run dark mode example
make test       # Run tests
make lint       # Run linting
make clean      # Remove build artifacts
```

## Project Structure

```
tailwind-css-4/
├── src/
│   ├── main.ts
│   ├── style.css
│   └── examples/
│       ├── 01-layout-fundamentals/
│       ├── 02-component-patterns/
│       ├── 03-responsive-design/
│       └── 04-dark-mode-theming/
├── exercises/
│   ├── exercise-1-dashboard/
│   ├── exercise-2-component-library/
│   ├── exercise-3-landing-page/
│   └── solutions/
├── tests/
│   └── utilities.test.ts
├── docs/
│   ├── concepts.md
│   └── patterns.md
├── tailwind.config.ts
├── vite.config.ts
├── tsconfig.json
└── package.json
```

## Code Patterns

### Pattern 1: Flex Layout
```html
<!-- Centered content -->
<div class="flex items-center justify-center min-h-screen">
  <div>Centered</div>
</div>

<!-- Space between items -->
<div class="flex items-center justify-between">
  <span>Left</span>
  <span>Right</span>
</div>

<!-- Column layout with gap -->
<div class="flex flex-col gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
</div>
```

### Pattern 2: Grid Layout
```html
<!-- 3-column grid -->
<div class="grid grid-cols-3 gap-4">
  <div>1</div>
  <div>2</div>
  <div>3</div>
</div>

<!-- Responsive grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <!-- Items -->
</div>

<!-- Auto-fit grid -->
<div class="grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))] gap-4">
  <!-- Items -->
</div>
```

### Pattern 3: Card Component
```html
<div class="rounded-lg bg-white p-6 shadow-lg dark:bg-gray-800">
  <img class="mb-4 h-48 w-full rounded-md object-cover" src="..." alt="">
  <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
    Card Title
  </h3>
  <p class="mt-2 text-gray-600 dark:text-gray-300">
    Card description...
  </p>
  <button class="mt-4 rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600">
    Action
  </button>
</div>
```

### Pattern 4: Form Inputs
```html
<div class="space-y-4">
  <div>
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      Email
    </label>
    <input
      type="email"
      class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2
             focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500
             dark:border-gray-600 dark:bg-gray-700 dark:text-white"
    >
  </div>
</div>
```

### Pattern 5: Button Variants
```html
<!-- Primary -->
<button class="rounded-lg bg-blue-500 px-4 py-2 font-medium text-white
               hover:bg-blue-600 active:bg-blue-700
               disabled:cursor-not-allowed disabled:opacity-50">
  Primary
</button>

<!-- Secondary -->
<button class="rounded-lg border border-gray-300 bg-white px-4 py-2
               font-medium text-gray-700 hover:bg-gray-50
               dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200">
  Secondary
</button>

<!-- Outline -->
<button class="rounded-lg border-2 border-blue-500 bg-transparent px-4 py-2
               font-medium text-blue-500 hover:bg-blue-50
               dark:hover:bg-blue-950">
  Outline
</button>
```

### Pattern 6: Responsive Navigation
```html
<nav class="bg-white shadow dark:bg-gray-800">
  <div class="mx-auto max-w-7xl px-4">
    <div class="flex h-16 items-center justify-between">
      <div class="flex-shrink-0">Logo</div>

      <!-- Desktop menu -->
      <div class="hidden md:flex md:space-x-4">
        <a href="#" class="text-gray-700 hover:text-blue-500 dark:text-gray-200">
          Home
        </a>
        <a href="#" class="text-gray-700 hover:text-blue-500 dark:text-gray-200">
          About
        </a>
      </div>

      <!-- Mobile menu button -->
      <button class="md:hidden">
        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
    </div>
  </div>
</nav>
```

## Common Mistakes

1. **Not using mobile-first approach**
   - Unprefixed classes apply to all screen sizes
   - Use `md:`, `lg:` for larger screens, not `sm:` for smaller

2. **Overriding with custom CSS**
   - Use Tailwind's configuration to extend theme
   - Use arbitrary values `[value]` for one-offs

3. **Not extracting repeated patterns**
   - Create React/Vue components for repeated UI
   - Use `@apply` sparingly in CSS

4. **Forgetting dark mode classes**
   - Always add `dark:` variants for colors
   - Test both light and dark modes

5. **Using `!important` unnecessarily**
   - Use `!` prefix for important: `!text-red-500`
   - Prefer proper specificity over important

## When Users Ask About...

### "How do I center something?"
```html
<!-- Flexbox center -->
<div class="flex items-center justify-center">Centered</div>

<!-- Grid center -->
<div class="grid place-items-center">Centered</div>

<!-- Absolute center -->
<div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
  Centered
</div>
```

### "How do I make a responsive layout?"
Use mobile-first breakpoints:
```html
<div class="flex flex-col md:flex-row">
  <div class="w-full md:w-1/3">Sidebar</div>
  <div class="w-full md:w-2/3">Content</div>
</div>
```

### "How do I add dark mode?"
1. Configure in tailwind.config.ts: `darkMode: 'class'` or `'media'`
2. Add dark variants: `class="bg-white dark:bg-gray-900"`
3. Toggle `.dark` class on `<html>` for class strategy

### "How do I customize colors?"
Extend the theme in tailwind.config.ts:
```typescript
export default {
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          500: '#0ea5e9',
          900: '#0c4a6e',
        },
      },
    },
  },
}
```

### "How do I add custom fonts?"
```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Poppins', 'sans-serif'],
      },
    },
  },
}

// Usage: class="font-sans" or class="font-display"
```

## Testing Notes

- Visual testing recommended for Tailwind
- Use snapshot tests for component output
- Test responsive breakpoints with viewport changes
- Test dark mode toggle functionality

## Dependencies

Key dependencies in package.json:
- tailwindcss@^4.0.0: Core utility framework
- @tailwindcss/vite@^4.0.0: Vite integration
- @tailwindcss/typography@^0.5.0: Prose styling
- @tailwindcss/forms@^0.5.0: Form element reset
- @tailwindcss/container-queries@^0.1.0: Container queries
