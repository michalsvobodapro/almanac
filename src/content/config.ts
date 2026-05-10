import { defineCollection, z } from 'astro:content';

export const CATEGORIES = [
  'conservative',
  'endodontics',
  'periodontology',
  'implantology',
  'orthodontics',
  'other',
] as const;

export type Category = (typeof CATEGORIES)[number];

export const CATEGORY_LABELS: Record<Category, string> = {
  conservative: 'Conservative',
  endodontics: 'Endodontics',
  periodontology: 'Periodontology',
  implantology: 'Implantology',
  orthodontics: 'Orthodontics',
  other: 'Other',
};

const articles = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    originalTitle: z.string(),
    date: z.coerce.date(),
    digestDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
    category: z.enum(CATEGORIES),
    rank: z.number().int().min(1).max(20),
    summary: z.string(),
    summaryDeep: z.string().optional(),
    summaryLang: z.enum(['en', 'cs']),
    sourceId: z.string(),
    sourceName: z.string(),
    sourceUrl: z.string().url(),
    excerpt: z.string().optional(),
    excerptFull: z.string().optional(),
    coverImage: z.string().optional(),
    coverAlt: z.string().optional(),
    coverSourceUrl: z.string().url().optional(),
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
    articleSlugs: z.array(z.string()),
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
