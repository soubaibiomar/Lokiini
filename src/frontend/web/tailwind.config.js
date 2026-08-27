/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        lokiini: {
          teal: '#0F6E56',
          'teal-dark': '#0B5341',
          'teal-light': '#E6FCF5',
          terracotta: '#D85A30',
          'terracotta-dark': '#B84520',
          'terracotta-light': '#FFE8CC',
          sand: '#F7F4EE',
          charcoal: '#1E293B',
          amber: '#F59E0B',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Outfit', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
