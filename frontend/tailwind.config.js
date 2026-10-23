/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
        festive: {
          gold: '#F59E0B',
          amber: '#D97706',
          ruby: '#E11D48',
          emerald: '#10B981',
          royal: '#1E3A8A'
        }
      }
    },
  },
  plugins: [],
}
