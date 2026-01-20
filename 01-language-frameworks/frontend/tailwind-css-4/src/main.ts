/**
 * Tailwind CSS 4 Skill - Main Entry Point
 */

import './style.css'

// Theme toggle functionality
function initThemeToggle(): void {
  const themeToggle = document.getElementById('theme-toggle')

  if (!themeToggle) return

  // Check for saved preference or system preference
  const savedTheme = localStorage.getItem('theme')
  const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches

  if (savedTheme === 'dark' || (!savedTheme && systemDark)) {
    document.documentElement.classList.add('dark')
  }

  themeToggle.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark')
    const isDark = document.documentElement.classList.contains('dark')
    localStorage.setItem('theme', isDark ? 'dark' : 'light')
  })
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initThemeToggle)

console.log('Tailwind CSS 4 Skill loaded')
console.log('Run `make dev` to start the development server')

export { initThemeToggle }
