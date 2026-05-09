import { defineConfig } from 'astro/config';
import svelte from '@astrojs/svelte';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  extensions: ['.astro', '.svelte'],
  integrations: [svelte(), tailwind()],
  output: 'static',
  site: 'http://localhost:3000',
  prefetch: true
});