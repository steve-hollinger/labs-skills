/**
 * Exercise 1 Solution: Multi-Page Application Configuration
 */

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],

  // Multi-page application type
  appType: 'mpa',

  // Path aliases
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@shared': resolve(__dirname, './src/shared'),
      '@components': resolve(__dirname, './src/components'),
    },
  },

  // Build configuration
  build: {
    rollupOptions: {
      // Define multiple entry points
      input: {
        main: resolve(__dirname, 'index.html'),
        admin: resolve(__dirname, 'admin/index.html'),
        login: resolve(__dirname, 'login/index.html'),
      },

      output: {
        // Organize output by type
        assetFileNames: 'assets/[name]-[hash][extname]',
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',

        // Manual chunk splitting for shared code
        manualChunks(id) {
          // React and React DOM in vendor-react
          if (id.includes('node_modules/react')) {
            return 'vendor-react'
          }

          // Other node_modules in vendor
          if (id.includes('node_modules')) {
            return 'vendor'
          }

          // Shared application code
          if (id.includes('/src/shared/')) {
            return 'shared'
          }

          return undefined
        },
      },
    },
  },

  // Development server
  server: {
    port: 3000,
    open: '/index.html',
  },
})

/**
 * Example HTML files structure:
 *
 * index.html:
 * ```html
 * <!DOCTYPE html>
 * <html>
 *   <head><title>Main App</title></head>
 *   <body>
 *     <div id="root"></div>
 *     <script type="module" src="/src/main.ts"></script>
 *   </body>
 * </html>
 * ```
 *
 * admin/index.html:
 * ```html
 * <!DOCTYPE html>
 * <html>
 *   <head><title>Admin Dashboard</title></head>
 *   <body>
 *     <div id="root"></div>
 *     <script type="module" src="/src/admin/main.ts"></script>
 *   </body>
 * </html>
 * ```
 *
 * login/index.html:
 * ```html
 * <!DOCTYPE html>
 * <html>
 *   <head><title>Login</title></head>
 *   <body>
 *     <div id="root"></div>
 *     <script type="module" src="/src/login/main.ts"></script>
 *   </body>
 * </html>
 * ```
 */

/**
 * Example shared module usage:
 *
 * src/shared/api.ts:
 * ```typescript
 * export const API_BASE = '/api/v1'
 *
 * export async function fetchData<T>(endpoint: string): Promise<T> {
 *   const response = await fetch(`${API_BASE}${endpoint}`)
 *   return response.json()
 * }
 * ```
 *
 * src/main.ts:
 * ```typescript
 * import { fetchData } from '@shared/api'
 * // Uses the shared chunk
 * ```
 *
 * src/admin/main.ts:
 * ```typescript
 * import { fetchData } from '@shared/api'
 * // Also uses the same shared chunk - no duplication!
 * ```
 */
