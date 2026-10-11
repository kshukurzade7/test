// Export final/svg/*.svg to transparent PNGs and vector PDFs with the pre-installed Chromium.
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { mkdirSync, readFileSync, readdirSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const dir = join(dirname(fileURLToPath(import.meta.url)), 'final');
mkdirSync(join(dir, 'png'), { recursive: true });
mkdirSync(join(dir, 'pdf'), { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage();
for (const file of readdirSync(join(dir, 'svg')).filter((f) => f.endsWith('.svg')).sort()) {
  const name = file.replace(/\.svg$/, '');
  const svg = readFileSync(join(dir, 'svg', file), 'utf8');
  const [, w, h] = svg.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/).map(Number);
  // PNG: 2000 px on the long side (1080 x 1080 for the avatar), transparent unless the SVG has a background.
  const px = name === 'shira-avatar' ? 1080 : 2000;
  const scale = px / Math.max(w, h);
  const W = Math.round(w * scale), H = Math.round(h * scale);
  const sized = svg.replace(/width="\d+" height="\d+"/, `width="${W}" height="${H}"`);
  await page.setViewportSize({ width: W, height: H });
  await page.setContent(`<html><body style="margin:0;background:transparent">${sized}</body></html>`);
  await page.screenshot({ path: join(dir, 'png', `${name}.png`), omitBackground: true, clip: { x: 0, y: 0, width: W, height: H } });
  // PDF: vector, page size = artwork size (1 SVG unit = 1 mm).
  const mm = svg.replace(/width="\d+" height="\d+"/, `width="${w}mm" height="${h}mm"`);
  await page.setContent(`<html><head><style>@page{size:${w}mm ${h}mm;margin:0}html,body{margin:0}svg{display:block}</style></head><body>${mm}</body></html>`);
  await page.pdf({ path: join(dir, 'pdf', `${name}.pdf`), width: `${w}mm`, height: `${h}mm`, printBackground: true, pageRanges: '1' });
}
await browser.close();
