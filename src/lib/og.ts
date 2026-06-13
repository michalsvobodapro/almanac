import { Resvg } from '@resvg/resvg-js';
import { join } from 'node:path';

// Build-time social-share card + app-icon renderer. Editorial brand: warm
// paper, Fraunces display serif, category-coloured accent. Rasterized to PNG
// with resvg using the vendored fonts in src/assets/og/.
const FONT_DIR = join(process.cwd(), 'src/assets/og');
const W = 1200;
const H = 630;
const PAD = 80;

export const OG_PALETTE: Record<string, string> = {
  conservative: '#b45309',
  endodontics: '#c2410c',
  periodontology: '#be185d',
  implantology: '#1d4ed8',
  orthodontics: '#15803d',
  other: '#475569',
  default: '#b91c1c',
};

const esc = (s: string) =>
  String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function wrap(text: string, max: number, maxLines: number): string[] {
  const words = text.split(/\s+/);
  const lines: string[] = [];
  let cur = '';
  for (const w of words) {
    const t = cur ? cur + ' ' + w : w;
    if (t.length > max && cur) {
      lines.push(cur);
      cur = w;
    } else {
      cur = t;
    }
    if (lines.length === maxLines) break;
  }
  if (cur && lines.length < maxLines) lines.push(cur);
  if (lines.length === maxLines) {
    const used = lines.join(' ').split(/\s+/).length;
    if (used < words.length) {
      lines[maxLines - 1] = lines[maxLines - 1].replace(/[.,;:]?$/, '') + '…';
    }
  }
  return lines;
}

export interface CardOpts {
  kicker?: string;
  title: string;
  footer?: string;
  accent?: string;
}

function cardSvg({
  kicker = 'Daily edition',
  title,
  footer = 'michalsvobodapro.github.io/almanac',
  accent = OG_PALETTE.default,
}: CardOpts): string {
  const fontSize = title.length > 78 ? 50 : title.length > 50 ? 58 : 70;
  const lines = wrap(title, Math.floor((W - 2 * PAD) / (fontSize * 0.6)), 3);
  const lh = fontSize * 1.12;
  const startY = (H - lines.length * lh) / 2 + fontSize * 0.78;
  const titleSvg = lines
    .map(
      (l, i) =>
        `<text x="${PAD}" y="${startY + i * lh}" font-family="Fraunces" font-weight="600" font-size="${fontSize}" fill="#1a1814">${esc(l)}</text>`,
    )
    .join('');

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <rect width="${W}" height="${H}" fill="#faf8f3"/>
  <rect x="0" y="0" width="10" height="${H}" fill="${accent}"/>
  <g stroke="#e6dfd0" stroke-width="1">
    <line x1="${PAD}" y1="${PAD + 44}" x2="${W - PAD}" y2="${PAD + 44}"/>
    <line x1="${PAD}" y1="${H - PAD - 40}" x2="${W - PAD}" y2="${H - PAD - 40}"/>
  </g>
  <circle cx="${PAD + 7}" cy="${PAD + 12}" r="7" fill="${accent}"/>
  <text x="${PAD + 26}" y="${PAD + 20}" font-family="Inter" font-weight="700" font-size="27" letter-spacing="5" fill="#1a1814">ALMANAC</text>
  <text x="${W - PAD}" y="${PAD + 20}" text-anchor="end" font-family="Inter" font-weight="600" font-size="22" letter-spacing="3" fill="${accent}">${esc(kicker.toUpperCase())}</text>
  ${titleSvg}
  <text x="${PAD}" y="${H - PAD + 2}" font-family="Inter" font-weight="500" font-size="25" fill="#5c574d">A daily brief on dentistry</text>
  <text x="${W - PAD}" y="${H - PAD + 2}" text-anchor="end" font-family="Inter" font-weight="500" font-size="22" fill="#8a8478">${esc(footer)}</text>
</svg>`;
}

function rasterize(svg: string, width: number): Buffer {
  const r = new Resvg(svg, {
    fitTo: { mode: 'width', value: width },
    font: { fontDirs: [FONT_DIR], loadSystemFonts: false, defaultFontFamily: 'Fraunces' },
  });
  return Buffer.from(r.render().asPng());
}

export function renderCard(opts: CardOpts): Buffer {
  return rasterize(cardSvg(opts), W);
}

/** Square app icon — dark tile, cream Fraunces "A", accent dot. */
export function renderIcon(size = 180): Buffer {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="180" height="180" viewBox="0 0 180 180">
  <rect width="180" height="180" rx="38" fill="#1a1814"/>
  <text x="86" y="128" text-anchor="middle" font-family="Fraunces" font-weight="600" font-size="124" fill="#faf8f3">A</text>
  <circle cx="134" cy="54" r="11" fill="#b91c1c"/>
</svg>`;
  return rasterize(svg, size);
}
