import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export const GET: APIRoute = async ({ site }) => {
  const articles = (await getCollection('articles'))
    .sort((a, b) => b.data.date.getTime() - a.data.date.getTime())
    .slice(0, 50);

  const base = (import.meta.env.BASE_URL ?? '/').replace(/\/$/, '');
  const siteUrl = site?.toString().replace(/\/$/, '') ?? '';

  const items = articles
    .map((a) => {
      const link = `${siteUrl}${base}/articles/${a.slug}/`;
      const summary = escapeXml(a.data.summary);
      const title = escapeXml(a.data.title);
      return `
    <item>
      <title>${title}</title>
      <link>${link}</link>
      <guid isPermaLink="true">${link}</guid>
      <pubDate>${a.data.date.toUTCString()}</pubDate>
      <category>${a.data.category}</category>
      <description>${summary}</description>
    </item>`;
    })
    .join('');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Almanac — Dentistry</title>
    <description>A daily curated brief on dentistry.</description>
    <link>${siteUrl}${base}/</link>
    <language>en</language>${items}
  </channel>
</rss>`;

  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};

function escapeXml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}
