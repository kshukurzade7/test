import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const [,, html, out, x, y, w, h, scale] = process.argv;
const b = await chromium.launch(); const p = await b.newPage({deviceScaleFactor:+scale||3, viewport:{width:613,height:569}});
await p.goto('file://'+process.cwd()+'/'+html); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(300);
await p.screenshot({path:out, clip:{x:+x,y:+y,width:+w,height:+h}}); await b.close();
