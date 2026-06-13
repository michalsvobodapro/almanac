// Build-time helpers for one-card Anki (Basic) export. A probe — no SM-2, no
// scheduler. Front = the story; Back = the chairside takeaway + source +
// evidence level.

interface CardData {
  title: string;
  clinicalTakeaway?: string;
  summary: string;
  sourceName: string;
  evidenceType?: string | null;
  evidenceGrade?: string;
}

export function cardFront(d: CardData): string {
  return d.title;
}

export function cardBack(d: CardData): string {
  const body = (d.clinicalTakeaway && d.clinicalTakeaway.trim()) || d.summary;
  const grade = d.evidenceGrade && d.evidenceGrade !== 'na' ? `, ${d.evidenceGrade}` : '';
  const ev = d.evidenceType ? ` [${d.evidenceType}${grade}]` : '';
  return `${body} — ${d.sourceName}${ev}`;
}
