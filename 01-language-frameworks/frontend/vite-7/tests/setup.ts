/**
 * Vitest Setup File
 *
 * This file runs before all tests to set up the testing environment.
 */

import { vi } from 'vitest'

// Mock import.meta.env
vi.stubGlobal('import.meta', {
  env: {
    MODE: 'test',
    DEV: true,
    PROD: false,
    BASE_URL: '/',
    VITE_API_URL: 'http://test-api.example.com',
  },
  hot: {
    accept: vi.fn(),
    dispose: vi.fn(),
    data: {},
  },
})

// Mock console methods for cleaner test output
const originalConsole = { ...console }

beforeAll(() => {
  // Suppress console.log during tests unless debugging
  if (!process.env.DEBUG) {
    console.log = vi.fn()
  }
})

afterAll(() => {
  // Restore console
  console.log = originalConsole.log
})

// Clean up after each test
afterEach(() => {
  vi.clearAllMocks()
})
