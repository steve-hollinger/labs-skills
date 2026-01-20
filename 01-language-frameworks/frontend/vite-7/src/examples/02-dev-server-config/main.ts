/**
 * Example 2: Development Server Configuration
 *
 * This example demonstrates how to configure Vite's development server
 * including proxies, CORS, custom middleware, and server options.
 */

import type { ServerOptions, ProxyOptions } from 'vite'

console.log('=== Example 2: Development Server Configuration ===\n')

/**
 * Server Configuration Examples
 *
 * These configurations would go in vite.config.ts
 */

// Basic server configuration
const basicServerConfig: ServerOptions = {
  port: 3000, // Default: 5173
  host: true, // Expose to network (0.0.0.0)
  open: true, // Open browser on start
  cors: true, // Enable CORS
  strictPort: false, // Try next port if 3000 is taken
}

console.log('Basic Server Config:')
console.log(JSON.stringify(basicServerConfig, null, 2))

// Proxy configuration for API calls
const proxyConfig: Record<string, ProxyOptions> = {
  // Simple proxy - forwards /api/* to localhost:8080/api/*
  '/api': {
    target: 'http://localhost:8080',
    changeOrigin: true,
  },

  // Proxy with path rewriting - /api/v1/* becomes /*
  '/api/v1': {
    target: 'http://api.example.com',
    changeOrigin: true,
    rewrite: (path: string) => path.replace(/^\/api\/v1/, ''),
  },

  // WebSocket proxy
  '/socket.io': {
    target: 'ws://localhost:8080',
    ws: true,
  },
}

console.log('\nProxy Configuration:')
console.log(JSON.stringify(proxyConfig, null, 2))

// HTTPS configuration
const httpsConfig = {
  // Option 1: Use @vitejs/plugin-basic-ssl for self-signed cert
  // Option 2: Provide custom certificates
  https: {
    key: './certs/localhost-key.pem',
    cert: './certs/localhost.pem',
  },
}

console.log('\nHTTPS Configuration:')
console.log('Use @vitejs/plugin-basic-ssl for quick HTTPS setup')
console.log('Or provide custom certificates for production-like testing')

// HMR configuration
const hmrConfig = {
  hmr: {
    overlay: true, // Show error overlay
    protocol: 'ws', // or 'wss' for HTTPS
    host: 'localhost',
    port: 24678, // Custom HMR port
    clientPort: 443, // For proxy setups
  },
}

console.log('\nHMR Configuration:')
console.log(JSON.stringify(hmrConfig, null, 2))

/**
 * Custom Headers Example
 */
const headersConfig = {
  headers: {
    'Access-Control-Allow-Origin': '*',
    'X-Custom-Header': 'vite-dev-server',
  },
}

console.log('\nCustom Headers:')
console.log(JSON.stringify(headersConfig, null, 2))

/**
 * File System Configuration
 */
const fsConfig = {
  fs: {
    // Allow serving files from one level up
    allow: ['..'],
    // Deny access to sensitive files
    deny: ['.env', '.git'],
    // Strict file serving
    strict: true,
  },
}

console.log('\nFile System Configuration:')
console.log(JSON.stringify(fsConfig, null, 2))

/**
 * Key Takeaways:
 *
 * 1. Use `server.proxy` to forward API requests to backend
 * 2. Enable `cors: true` for cross-origin development
 * 3. Use `host: true` to expose dev server to network
 * 4. Configure HTTPS for testing secure features
 * 5. Customize HMR behavior for complex setups
 * 6. Use `fs.allow` to serve files outside project root
 */

export {
  basicServerConfig,
  proxyConfig,
  httpsConfig,
  hmrConfig,
  headersConfig,
  fsConfig,
}
