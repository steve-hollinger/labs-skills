/**
 * Vite 7 Skill - Main Entry Point
 *
 * This is the main entry point for the Vite skill examples.
 * Run `npm run dev` to start the development server.
 */

import './style.css'

// Type-safe environment variables
declare global {
  interface ImportMetaEnv {
    readonly VITE_API_URL: string
    readonly VITE_APP_TITLE: string
  }
}

function main(): void {
  const app = document.querySelector<HTMLDivElement>('#app')

  if (!app) {
    console.error('App container not found')
    return
  }

  // Display environment info
  const envInfo = {
    mode: import.meta.env.MODE,
    dev: import.meta.env.DEV,
    prod: import.meta.env.PROD,
    baseUrl: import.meta.env.BASE_URL,
    apiUrl: import.meta.env.VITE_API_URL || 'Not configured',
  }

  app.innerHTML = `
    <div class="container">
      <h1>Vite 7 Skill</h1>
      <p>Modern Frontend Build Tooling</p>

      <section>
        <h2>Environment</h2>
        <pre>${JSON.stringify(envInfo, null, 2)}</pre>
      </section>

      <section>
        <h2>Examples</h2>
        <ul>
          <li><strong>Example 1:</strong> Basic Setup - Project structure and configuration</li>
          <li><strong>Example 2:</strong> Dev Server - Proxy, CORS, and middleware</li>
          <li><strong>Example 3:</strong> Build Optimization - Code splitting and chunks</li>
          <li><strong>Example 4:</strong> Custom Plugins - Transform and virtual modules</li>
        </ul>
        <p>Run <code>make examples</code> to execute all examples.</p>
      </section>

      <section>
        <h2>Quick Commands</h2>
        <pre>
make setup      # Install dependencies
make dev        # Start dev server
make build      # Build for production
make test       # Run tests
make examples   # Run all examples
        </pre>
      </section>

      <section>
        <h2>HMR Status</h2>
        <p id="hmr-status">${import.meta.hot ? 'HMR is enabled - edit this file to see updates!' : 'HMR not available'}</p>
        <p>Last updated: <span id="timestamp">${new Date().toLocaleTimeString()}</span></p>
      </section>
    </div>
  `

  // Demonstrate HMR
  if (import.meta.hot) {
    import.meta.hot.accept(() => {
      console.log('HMR update received')
    })
  }
}

// Initialize app
main()

// Export for testing
export { main }
