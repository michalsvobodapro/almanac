/** Build-time citation strings. Vancouver (the style used in Czech medical/
 * dental academic writing) + BibTeX. No AI, no runtime cost — just formatting
 * the frontmatter the pipeline already produced. */

interface CiteData {
  title: string;
  originalTitle: string;
  author?: string;
  sourceName: string;
  sourceUrl: string;
  date: Date;
}

function doiFrom(url: string): string | null {
  const m = url.match(/doi\.org\/(10\.[^\s?#]+)/i);
  return m ? m[1] : null;
}

function year(d: Date): number {
  return new Date(d).getUTCFullYear();
}

function cleanTitle(d: CiteData): string {
  return (d.originalTitle || d.title).replace(/\s*\.\s*$/, '').trim();
}

/** e.g. "Issrani R et al. Comparative evaluation of … Acta Odontol Scand. 2026. doi:10.2340/aos.v85.46274" */
export function citationVancouver(d: CiteData): string {
  const author = (d.author || '').trim();
  const title = cleanTitle(d);
  const doi = doiFrom(d.sourceUrl);
  const tail = doi ? `doi:${doi}` : `Available from: ${d.sourceUrl}`;
  const lead = author ? `${author}. ` : '';
  return `${lead}${title}. ${d.sourceName}. ${year(d.date)}. ${tail}`;
}

export function citationBibtex(d: CiteData): string {
  const title = cleanTitle(d);
  const doi = doiFrom(d.sourceUrl);
  const firstAuthor = (d.author || 'anon').split(/[ ,]/)[0].toLowerCase().replace(/[^a-z]/g, '') || 'anon';
  const firstTitleWord = (title.match(/[A-Za-z]+/) || ['ref'])[0].toLowerCase();
  const key = `${firstAuthor}${year(d.date)}${firstTitleWord}`;
  const lines = [
    `@article{${key},`,
    `  title = {${title}},`,
    d.author ? `  author = {${d.author}},` : null,
    `  journal = {${d.sourceName}},`,
    `  year = {${year(d.date)}},`,
    doi ? `  doi = {${doi}},` : null,
    `  url = {${d.sourceUrl}}`,
    `}`,
  ].filter(Boolean);
  return lines.join('\n');
}
