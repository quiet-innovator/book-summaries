// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import icons from 'astro-icon';
import dotenv from 'dotenv';

dotenv.config(); // ✅ Load environment variables from .env file

export default defineConfig({
  site: 'https://minutereads.io', // ✅ Set to live domain
  output: 'static', // ✅ Ensures proper static site generation
  integrations: [
    mdx(),
    sitemap(),
    icons() // ✅ For social icons
  ],
});
