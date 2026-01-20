# Exercise 1: Build a Type-Safe Form

## Objective

Create a fully type-safe contact form with validation, error handling, and proper TypeScript integration.

## Requirements

1. Create a form with the following fields:
   - Name (required, min 2 characters)
   - Email (required, valid email format)
   - Subject (required, select from predefined options)
   - Message (required, min 10 characters)
   - Subscribe to newsletter (optional checkbox)

2. Implement proper TypeScript types for:
   - Form data
   - Validation errors
   - Form state
   - Event handlers

3. Features to implement:
   - Real-time validation as user types
   - Show error messages below each field
   - Disable submit button when form is invalid
   - Loading state during submission
   - Success/error message after submission

## Starting Point

```tsx
interface FormData {
  name: string
  email: string
  subject: string
  message: string
  subscribe: boolean
}

interface FormErrors {
  // TODO: Define error types
}

function ContactForm() {
  // TODO: Implement form state

  // TODO: Implement validation

  // TODO: Implement submit handler

  return (
    <form>
      {/* TODO: Implement form fields */}
    </form>
  )
}
```

## Tasks

### Task 1: Define Types

Create TypeScript interfaces for:
- FormData with all form fields
- FormErrors with optional error message for each field
- FormState including loading, submitted, and submitError

### Task 2: Implement Validation

Create a validation function that:
- Returns an object with error messages
- Validates all required fields
- Validates email format
- Validates minimum lengths

### Task 3: Create Custom Hook

Extract form logic into a `useForm` hook that:
- Manages form state
- Handles validation
- Provides typed event handlers
- Returns form state and handlers

### Task 4: Build the Form UI

Create the form component with:
- Labeled input fields
- Error message display
- Submit button with loading state
- Success/error message area

## Expected Behavior

1. As user types, validate after blur
2. Show errors in red below each field
3. Submit button disabled until form is valid
4. Show loading spinner during submission
5. Show success message on successful submit
6. Show error message on failed submit

## Hints

1. Use `Record<keyof FormData, string | undefined>` for errors
2. Create separate handlers for change and blur
3. Use a discriminated union for form state
4. Consider debouncing validation for performance

## Validation Checklist

- [ ] All form fields properly typed
- [ ] Validation runs on blur
- [ ] Errors display below fields
- [ ] Submit disabled when invalid
- [ ] Loading state works
- [ ] Success/error states work
- [ ] No TypeScript errors
