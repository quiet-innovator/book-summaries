// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
	site: 'https://example.com',
	integrations: [mdx(), sitemap()],
});

import { defineConfig } from 'astro/config';
import dotenv from 'dotenv';

dotenv.config(); // ✅ Load .env variables

export default defineConfig({
  // Your Astro config
});
