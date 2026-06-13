import type { CollectionEntry } from 'astro:content';
import type { Category } from '../content/config';

// Story Arcs: research threads built at BUILD TIME from the `topicThread` the
// triage pass assigns. No pipeline change, no AI cost, no committed memory file
// — pure derivation from existing article data. A thread becomes an arc once it
// has ≥2 stories. The triage model is told to reuse phrasing for the same
// thread, so exact normalized matching is enough; fuzzy merging is a future
// refinement.

export interface Arc {
  id: string;
  label: string;
  articles: CollectionEntry<'articles'>[]; // chronological, oldest → newest
  firstSeen: string;
  lastSeen: string;
  categories: Category[];
}

function normThread(s: string): string {
  return s.toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}

function labelFor(key: string): string {
  const words = key.replace(/-/g, ' ').trim();
  return words.charAt(0).toUpperCase() + words.slice(1);
}

export function buildArcs(articles: CollectionEntry<'articles'>[]): Arc[] {
  const byKey = new Map<string, CollectionEntry<'articles'>[]>();
  for (const a of articles) {
    const t = a.data.topicThread;
    if (!t) continue;
    const key = normThread(t);
    if (!key) continue;
    const bucket = byKey.get(key);
    if (bucket) bucket.push(a);
    else byKey.set(key, [a]);
  }

  const arcs: Arc[] = [];
  for (const [key, arts] of byKey) {
    if (arts.length < 2) continue;
    const sorted = [...arts].sort((a, b) =>
      a.data.digestDate.localeCompare(b.data.digestDate),
    );
    arcs.push({
      id: key,
      label: labelFor(key),
      articles: sorted,
      firstSeen: sorted[0].data.digestDate,
      lastSeen: sorted[sorted.length - 1].data.digestDate,
      categories: [...new Set(sorted.map((a) => a.data.category))],
    });
  }

  // Most recently active first, then deepest threads.
  return arcs.sort(
    (a, b) => b.lastSeen.localeCompare(a.lastSeen) || b.articles.length - a.articles.length,
  );
}

/** The arc containing a given article slug, plus its chronological position. */
export function findArc(
  arcs: Arc[],
  slug: string,
): { arc: Arc; index: number } | null {
  for (const arc of arcs) {
    const index = arc.articles.findIndex((a) => a.slug === slug);
    if (index >= 0) return { arc, index };
  }
  return null;
}
