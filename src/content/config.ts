import { defineCollection, z } from 'astro:content';

const articles = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    originalTitle: z.string(),
    date: z.coerce.date(),
    digestDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
    section: z.enum(['ai', 'dentistry']),
    rank: z.number().int().min(1).max(10),
    summary: z.string(),
    summaryLang: z.enum(['en', 'cs']),
    sourceId: z.string(),
    sourceName: z.string(),
    sourceUrl: z.string().url(),
    excerpt: z.string().optional(),
    author: z.string().optional(),
    tags: z.array(z.string()).default([]),
    relatedSlugs: z.array(z.string()).default([]),
  }),
});

const digests = defineCollection({
  type: 'content',
  schema: z.object({
    date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
    builtAt: z.coerce.date(),
    intro: z.string(),
    aiSlugs: z.array(z.string()),
    dentistrySlugs: z.array(z.string()),
    heroSlug: z.string(),
    stats: z.object({
      itemsFetched: z.number(),
      itemsConsidered: z.number(),
      sourcesOk: z.number(),
      sourcesError: z.number(),
      claudeInputTokens: z.number(),
      claudeOutputTokens: z.number(),
      claudeCachedTokens: z.number(),
      costUsd: z.number(),
    }),
  }),
});

export const collections = { articles, digests };
