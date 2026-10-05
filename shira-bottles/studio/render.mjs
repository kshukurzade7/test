// Render the SHIRÁ studio scene to PNG.
//   1. rasterise the flat label SVGs into textures/
//   2. serve this folder over http and screenshot scene.html
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { readFileSync, mkdirSync } from 'fs';
import { createServer } from 'http';
import { extname, join, dirname } from 'path';
import { fileURLToPath } from 'url';

const dir = dirname(fileURLToPath(import.meta.url));
const [w = 1600, h = 1200, out = 'shira-studio.png', sceneFile = 'scene.html', extra = ''] = process.argv.slice(2);
const types = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png' };
const server = createServer((req, res) => {
  try {
    const p = join(dir, decodeURIComponent(req.url.split('?')[0]));
    res.writeHead(200, { 'Content-Type': types[extname(p)] || 'application/octet-stream' });
    res.end(readFileSync(p));
  } catch { res.writeHead(404); res.end(); }
}).listen(8765);

const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage();
const texPage = await browser.newPage({ deviceScaleFactor: 3 });
page.on('console', (m) => console.log('page:', m.text()));
page.on('pageerror', (e) => console.log('error:', e.message));

mkdirSync(join(dir, 'textures'), { recursive: true });
for (const key of ['apricot', 'pomegranate', 'grape']) {
  const svg = readFileSync(join(dir, '..', 'photo', 'flat', `${key}-label.svg`), 'utf8');
  await texPage.setViewportSize({ width: 1400, height: 1400 });
  await texPage.setContent(`<body style="margin:0">${svg}</body>`);
  await texPage.evaluate(() => document.fonts.ready);
  await texPage.waitForTimeout(200);
  await texPage.locator('svg').screenshot({ path: join(dir, 'textures', `${key}.png`) });
}

await page.setViewportSize({ width: +w, height: +h });
await page.goto(`http://localhost:8765/${sceneFile}?w=${w}&h=${h}${extra}`, { waitUntil: 'commit', timeout: 300000 });
await page.waitForFunction(() => window.READY, null, { timeout: 300000 });
await page.waitForTimeout(500);
await page.locator('#final').screenshot({ path: join(dir, out) });
await browser.close();
server.close();
