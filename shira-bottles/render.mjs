// Render shira-lineup.svg to PNG with the pre-installed Chromium.
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const dir = dirname(fileURLToPath(import.meta.url));
const svg = readFileSync(join(dir, 'shira-lineup.svg'), 'utf8');
const browser = await chromium.launch();
const page = await browser.newPage({ deviceScaleFactor: 2 });
await page.setContent(`<html><body style="margin:0">${svg}</body></html>`);
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(800);
await page.locator('svg').screenshot({ path: join(dir, 'shira-lineup.png') });
await browser.close();
