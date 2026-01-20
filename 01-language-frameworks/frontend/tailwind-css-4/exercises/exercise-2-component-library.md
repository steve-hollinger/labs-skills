# Exercise 2: Build a Component Library

## Objective

Create a reusable component library using Tailwind CSS that can be used across projects.

## Components to Build

### 1. Button Component

Create buttons with:
- Variants: primary, secondary, outline, ghost, danger
- Sizes: sm, md, lg
- States: default, hover, active, disabled, loading
- Optional icon support (left or right)

### 2. Input Component

Create form inputs with:
- Text, email, password, number types
- Label and helper text
- Error state
- Disabled state
- Icon prefix/suffix

### 3. Card Component

Create cards with:
- Header, body, footer sections
- Image support
- Clickable variant
- Shadow options

### 4. Badge Component

Create badges with:
- Color variants (info, success, warning, error)
- Sizes (sm, md)
- Dot indicator option

### 5. Avatar Component

Create avatars with:
- Image or initials fallback
- Sizes (xs, sm, md, lg, xl)
- Status indicator (online, offline, busy)
- Avatar group

### 6. Alert Component

Create alerts with:
- Variants (info, success, warning, error)
- Dismissible option
- Icon support
- Title and description

### 7. Modal Component

Create modals with:
- Backdrop blur
- Close button
- Header, body, footer sections
- Size variants (sm, md, lg)

### 8. Dropdown Component

Create dropdowns with:
- Trigger button
- Menu items
- Dividers
- Icon support

## Requirements

For each component:
1. Support dark mode
2. Support keyboard navigation (where applicable)
3. Include hover/focus states
4. Be fully responsive

## Starting Structure

```html
<!-- Component Library Showcase -->
<div class="mx-auto max-w-6xl p-8">
  <h1 class="mb-12 text-3xl font-bold">Component Library</h1>

  <!-- Buttons Section -->
  <section class="mb-12">
    <h2 class="mb-6 text-xl font-semibold">Buttons</h2>
    <div class="space-y-4">
      <!-- Button variants -->
    </div>
  </section>

  <!-- Continue for each component... -->
</div>
```

## Example: Button Variants

```html
<!-- Primary -->
<button class="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
  Primary Button
</button>

<!-- Secondary -->
<button class="inline-flex items-center justify-center rounded-lg bg-gray-100 px-4 py-2 font-medium text-gray-900 transition-colors hover:bg-gray-200 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600">
  Secondary Button
</button>

<!-- With icon -->
<button class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700">
  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
  </svg>
  Add Item
</button>

<!-- Loading -->
<button class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white" disabled>
  <svg class="h-5 w-5 animate-spin" viewBox="0 0 24 24">
    <!-- Spinner SVG -->
  </svg>
  Loading...
</button>
```

## Deliverables

1. Single HTML file showcasing all components
2. Each component should be demonstrated with:
   - All variants
   - All sizes
   - All states
   - Light and dark mode

## Hints

1. Group related utilities into logical sections
2. Use consistent spacing and sizing
3. Test all components in both light and dark modes
4. Consider accessibility (focus states, contrast)
5. Use CSS variables for customization points

## Validation Checklist

- [ ] All 8 components built
- [ ] Each component has all specified variants
- [ ] Dark mode works for all components
- [ ] Focus states are visible
- [ ] Disabled states look appropriate
- [ ] Components are visually consistent
- [ ] All hover/active states work
