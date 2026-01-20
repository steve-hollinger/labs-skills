/**
 * Exercise 3 Solution: Custom Vite Plugin for Markdown Components
 */

import type { Plugin } from 'vite'
import matter from 'gray-matter'
import { marked } from 'marked'

interface PluginOptions {
  /**
   * Enable syntax highlighting
   */
  highlight?: boolean

  /**
   * Custom marked options
   */
  markedOptions?: marked.MarkedOptions
}

export function mdxComponentPlugin(options: PluginOptions = {}): Plugin {
  const { markedOptions = {} } = options

  // Configure marked
  marked.setOptions({
    gfm: true, // GitHub Flavored Markdown
    breaks: true, // Convert \n to <br>
    ...markedOptions,
  })

  return {
    name: 'vite-plugin-mdx-component',

    // Optionally resolve .md imports to a virtual module
    resolveId(id, importer) {
      // Handle relative imports of .md files
      if (id.endsWith('.md') && importer) {
        // Let Vite handle the resolution
        return null
      }
      return null
    },

    // Transform markdown files
    transform(code: string, id: string) {
      if (!id.endsWith('.md')) {
        return null
      }

      try {
        // Parse frontmatter
        const { data: frontmatter, content } = matter(code)

        // Convert markdown to HTML
        const html = marked.parse(content) as string

        // Escape the HTML for embedding in JS
        const escapedHtml = html
          .replace(/\\/g, '\\\\')
          .replace(/`/g, '\\`')
          .replace(/\$/g, '\\$')

        // Escape frontmatter values
        const frontmatterJson = JSON.stringify(frontmatter, null, 2)

        // Generate the component code
        const componentCode = `
import { createElement } from 'react'

// Frontmatter metadata
export const frontmatter = ${frontmatterJson}

// HTML content
const htmlContent = \`${escapedHtml}\`

// React component
export default function MarkdownContent(props) {
  return createElement('article', {
    ...props,
    className: \`markdown-content \${props.className || ''}\`.trim(),
    dangerouslySetInnerHTML: { __html: htmlContent }
  })
}

// Named exports for convenience
export const title = frontmatter.title || null
export const date = frontmatter.date || null
export const author = frontmatter.author || null
export const tags = frontmatter.tags || []

// Raw content for custom rendering
export const rawContent = ${JSON.stringify(content)}
export const rawHtml = htmlContent
`

        // Add HMR support
        const hmrCode = `
if (import.meta.hot) {
  import.meta.hot.accept()
}
`

        return {
          code: componentCode + hmrCode,
          map: null, // Source maps could be added for better debugging
        }
      } catch (error) {
        this.error(`Failed to process markdown file: ${id}\n${error}`)
        return null
      }
    },

    // Add TypeScript support via virtual module
    resolveId(id) {
      if (id === 'virtual:markdown-types') {
        return '\0virtual:markdown-types'
      }
      return null
    },

    load(id) {
      if (id === '\0virtual:markdown-types') {
        return `
// Type definitions for .md imports
declare module '*.md' {
  import { FC, HTMLAttributes } from 'react'

  interface Frontmatter {
    title?: string
    date?: string
    author?: string
    tags?: string[]
    [key: string]: unknown
  }

  export const frontmatter: Frontmatter
  export const title: string | null
  export const date: string | null
  export const author: string | null
  export const tags: string[]
  export const rawContent: string
  export const rawHtml: string

  const MarkdownContent: FC<HTMLAttributes<HTMLElement>>
  export default MarkdownContent
}
`
      }
      return null
    },
  }
}

/**
 * Enhanced version with syntax highlighting using Shiki
 */
export function mdxComponentPluginWithHighlight(): Plugin {
  // Note: This would require async initialization for Shiki
  // This is a simplified example

  return {
    name: 'vite-plugin-mdx-component-highlight',

    async transform(code: string, id: string) {
      if (!id.endsWith('.md')) {
        return null
      }

      const { data: frontmatter, content } = matter(code)

      // In a real implementation, you would:
      // 1. Parse code blocks
      // 2. Highlight with Shiki
      // 3. Replace code blocks with highlighted HTML

      const html = marked.parse(content) as string
      const frontmatterJson = JSON.stringify(frontmatter, null, 2)

      const componentCode = `
import { createElement } from 'react'

export const frontmatter = ${frontmatterJson}

export default function MarkdownContent(props) {
  return createElement('article', {
    ...props,
    dangerouslySetInnerHTML: { __html: ${JSON.stringify(html)} }
  })
}

if (import.meta.hot) {
  import.meta.hot.accept()
}
`

      return { code: componentCode, map: null }
    },
  }
}

/**
 * Usage in vite.config.ts:
 *
 * import { defineConfig } from 'vite'
 * import { mdxComponentPlugin } from './plugins/vite-plugin-mdx-component'
 *
 * export default defineConfig({
 *   plugins: [mdxComponentPlugin()],
 * })
 */

/**
 * Usage in application:
 *
 * import GettingStarted, { frontmatter, title } from './docs/getting-started.md'
 *
 * function DocsPage() {
 *   return (
 *     <div>
 *       <h1>{title}</h1>
 *       <p>By {frontmatter.author} on {frontmatter.date}</p>
 *       <GettingStarted className="prose" />
 *     </div>
 *   )
 * }
 */

/**
 * Add to src/vite-env.d.ts for TypeScript support:
 *
 * /// <reference types="vite/client" />
 *
 * declare module '*.md' {
 *   import { FC, HTMLAttributes } from 'react'
 *
 *   interface Frontmatter {
 *     title?: string
 *     date?: string
 *     author?: string
 *     tags?: string[]
 *     [key: string]: unknown
 *   }
 *
 *   export const frontmatter: Frontmatter
 *   export const title: string | null
 *   export const date: string | null
 *   export const author: string | null
 *   export const tags: string[]
 *
 *   const MarkdownContent: FC<HTMLAttributes<HTMLElement>>
 *   export default MarkdownContent
 * }
 */

export default mdxComponentPlugin
