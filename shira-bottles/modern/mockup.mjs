// Wrap the modern labels (svg/<concept>-<flavour>.svg, 60 x 100 mm) onto the bottle
// photos. Writes mockups/<concept>-<photo>.png, mockups/<concept>-lineup.png,
// mockups/compare.png (all concepts) and mockups/closeup.png.
// Run:  python3 design.py && node mockup.mjs
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { mkdirSync, readFileSync, writeFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const here = dirname(fileURLToPath(import.meta.url));
const photos = join(here, '..', 'band', 'photos');
const BOTTLES = [
  ['bottle-1', 'rosehip'], ['bottle-2', 'apple'], ['bottle-3', 'blackcurrant'],
  ['bottle-4', 'cranberry'], ['bottle-5', 'redcurrant'],
];
const CONCEPTS = [
  { id: 'noir', paper: true, title: '1 — Noir: qara etiket, qızılı SHIRÁ' },
  { id: 'colour', paper: true, title: '2 — Rəngli: dadın tünd rəngində etiket' },
  { id: 'clear', paper: false, title: '3 — Şəffaf: yazı birbaşa şüşədə' },
];
const DIAMETER = 66, LABEL_W = 60, LABEL_H = 100; // mm
const dataUrl = (file, type) => `data:${type};base64,${readFileSync(file).toString('base64')}`;

mkdirSync(join(here, 'mockups'), { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage();

for (const [photo, flavour] of BOTTLES) {
  const photoUrl = dataUrl(join(photos, `${photo}.webp`), 'image/webp');
  for (const c of CONCEPTS) {
    const labelUrl = dataUrl(join(here, 'svg', `${c.id}-${flavour}.svg`), 'image/svg+xml');
    const png = await page.evaluate(async ({ photoUrl, labelUrl, paper, DIAMETER, LABEL_W, LABEL_H }) => {
      const load = (src) => new Promise((ok, err) => { const i = new Image(); i.onload = () => ok(i); i.onerror = err; i.src = src; });
      const [img, label] = await Promise.all([load(photoUrl), load(labelUrl)]);
      const W = img.naturalWidth, H = img.naturalHeight;
      const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
      const ctx = cv.getContext('2d'); ctx.drawImage(img, 0, 0);
      const px = ctx.getImageData(0, 0, W, H).data;
      const bg = [px[0], px[1], px[2]];
      const diff = (x, y) => { const i = (y * W + x) * 4; return Math.abs(px[i] - bg[0]) + Math.abs(px[i + 1] - bg[1]) + Math.abs(px[i + 2] - bg[2]); };
      // Straight body = rows at (nearly) full width; ignore the soft grey shadow low down.
      const rows = [];
      for (let y = Math.round(H * 0.3); y < Math.round(H * 0.86); y++) {
        let l = 0, r = W - 1; while (l < W && diff(l, y) < 120) l++; while (r > 0 && diff(r, y) < 120) r--;
        rows.push({ y, l, r, w: r - l });
      }
      const maxW = Math.max(...rows.map((r) => r.w));
      const body = rows.filter((r) => r.w > maxW * 0.97);
      const mid = body[Math.floor(body.length / 2)];
      const cx = (mid.l + mid.r) / 2, rad = (mid.r - mid.l) / 2 * 0.985, s = 2 * rad / DIAMETER;
      const fw = Math.round(LABEL_W * s), fh = Math.round(LABEL_H * s);
      const flat = document.createElement('canvas'); flat.width = fw; flat.height = fh;
      flat.getContext('2d').drawImage(label, 0, 0, fw, fh);
      const yTop = (body[0].y + body[body.length - 1].y) / 2 - fh / 2 + 4 * s;
      const layer = document.createElement('canvas'); layer.width = W; layer.height = H;
      const lc = layer.getContext('2d');
      for (let x = Math.ceil(cx - rad); x < cx + rad; x++) {
        const t = (x + 0.5 - cx) / rad; if (Math.abs(t) >= 1) continue;
        const th = Math.asin(t), u = th * rad; if (Math.abs(u) > fw / 2) continue;
        lc.drawImage(flat, u + fw / 2, 0, 1 / Math.cos(th), fh, x, yTop + rad * 0.035 * (1 - Math.cos(th)), 1, fh);
      }
      lc.globalCompositeOperation = 'source-atop';
      const k = paper ? 1 : 0.5;
      const g = lc.createLinearGradient(cx - rad, 0, cx + rad, 0);
      for (const [o, a] of [[0, 0.5], [0.12, 0.25], [0.3, 0.06], [0.5, 0], [0.72, 0.08], [0.9, 0.26], [1, 0.52]]) g.addColorStop(o, `rgba(0,0,0,${a * k})`);
      lc.fillStyle = g; lc.fillRect(0, 0, W, H);
      const hl = lc.createLinearGradient(cx - rad, 0, cx + rad, 0);
      hl.addColorStop(0.17, 'rgba(255,255,255,0)'); hl.addColorStop(0.27, `rgba(255,255,255,${0.16 * k})`); hl.addColorStop(0.37, 'rgba(255,255,255,0)');
      lc.fillStyle = hl; lc.fillRect(0, 0, W, H);
      ctx.globalAlpha = paper ? 1 : 0.95;
      ctx.drawImage(layer, 0, 0);
      return cv.toDataURL('image/png');
    }, { photoUrl, labelUrl, paper: c.paper, DIAMETER, LABEL_W, LABEL_H });
    writeFileSync(join(here, 'mockups', `${c.id}-${photo}.png`), Buffer.from(png.split(',')[1], 'base64'));
  }
}

const img = (f, style) => `<img src="${dataUrl(join(here, 'mockups', f), 'image/png')}" style="${style}">`;
const row = (c) => `<div style="display:flex;justify-content:center;align-items:flex-start">${BOTTLES.map(([p]) => img(`${c.id}-${p}.png`, 'width:280px;height:auto')).join('')}</div>`;
for (const c of CONCEPTS) {
  await page.setViewportSize({ width: 1400, height: 374 });
  await page.setContent(`<body style="margin:0;background:#fff">${row(c)}</body>`);
  await page.screenshot({ path: join(here, 'mockups', `${c.id}-lineup.png`) });
}
await page.setViewportSize({ width: 1400, height: 800 });
await page.setContent(`<body style="margin:0;background:#F4F2EF;font:700 24px Arial,sans-serif;color:#231E1A">
${CONCEPTS.map((c) => `<div style="padding:16px 24px 4px">${c.title}</div>${row(c)}`).join('')}</body>`);
await page.screenshot({ path: join(here, 'mockups', 'compare.png'), fullPage: true });
const crop = (f) => `<div style="width:460px;height:820px;overflow:hidden;background:#fff">${img(f, 'width:1260px;margin:-620px 0 0 -400px')}</div>`;
await page.setViewportSize({ width: 1380, height: 820 });
await page.setContent(`<body style="margin:0;display:flex">${crop('noir-bottle-3.png')}${crop('colour-bottle-1.png')}${crop('noir-bottle-2.png')}</body>`);
await page.screenshot({ path: join(here, 'mockups', 'closeup.png') });
await browser.close();
