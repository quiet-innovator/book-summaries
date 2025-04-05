import { defineCollection, z } from 'astro:content';

const books = defineCollection({
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    heroImage: z.string().optional(),
    tags: z.array(z.string()).optional(),
    author: z.string() // ✅ Automatically extracted in Colab script
  }),
});

export const collections = {
  books,
};
