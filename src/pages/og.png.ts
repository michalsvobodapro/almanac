import type { APIRoute } from 'astro';
import { renderCard } from '../lib/og';

// Default social-share card (homepage + any page without a specific card).
export const GET: APIRoute = () => {
  const png = renderCard({
    kicker: 'Daily edition',
    title: 'Every morning, the dentistry worth your time.',
  });
  return new Response(new Uint8Array(png), {
    headers: { 'content-type': 'image/png', 'cache-control': 'public, max-age=86400' },
  });
};
