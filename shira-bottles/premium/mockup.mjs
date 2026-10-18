// Premium direction on the bottle photos: the narrow ivory front label wrapped onto
// the body and the gold-foil collar wrapped onto the neck under the cap.
// Writes mockups/<photo>.png, mockups/lineup.png (all five) and mockups/closeup.png.
// Run:  python3 label.py && node mockup.mjs
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
const DIAMETER = 66;     // body, mm
const LABEL_H = 95;      // front label height, mm
const COLLAR_H = 9;      // neck collar height, mm
const dataUrl = (file, type) => `data:${type};base64,${readFileSync(file).toString('base64')}`;
const collarUrl = dataUrl(join(here, 'svg', 'collar.svg'), 'image/svg+xml');

mkdirSync(join(here, 'mockups'), { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage();

for (const [photo, flavour] of BOTTLES) {
  const png = await page.evaluate(async ({ photoUrl, labelUrl, collarUrl, DIAMETER, LABEL_H, COLLAR_H }) => {
    const load = (src) => new Promise((ok, err) => { const i = new Image(); i.onload = () => ok(i); i.onerror = err; i.src = src; });
    const [img, label, collar] = await Promise.all([load(photoUrl), load(labelUrl), load(collarUrl)]);
    const W = img.naturalWidth, H = img.naturalHeight;
    const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
    const ctx = cv.getContext('2d'); ctx.drawImage(img, 0, 0);
    const px = ctx.getImageData(0, 0, W, H).data;
    const at = (x, y) => { const i = (y * W + x) * 4; return [px[i], px[i + 1], px[i + 2]]; };
    const bg = at(0, 0);
    const diff = (x, y) => { const p = at(x, y); return Math.abs(p[0] - bg[0]) + Math.abs(p[1] - bg[1]) + Math.abs(p[2] - bg[2]); };
    const edges = (y, thr) => { let l = 0, r = W - 1; while (l < W && diff(l, y) < thr) l++; while (r > 0 && diff(r, y) < thr) r--; return { y, l, r, w: r - l }; };

    // Body: rows at (nearly) full width between 30% and 86% of the height.
    const rows = []; for (let y = Math.round(H * 0.3); y < Math.round(H * 0.86); y++) rows.push(edges(y, 120));
    const maxW = Math.max(...rows.map((r) => r.w));
    const body = rows.filter((r) => r.w > maxW * 0.97);
    const mid = body[Math.floor(body.length / 2)];
    const cx = (mid.l + mid.r) / 2, rad = (mid.r - mid.l) / 2 * 0.985;
    const s = 2 * rad / DIAMETER; // px per mm
    // Cap: the last row (from the top) with gold pixels near the centre line.
    let capBottom = 0;
    for (let y = 0; y < H * 0.25; y++) {
      let gold = 0; for (let x = Math.round(cx - 40); x < cx + 40; x++) { const [r, g, b] = at(x, y); if (r > 150 && g > 110 && b < 110 && r - b > 70) gold++; }
      if (gold > 20) capBottom = y;
    }
    // Neck under the cap: glass edges are faint, so use a low threshold close to the centre.
    const neckY = Math.round(capBottom + COLLAR_H * s * 0.5 + 4);
    // Walk outwards from the centre until the glass edge (darkest line); fall back to cap width.
    const findEdge = (dir) => { let x = Math.round(cx), best = x, dmax = 0; for (let k = 0; k < rad; k++, x += dir) { const d = diff(x, neckY); if (d > dmax) { dmax = d; best = x; } if (dmax > 40 && d < 8) break; } return best; };
    const L = findEdge(-1), R = findEdge(1);
    const neckCx = (L + R) / 2, neckRad = (R - L) / 2 * 0.97;

    // Wrap a flat image round a vertical cylinder (cx, radius) with its top at yTop.
    function wrap(flatImg, wmm, hmm, ccx, crad, yTop, mmToPx, shade) {
      const fw = Math.round(wmm * mmToPx), fh = Math.round(hmm * mmToPx);
      const flat = document.createElement('canvas'); flat.width = fw; flat.height = fh;
      flat.getContext('2d').drawImage(flatImg, 0, 0, fw, fh);
      const layer = document.createElement('canvas'); layer.width = W; layer.height = H;
      const lc = layer.getContext('2d');
      for (let x = Math.ceil(ccx - crad); x < ccx + crad; x++) {
        const t = (x + 0.5 - ccx) / crad; if (Math.abs(t) >= 1) continue;
        const th = Math.asin(t), u = th * crad;
        if (Math.abs(u) > fw / 2) continue;
        const dy = crad * 0.035 * (1 - Math.cos(th));
        lc.drawImage(flat, u + fw / 2, 0, 1 / Math.cos(th), fh, x, yTop + dy, 1, fh);
      }
      lc.globalCompositeOperation = 'source-atop';
      const g = lc.createLinearGradient(ccx - crad, 0, ccx + crad, 0);
      for (const [o, a] of [[0, 0.45], [0.12, 0.22], [0.3, 0.05], [0.5, 0], [0.72, 0.07], [0.9, 0.24], [1, 0.48]]) g.addColorStop(o, `rgba(25,15,8,${a * shade})`);
      lc.fillStyle = g; lc.fillRect(0, 0, W, H);
      const hl = lc.createLinearGradient(ccx - crad, 0, ccx + crad, 0);
      hl.addColorStop(0.17, 'rgba(255,255,255,0)'); hl.addColorStop(0.27, 'rgba(255,255,255,0.24)'); hl.addColorStop(0.37, 'rgba(255,255,255,0)');
      lc.fillStyle = hl; lc.fillRect(0, 0, W, H);
      ctx.drawImage(layer, 0, 0);
    }
    const labelTop = (body[0].y + body[body.length - 1].y) / 2 - LABEL_H * s / 2;
    wrap(label, 55, LABEL_H, cx, rad, labelTop, s, 1);
    wrap(collar, 70, COLLAR_H, neckCx, neckRad, capBottom + 3, s, 0.8);
    return cv.toDataURL('image/png');
  }, { photoUrl: dataUrl(join(photos, `${photo}.webp`), 'image/webp'), labelUrl: dataUrl(join(here, 'svg', `front-${flavour}.svg`), 'image/svg+xml'), collarUrl, DIAMETER, LABEL_H, COLLAR_H });
  writeFileSync(join(here, 'mockups', `${photo}.png`), Buffer.from(png.split(',')[1], 'base64'));
}

// Line-up of all five, and a close-up of two labels.
const img = (p, style) => `<img src="${dataUrl(join(here, 'mockups', `${p}.png`), 'image/png')}" style="${style}">`;
await page.setViewportSize({ width: 1400, height: 374 }); // 280 px wide photos are 373 px tall
await page.setContent(`<body style="margin:0;background:#F4F2EF;display:flex;justify-content:center;align-items:flex-start;gap:0">${BOTTLES.map(([p]) => img(p, 'width:280px;height:auto')).join('')}</body>`);
await page.screenshot({ path: join(here, 'mockups', 'lineup.png'), fullPage: true });
await page.setViewportSize({ width: 1000, height: 900 });
const crop = (p) => `<div style="width:500px;height:900px;overflow:hidden;background:#fff">${img(p, 'width:1300px;margin:-700px 0 0 -400px')}</div>`;
await page.setContent(`<body style="margin:0;display:flex">${crop('bottle-3')}${crop('bottle-2')}</body>`);
await page.screenshot({ path: join(here, 'mockups', 'closeup.png') });
await browser.close();
