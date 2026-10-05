// Render label SVGs to PNG previews (and 3D textures without dieline).
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { readFileSync } from 'fs';
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 2400, height: 1300 } });
for (const k of ['apricot', 'pomegranate', 'grape']) {
  for (const [src, out, html] of [
    [`shira-${k}-label.svg`, `preview-${k}.png`, (s) => s.replace(/width="196mm" height="101mm"/, 'width="2352" height="1212"')],
    [`shira-${k}-label-texture.svg`, `../studio/textures/${k}-wrap.png`, (s) => s]]) {
    await p.setContent(`<body style="margin:0">${html(readFileSync(src, 'utf8'))}</body>`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150);
    await p.locator('svg').screenshot({ path: out });
  }
}
await b.close();
