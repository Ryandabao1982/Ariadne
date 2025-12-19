/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'deep-space': '#0A0E1A',
        'charcoal': '#151923',
        'graphite': '#2A3142',
        'cosmic-white': '#E4E6EB',
        'nebula-grey': '#9CA3AF',
        'stardust': '#6B7280',
        'ariadne-glow': '#818CF8',
        'verified-green': '#34D399',
        'attention-amber': '#FCD34D',
        'critical-red': '#F87171',
      }
    },
    fontFamily: {
      'sans': ['Inter', 'sans-serif'],
      'serif': ['Lora', 'serif'],
    }
  },
}
