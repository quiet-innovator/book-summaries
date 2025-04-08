// astro.config.mjs
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://minutereads.io',
  output: 'static',
  build: {
    format: 'file',
  },
  // ... other settings if any
});
