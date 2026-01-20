/**
 * Example 4: Custom Vite Plugins
 *
 * This example demonstrates how to create custom Vite plugins
 * for various use cases including transformations, virtual modules,
 * and build hooks.
 */

import type { Plugin, ResolvedConfig } from 'vite'

console.log('=== Example 4: Custom Vite Plugins ===\n')

/**
 * Plugin 1: Markdown Transform
 *
 * Transforms .md files into exportable modules.
 */
function markdownPlugin(): Plugin {
  return {
    name: 'vite-plugin-markdown',

    // Transform markdown files
    transform(code: string, id: string) {
      if (!id.endsWith('.md')) {
        return null
      }

      // Simple markdown to HTML conversion
      const html = code
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        .replace(/\*\*(.*)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>')

      return {
        code: `export default ${JSON.stringify(html)}`,
        map: null, // No source map for this simple transform
      }
    },
  }
}

console.log('Plugin 1: markdownPlugin')
console.log('- Transforms .md files to HTML strings')
console.log('- Usage: import content from "./readme.md"')

/**
 * Plugin 2: Virtual Module
 *
 * Creates a virtual module that doesn't exist on disk.
 */
function virtualModulePlugin(): Plugin {
  const virtualModuleId = 'virtual:build-info'
  const resolvedVirtualModuleId = '\0' + virtualModuleId

  return {
    name: 'vite-plugin-virtual-module',

    // Resolve virtual module imports
    resolveId(id: string) {
      if (id === virtualModuleId) {
        return resolvedVirtualModuleId
      }
      return null
    },

    // Load virtual module content
    load(id: string) {
      if (id === resolvedVirtualModuleId) {
        const buildInfo = {
          timestamp: new Date().toISOString(),
          version: process.env.npm_package_version || '0.0.0',
          nodeVersion: process.version,
        }

        return `export default ${JSON.stringify(buildInfo, null, 2)}`
      }
      return null
    },
  }
}

console.log('\nPlugin 2: virtualModulePlugin')
console.log('- Creates virtual:build-info module')
console.log('- Usage: import buildInfo from "virtual:build-info"')

/**
 * Plugin 3: Auto Import
 *
 * Automatically imports commonly used utilities.
 */
function autoImportPlugin(imports: Record<string, string[]>): Plugin {
  const importStatements = Object.entries(imports)
    .map(([from, names]) => `import { ${names.join(', ')} } from '${from}'`)
    .join('\n')

  return {
    name: 'vite-plugin-auto-import',

    transform(code: string, id: string) {
      // Only transform .ts and .tsx files
      if (!id.match(/\.[tj]sx?$/)) {
        return null
      }

      // Skip node_modules
      if (id.includes('node_modules')) {
        return null
      }

      // Check if any imports are used in the code
      const usedImports: string[] = []
      for (const names of Object.values(imports)) {
        for (const name of names) {
          if (code.includes(name)) {
            usedImports.push(name)
          }
        }
      }

      if (usedImports.length === 0) {
        return null
      }

      // Prepend imports
      return {
        code: importStatements + '\n' + code,
        map: null,
      }
    },
  }
}

console.log('\nPlugin 3: autoImportPlugin')
console.log('- Automatically imports specified utilities')
console.log('- Usage: autoImportPlugin({ "react": ["useState", "useEffect"] })')

/**
 * Plugin 4: Build Hooks
 *
 * Demonstrates various build lifecycle hooks.
 */
function buildHooksPlugin(): Plugin {
  let config: ResolvedConfig

  return {
    name: 'vite-plugin-build-hooks',

    // Called when config is resolved
    configResolved(resolvedConfig: ResolvedConfig) {
      config = resolvedConfig
      console.log('[build-hooks] Config resolved, mode:', config.mode)
    },

    // Called at build start
    buildStart() {
      console.log('[build-hooks] Build started')
    },

    // Called when bundle is generated
    generateBundle(_options, bundle) {
      console.log('[build-hooks] Generating bundle...')
      console.log('[build-hooks] Files:', Object.keys(bundle).length)

      // Add a custom asset to the bundle
      this.emitFile({
        type: 'asset',
        fileName: 'build-manifest.json',
        source: JSON.stringify(
          {
            generatedAt: new Date().toISOString(),
            files: Object.keys(bundle),
          },
          null,
          2
        ),
      })
    },

    // Called when bundle is written to disk
    writeBundle() {
      console.log('[build-hooks] Bundle written to disk')
    },

    // Called when build ends
    buildEnd() {
      console.log('[build-hooks] Build ended')
    },

    // Called when Vite server closes
    closeBundle() {
      console.log('[build-hooks] Bundle closed')
    },
  }
}

console.log('\nPlugin 4: buildHooksPlugin')
console.log('- Demonstrates build lifecycle hooks')
console.log('- Emits build-manifest.json with file list')

/**
 * Plugin 5: Dev Server Plugin
 *
 * Adds custom functionality to the dev server.
 */
function devServerPlugin(): Plugin {
  return {
    name: 'vite-plugin-dev-server',

    // Configure dev server
    configureServer(server) {
      // Add custom middleware
      server.middlewares.use('/api/health', (_req, res) => {
        res.setHeader('Content-Type', 'application/json')
        res.end(JSON.stringify({ status: 'ok', timestamp: Date.now() }))
      })

      // Listen for file changes
      server.watcher.on('change', (file) => {
        console.log('[dev-server] File changed:', file)
      })

      // Custom HMR handling
      server.ws.on('custom:event', (data) => {
        console.log('[dev-server] Custom event:', data)
      })
    },

    // Configure preview server
    configurePreviewServer(server) {
      server.middlewares.use('/api/health', (_req, res) => {
        res.setHeader('Content-Type', 'application/json')
        res.end(JSON.stringify({ status: 'preview', timestamp: Date.now() }))
      })
    },
  }
}

console.log('\nPlugin 5: devServerPlugin')
console.log('- Adds /api/health endpoint')
console.log('- Logs file changes')
console.log('- Handles custom HMR events')

/**
 * Plugin 6: Conditional Plugin
 *
 * Plugin that only runs in specific modes.
 */
function conditionalPlugin(options: { mode: 'dev' | 'build' | 'both' }): Plugin {
  return {
    name: 'vite-plugin-conditional',

    // Only apply during serve (development)
    apply: options.mode === 'dev' ? 'serve' : options.mode === 'build' ? 'build' : undefined,

    transform(code: string, id: string) {
      if (id.endsWith('.ts')) {
        // Add mode indicator to console output
        return {
          code: code.replace(
            /console\.log\(/g,
            `console.log('[${options.mode}]',`
          ),
          map: null,
        }
      }
      return null
    },
  }
}

console.log('\nPlugin 6: conditionalPlugin')
console.log('- Runs only in specified mode (dev/build/both)')
console.log('- Uses "apply" option for conditional execution')

/**
 * Key Takeaways:
 *
 * 1. Use transform() for file content modification
 * 2. Use resolveId() and load() for virtual modules
 * 3. Build hooks provide access to the build lifecycle
 * 4. configureServer() adds custom dev server functionality
 * 5. Use "apply" option for mode-specific plugins
 * 6. Always return null when not handling a file
 */

export {
  markdownPlugin,
  virtualModulePlugin,
  autoImportPlugin,
  buildHooksPlugin,
  devServerPlugin,
  conditionalPlugin,
}
