// Contact sheet of all front panels (first 95 mm of each texture) for review.
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { readFileSync, readdirSync } from 'fs';
const keys = process.argv.slice(2);
const svgs = keys.map((k) => readFileSync(`collection/shira-${k}-label-texture.svg`, 'utf8')
  .replace(/viewBox="0 0 196 101"[^>]*>/, 'viewBox="3 3 95 95" width="380" height="380">'));
const html = `<body style="margin:0;background:#E9DDCB;display:grid;grid-template-columns:repeat(4,380px);gap:22px;padding:28px">${svgs.join('')}</body>`;
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1700, height: 1400 } });
await p.setContent(html); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
await p.screenshot({ path: 'collection/contact-sheet.png', fullPage: true }); await b.close();
