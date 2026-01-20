/**
 * Custom Middleware Examples
 *
 * Demonstrates how to add custom middleware to Vite's dev server.
 */

import type { Plugin, Connect } from 'vite'

/**
 * Logging Middleware
 *
 * Logs all incoming requests with timing information.
 */
function loggingMiddleware(): Connect.NextHandleFunction {
  return (req, res, next) => {
    const start = Date.now()
    const { method, url } = req

    res.on('finish', () => {
      const duration = Date.now() - start
      const status = res.statusCode
      console.log(`[${new Date().toISOString()}] ${method} ${url} ${status} - ${duration}ms`)
    })

    next()
  }
}

/**
 * Mock API Middleware
 *
 * Provides mock API responses for development.
 */
function mockApiMiddleware(): Connect.NextHandleFunction {
  const mockData: Record<string, unknown> = {
    '/api/users': [
      { id: 1, name: 'Alice', email: 'alice@example.com' },
      { id: 2, name: 'Bob', email: 'bob@example.com' },
    ],
    '/api/products': [
      { id: 1, name: 'Widget', price: 9.99 },
      { id: 2, name: 'Gadget', price: 19.99 },
    ],
  }

  return (req, res, next) => {
    const { url } = req

    if (url && url.startsWith('/api/mock/')) {
      const endpoint = url.replace('/mock', '')
      const data = mockData[endpoint]

      if (data) {
        res.setHeader('Content-Type', 'application/json')
        res.end(JSON.stringify(data))
        return
      }
    }

    next()
  }
}

/**
 * Auth Middleware
 *
 * Simulates authentication for protected routes.
 */
function authMiddleware(): Connect.NextHandleFunction {
  return (req, res, next) => {
    const { url } = req

    if (url?.startsWith('/api/protected/')) {
      const authHeader = req.headers.authorization

      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        res.statusCode = 401
        res.setHeader('Content-Type', 'application/json')
        res.end(JSON.stringify({ error: 'Unauthorized' }))
        return
      }
    }

    next()
  }
}

/**
 * Vite Plugin with Middleware
 *
 * Package middleware as a Vite plugin for easy reuse.
 */
export function devServerMiddlewarePlugin(): Plugin {
  return {
    name: 'dev-server-middleware',
    configureServer(server) {
      // Middleware runs before Vite's internal middleware
      server.middlewares.use(loggingMiddleware())
      server.middlewares.use(authMiddleware())
      server.middlewares.use(mockApiMiddleware())

      // Return a function to add middleware after Vite's
      return () => {
        server.middlewares.use((req, res, next) => {
          // This runs after Vite's middleware
          // Useful for catch-all handlers
          next()
        })
      }
    },
  }
}

/**
 * Example vite.config.ts usage:
 *
 * import { defineConfig } from 'vite'
 * import { devServerMiddlewarePlugin } from './middleware'
 *
 * export default defineConfig({
 *   plugins: [devServerMiddlewarePlugin()],
 * })
 */

console.log('Middleware Examples Loaded')
console.log('- loggingMiddleware: Logs all requests with timing')
console.log('- mockApiMiddleware: Provides mock API responses')
console.log('- authMiddleware: Simulates authentication')
console.log('- devServerMiddlewarePlugin: Packages middleware as Vite plugin')

export {
  loggingMiddleware,
  mockApiMiddleware,
  authMiddleware,
}
