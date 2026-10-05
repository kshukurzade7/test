// Combine collection/page*.svg into one A4 PDF at true size.
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { readFileSync, readdirSync } from 'fs';
const files = readdirSync('collection').filter((f) => /^page\d+\.svg$/.test(f)).sort((a, b) => parseInt(a.slice(4)) - parseInt(b.slice(4)));
const html = `<!doctype html><meta charset="utf-8"><style>@page{size:A4;margin:0}html,body{margin:0}
.p{width:210mm;height:297mm;page-break-after:always;overflow:hidden}.p svg{display:block}</style>
${files.map((f) => `<div class="p">${readFileSync('collection/' + f, 'utf8')}</div>`).join('')}`;
const b = await chromium.launch(); const pg = await b.newPage();
await pg.setContent(html); await pg.evaluate(() => document.fonts.ready); await pg.waitForTimeout(300);
await pg.pdf({ path: 'collection/shira-collection-label-proof.pdf', format: 'A4', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
await b.close();
