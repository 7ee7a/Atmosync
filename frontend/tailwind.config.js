/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0A0A0A',
        text: '#EAEAEA',
        accent: '#00FFFF', // neon cyan
      }
    },
  },
  plugins: [],
}
