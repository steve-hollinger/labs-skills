/**
 * Exercise 1 Solution: Type-Safe Form
 */

import React, { useState, useCallback, FormEvent, ChangeEvent, FocusEvent } from 'react'

// ============================================
// Type Definitions
// ============================================

interface FormData {
  name: string
  email: string
  subject: string
  message: string
  subscribe: boolean
}

type FormErrors = {
  [K in keyof FormData]?: string
}

type FormTouched = {
  [K in keyof FormData]?: boolean
}

interface FormState {
  isSubmitting: boolean
  isSubmitted: boolean
  submitError: string | null
}

// ============================================
// Validation
// ============================================

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validateField(name: keyof FormData, value: string | boolean): string | undefined {
  switch (name) {
    case 'name':
      if (!value || (typeof value === 'string' && value.trim().length === 0)) {
        return 'Name is required'
      }
      if (typeof value === 'string' && value.trim().length < 2) {
        return 'Name must be at least 2 characters'
      }
      return undefined

    case 'email':
      if (!value || (typeof value === 'string' && value.trim().length === 0)) {
        return 'Email is required'
      }
      if (typeof value === 'string' && !EMAIL_REGEX.test(value)) {
        return 'Please enter a valid email address'
      }
      return undefined

    case 'subject':
      if (!value || (typeof value === 'string' && value.trim().length === 0)) {
        return 'Please select a subject'
      }
      return undefined

    case 'message':
      if (!value || (typeof value === 'string' && value.trim().length === 0)) {
        return 'Message is required'
      }
      if (typeof value === 'string' && value.trim().length < 10) {
        return 'Message must be at least 10 characters'
      }
      return undefined

    case 'subscribe':
      return undefined // Optional field, no validation

    default:
      return undefined
  }
}

function validateForm(data: FormData): FormErrors {
  const errors: FormErrors = {}

  ;(Object.keys(data) as Array<keyof FormData>).forEach((key) => {
    const error = validateField(key, data[key])
    if (error) {
      errors[key] = error
    }
  })

  return errors
}

// ============================================
// Custom Hook
// ============================================

interface UseFormOptions<T> {
  initialValues: T
  onSubmit: (values: T) => Promise<void>
  validate?: (values: T) => Partial<Record<keyof T, string>>
}

function useForm<T extends Record<string, unknown>>({
  initialValues,
  onSubmit,
  validate,
}: UseFormOptions<T>) {
  const [values, setValues] = useState<T>(initialValues)
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({})
  const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({})
  const [state, setState] = useState<FormState>({
    isSubmitting: false,
    isSubmitted: false,
    submitError: null,
  })

  const handleChange = useCallback(
    (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const { name, value, type } = e.target
      const newValue =
        type === 'checkbox' ? (e.target as HTMLInputElement).checked : value

      setValues((prev) => ({ ...prev, [name]: newValue }))

      // Clear error when user starts typing
      if (errors[name as keyof T]) {
        setErrors((prev) => ({ ...prev, [name]: undefined }))
      }
    },
    [errors]
  )

  const handleBlur = useCallback(
    (e: FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const { name, value, type } = e.target
      const fieldValue =
        type === 'checkbox' ? (e.target as HTMLInputElement).checked : value

      setTouched((prev) => ({ ...prev, [name]: true }))

      // Validate on blur
      if (validate) {
        const allErrors = validate(values as T)
        setErrors((prev) => ({ ...prev, [name]: allErrors[name as keyof T] }))
      }
    },
    [validate, values]
  )

  const handleSubmit = useCallback(
    async (e: FormEvent<HTMLFormElement>) => {
      e.preventDefault()

      // Mark all fields as touched
      const allTouched = Object.keys(values).reduce(
        (acc, key) => ({ ...acc, [key]: true }),
        {} as Record<keyof T, boolean>
      )
      setTouched(allTouched)

      // Validate all fields
      const validationErrors = validate ? validate(values as T) : {}
      setErrors(validationErrors)

      // Check if there are any errors
      if (Object.values(validationErrors).some((error) => error)) {
        return
      }

      setState((prev) => ({ ...prev, isSubmitting: true, submitError: null }))

      try {
        await onSubmit(values as T)
        setState((prev) => ({ ...prev, isSubmitting: false, isSubmitted: true }))
        setValues(initialValues)
        setTouched({})
      } catch (error) {
        setState((prev) => ({
          ...prev,
          isSubmitting: false,
          submitError: error instanceof Error ? error.message : 'Submission failed',
        }))
      }
    },
    [values, validate, onSubmit, initialValues]
  )

  const isValid = Object.keys(errors).length === 0 || !Object.values(errors).some(Boolean)

  return {
    values,
    errors,
    touched,
    state,
    handleChange,
    handleBlur,
    handleSubmit,
    isValid,
    setValues,
    setErrors,
  }
}

// ============================================
// Form Component
// ============================================

const SUBJECTS = [
  { value: '', label: 'Select a subject' },
  { value: 'general', label: 'General Inquiry' },
  { value: 'support', label: 'Technical Support' },
  { value: 'feedback', label: 'Feedback' },
  { value: 'other', label: 'Other' },
]

const initialValues: FormData = {
  name: '',
  email: '',
  subject: '',
  message: '',
  subscribe: false,
}

async function submitForm(data: FormData): Promise<void> {
  // Simulate API call
  await new Promise((resolve) => setTimeout(resolve, 1500))

  // Simulate occasional failure
  if (Math.random() < 0.2) {
    throw new Error('Server error. Please try again.')
  }

  console.log('Form submitted:', data)
}

function ContactForm() {
  const {
    values,
    errors,
    touched,
    state,
    handleChange,
    handleBlur,
    handleSubmit,
    isValid,
  } = useForm({
    initialValues,
    onSubmit: submitForm,
    validate: validateForm,
  })

  if (state.isSubmitted) {
    return (
      <div className="success-message">
        <h3>Thank you!</h3>
        <p>Your message has been sent successfully.</p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      {/* Name Field */}
      <div className="form-group">
        <label htmlFor="name">Name *</label>
        <input
          id="name"
          name="name"
          type="text"
          value={values.name}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={state.isSubmitting}
          aria-invalid={touched.name && !!errors.name}
          aria-describedby={errors.name ? 'name-error' : undefined}
        />
        {touched.name && errors.name && (
          <span id="name-error" className="error">
            {errors.name}
          </span>
        )}
      </div>

      {/* Email Field */}
      <div className="form-group">
        <label htmlFor="email">Email *</label>
        <input
          id="email"
          name="email"
          type="email"
          value={values.email}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={state.isSubmitting}
          aria-invalid={touched.email && !!errors.email}
        />
        {touched.email && errors.email && (
          <span className="error">{errors.email}</span>
        )}
      </div>

      {/* Subject Field */}
      <div className="form-group">
        <label htmlFor="subject">Subject *</label>
        <select
          id="subject"
          name="subject"
          value={values.subject}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={state.isSubmitting}
          aria-invalid={touched.subject && !!errors.subject}
        >
          {SUBJECTS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {touched.subject && errors.subject && (
          <span className="error">{errors.subject}</span>
        )}
      </div>

      {/* Message Field */}
      <div className="form-group">
        <label htmlFor="message">Message *</label>
        <textarea
          id="message"
          name="message"
          rows={5}
          value={values.message}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={state.isSubmitting}
          aria-invalid={touched.message && !!errors.message}
        />
        {touched.message && errors.message && (
          <span className="error">{errors.message}</span>
        )}
      </div>

      {/* Subscribe Checkbox */}
      <div className="form-group checkbox">
        <label>
          <input
            name="subscribe"
            type="checkbox"
            checked={values.subscribe}
            onChange={handleChange}
            disabled={state.isSubmitting}
          />
          Subscribe to newsletter
        </label>
      </div>

      {/* Submit Error */}
      {state.submitError && (
        <div className="error submit-error">{state.submitError}</div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={state.isSubmitting || !isValid}
      >
        {state.isSubmitting ? 'Sending...' : 'Send Message'}
      </button>
    </form>
  )
}

export { ContactForm, useForm, validateForm, validateField }
export type { FormData, FormErrors, FormState }
