# Almanac

A daily curated brief covering **AI** and **Dentistry** news. Built for one reader; published openly.

- **Live site:** `https://<gh-user>.github.io/almanac/` (set after first deploy)
- **Schedule:** every day at 04:00 UTC (≈06:00 Prague summer / 05:00 winter — we accept the DST drift)
- **Stack:** Astro (static site) + Python (digest pipeline) + Claude Sonnet 4.6 (curation & summaries)
- **Hosting:** GitHub Pages, deployed by GitHub Actions

## How it works

Every morning a GitHub Actions job:

1. Fetches RSS/Atom feeds listed in [`sources.yaml`](./sources.yaml).
2. Dedupes, filters to the last 24h, caps total volume.
3. Sends candidates to Claude, which picks 5 AI + 5 dentistry stories, ranks them, and writes 2–3 sentence summaries in each story's original language (English or Czech).
4. Writes one Markdown file per story to `src/content/articles/` and commits back.
5. Builds the Astro site and deploys to GitHub Pages.

Cost target: ~$0.10/day.

## Local development

```bash
# Install everything
uv sync
pnpm install

# Run the site (uses whatever's already in src/content/)
pnpm dev

# Run the pipeline (writes new articles/digests)
echo 'ANTHROPIC_API_KEY=sk-ant-...' > .env.local
uv run python scripts/digest.py --dry-run    # fetch only, no Claude call
uv run python scripts/digest.py              # full live run

# Build & preview
pnpm build
pnpm preview
```

## Repo layout

```
src/          Astro site (pages, components, layouts, styles)
scripts/      Python digest pipeline (fetch → dedupe → Claude → write)
sources.yaml  All RSS feeds, single source of truth
data/         ETag cache + last-fetch status (committed)
.github/      Workflows
```

See [`tasks/todo.md`](./tasks/todo.md) for ongoing work.
