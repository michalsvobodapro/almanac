import { defineConfig } from 'astro/config';

const GH_USER = process.env.ALMANAC_GH_USER || 'michalsvobodapro';

export default defineConfig({
  site: `https://${GH_USER}.github.io`,
  base: '/almanac',
  trailingSlash: 'always',
  output: 'static',
  build: {
    format: 'directory',
  },
  vite: {
    server: { fs: { allow: ['..'] } },
  },
});
