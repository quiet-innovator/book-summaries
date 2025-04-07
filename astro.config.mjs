// astro.config.mjs
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import icons from 'astro-icon';
import react from '@astrojs/react';
import dotenv from 'dotenv';

// Import astro-i18n using the suggested way
import pkg from 'astro-i18n';
const astroI18n = pkg.default || pkg;

dotenv.config();

export default defineConfig({
  site: 'https://minutereads.io', // make sure this is your live domain
  integrations: [
    mdx(), 
    sitemap(), 
    icons(),
    react(), // React integration
    astroI18n() // Using the correctly imported function
  ],
  content: {
    // ✅ register the content config!
    entryGlob: './src/content/**/*.{md,mdx}',
  },
});