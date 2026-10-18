// Rasterise the arch wrap-label textures (no dieline) to PNG for mock.py.
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { readFileSync, mkdirSync } from 'fs';
const keys = process.argv.slice(2);
const wd = process.env.DESIGN ? `wraps-${process.env.DESIGN}` : 'wraps';
mkdirSync(wd, { recursive: true });
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 2400, height: 1300 } });
for (const k of keys) {
  const svg = readFileSync(`../label/collection-${process.env.DESIGN || 'arch'}/shira-${k}-label-texture.svg`, 'utf8');
  await p.setContent(`<body style="margin:0">${svg}</body>`);
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200);
  await p.locator('svg').screenshot({ path: `${wd}/${k}.png` });
}
await b.close();
