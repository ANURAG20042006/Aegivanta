/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: '#080C14',
          surface: '#0F172A',
          card: '#1E293B',
          border: '#334155',
          cyan: '#00F0FF',
          green: '#00FF9D',
          red: '#FF0055',
          amber: '#FFB800',
          purple: '#A855F7',
          text: '#F8FAFC',
          muted: '#94A3B8'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'cyan-glow': '0 0 20px rgba(0, 240, 255, 0.35)',
        'red-glow': '0 0 20px rgba(255, 0, 85, 0.35)',
        'green-glow': '0 0 20px rgba(0, 255, 157, 0.35)',
      }
    },
  },
  plugins: [],
}
