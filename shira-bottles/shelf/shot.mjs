import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const [,, html, out, x, y, w, h, scale] = process.argv;
const b = await chromium.launch(); const p = await b.newPage({deviceScaleFactor:+scale||3, viewport:{width:Math.max(613,+x + +w),height:Math.max(569,+y + +h)}});
await p.goto('file://'+process.cwd()+'/'+html); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(300);
await p.screenshot({path:out, clip:{x:+x,y:+y,width:+w,height:+h}}); await b.close();
