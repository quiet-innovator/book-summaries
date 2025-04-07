// astro.config.mjs
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import icons from 'astro-icon';
import react from '@astrojs/react';

export default defineConfig({
  site: 'https://minutereads.io',
  integrations: [
    mdx(), 
    sitemap(), 
    icons(),
    react()
  ],
  output: 'static', // Make sure we're doing a static build
  build: {
    format: 'file'
  }
});