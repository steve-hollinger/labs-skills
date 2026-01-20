# Tailwind CSS 4 Concepts

This document covers fundamental concepts for building with Tailwind CSS.

## Utility-First CSS

### The Philosophy

Traditional CSS:
```css
.card {
  padding: 1.5rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

Utility-first approach:
```html
<div class="p-6 bg-white rounded-lg shadow-md">
  Content
</div>
```

### Benefits

1. **No naming**: Don't waste time on class names like `.sidebar-inner-wrapper`
2. **Local changes**: Styling is scoped to the element
3. **Smaller CSS**: Utilities are reused, CSS doesn't grow with features
4. **Design constraints**: Limited options enforce consistency

## The Design System

### Spacing Scale

Tailwind uses a consistent spacing scale:

```
Class     Size
p-0       0
p-px      1px
p-0.5     0.125rem  (2px)
p-1       0.25rem   (4px)
p-2       0.5rem    (8px)
p-3       0.75rem   (12px)
p-4       1rem      (16px)
p-5       1.25rem   (20px)
p-6       1.5rem    (24px)
p-8       2rem      (32px)
p-10      2.5rem    (40px)
p-12      3rem      (48px)
p-16      4rem      (64px)
p-20      5rem      (80px)
p-24      6rem      (96px)
```

Works with: `m-`, `p-`, `gap-`, `space-`, `w-`, `h-`, etc.

### Color System

Colors have shades from 50-950:

```
gray-50   Lightest
gray-100
gray-200
gray-300
gray-400
gray-500  Base
gray-600
gray-700
gray-800
gray-900
gray-950  Darkest
```

Available colors: slate, gray, zinc, neutral, stone, red, orange, amber, yellow, lime, green, emerald, teal, cyan, sky, blue, indigo, violet, purple, fuchsia, pink, rose

### Typography Scale

```
Class       Size
text-xs     0.75rem   (12px)
text-sm     0.875rem  (14px)
text-base   1rem      (16px)
text-lg     1.125rem  (18px)
text-xl     1.25rem   (20px)
text-2xl    1.5rem    (24px)
text-3xl    1.875rem  (30px)
text-4xl    2.25rem   (36px)
text-5xl    3rem      (48px)
```

## Responsive Design

### Mobile-First Approach

Unprefixed utilities apply to all screen sizes. Prefixed utilities apply at that breakpoint and above:

```
Default   → All sizes (mobile first)
sm:       → 640px and up
md:       → 768px and up
lg:       → 1024px and up
xl:       → 1280px and up
2xl:      → 1536px and up
```

### Examples

```html
<!-- Stack on mobile, row on tablet+ -->
<div class="flex flex-col md:flex-row">
  <div class="w-full md:w-1/2">Left</div>
  <div class="w-full md:w-1/2">Right</div>
</div>

<!-- Different padding at breakpoints -->
<div class="p-4 md:p-6 lg:p-8">
  Content
</div>

<!-- Show/hide at breakpoints -->
<div class="hidden md:block">Desktop only</div>
<div class="block md:hidden">Mobile only</div>
```

### Container Queries

Tailwind 4 supports container queries:

```html
<div class="@container">
  <div class="@md:flex @lg:grid">
    Responds to container width, not viewport
  </div>
</div>
```

## State Variants

### Hover, Focus, Active

```html
<button class="bg-blue-500 hover:bg-blue-600 active:bg-blue-700
               focus:outline-none focus:ring-2 focus:ring-blue-400">
  Click me
</button>
```

### Form States

```html
<input class="border-gray-300
              focus:border-blue-500 focus:ring-blue-500
              invalid:border-red-500 invalid:text-red-600
              disabled:bg-gray-100 disabled:cursor-not-allowed">
```

### Group and Peer

```html
<!-- Group: style children based on parent state -->
<div class="group">
  <p class="text-gray-500 group-hover:text-black">
    Changes when parent is hovered
  </p>
</div>

<!-- Peer: style siblings based on element state -->
<input class="peer" placeholder="Email">
<p class="invisible peer-invalid:visible text-red-500">
  Shows when input is invalid
</p>
```

### First, Last, Odd, Even

```html
<ul>
  <li class="first:pt-0 last:pb-0">Item</li>
  <li class="odd:bg-gray-50 even:bg-white">Item</li>
</ul>
```

## Dark Mode

### Configuration

```typescript
// tailwind.config.ts
export default {
  darkMode: 'class', // or 'media' for system preference
}
```

### Usage

```html
<div class="bg-white dark:bg-gray-900">
  <h1 class="text-gray-900 dark:text-white">Title</h1>
  <p class="text-gray-600 dark:text-gray-300">Content</p>
</div>
```

### Toggling

```javascript
// Toggle dark mode
document.documentElement.classList.toggle('dark')

// Set based on preference
if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
  document.documentElement.classList.add('dark')
}
```

## Layout Utilities

### Flexbox

```html
<!-- Direction -->
<div class="flex flex-row">Horizontal (default)</div>
<div class="flex flex-col">Vertical</div>

<!-- Justify (main axis) -->
<div class="flex justify-start">Start</div>
<div class="flex justify-center">Center</div>
<div class="flex justify-end">End</div>
<div class="flex justify-between">Space between</div>
<div class="flex justify-around">Space around</div>
<div class="flex justify-evenly">Space evenly</div>

<!-- Align (cross axis) -->
<div class="flex items-start">Top</div>
<div class="flex items-center">Center</div>
<div class="flex items-end">Bottom</div>
<div class="flex items-stretch">Stretch</div>

<!-- Wrap -->
<div class="flex flex-wrap">Wrap</div>
<div class="flex flex-nowrap">No wrap</div>

<!-- Gap -->
<div class="flex gap-4">4 unit gap</div>
<div class="flex gap-x-4 gap-y-2">Different x/y gaps</div>
```

### CSS Grid

```html
<!-- Columns -->
<div class="grid grid-cols-3">3 columns</div>
<div class="grid grid-cols-12">12 columns</div>

<!-- Rows -->
<div class="grid grid-rows-3">3 rows</div>

<!-- Span -->
<div class="col-span-2">Spans 2 columns</div>
<div class="col-span-full">Full width</div>

<!-- Auto -->
<div class="grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))]">
  Auto-fit responsive grid
</div>

<!-- Place items -->
<div class="grid place-items-center">Center all items</div>
```

## Arbitrary Values

For one-off values not in the design system:

```html
<!-- Arbitrary values -->
<div class="w-[137px]">Exact width</div>
<div class="bg-[#1da1f2]">Custom color</div>
<div class="text-[22px]">Custom size</div>
<div class="grid-cols-[1fr_2fr_1fr]">Custom columns</div>

<!-- Arbitrary properties -->
<div class="[mask-image:linear-gradient(180deg,white,transparent)]">
  Custom CSS property
</div>
```

## Important Modifier

Use `!` prefix to make a utility `!important`:

```html
<div class="!text-red-500">Always red</div>
<div class="sm:hover:!text-blue-500">Important on hover at sm+</div>
```

## Customization

### Extending Theme

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        brand: '#1da1f2',
      },
      spacing: {
        '128': '32rem',
      },
      fontFamily: {
        custom: ['CustomFont', 'sans-serif'],
      },
    },
  },
}
```

### Custom Utilities

```css
/* In your CSS */
@layer utilities {
  .content-auto {
    content-visibility: auto;
  }
}
```
