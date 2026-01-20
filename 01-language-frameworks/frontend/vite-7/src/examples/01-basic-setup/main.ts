/**
 * Example 1: Basic Vite Setup
 *
 * This example demonstrates the fundamental concepts of Vite configuration.
 * It covers project structure, entry points, and basic configuration options.
 */

// Vite uses ES modules natively
// This import would be transformed by Vite during development
import { createApp } from './app'
import { CONFIG } from './config'

console.log('=== Example 1: Basic Vite Setup ===\n')

// Demonstrate Vite's environment variables
console.log('Environment Mode:', import.meta.env.MODE)
console.log('Dev Mode:', import.meta.env.DEV)
console.log('Prod Mode:', import.meta.env.PROD)
console.log('Base URL:', import.meta.env.BASE_URL)

// Custom environment variables must be prefixed with VITE_
console.log('\nCustom Environment Variables:')
console.log('VITE_API_URL:', import.meta.env.VITE_API_URL || '(not set)')

// Demonstrate Vite's module hot reload API
if (import.meta.hot) {
  console.log('\nHMR is available!')
  import.meta.hot.accept(() => {
    console.log('Module updated via HMR')
  })
}

// Show configuration
console.log('\nConfiguration:')
console.log(JSON.stringify(CONFIG, null, 2))

// Create and mount the application
const app = createApp()
console.log('\nApp created:', app.name)

/**
 * Key Takeaways:
 *
 * 1. Vite serves native ES modules during development
 * 2. Use import.meta.env for environment variables
 * 3. Only VITE_ prefixed env vars are exposed to client
 * 4. import.meta.hot provides HMR API access
 * 5. Configuration is in vite.config.ts
 */

export { app }
