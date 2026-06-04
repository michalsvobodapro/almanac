# Almanac — Project Conventions

This file is read by Claude Code at the start of every session in this repo.

## What this is

A static news portal aggregating dentistry news across six specialties (conservative, endodontics, periodontology, implantology, orthodontics, other), regenerated daily by a GitHub Actions cron at 23:23 UTC (≈ Prague midnight; see Cron drift below). See [README.md](./README.md) for the high-level pitch.

## Stack

- **Site:** Astro 4 (static output), TypeScript strict, zero JS by default
- **Pipeline:** Python 3.12 via `uv`, Pydantic v2 for schemas
- **AI:** Claude Sonnet 4.6 (`claude-sonnet-4-6`), tool-forced JSON output
- **Hosting:** GitHub Pages via Actions

## Conventions

- **Schemas:** Truth lives in `src/content/config.ts` (Zod, Astro reads). Mirrored in `scripts/models.py` (Pydantic, pipeline writes). Update both together. The `CATEGORIES` enum (`conservative | endodontics | periodontology | implantology | orthodontics | other`) is defined in both — keep in sync.
- **Hydration:** Only `ThemeToggle`, `SourceFilter`, `LandingPicker` ship JS. Everything else is zero-JS Astro components.
- **Settings:** Client-side only. localStorage keys prefixed `almanac.*`. No backend, no accounts.
- **Languages:** Articles preserve source language (EN or CS). Site chrome (nav, footer, settings) is English.
- **Categorization:** Sources don't map 1:1 to specialties — Claude classifies each *item* into a category at digest time. Sources may set `primaryCategory` in `sources.yaml` as a hint for the /sources page only.
- **Design:** Editorial / magazine. Warm paper light + true editorial dark. Fraunces (display) + Inter (body), both self-hosted woff2. No Google Fonts at runtime. **Not** Alveodont's clinical blue.
- **Cron drift:** Accepted (GitHub schedules are best-effort). Cron is `23 23 * * *` UTC ≈ local midnight in Prague — the earliest slot that's already "tomorrow" in `Europe/Prague` (which `digest.py` uses to date the edition), so the run can't generate the previous day. The typical +2.5–5h GitHub delay lands it ~03:00–06:00 local, before a 06:00 wake-up on a normal day. Year-round; DST drift accepted. A hard "done by 06:00" guarantee would need an external trigger.

## Workflow rules (inherited from ~/claude/CLAUDE.md)

- Never commit to `main` — feature branches only (`feature/`, `fix/`, `chore/`)
- Push branches to remote immediately after creation
- Never blur the line between planning and implementing
- Track work in `tasks/todo.md`

## Generated files

The daily workflow auto-commits to `main` as `almanac-bot`:
- `src/content/articles/YYYY-MM-DD-*.md`
- `src/content/digests/YYYY-MM-DD.md`
- `data/source-status.json`
- `data/feed-cache/`

Filter these from `git log` with: `git log --invert-grep --grep="^digest:"`

## Don't

- Don't reuse Alveodont's design tokens or Urbanist/blue palette here
- Don't add a backend or database
- Don't add Google Fonts at runtime
- Don't ship JS for components that don't need interactivity
- Don't fail the daily run because one source died — surface it on `/sources` and continue
