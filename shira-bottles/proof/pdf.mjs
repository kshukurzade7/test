// Combine page1.svg + page2.svg into an A4 PDF at true size, and save PNG previews.
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { readFileSync } from 'fs';

const pages = ['page1.svg', 'page2.svg'].map((f) => readFileSync(f, 'utf8'));
const html = `<!doctype html><meta charset="utf-8"><style>@page{size:A4;margin:0}html,body{margin:0}
.p{width:210mm;height:297mm;page-break-after:always;overflow:hidden}.p svg{display:block}</style>
${pages.map((p) => `<div class="p">${p}</div>`).join('')}`;
const b = await chromium.launch();
const pg = await b.newPage();
await pg.setContent(html);
await pg.evaluate(() => document.fonts.ready);
await pg.waitForTimeout(300);
await pg.pdf({ path: 'shira-label-proof.pdf', format: 'A4', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
const prev = await b.newPage({ viewport: { width: 794, height: 1123 }, deviceScaleFactor: 1.5 });
for (const [i, p] of pages.entries()) {
  await prev.setContent(`<body style="margin:0">${p.replace('width="210mm" height="297mm"', 'width="794" height="1123"')}</body>`);
  await prev.evaluate(() => document.fonts.ready); await prev.waitForTimeout(200);
  await prev.screenshot({ path: `preview-page${i + 1}.png` });
}
await b.close();
