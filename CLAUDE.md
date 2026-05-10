# Almanac — Project Conventions

This file is read by Claude Code at the start of every session in this repo.

## What this is

A static news portal aggregating dentistry news across six specialties (conservative, endodontics, periodontology, implantology, orthodontics, other), regenerated daily by a GitHub Actions cron at 04:00 UTC. See [README.md](./README.md) for the high-level pitch.

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
- **Cron drift:** Accepted. Cron is `0 4 * * *` UTC year-round.

## Workflow rules (inherited from ~/claude/CLAUDE.md)

- Never commit to `main` — feature branches only (`feature/`, `fix/`, `chore/`). The user-level `guard-main-branch.sh` hook enforces this; it fires from `~/.claude/hooks/`.
- Push branches to remote immediately after creation
- Never blur the line between planning and implementing
- Track work in `tasks/todo.md`

## Project config — `.claude/project.json`

Drives the parameterization of user-level skills and hooks (live at `~/.claude/`). Key fields for Almanac:

- `ticket_prefix: "MIC-"` — Linear tickets share the MIC team with Alveodont and Alabooster (sibling dental projects). Project on Linear: "Almanac" under team `michalsvoboda`.
- `base_port: 4321` — Astro's dev default. The user-level `/server` skill assumes uvicorn and **does not apply here**. Use `pnpm dev` directly.
- `db_file: null` — no database.
- `github_repo: "michalsvobodapro/almanac"` — used by `/commit`, future `/ship`, and any GitHub-aware skill.
- `linear: { … }` — populated with the MIC team UUID + Almanac project UUID. Generalized `/plan` and `/start` will create MIC-prefixed tickets under the Almanac project.

If you change the schema (e.g. add a custom Almanac-only field), reflect it in `~/.claude-personal/projects/-Users-michalsvoboda-claude/memory/reference_claude_config_layout.md` so future sessions know.

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
