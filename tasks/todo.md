# Almanac — TODO

Build is being driven by harness task list. This file mirrors major milestones for posterity.

## MVP (in progress)

- [x] Scaffold repo (Astro + uv + configs)
- [ ] Design system (tokens, fonts, BaseLayout)
- [ ] Content collections (Zod schemas + sample fixtures)
- [ ] All v1 pages with sample data
- [ ] Settings page interactivity
- [ ] sources.yaml (6–8 hand-tested feeds)
- [ ] Python pipeline (fetch + dedupe + models)
- [ ] Claude rank + write articles + orchestrator
- [ ] Tests (pytest)
- [ ] GitHub Actions workflows
- [ ] Local end-to-end verification
- [ ] Push to GitHub + flip Pages settings

## v1.1 (after MVP ships)

- [ ] **Source URL curation** — most feed URLs in `sources.yaml` are best-guesses and 404/500. Verify each on the publisher site, replace with real RSS endpoints. PubMed needs real saved-search IDs (create on pubmed.ncbi.nlm.nih.gov, take the RSS link they generate).
- [ ] Expand to ~20 sources (more journals: J. Endo, J. Perio, Clin. Oral Implants, EJO, J. Prosthet. Dent.)
- [ ] OG image generation per article
- [ ] Per-category RSS feeds (`/conservative/rss.xml` etc.)
- [ ] Title-similarity dedupe v2

## v1.2+ (deferred)

- [ ] Pagefind static search
- [ ] Save-for-later (localStorage)
- [ ] Sunday weekly best-of digest
- [ ] Telegram/Discord webhook
- [ ] Per-source contribution heatmap
- [ ] On-demand CZ→EN translation button
