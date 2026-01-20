/**
 * Exercise 2 Solution: Build Performance Optimization
 */

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'
import { resolve } from 'path'

export default defineConfig(({ mode }) => ({
  plugins: [
    react(),

    // Bundle analyzer - only in analyze mode
    mode === 'analyze' &&
      visualizer({
        filename: 'dist/stats.html',
        open: true,
        gzipSize: true,
        brotliSize: true,
      }),
  ].filter(Boolean),

  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },

  build: {
    // Target modern browsers
    target: 'esnext',

    // Enable source maps for debugging (disable in production)
    sourcemap: mode === 'development',

    // Minification
    minify: 'esbuild',

    // Warn for large chunks
    chunkSizeWarningLimit: 150, // 150KB

    // CSS optimization
    cssCodeSplit: true,
    cssMinify: 'esbuild',

    rollupOptions: {
      output: {
        // Organize output files
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: ({ name }) => {
          // Organize assets by type
          if (/\.(gif|jpe?g|png|svg|webp)$/.test(name ?? '')) {
            return 'assets/images/[name]-[hash][extname]'
          }
          if (/\.(woff2?|eot|ttf|otf)$/.test(name ?? '')) {
            return 'assets/fonts/[name]-[hash][extname]'
          }
          if (/\.css$/.test(name ?? '')) {
            return 'assets/css/[name]-[hash][extname]'
          }
          return 'assets/[name]-[hash][extname]'
        },

        // Manual chunk splitting for optimal caching
        manualChunks(id) {
          if (id.includes('node_modules')) {
            // React ecosystem
            if (
              id.includes('react') ||
              id.includes('react-dom') ||
              id.includes('react-router') ||
              id.includes('scheduler')
            ) {
              return 'vendor-react'
            }

            // UI framework (if using one)
            if (
              id.includes('@headlessui') ||
              id.includes('@heroicons') ||
              id.includes('@radix-ui')
            ) {
              return 'vendor-ui'
            }

            // Utility libraries
            if (
              id.includes('lodash') ||
              id.includes('date-fns') ||
              id.includes('dayjs') ||
              id.includes('axios')
            ) {
              return 'vendor-utils'
            }

            // State management
            if (
              id.includes('zustand') ||
              id.includes('redux') ||
              id.includes('jotai') ||
              id.includes('@tanstack/query')
            ) {
              return 'vendor-state'
            }

            // Everything else from node_modules
            return 'vendor'
          }

          // Split by feature/page for lazy loading
          if (id.includes('/pages/')) {
            const match = id.match(/\/pages\/([^/]+)/)
            if (match) {
              return `page-${match[1].toLowerCase()}`
            }
          }

          return undefined
        },
      },

      // Tree shaking optimizations
      treeshake: {
        moduleSideEffects: false,
        propertyReadSideEffects: false,
        tryCatchDeoptimization: false,
      },
    },

    // Inline small assets
    assetsInlineLimit: 4096, // 4KB
  },

  // Optimize dependency pre-bundling
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      // Add other frequently used deps
    ],
    exclude: [
      // Exclude packages that don't need pre-bundling
    ],
  },
}))

/**
 * Route-based code splitting example:
 *
 * src/App.tsx:
 * ```tsx
 * import { lazy, Suspense } from 'react'
 * import { BrowserRouter, Routes, Route } from 'react-router-dom'
 *
 * // Lazy load route components
 * const Dashboard = lazy(() => import('./pages/Dashboard'))
 * const Settings = lazy(() => import('./pages/Settings'))
 * const Profile = lazy(() => import('./pages/Profile'))
 *
 * function App() {
 *   return (
 *     <BrowserRouter>
 *       <Suspense fallback={<Loading />}>
 *         <Routes>
 *           <Route path="/" element={<Dashboard />} />
 *           <Route path="/settings" element={<Settings />} />
 *           <Route path="/profile" element={<Profile />} />
 *         </Routes>
 *       </Suspense>
 *     </BrowserRouter>
 *   )
 * }
 * ```
 */

/**
 * To analyze the bundle:
 *
 * 1. Add to package.json scripts:
 *    "analyze": "vite build --mode analyze"
 *
 * 2. Run: npm run analyze
 *
 * 3. Open dist/stats.html to see the visualization
 */
