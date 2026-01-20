/**
 * Example 3: Build Optimization
 *
 * This example demonstrates advanced build configuration for production,
 * including code splitting, chunk optimization, and asset handling.
 */

import type { BuildOptions } from 'vite'

console.log('=== Example 3: Build Optimization ===\n')

/**
 * Basic Build Configuration
 */
const basicBuildConfig: BuildOptions = {
  outDir: 'dist',
  assetsDir: 'assets',
  sourcemap: true,
  minify: 'esbuild', // or 'terser' for more control
  target: 'esnext',
}

console.log('Basic Build Config:')
console.log(JSON.stringify(basicBuildConfig, null, 2))

/**
 * Manual Chunk Splitting
 *
 * Split code into logical chunks for better caching.
 */
const chunkSplittingConfig = {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunk for React
          'vendor-react': ['react', 'react-dom'],

          // Vendor chunk for utilities
          'vendor-utils': ['lodash-es', 'date-fns'],

          // Vendor chunk for UI libraries
          'vendor-ui': ['@headlessui/react', '@heroicons/react'],
        },
      },
    },
  },
}

console.log('\nChunk Splitting Config:')
console.log(JSON.stringify(chunkSplittingConfig, null, 2))

/**
 * Dynamic Chunk Naming
 *
 * Use a function for more complex splitting logic.
 */
function manualChunks(id: string): string | undefined {
  // Put all node_modules in vendor chunk
  if (id.includes('node_modules')) {
    // Split by package name
    const parts = id.split('node_modules/')
    const packagePath = parts[parts.length - 1]
    const packageName = packagePath.split('/')[0]

    // Group related packages
    if (['react', 'react-dom', 'react-router'].includes(packageName)) {
      return 'vendor-react'
    }
    if (['lodash', 'lodash-es', 'date-fns', 'dayjs'].includes(packageName)) {
      return 'vendor-utils'
    }

    return 'vendor'
  }

  // Split by feature folder
  if (id.includes('/features/')) {
    const match = id.match(/\/features\/([^/]+)/)
    if (match) {
      return `feature-${match[1]}`
    }
  }

  return undefined
}

console.log('\nDynamic Chunk Function:')
console.log('Groups packages and features into logical chunks')

/**
 * Asset Handling Configuration
 */
const assetConfig = {
  build: {
    // Inline assets smaller than 4kb as base64
    assetsInlineLimit: 4096,

    rollupOptions: {
      output: {
        // Custom asset file names
        assetFileNames: (assetInfo: { name?: string }) => {
          const name = assetInfo.name || ''
          // Group by file type
          if (/\.(gif|jpe?g|png|svg|webp)$/.test(name)) {
            return 'assets/images/[name]-[hash][extname]'
          }
          if (/\.(woff2?|eot|ttf|otf)$/.test(name)) {
            return 'assets/fonts/[name]-[hash][extname]'
          }
          return 'assets/[name]-[hash][extname]'
        },

        // Custom chunk file names
        chunkFileNames: 'assets/js/[name]-[hash].js',

        // Custom entry file names
        entryFileNames: 'assets/js/[name]-[hash].js',
      },
    },
  },
}

console.log('\nAsset Configuration:')
console.log('- Images: assets/images/')
console.log('- Fonts: assets/fonts/')
console.log('- JS: assets/js/')

/**
 * CSS Configuration
 */
const cssConfig = {
  build: {
    cssCodeSplit: true, // Split CSS by chunk (default)
    cssMinify: 'esbuild', // or 'lightningcss'
  },
  css: {
    modules: {
      localsConvention: 'camelCaseOnly',
      generateScopedName: '[name]__[local]___[hash:base64:5]',
    },
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`,
      },
    },
  },
}

console.log('\nCSS Configuration:')
console.log(JSON.stringify(cssConfig.css, null, 2))

/**
 * Performance Optimization
 */
const performanceConfig = {
  build: {
    // Warn if chunks exceed this size (in KB)
    chunkSizeWarningLimit: 500,

    // Rollup options for better tree shaking
    rollupOptions: {
      treeshake: {
        moduleSideEffects: false,
        propertyReadSideEffects: false,
      },
    },
  },

  // Dependency optimization
  optimizeDeps: {
    // Pre-bundle these for faster dev start
    include: ['react', 'react-dom', 'lodash-es'],

    // Exclude from pre-bundling
    exclude: ['@my-org/internal-lib'],
  },
}

console.log('\nPerformance Configuration:')
console.log('- Chunk size warning: 500KB')
console.log('- Tree shaking enabled')
console.log('- Dependencies pre-bundled')

/**
 * Bundle Analysis
 *
 * Use rollup-plugin-visualizer to analyze bundle size.
 */
const analyzerConfig = `
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    visualizer({
      filename: 'dist/stats.html',
      open: true,
      gzipSize: true,
      brotliSize: true,
    }),
  ],
})
`

console.log('\nBundle Analysis:')
console.log('Install: npm install -D rollup-plugin-visualizer')
console.log('Run: npm run build && open dist/stats.html')

/**
 * Key Takeaways:
 *
 * 1. Use manualChunks for predictable code splitting
 * 2. Configure asset file names for organized output
 * 3. Enable sourcemaps for debugging (but not in production)
 * 4. Use chunk size warnings to catch large bundles
 * 5. Analyze bundles with rollup-plugin-visualizer
 * 6. Pre-bundle large dependencies for faster dev start
 */

export {
  basicBuildConfig,
  chunkSplittingConfig,
  manualChunks,
  assetConfig,
  cssConfig,
  performanceConfig,
}
