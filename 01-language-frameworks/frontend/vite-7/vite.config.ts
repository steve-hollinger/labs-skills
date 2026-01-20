import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  const isDev = command === 'serve'

  return {
    plugins: [react()],

    // Development server configuration
    server: {
      port: 3000,
      open: false,
      cors: true,
      // Example proxy configuration
      proxy: {
        '/api': {
          target: 'http://localhost:8080',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },

    // Preview server configuration (for production builds)
    preview: {
      port: 4173,
    },

    // Path resolution
    resolve: {
      alias: {
        '@': resolve(__dirname, './src'),
        '@examples': resolve(__dirname, './src/examples'),
      },
    },

    // Build configuration
    build: {
      outDir: 'dist',
      sourcemap: isDev,
      // Rollup options for production builds
      rollupOptions: {
        output: {
          // Manual chunk splitting for better caching
          manualChunks: {
            vendor: ['react', 'react-dom'],
          },
        },
      },
      // Target modern browsers
      target: 'esnext',
      // Minification options
      minify: mode === 'production' ? 'esbuild' : false,
    },

    // Environment variable handling
    define: {
      __DEV__: isDev,
      __VERSION__: JSON.stringify(process.env.npm_package_version),
    },

    // Dependency optimization
    optimizeDeps: {
      include: ['react', 'react-dom'],
    },

    // Test configuration (Vitest)
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: ['./tests/setup.ts'],
      include: ['tests/**/*.test.ts', 'tests/**/*.test.tsx'],
    },
  }
})
