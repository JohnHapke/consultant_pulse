/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        condensed: ['"Barlow Condensed"', 'sans-serif'],
        sans: ['Barlow', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        base: '#080809',
        surface: '#0F0F11',
        elevated: '#161619',
        hover: '#1C1C20',
        border: '#222226',
        'border-bright': '#32323A',
      },
    },
  },
  plugins: [],
}
