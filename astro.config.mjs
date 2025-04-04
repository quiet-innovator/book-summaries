// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import dotenv from 'dotenv';

dotenv.config(); // ✅ Load environment variables from .env file

export default defineConfig({
  site: 'http://localhost:4321', // Replace with your live domain when ready
  integrations: [mdx(), sitemap()],
});
