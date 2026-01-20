# Tailwind CSS 4

Master utility-first CSS with Tailwind CSS 4 - the modern approach to styling that enables rapid UI development with a comprehensive design system built directly into your HTML.

## Learning Objectives

After completing this skill, you will be able to:
- Build responsive, modern UIs with utility classes
- Configure and customize the Tailwind design system
- Implement responsive design with breakpoint prefixes
- Create dark mode support and theme switching
- Build reusable component patterns
- Optimize for production with minimal CSS output

## Prerequisites

- HTML and CSS fundamentals
- Basic understanding of responsive design
- Node.js 20+
- Familiarity with Vite (recommended)

## Quick Start

```bash
# Install dependencies
make setup

# Start development server
make dev

# Run examples
make examples

# Build for production
make build
```

## Concepts

### Utility-First CSS

Instead of writing custom CSS, compose utilities directly in HTML:

```html
<!-- Traditional CSS approach -->
<div class="card">
  <h2 class="card-title">Title</h2>
</div>

<!-- Tailwind utility approach -->
<div class="rounded-lg bg-white p-6 shadow-lg">
  <h2 class="text-xl font-bold text-gray-900">Title</h2>
</div>
```

### The Design System

Tailwind provides a comprehensive design system:

```
Spacing:     0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24...
Colors:      slate, gray, zinc, neutral, red, orange, amber...
Typography:  xs, sm, base, lg, xl, 2xl, 3xl, 4xl, 5xl...
Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)...
```

### Responsive Design

Apply styles at specific breakpoints:

```html
<!-- Stack on mobile, row on medium+ screens -->
<div class="flex flex-col md:flex-row">
  <div class="w-full md:w-1/2">Left</div>
  <div class="w-full md:w-1/2">Right</div>
</div>
```

### State Variants

Style based on element state:

```html
<button class="bg-blue-500 hover:bg-blue-600 active:bg-blue-700
               disabled:opacity-50 disabled:cursor-not-allowed">
  Click me
</button>
```

### Dark Mode

Support system or manual dark mode:

```html
<div class="bg-white dark:bg-gray-900">
  <p class="text-gray-900 dark:text-gray-100">
    Adapts to light/dark mode
  </p>
</div>
```

## Examples

### Example 1: Layout Fundamentals

Master Flexbox and Grid layouts with Tailwind utilities.

```bash
make example-1
```

### Example 2: Component Patterns

Build common UI components: cards, buttons, forms, navigation.

```bash
make example-2
```

### Example 3: Responsive Design

Create fully responsive layouts that work on all devices.

```bash
make example-3
```

### Example 4: Dark Mode & Theming

Implement theme switching and custom color schemes.

```bash
make example-4
```

## Exercises

See the [exercises](./exercises/) directory for practice problems:

1. **Exercise 1**: Build a Responsive Dashboard - Create a dashboard layout with sidebar, header, and content area
2. **Exercise 2**: Component Library - Build a set of reusable UI components
3. **Exercise 3**: Landing Page - Create a complete landing page with dark mode

Solutions are available in [exercises/solutions/](./exercises/solutions/).

## Common Mistakes

### Fighting Utility Classes

Don't mix traditional CSS with utilities unnecessarily:

```html
<!-- Avoid: mixing approaches -->
<div class="card p-4">...</div>

<!-- Better: use utilities consistently -->
<div class="rounded-lg bg-white p-4 shadow">...</div>
```

### Forgetting Mobile-First

Tailwind is mobile-first; unprefixed classes apply to all sizes:

```html
<!-- Wrong: hiding on mobile requires explicit mobile class -->
<div class="hidden md:block">...</div>

<!-- This shows on all sizes, then hides on md+ -->
<div class="block md:hidden">...</div>
```

### Overusing Custom CSS

Before writing custom CSS, check if Tailwind provides the utility:

```css
/* Instead of custom CSS */
.text-center-important { text-align: center !important; }

/* Use Tailwind's arbitrary values or important modifier */
/* class="!text-center" */
```

### Not Using Component Extraction

For repeated patterns, extract components instead of copying classes:

```tsx
// Extract to a component
function Button({ children, variant = 'primary' }) {
  const baseClasses = 'px-4 py-2 rounded-lg font-medium'
  const variants = {
    primary: 'bg-blue-500 text-white hover:bg-blue-600',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
  }
  return (
    <button className={`${baseClasses} ${variants[variant]}`}>
      {children}
    </button>
  )
}
```

## Further Reading

- [Official Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Tailwind CSS v4 Release Notes](https://tailwindcss.com/blog/tailwindcss-v4)
- [Headless UI](https://headlessui.com/) - Unstyled components for Tailwind
- Related skills in this repository:
  - [Vite 7](../vite-7/) - Build tooling for Tailwind projects
  - [React 19 + TypeScript](../react-19-typescript/) - Use Tailwind with React
