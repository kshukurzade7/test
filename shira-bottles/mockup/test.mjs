// Local preview: serves the CDN three.js from the local copy and screenshots the page.
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { readFileSync } from 'fs';
const [out = 'test.png', w = 1100, h = 1500] = process.argv.slice(2);
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: +w, height: +h } });
p.on('pageerror', (e) => console.log('error:', e.message));
p.on('console', (m) => { if (m.type() === 'error') console.log('console:', m.text()); });
await p.route('https://cdn.jsdelivr.net/npm/three@0.186.1/**', (r) => {
  const path = new URL(r.request().url()).pathname.replace('/npm/three@0.186.1/', '');
  r.fulfill({ body: readFileSync('../studio/three/' + path), contentType: 'text/javascript' });
});
await p.route('https://fonts.googleapis.com/**', (r) => r.abort());
const html = readFileSync('index.html', 'utf8');
await p.route('http://mock.local/', (r) => r.fulfill({ body: `<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">${html}`, contentType: 'text/html' }));
await p.goto('http://mock.local/');
await p.waitForFunction(() => window.READY, null, { timeout: 120000 });
await p.waitForTimeout(4000);
await p.screenshot({ path: out, fullPage: true, timeout: 180000 });
await b.close();
