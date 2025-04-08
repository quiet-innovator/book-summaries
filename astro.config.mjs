import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import { z } from 'zod';

export default defineConfig({
  site: 'https://minutereads.io',
  output: 'static',
  build: {
    format: 'file',
  },
  integrations: [
    react(), // Enables support for .jsx/.tsx components
  ],
  content: {
    collections: {
      books: {
        schema: ({ z }) =>
          z.object({
            title: z.string(),
            author: z.string(),
            pubDate: z.string().refine(val => !isNaN(Date.parse(val)), {
              message: "Invalid date",
            }),
            description: z.string().optional(),
            language: z.string(),
            amazonLink: z.string().url(),
          }),
      },
    },
  },
});
