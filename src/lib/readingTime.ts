/** Estimate reading time in whole minutes from one or more text blobs.
 * ~200 wpm, floored at 1 minute. Build-time only — no AI, no JS shipped. */
export function readingMinutes(...texts: (string | undefined | null)[]): number {
  const words = texts
    .filter((t): t is string => Boolean(t))
    .join(' ')
    .trim()
    .split(/\s+/)
    .filter(Boolean).length;
  return Math.max(1, Math.round(words / 200));
}
