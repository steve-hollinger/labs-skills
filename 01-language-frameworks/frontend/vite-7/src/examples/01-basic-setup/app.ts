/**
 * Basic App Module
 *
 * Demonstrates a simple module structure that Vite can serve as an ES module.
 */

interface App {
  name: string
  version: string
  mount: (element: HTMLElement | null) => void
  unmount: () => void
}

export function createApp(): App {
  let mountedElement: HTMLElement | null = null

  return {
    name: 'ViteBasicApp',
    version: '1.0.0',

    mount(element: HTMLElement | null) {
      if (!element) {
        console.warn('Mount element not found')
        return
      }

      mountedElement = element
      element.innerHTML = `
        <div id="app">
          <h1>Vite Basic Setup</h1>
          <p>This app was served using Vite's native ES module system.</p>
          <p>Edit this file and see HMR in action!</p>
        </div>
      `
      console.log('App mounted to:', element.id || 'element')
    },

    unmount() {
      if (mountedElement) {
        mountedElement.innerHTML = ''
        mountedElement = null
        console.log('App unmounted')
      }
    },
  }
}

// Named exports work seamlessly with Vite
export const APP_NAME = 'ViteBasicApp'
export const APP_VERSION = '1.0.0'
