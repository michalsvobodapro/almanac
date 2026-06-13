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

// Mirrors EvidenceType in scripts/models.py — keep the two in sync.
export const EVIDENCE_TYPES = [
  'guideline',
  'systematic-review',
  'rct',
  'cohort',
  'case-control',
  'lab',
  'news',
] as const;

export type EvidenceType = (typeof EVIDENCE_TYPES)[number];

export const EVIDENCE_TYPE_LABELS: Record<EvidenceType, string> = {
  guideline: 'Guideline',
  'systematic-review': 'Systematic review',
  rct: 'RCT',
  cohort: 'Cohort',
  'case-control': 'Case-control',
  lab: 'Lab study',
  news: 'News / opinion',
};

export const EVIDENCE_GRADES = ['high', 'moderate', 'low', 'na'] as const;
export type EvidenceGrade = (typeof EVIDENCE_GRADES)[number];

export const EVIDENCE_GRADE_LABELS: Record<EvidenceGrade, string> = {
  high: 'High',
  moderate: 'Moderate',
  low: 'Low',
  na: 'Not graded',
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
    // Evidence appraisal — all optional so pre-migration articles render as
    // "unrated". Mirrors ArticleFrontmatter in scripts/models.py.
    evidenceType: z.enum(EVIDENCE_TYPES).optional(),
    evidenceGrade: z.enum(EVIDENCE_GRADES).default('na'),
    sampleSize: z.number().int().optional(),
    evidenceNote: z.string().optional(),
    topicThread: z.string().optional(),
    clinicalTakeaway: z.string().optional(),
    guidelineFlag: z.boolean().default(false),
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
