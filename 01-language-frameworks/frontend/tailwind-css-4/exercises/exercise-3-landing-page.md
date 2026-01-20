# Exercise 3: Create a Landing Page

## Objective

Build a complete, professional landing page using Tailwind CSS with responsive design and dark mode support.

## Page Sections

### 1. Navigation
- Logo
- Menu items (features, pricing, about, contact)
- CTA button
- Mobile hamburger menu
- Sticky on scroll

### 2. Hero Section
- Large headline
- Subheadline
- Two CTA buttons (primary and secondary)
- Hero image or illustration
- Background gradient or pattern

### 3. Social Proof
- Company logos
- "Trusted by" text
- Responsive logo grid

### 4. Features Section
- Section title and description
- 3-6 feature cards with icons
- Responsive grid layout

### 5. How It Works
- Step-by-step process
- Numbered steps or timeline
- Icons or illustrations

### 6. Testimonials
- Customer quotes
- Avatar, name, and title
- Carousel or grid layout

### 7. Pricing Section
- 3 pricing tiers
- Feature lists
- CTA buttons
- Popular/recommended badge

### 8. FAQ Section
- Accordion-style questions
- Expand/collapse functionality
- Clear typography

### 9. CTA Section
- Final call-to-action
- Email signup or button
- Background color/gradient

### 10. Footer
- Logo
- Navigation links (4 columns)
- Social media icons
- Copyright text

## Design Requirements

1. **Responsive**: Mobile-first design
2. **Dark Mode**: Full dark mode support
3. **Animations**: Subtle hover animations
4. **Typography**: Clear hierarchy
5. **Spacing**: Consistent padding/margins
6. **Colors**: Cohesive color palette

## Wireframe

```
┌─────────────────────────────────────┐
│           Navigation                │
├─────────────────────────────────────┤
│                                     │
│            Hero Section             │
│                                     │
├─────────────────────────────────────┤
│         Social Proof Logos          │
├─────────────────────────────────────┤
│                                     │
│          Features Grid              │
│                                     │
├─────────────────────────────────────┤
│                                     │
│          How It Works               │
│                                     │
├─────────────────────────────────────┤
│                                     │
│          Testimonials               │
│                                     │
├─────────────────────────────────────┤
│                                     │
│            Pricing                  │
│                                     │
├─────────────────────────────────────┤
│             FAQ                     │
├─────────────────────────────────────┤
│         CTA Section                 │
├─────────────────────────────────────┤
│            Footer                   │
└─────────────────────────────────────┘
```

## Starting Point

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Product Landing Page</title>
</head>
<body class="bg-white text-gray-900 dark:bg-gray-900 dark:text-white">
  <!-- Navigation -->
  <nav class="sticky top-0 z-50">
    <!-- TODO -->
  </nav>

  <main>
    <!-- Hero -->
    <section class="py-20">
      <!-- TODO -->
    </section>

    <!-- Social Proof -->
    <section class="border-y py-12">
      <!-- TODO -->
    </section>

    <!-- Features -->
    <section class="py-20">
      <!-- TODO -->
    </section>

    <!-- Continue with other sections... -->
  </main>

  <footer class="bg-gray-50 dark:bg-gray-800">
    <!-- TODO -->
  </footer>
</body>
</html>
```

## Hints

1. Use `max-w-7xl mx-auto px-4` for consistent container widths
2. Use `py-16 md:py-24` for responsive section spacing
3. Use gradients for visual interest: `bg-gradient-to-r from-blue-600 to-purple-600`
4. Add subtle shadows: `shadow-lg hover:shadow-xl`
5. Use `transition-all duration-300` for smooth animations
6. Test at all breakpoints: 320px, 640px, 768px, 1024px, 1280px

## Example Components

### Feature Card

```html
<div class="rounded-xl bg-white p-6 shadow-lg dark:bg-gray-800">
  <div class="mb-4 inline-flex rounded-lg bg-blue-100 p-3 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400">
    <svg class="h-6 w-6"><!-- Icon --></svg>
  </div>
  <h3 class="mb-2 text-lg font-semibold">Feature Title</h3>
  <p class="text-gray-600 dark:text-gray-400">
    Feature description goes here explaining the benefit.
  </p>
</div>
```

### Pricing Card

```html
<div class="relative rounded-2xl border border-gray-200 bg-white p-8 dark:border-gray-700 dark:bg-gray-800">
  <span class="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-blue-600 px-3 py-1 text-sm text-white">
    Popular
  </span>
  <h3 class="text-xl font-bold">Pro Plan</h3>
  <p class="mt-4">
    <span class="text-4xl font-bold">$29</span>
    <span class="text-gray-500">/month</span>
  </p>
  <ul class="mt-8 space-y-4">
    <li class="flex items-center gap-2">
      <svg class="h-5 w-5 text-green-500"><!-- Check icon --></svg>
      <span>Feature one</span>
    </li>
    <!-- More features -->
  </ul>
  <button class="mt-8 w-full rounded-lg bg-blue-600 py-3 font-medium text-white hover:bg-blue-700">
    Get Started
  </button>
</div>
```

## Validation Checklist

- [ ] All 10 sections completed
- [ ] Fully responsive on all devices
- [ ] Dark mode toggle works
- [ ] Navigation is sticky
- [ ] Mobile menu works
- [ ] Smooth hover animations
- [ ] Consistent spacing throughout
- [ ] Clear typography hierarchy
- [ ] All links have hover states
- [ ] Page loads without layout shift
