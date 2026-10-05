// Wrap the flat SHIRÁ labels onto the real bottle photo, pixel by pixel.
// For every output pixel on a label: find its angle on the bottle cylinder,
// sample the flat label there, relight it with the original label's measured
// lighting, and composite over the (upscaled) photo.
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { readFileSync } from 'fs';

const S = 3; // output scale vs the source photo
const params = JSON.parse(readFileSync('params.json', 'utf8'));
const b64 = (p) => readFileSync(p).toString('base64');
const browser = await chromium.launch();
const page = await browser.newPage();

// rasterise the flat labels (fonts are embedded in the SVGs)
const flats = {};
for (const p of params) {
  await page.setContent(`<body style="margin:0">${readFileSync(p.svg, 'utf8')}</body>`);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(200);
  flats[p.svg] = (await page.locator('svg').screenshot({ omitBackground: true })).toString('base64');
}

const out = await page.evaluate(async ({ base, flats, params, S }) => {
  const load = async (src) => { const i = new Image(); i.src = src; await i.decode(); return i; };
  const img = await load('data:image/png;base64,' + base);
  const W = img.width * S, H = img.height * S;
  const main = new OffscreenCanvas(W, H), mc = main.getContext('2d');
  mc.imageSmoothingQuality = 'high'; mc.drawImage(img, 0, 0, W, H);
  const layer = new OffscreenCanvas(W, H), lc = layer.getContext('2d');
  const outData = lc.createImageData(W, H), o = outData.data;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  for (const p of params) {
    const f = await load('data:image/png;base64,' + flats[p.svg]);
    const fc = new OffscreenCanvas(f.width, f.height).getContext('2d'); fc.drawImage(f, 0, 0);
    const fd = fc.getImageData(0, 0, f.width, f.height).data, FW = f.width, FH = f.height;
    const sample = (u, v) => { // bilinear, premultiplied
      const x = clamp(u * FW - 0.5, 0, FW - 1.001), y = clamp(v * FH - 0.5, 0, FH - 1.001);
      const ix = x | 0, iy = y | 0, dx = x - ix, dy = y - iy, r = [0, 0, 0, 0];
      for (const [ox, oy, w] of [[0, 0, (1 - dx) * (1 - dy)], [1, 0, dx * (1 - dy)], [0, 1, (1 - dx) * dy], [1, 1, dx * dy]]) {
        const k = ((iy + oy) * FW + ix + ox) * 4, a = fd[k + 3] / 255;
        r[0] += fd[k] * a * w; r[1] += fd[k + 1] * a * w; r[2] += fd[k + 2] * a * w; r[3] += a * w;
      }
      return r;
    };
    const edge = (arr, X) => { const t = (X * 4 - p.qx0); const i = clamp(Math.floor(t), 0, arr.length - 2); return arr[i] + (arr[i + 1] - arr[i]) * (t - i); };
    const light = (X) => { const i = clamp(Math.round(X - p.lum_x0), 0, p.lum.length - 1); return p.lum[i]; };
    const yMin = Math.floor(Math.min(...p.top) * S) - 2, yMax = Math.ceil(Math.max(...p.bot) * S) + 2;
    for (let py = yMin; py <= yMax; py++) for (let px = Math.floor(p.x0 * S) - 2; px <= Math.ceil(p.x1 * S) + 2; px++) {
      const X = (px + 0.5) / S, Y = (py + 0.5) / S;
      const t = edge(p.top, X), b = edge(p.bot, X);
      const cov = clamp((Y - t) * S + 0.5, 0, 1) * clamp((b - Y) * S + 0.5, 0, 1)
                * clamp((X - p.x0) * S + 0.5, 0, 1) * clamp((p.x1 - X) * S + 0.5, 0, 1);
      if (cov <= 0) continue;
      const th = Math.asin(clamp((X - p.cx) / p.R, -0.999, 0.999));
      const u = (th - p.ta) / (p.tb - p.ta), v = (Y - t) / (b - t);
      const s = sample(clamp(u, 0, 1), clamp(v, 0, 1));
      if (s[3] <= 0) continue;
      const L = Math.min(1.02, light(X) / p.lum_max);
      const k = (py * W + px) * 4, a = s[3] * cov;
      for (let c = 0; c < 3; c++) o[k + c] = clamp(s[c] / s[3] * L * p.tint[c], 0, 255);
      o[k + 3] = a * 255;
    }
  }
  lc.putImageData(outData, 0, 0);
  mc.filter = 'blur(0.7px)'; mc.drawImage(layer, 0, 0); mc.filter = 'none';
  const CROP_X = 40 * S; // drop the half-visible bottle on the far left
  const outC = new OffscreenCanvas(W - CROP_X, H); outC.getContext('2d').drawImage(main, -CROP_X, 0);
  const blob = await outC.convertToBlob({ type: 'image/png' });
  const buf = new Uint8Array(await blob.arrayBuffer()); let s = '';
  for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode(...buf.subarray(i, i + 0x8000));
  return btoa(s);
}, { base: b64('base.png'), flats, params, S });

(await import('fs')).writeFileSync('shira-shelf.png', Buffer.from(out, 'base64'));
await browser.close();
