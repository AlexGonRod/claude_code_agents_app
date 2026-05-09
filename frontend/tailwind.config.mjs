/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        'surface': '#FDF8F5',
        'surface-2': '#FBF2EE',
        'surface-3': '#F5E6DE',
        'primary': '#2D2836',
        'secondary': '#5D576B',
        'tertiary': '#1A1520',
        'accent-main': '#C46B60',
        'accent-2': '#98D4BE',
        'border': '#DDD0C8',
        'error': '#C95050',
        'success': '#5BA86D'
      },
      fontFamily: {
        display: ['Outfit', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      },
      boxShadow: {
        'swiss': '4px 4px 0 #E8D8D0',
        'swiss-sm': '2px 2px 0 #E8D8D0'
      }
    }
  },
  plugins: []
};