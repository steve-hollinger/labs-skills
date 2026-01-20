/**
 * Configuration Module
 *
 * Demonstrates environment-aware configuration in Vite.
 */

interface AppConfig {
  apiUrl: string
  debugMode: boolean
  features: {
    darkMode: boolean
    analytics: boolean
  }
}

// Use import.meta.env for Vite environment variables
// Only VITE_ prefixed variables are exposed to the client
export const CONFIG: AppConfig = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8080',
  debugMode: import.meta.env.DEV,
  features: {
    darkMode: true,
    analytics: import.meta.env.PROD,
  },
}

// Type-safe environment variable access
// Define in src/vite-env.d.ts:
// interface ImportMetaEnv {
//   readonly VITE_API_URL: string
// }

export function getConfig(): AppConfig {
  return { ...CONFIG }
}

export function isProduction(): boolean {
  return import.meta.env.PROD
}

export function isDevelopment(): boolean {
  return import.meta.env.DEV
}
