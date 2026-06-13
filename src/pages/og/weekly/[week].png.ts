import type { APIRoute, GetStaticPaths } from 'astro';
import { getCollection, type CollectionEntry } from 'astro:content';
import { renderCard } from '../../../lib/og';

export const getStaticPaths: GetStaticPaths = async () => {
  const weeks = await getCollection('weekly');
  return weeks.map((entry) => ({ params: { week: entry.data.week }, props: { entry } }));
};

export const GET: APIRoute = ({ props }) => {
  const { data } = (props as { entry: CollectionEntry<'weekly'> }).entry;
  const png = renderCard({ kicker: `Weekly · ${data.rangeEnd}`, title: data.title });
  return new Response(new Uint8Array(png), {
    headers: { 'content-type': 'image/png', 'cache-control': 'public, max-age=86400' },
  });
};
