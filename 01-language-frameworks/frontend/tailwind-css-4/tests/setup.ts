/**
 * Vitest Setup File for Tailwind CSS Tests
 */

import { vi, afterEach } from 'vitest'

// Clean up after each test
afterEach(() => {
  vi.clearAllMocks()
})

// Mock window.matchMedia for responsive tests
vi.stubGlobal('matchMedia', (query: string) => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: vi.fn(),
  removeListener: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
}))
