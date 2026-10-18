// Wrap the flat label artwork (svg/v<n>-<flavour>.svg) onto the bottle photos and
// write mockups/v<n>-<photo>.png plus mockups/compare.png (all three concepts, all bottles).
//
// The bottle body is found in each photo (widest straight section), treated as a
// 66 mm cylinder, and each label column is placed by its arc position (sin mapping),
// darkened towards the edges and given a soft highlight like the glass in the photo.
// Run:  python3 labels.py && node mockup.mjs
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { mkdirSync, readFileSync, writeFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const here = dirname(fileURLToPath(import.meta.url));
const BOTTLES = [
  ['bottle-1', 'rosehip'], ['bottle-2', 'apple'], ['bottle-3', 'blackcurrant'],
  ['bottle-4', 'cranberry'], ['bottle-5', 'redcurrant'],
];
const CONCEPTS = [
  // label height (mm), centre offset from the middle of the straight body (mm, + = lower), paper?
  { id: 'v1', height: 84, offset: 4, paper: true, title: '1 — Kiçik ön etiket' },
  { id: 'v2', height: 70, offset: 0, paper: false, title: '2 — Şəffaf etiket' },
  { id: 'v3', height: 45, offset: 6, paper: true, title: '3 — Ortada zolaq' },
];
const DIAMETER = 66; // mm
const dataUrl = (file, type) => `data:${type};base64,${readFileSync(file).toString('base64')}`;

mkdirSync(join(here, 'mockups'), { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage();
await page.setContent('<canvas id="c"></canvas>');

for (const [photo, flavour] of BOTTLES) {
  const photoUrl = dataUrl(join(here, 'photos', `${photo}.webp`), 'image/webp');
  for (const c of CONCEPTS) {
    const labelUrl = dataUrl(join(here, 'svg', `${c.id}-${flavour}.svg`), 'image/svg+xml');
    const png = await page.evaluate(async ({ photoUrl, labelUrl, c, DIAMETER }) => {
      const load = (src) => new Promise((ok, err) => { const i = new Image(); i.onload = () => ok(i); i.onerror = err; i.src = src; });
      const [img, label] = await Promise.all([load(photoUrl), load(labelUrl)]);
      const W = img.naturalWidth, H = img.naturalHeight;
      const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
      const ctx = cv.getContext('2d'); ctx.drawImage(img, 0, 0);
      const px = ctx.getImageData(0, 0, W, H).data;
      const bg = [px[0], px[1], px[2]];
      const differs = (x, y) => { const i = (y * W + x) * 4; return Math.abs(px[i] - bg[0]) + Math.abs(px[i + 1] - bg[1]) + Math.abs(px[i + 2] - bg[2]) > 120; }; // the backdrop has a soft grey shadow low down: ignore mild differences
      // Bottle edges per row, then the straight body = rows at (nearly) full width.
      const rows = [];
      for (let y = Math.round(H * 0.3); y < Math.round(H * 0.86); y++) {
        let l = 0, r = W - 1;
        while (l < W && !differs(l, y)) l++;
        while (r > 0 && !differs(r, y)) r--;
        rows.push({ y, l, r, w: r - l });
      }
      const maxW = Math.max(...rows.map((r) => r.w));
      const body = rows.filter((r) => r.w > maxW * 0.97);
      const top = body[0].y, bottom = body[body.length - 1].y;
      const mid = body[Math.floor(body.length / 2)];
      const cx = (mid.l + mid.r) / 2, rad = (mid.r - mid.l) / 2 * 0.985; // label sits just inside the glass edge
      const s = (2 * rad) / DIAMETER; // px per mm
      // Flat label rendered at screen resolution.
      const lw = label.naturalWidth, lh = label.naturalHeight;
      const flatW = Math.round(lw / lh * c.height * s), flatH = Math.round(c.height * s);
      const flat = document.createElement('canvas'); flat.width = flatW; flat.height = flatH;
      flat.getContext('2d').drawImage(label, 0, 0, flatW, flatH);
      const yc = (top + bottom) / 2 + c.offset * s - flatH / 2;
      // Wrap: one screen column at a time.
      const layer = document.createElement('canvas'); layer.width = W; layer.height = H;
      const lc = layer.getContext('2d');
      const halfArc = flatW / 2; // px of label from its centre to each side
      for (let x = Math.ceil(cx - rad); x < cx + rad; x++) {
        const t = (x + 0.5 - cx) / rad; if (Math.abs(t) >= 1) continue;
        const theta = Math.asin(t);
        const u = theta * rad; // arc length from the front centre, px
        if (Math.abs(u) > halfArc) continue;
        const sx = u + halfArc;
        const dy = rad * 0.035 * (1 - Math.cos(theta)); // slight smile: camera a little above the label
        lc.drawImage(flat, sx, 0, 1 / Math.cos(theta), flatH, x, yc + dy, 1, flatH); // 1 screen px = 1/cos(θ) px of label
      }
      // Light: darker towards the sides, soft highlight left of centre (as on the glass).
      lc.globalCompositeOperation = 'source-atop';
      const g = lc.createLinearGradient(cx - rad, 0, cx + rad, 0);
      const stops = [[0, 0.42], [0.12, 0.2], [0.3, 0.04], [0.5, 0.0], [0.72, 0.06], [0.9, 0.22], [1, 0.45]];
      for (const [o, a] of stops) g.addColorStop(o, `rgba(20,10,5,${c.paper ? a : a * 0.6})`);
      lc.fillStyle = g; lc.fillRect(0, 0, W, H);
      const hl = lc.createLinearGradient(cx - rad, 0, cx + rad, 0);
      hl.addColorStop(0.18, 'rgba(255,255,255,0)'); hl.addColorStop(0.27, `rgba(255,255,255,${c.paper ? 0.22 : 0.12})`);
      hl.addColorStop(0.36, 'rgba(255,255,255,0)');
      lc.fillStyle = hl; lc.fillRect(0, 0, W, H);
      ctx.globalAlpha = c.paper ? 1 : 0.93; // clear-film print lets a hint of the juice through
      ctx.drawImage(layer, 0, 0);
      return cv.toDataURL('image/png');
    }, { photoUrl, labelUrl, c, DIAMETER });
    writeFileSync(join(here, 'mockups', `${c.id}-${photo}.png`), Buffer.from(png.split(',')[1], 'base64'));
  }
}

// Comparison sheet: one row per concept, all bottles side by side.
const cell = (f) => `<img src="${dataUrl(join(here, 'mockups', f), 'image/png')}">`;
const rows = CONCEPTS.map((c) => `<h2>${c.title}</h2><div class="row">${BOTTLES.map(([p]) => cell(`${c.id}-${p}.png`)).join('')}</div>`).join('');
await page.setViewportSize({ width: 1400, height: 900 });
await page.setContent(`<!doctype html><meta charset="utf-8"><body style="margin:0;padding:24px;background:#F3F1EE;font:700 26px Arial,sans-serif;color:#2A1A12">
<style>.row{display:flex;gap:6px}.row img{width:266px;height:auto;border-radius:6px}h2{font-size:26px;margin:10px 0 10px}</style>${rows}</body>`);
await page.screenshot({ path: join(here, 'mockups', 'compare.png'), fullPage: true });
await browser.close();
