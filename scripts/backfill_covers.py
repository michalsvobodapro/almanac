"""One-shot: re-download cover images for already-committed articles.

For each article in `src/content/articles/*.md`:

- If `coverImage` is set but the file under `public/<coverImage>` is missing,
  try to re-download it from `coverSourceUrl` (preferred) or by re-parsing
  the article page's og:image via `enrich_metadata(sourceUrl)`.
- If the download still fails, strip `coverImage`, `coverAlt`, and
  `coverSourceUrl` from the frontmatter so the card's category-band fallback
  engages instead of a broken <img>.

Idempotent. Re-running is cheap (download_image() short-circuits on cache hits).

Usage:
    uv run python scripts/backfill_covers.py
"""

from __future__ import annotations

from pathlib import Path

import frontmatter
import httpx

from enrichment import download_image, enrich_metadata


REPO_ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = REPO_ROOT / "src" / "content" / "articles"
COVER_DIR = REPO_ROOT / "public" / "og-cache"
PUBLIC_DIR = REPO_ROOT / "public"
USER_AGENT = "almanac-bot/1.0 (+https://github.com/michalsvobodapro/almanac)"


def main() -> int:
    if not ARTICLES_DIR.exists():
        print(f"No articles dir at {ARTICLES_DIR}")
        return 1

    paths = sorted(ARTICLES_DIR.glob("*.md"))
    print(f"Scanning {len(paths)} articles in {ARTICLES_DIR}")

    fixed = 0
    refetched = 0
    stripped = 0
    skipped_ok = 0

    headers = {"User-Agent": USER_AGENT}
    with httpx.Client(headers=headers, follow_redirects=True) as client:
        for path in paths:
            post = frontmatter.load(path)
            cover_image = post.get("coverImage")
            if not cover_image:
                continue

            # The frontmatter path is site-absolute, e.g. "/og-cache/foo.jpg".
            # Resolve against public/ on disk.
            rel = str(cover_image).lstrip("/")
            on_disk = PUBLIC_DIR / rel

            if on_disk.exists() and on_disk.stat().st_size > 0:
                skipped_ok += 1
                continue

            slug = path.stem
            cover_source_url = post.get("coverSourceUrl")

            # Try the explicit coverSourceUrl first.
            new_filename = None
            if cover_source_url:
                new_filename = download_image(
                    str(cover_source_url),
                    dest_dir=COVER_DIR,
                    slug=slug,
                    client=client,
                )

            # Fall back to re-parsing og:image from the article page.
            if not new_filename:
                article_url = post.get("sourceUrl")
                if article_url:
                    enr = enrich_metadata(str(article_url), client=client)
                    if enr and enr.og_image_url:
                        new_filename = download_image(
                            enr.og_image_url,
                            dest_dir=COVER_DIR,
                            slug=slug,
                            client=client,
                        )
                        if new_filename:
                            post["coverSourceUrl"] = enr.og_image_url

            if new_filename:
                new_path = f"/og-cache/{new_filename}"
                if new_path != cover_image:
                    post["coverImage"] = new_path
                    path.write_text(frontmatter.dumps(post) + "\n", encoding="utf-8")
                print(f"  ✓ {slug}  →  {new_filename}")
                fixed += 1
                refetched += 1
                continue

            # Give up: strip the broken refs so the band fallback shows.
            removed_any = False
            for key in ("coverImage", "coverAlt", "coverSourceUrl"):
                if key in post.metadata:
                    del post.metadata[key]
                    removed_any = True
            if removed_any:
                path.write_text(frontmatter.dumps(post) + "\n", encoding="utf-8")
                print(f"  ✗ {slug}  (stripped frontmatter — no usable og:image)")
                stripped += 1

    print()
    print(f"  on-disk already OK: {skipped_ok}")
    print(f"  re-downloaded:      {refetched}")
    print(f"  stripped:           {stripped}")
    print(f"  total touched:      {fixed + stripped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
