# Tailwind CSS 4 Patterns

This document contains common component patterns and best practices.

## Layout Patterns

### Page Layout with Sidebar

```html
<div class="flex min-h-screen">
  <!-- Sidebar -->
  <aside class="w-64 flex-shrink-0 border-r bg-gray-50 dark:bg-gray-800">
    <nav class="p-4">
      <!-- Navigation items -->
    </nav>
  </aside>

  <!-- Main content -->
  <main class="flex-1 overflow-auto">
    <div class="p-6">
      <!-- Content -->
    </div>
  </main>
</div>
```

### Sticky Header

```html
<header class="sticky top-0 z-50 border-b bg-white/80 backdrop-blur-sm dark:bg-gray-900/80">
  <div class="mx-auto max-w-7xl px-4 py-4">
    <!-- Header content -->
  </div>
</header>
```

### Centered Container

```html
<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
  <!-- Content stays centered with responsive padding -->
</div>
```

### Hero Section

```html
<section class="relative overflow-hidden bg-gradient-to-br from-blue-600 to-purple-700">
  <div class="absolute inset-0 bg-[url('/grid.svg')] opacity-20"></div>
  <div class="relative mx-auto max-w-7xl px-4 py-24 sm:py-32">
    <h1 class="text-4xl font-bold tracking-tight text-white sm:text-6xl">
      Hero Title
    </h1>
    <p class="mt-6 max-w-xl text-lg text-blue-100">
      Hero description text goes here.
    </p>
    <div class="mt-10 flex gap-4">
      <a href="#" class="rounded-lg bg-white px-6 py-3 font-semibold text-blue-600 hover:bg-blue-50">
        Get Started
      </a>
      <a href="#" class="rounded-lg border border-white/30 px-6 py-3 font-semibold text-white hover:bg-white/10">
        Learn More
      </a>
    </div>
  </div>
</section>
```

## Component Patterns

### Card

```html
<article class="overflow-hidden rounded-xl bg-white shadow-lg dark:bg-gray-800">
  <img
    src="/image.jpg"
    alt=""
    class="h-48 w-full object-cover"
  />
  <div class="p-6">
    <span class="text-sm font-medium text-blue-600 dark:text-blue-400">
      Category
    </span>
    <h3 class="mt-2 text-lg font-semibold text-gray-900 dark:text-white">
      Card Title
    </h3>
    <p class="mt-2 text-gray-600 dark:text-gray-300">
      Card description goes here with some detail text.
    </p>
    <div class="mt-4 flex items-center gap-4">
      <img
        src="/avatar.jpg"
        alt=""
        class="h-10 w-10 rounded-full"
      />
      <div>
        <p class="text-sm font-medium text-gray-900 dark:text-white">Author Name</p>
        <p class="text-sm text-gray-500">Jan 15, 2024</p>
      </div>
    </div>
  </div>
</article>
```

### Button Variants

```tsx
// React component with Tailwind
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  children: React.ReactNode
  className?: string
}

const variants = {
  primary: 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800',
  secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-gray-700 dark:text-white',
  outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950',
  ghost: 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800',
  danger: 'bg-red-600 text-white hover:bg-red-700 active:bg-red-800',
}

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
}

function Button({ variant = 'primary', size = 'md', children, className }: ButtonProps) {
  return (
    <button
      className={`
        inline-flex items-center justify-center rounded-lg font-medium
        transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
        disabled:cursor-not-allowed disabled:opacity-50
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
    >
      {children}
    </button>
  )
}
```

### Form Input

```html
<div>
  <label
    for="email"
    class="block text-sm font-medium text-gray-700 dark:text-gray-300"
  >
    Email Address
  </label>
  <div class="relative mt-1">
    <input
      type="email"
      id="email"
      class="block w-full rounded-lg border border-gray-300 px-4 py-2.5
             text-gray-900 placeholder-gray-400
             focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500
             dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
      placeholder="you@example.com"
    />
    <!-- Error state: add border-red-500 focus:border-red-500 focus:ring-red-500 -->
  </div>
  <p class="mt-1 text-sm text-gray-500">We'll never share your email.</p>
</div>
```

### Alert / Notification

```html
<!-- Success -->
<div class="flex items-start gap-3 rounded-lg bg-green-50 p-4 dark:bg-green-900/20">
  <svg class="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor">
    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
  </svg>
  <div>
    <h4 class="text-sm font-medium text-green-800 dark:text-green-200">Success!</h4>
    <p class="mt-1 text-sm text-green-700 dark:text-green-300">
      Your changes have been saved.
    </p>
  </div>
  <button class="ml-auto text-green-500 hover:text-green-600">
    <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
      <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
    </svg>
  </button>
</div>

<!-- Error variant: change green to red -->
<!-- Warning variant: change green to amber -->
<!-- Info variant: change green to blue -->
```

### Modal

```html
<!-- Backdrop -->
<div class="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"></div>

<!-- Modal -->
<div class="fixed inset-0 z-50 flex items-center justify-center p-4">
  <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl dark:bg-gray-800">
    <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
      Modal Title
    </h2>
    <p class="mt-2 text-gray-600 dark:text-gray-300">
      Modal content goes here.
    </p>
    <div class="mt-6 flex justify-end gap-3">
      <button class="rounded-lg px-4 py-2 text-gray-600 hover:bg-gray-100 dark:text-gray-300">
        Cancel
      </button>
      <button class="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700">
        Confirm
      </button>
    </div>
  </div>
</div>
```

### Avatar Group

```html
<div class="flex -space-x-2">
  <img class="h-10 w-10 rounded-full ring-2 ring-white dark:ring-gray-800" src="/avatar1.jpg" alt="" />
  <img class="h-10 w-10 rounded-full ring-2 ring-white dark:ring-gray-800" src="/avatar2.jpg" alt="" />
  <img class="h-10 w-10 rounded-full ring-2 ring-white dark:ring-gray-800" src="/avatar3.jpg" alt="" />
  <span class="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 text-sm font-medium text-gray-600 ring-2 ring-white dark:bg-gray-700 dark:text-gray-300 dark:ring-gray-800">
    +5
  </span>
</div>
```

### Dropdown Menu

```html
<div class="relative">
  <button class="flex items-center gap-2 rounded-lg px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-800">
    <span>Menu</span>
    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
    </svg>
  </button>

  <!-- Dropdown panel -->
  <div class="absolute right-0 mt-2 w-48 origin-top-right rounded-lg bg-white py-1 shadow-lg ring-1 ring-black/5 dark:bg-gray-800 dark:ring-white/10">
    <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700">
      Profile
    </a>
    <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700">
      Settings
    </a>
    <hr class="my-1 border-gray-200 dark:border-gray-700" />
    <a href="#" class="block px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20">
      Sign out
    </a>
  </div>
</div>
```

## Animation Patterns

### Fade In

```html
<div class="animate-fade-in">Fades in</div>

<!-- With custom animation -->
<style>
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
<div class="animate-[fade-in_0.3s_ease-in-out]">Custom animation</div>
```

### Skeleton Loading

```html
<div class="space-y-4">
  <div class="h-4 w-3/4 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
  <div class="h-4 w-1/2 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
  <div class="h-4 w-5/6 animate-pulse rounded bg-gray-200 dark:bg-gray-700"></div>
</div>
```

### Spinner

```html
<svg class="h-5 w-5 animate-spin text-blue-600" viewBox="0 0 24 24" fill="none">
  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
</svg>
```

## Responsive Patterns

### Show/Hide at Breakpoints

```html
<!-- Mobile only -->
<div class="block md:hidden">Shows on mobile</div>

<!-- Desktop only -->
<div class="hidden md:block">Shows on desktop</div>

<!-- Mobile menu button -->
<button class="md:hidden">
  <svg class="h-6 w-6">...</svg>
</button>
```

### Responsive Grid

```html
<!-- 1 col mobile, 2 cols tablet, 3 cols desktop, 4 cols wide -->
<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
  <!-- Items -->
</div>
```

### Responsive Text

```html
<h1 class="text-2xl font-bold sm:text-3xl md:text-4xl lg:text-5xl">
  Responsive Heading
</h1>
```
