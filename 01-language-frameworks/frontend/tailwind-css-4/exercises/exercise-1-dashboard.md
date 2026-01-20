# Exercise 1: Build a Responsive Dashboard

## Objective

Create a responsive admin dashboard layout using Tailwind CSS that works on mobile, tablet, and desktop devices.

## Requirements

### Layout Structure

1. **Header**
   - Fixed at the top
   - Contains logo, search bar, notifications, and user menu
   - Collapses appropriately on mobile

2. **Sidebar**
   - Fixed on desktop, hidden on mobile (hamburger menu)
   - Contains navigation items with icons
   - Active state for current page
   - Collapsible on tablet

3. **Main Content Area**
   - Grid of stat cards (4 cards)
   - Data table with responsive behavior
   - Chart placeholder area

4. **Footer**
   - Simple footer with copyright

### Responsive Behavior

- **Mobile (< 640px)**: Sidebar hidden, single column layout
- **Tablet (640px - 1024px)**: Collapsible sidebar, 2 column grid
- **Desktop (> 1024px)**: Full sidebar, 4 column grid

### Color Scheme

- Support both light and dark modes
- Use a professional color palette

## Starting Point

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard</title>
  <!-- Include Tailwind CSS -->
</head>
<body class="bg-gray-100 dark:bg-gray-900">
  <!-- TODO: Build the dashboard -->
</body>
</html>
```

## Components to Build

### Stat Card

```html
<div class="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
  <div class="flex items-center justify-between">
    <div>
      <p class="text-sm text-gray-500">Total Users</p>
      <p class="text-2xl font-bold text-gray-900 dark:text-white">12,345</p>
    </div>
    <div class="rounded-full bg-blue-100 p-3 dark:bg-blue-900/30">
      <!-- Icon -->
    </div>
  </div>
  <p class="mt-2 text-sm text-green-600">+12% from last month</p>
</div>
```

### Navigation Item

```html
<a href="#" class="flex items-center gap-3 rounded-lg px-3 py-2 text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700">
  <!-- Icon -->
  <span>Dashboard</span>
</a>
```

### Data Table

Create a responsive table that:
- Shows all columns on desktop
- Hides some columns on tablet
- Converts to card layout on mobile

## Hints

1. Use `flex` for the main layout with sidebar
2. Use `sticky top-0` for the header
3. Use `hidden md:block` pattern for sidebar visibility
4. Use `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4` for stat cards
5. Add `overflow-x-auto` for horizontal scrolling tables on mobile

## Validation Checklist

- [ ] Header stays fixed at top
- [ ] Sidebar hidden on mobile, visible on desktop
- [ ] Stat cards responsive grid
- [ ] Table is usable on all screen sizes
- [ ] Dark mode works correctly
- [ ] Smooth transitions when resizing
- [ ] Mobile menu toggle works
