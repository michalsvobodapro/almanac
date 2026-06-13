import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

// Minimal per-article index consumed client-side by /saved/ (save-for-later)
// and the Anki export. Keeps the saved page a static file that hydrates from
// localStorage — no backend.
export const GET: APIRoute = async () => {
  const articles = await getCollection('articles');
  const data = articles.map((a) => ({
    slug: a.slug,
    title: a.data.title,
    category: a.data.category,
    summary: a.data.summary,
    takeaway: a.data.clinicalTakeaway ?? '',
    date: a.data.digestDate,
    source: a.data.sourceName,
    et: a.data.evidenceType ?? null,
    eg: a.data.evidenceGrade ?? 'na',
  }));
  return new Response(JSON.stringify(data), {
    headers: { 'content-type': 'application/json' },
  });
};
