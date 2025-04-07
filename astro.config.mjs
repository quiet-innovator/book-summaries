// astro.config.mjs
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import icons from 'astro-icon';
import react from '@astrojs/react';
import astroI18n from 'astro-i18n';
import dotenv from 'dotenv';

dotenv.config();

export default defineConfig({
  site: 'https://minutereads.io', // make sure this is your live domain
  integrations: [
    mdx(), 
    sitemap(), 
    icons(),
    react(), // React integration
    astroI18n() // Adding astro-i18n integration
  ],
  content: {
    // ✅ register the content config!
    entryGlob: './src/content/**/*.{md,mdx}',
  },
});