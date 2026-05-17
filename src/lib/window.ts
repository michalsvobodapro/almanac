/**
 * Rolling-window article selection shared by the home page and the
 * specialisation pages.
 *
 * Both page types want to read like a *weekly* brief rather than a single
 * day. We take the last `WINDOW_DAYS` days of articles anchored to the most
 * recent `digestDate` present in the data (anchoring on the data — not
 * build-time `new Date()` — keeps builds deterministic and survives cron
 * drift, per Almanac's CLAUDE.md). On a slow news week the window can be
 * nearly empty, so if it yields fewer than `MIN_ARTICLES` we fall back to the
 * most recent `MIN_ARTICLES` regardless of age.
 */

export const WINDOW_DAYS = 7;
export const MIN_ARTICLES = 12;

/** Minimal shape this helper depends on — satisfied by CollectionEntry<'articles'>. */
type ArticleLike = { data: { digestDate: string; rank: number } };

export interface WindowResult<T> {
  /** All selected articles, `digestDate` desc then `rank` asc. */
  flat: T[];
  /** Same articles bucketed by `digestDate`, days desc, articles `rank` asc. */
  groups: { date: string; articles: T[] }[];
}

export interface WindowOptions {
  windowDays?: number;
  minArticles?: number;
}

/** Subtract whole days from a `YYYY-MM-DD` string, returning `YYYY-MM-DD`. */
function subtractDays(dateStr: string, days: number): string {
  const d = new Date(`${dateStr}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() - days);
  return d.toISOString().slice(0, 10);
}

export function selectWindow<T extends ArticleLike>(
  articles: T[],
  opts: WindowOptions = {},
): WindowResult<T> {
  const windowDays = opts.windowDays ?? WINDOW_DAYS;
  const minArticles = opts.minArticles ?? MIN_ARTICLES;

  if (articles.length === 0) return { flat: [], groups: [] };

  // `digestDate` is fixed-width `YYYY-MM-DD`, so lexicographic compare is
  // chronological — no Date parsing needed for ordering.
  const sorted = articles.slice().sort((a, b) => {
    if (a.data.digestDate !== b.data.digestDate) {
      return b.data.digestDate.localeCompare(a.data.digestDate);
    }
    return a.data.rank - b.data.rank;
  });

  const anchor = sorted[0].data.digestDate; // max digestDate in the data
  const cutoff = subtractDays(anchor, windowDays - 1); // inclusive lower bound

  let flat = sorted.filter((a) => a.data.digestDate >= cutoff);
  if (flat.length < minArticles) {
    flat = sorted.slice(0, minArticles);
  }

  // `flat` is already day-desc / rank-asc, so a single pass yields the groups
  // with each day's articles in the right order.
  const groups: WindowResult<T>['groups'] = [];
  for (const a of flat) {
    const last = groups[groups.length - 1];
    if (last && last.date === a.data.digestDate) {
      last.articles.push(a);
    } else {
      groups.push({ date: a.data.digestDate, articles: [a] });
    }
  }

  return { flat, groups };
}
