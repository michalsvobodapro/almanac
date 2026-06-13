import type { APIRoute, GetStaticPaths } from 'astro';
import { getCollection, type CollectionEntry } from 'astro:content';
import { renderCard, OG_PALETTE } from '../../../lib/og';
import { CATEGORY_LABELS, EVIDENCE_TYPE_LABELS } from '../../../content/config';

export const getStaticPaths: GetStaticPaths = async () => {
  const articles = await getCollection('articles');
  return articles.map((article) => ({ params: { slug: article.slug }, props: { article } }));
};

export const GET: APIRoute = ({ props }) => {
  const { data } = (props as { article: CollectionEntry<'articles'> }).article;
  const ev = data.evidenceType ? ` · ${EVIDENCE_TYPE_LABELS[data.evidenceType]}` : '';
  const png = renderCard({
    kicker: `${CATEGORY_LABELS[data.category]}${ev}`,
    title: data.title,
    accent: OG_PALETTE[data.category] ?? OG_PALETTE.default,
  });
  return new Response(new Uint8Array(png), {
    headers: { 'content-type': 'image/png', 'cache-control': 'public, max-age=86400' },
  });
};
