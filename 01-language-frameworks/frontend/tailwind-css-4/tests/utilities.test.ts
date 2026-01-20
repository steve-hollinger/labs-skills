/**
 * Tailwind CSS Utility Tests
 *
 * These tests verify understanding of Tailwind utility patterns.
 */

import { describe, it, expect } from 'vitest'

describe('Tailwind CSS Utility Patterns', () => {
  describe('Spacing System', () => {
    it('should understand the spacing scale', () => {
      const spacingScale: Record<string, string> = {
        '0': '0',
        'px': '1px',
        '0.5': '0.125rem',
        '1': '0.25rem',
        '2': '0.5rem',
        '3': '0.75rem',
        '4': '1rem',
        '5': '1.25rem',
        '6': '1.5rem',
        '8': '2rem',
        '10': '2.5rem',
        '12': '3rem',
        '16': '4rem',
        '20': '5rem',
        '24': '6rem',
      }

      expect(spacingScale['4']).toBe('1rem')
      expect(spacingScale['8']).toBe('2rem')
      expect(spacingScale['px']).toBe('1px')
    })

    it('should convert spacing values to pixels', () => {
      const remToPixels = (rem: number): number => rem * 16

      expect(remToPixels(0.25)).toBe(4) // p-1
      expect(remToPixels(0.5)).toBe(8) // p-2
      expect(remToPixels(1)).toBe(16) // p-4
      expect(remToPixels(1.5)).toBe(24) // p-6
    })
  })

  describe('Breakpoint System', () => {
    it('should understand mobile-first breakpoints', () => {
      const breakpoints: Record<string, number> = {
        sm: 640,
        md: 768,
        lg: 1024,
        xl: 1280,
        '2xl': 1536,
      }

      expect(breakpoints.sm).toBe(640)
      expect(breakpoints.md).toBe(768)
      expect(breakpoints.lg).toBe(1024)
    })

    it('should determine active breakpoints', () => {
      const getActiveBreakpoints = (width: number): string[] => {
        const breakpoints: Array<[string, number]> = [
          ['sm', 640],
          ['md', 768],
          ['lg', 1024],
          ['xl', 1280],
          ['2xl', 1536],
        ]

        return breakpoints
          .filter(([, minWidth]) => width >= minWidth)
          .map(([name]) => name)
      }

      expect(getActiveBreakpoints(320)).toEqual([])
      expect(getActiveBreakpoints(640)).toEqual(['sm'])
      expect(getActiveBreakpoints(768)).toEqual(['sm', 'md'])
      expect(getActiveBreakpoints(1024)).toEqual(['sm', 'md', 'lg'])
      expect(getActiveBreakpoints(1536)).toEqual(['sm', 'md', 'lg', 'xl', '2xl'])
    })
  })

  describe('Color System', () => {
    it('should understand color shade scale', () => {
      const shades = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]

      expect(shades).toContain(50)
      expect(shades).toContain(500)
      expect(shades).toContain(950)
      expect(shades.length).toBe(11)
    })

    it('should provide contrast pairs', () => {
      const contrastPairs: Record<number, number> = {
        50: 900,
        100: 800,
        200: 700,
        300: 700,
        400: 900,
        500: 50,
        600: 50,
        700: 100,
        800: 100,
        900: 50,
        950: 50,
      }

      // Light backgrounds need dark text
      expect(contrastPairs[50]).toBe(900)
      expect(contrastPairs[100]).toBe(800)

      // Dark backgrounds need light text
      expect(contrastPairs[900]).toBe(50)
      expect(contrastPairs[950]).toBe(50)
    })
  })

  describe('Typography Scale', () => {
    it('should understand font size scale', () => {
      const fontSizes: Record<string, string> = {
        xs: '0.75rem',
        sm: '0.875rem',
        base: '1rem',
        lg: '1.125rem',
        xl: '1.25rem',
        '2xl': '1.5rem',
        '3xl': '1.875rem',
        '4xl': '2.25rem',
        '5xl': '3rem',
      }

      expect(fontSizes.base).toBe('1rem')
      expect(fontSizes.lg).toBe('1.125rem')
      expect(fontSizes['2xl']).toBe('1.5rem')
    })
  })

  describe('Utility Class Patterns', () => {
    it('should parse utility class components', () => {
      const parseUtility = (className: string) => {
        // Simple parser for common patterns
        const patterns = [
          /^(p|m|w|h)-(\d+|px|auto)$/,
          /^(p|m)(x|y|t|r|b|l)-(\d+|px|auto)$/,
          /^(text|bg|border)-(\w+)-(\d+)$/,
          /^(flex|grid|block|hidden|inline)$/,
        ]

        for (const pattern of patterns) {
          const match = className.match(pattern)
          if (match) return { valid: true, parts: match.slice(1) }
        }

        return { valid: false, parts: [] }
      }

      expect(parseUtility('p-4').valid).toBe(true)
      expect(parseUtility('mx-auto').valid).toBe(true)
      expect(parseUtility('text-blue-500').valid).toBe(true)
      expect(parseUtility('flex').valid).toBe(true)
    })

    it('should understand responsive prefixes', () => {
      const parseResponsive = (className: string) => {
        const breakpoints = ['sm', 'md', 'lg', 'xl', '2xl']
        const parts = className.split(':')

        if (parts.length === 1) {
          return { breakpoint: null, utility: parts[0] }
        }

        const [prefix, utility] = parts
        if (breakpoints.includes(prefix)) {
          return { breakpoint: prefix, utility }
        }

        return { breakpoint: null, utility: className }
      }

      expect(parseResponsive('flex')).toEqual({ breakpoint: null, utility: 'flex' })
      expect(parseResponsive('md:flex')).toEqual({ breakpoint: 'md', utility: 'flex' })
      expect(parseResponsive('lg:hidden')).toEqual({ breakpoint: 'lg', utility: 'hidden' })
    })

    it('should understand state variants', () => {
      const stateVariants = [
        'hover',
        'focus',
        'active',
        'disabled',
        'first',
        'last',
        'odd',
        'even',
        'group-hover',
        'peer-focus',
      ]

      const parseVariant = (className: string) => {
        const parts = className.split(':')
        const variants: string[] = []
        let utility = className

        for (const part of parts) {
          if (stateVariants.includes(part)) {
            variants.push(part)
          } else {
            utility = part
          }
        }

        return { variants, utility }
      }

      expect(parseVariant('hover:bg-blue-600')).toEqual({
        variants: ['hover'],
        utility: 'bg-blue-600',
      })

      expect(parseVariant('focus:ring-2')).toEqual({
        variants: ['focus'],
        utility: 'ring-2',
      })
    })
  })

  describe('Dark Mode', () => {
    it('should parse dark mode classes', () => {
      const parseDarkMode = (className: string) => {
        if (className.startsWith('dark:')) {
          return {
            darkMode: true,
            utility: className.slice(5),
          }
        }
        return {
          darkMode: false,
          utility: className,
        }
      }

      expect(parseDarkMode('bg-white')).toEqual({ darkMode: false, utility: 'bg-white' })
      expect(parseDarkMode('dark:bg-gray-900')).toEqual({ darkMode: true, utility: 'bg-gray-900' })
    })

    it('should provide dark mode color pairs', () => {
      const darkModePairs: Record<string, string> = {
        'bg-white': 'dark:bg-gray-900',
        'bg-gray-50': 'dark:bg-gray-800',
        'bg-gray-100': 'dark:bg-gray-700',
        'text-gray-900': 'dark:text-white',
        'text-gray-700': 'dark:text-gray-200',
        'text-gray-500': 'dark:text-gray-400',
        'border-gray-200': 'dark:border-gray-700',
      }

      expect(darkModePairs['bg-white']).toBe('dark:bg-gray-900')
      expect(darkModePairs['text-gray-900']).toBe('dark:text-white')
    })
  })
})
