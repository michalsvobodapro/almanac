import type { APIRoute } from 'astro';
import { renderIcon } from '../lib/og';

// 180×180 home-screen / app icon — dark tile, cream serif "A", accent dot.
export const GET: APIRoute = () => {
  return new Response(new Uint8Array(renderIcon(180)), {
    headers: { 'content-type': 'image/png', 'cache-control': 'public, max-age=604800' },
  });
};
