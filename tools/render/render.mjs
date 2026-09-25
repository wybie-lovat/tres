// Headless renderer driver: node render.mjs job.json
// job = { size:[w,h], models:[{ url, steps:[...], shots:[{ step, mode, yaw, pitch, pad, focus, out, size, bg }] }] }
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');

const job = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const port = process.env.PORT || 8765;
const browser = await chromium.launch({
  executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
});
const [W, H] = job.size || [1200, 900];
const page = await browser.newPage({ viewport: { width: W, height: H } });
page.on('console', m => { const t = m.text(); if (!/Missing|THREE\.LDrawLoader: Line/.test(t) || process.env.VERBOSE) console.log('[page]', t.slice(0, 300)); });
page.on('pageerror', e => console.log('[pageerror]', e.message));
await page.addInitScript(([w, h]) => { window.RW = w; window.RH = h; }, [W, H]);
await page.goto(`http://127.0.0.1:${port}/render.html`);
await page.waitForFunction(() => window.READY === true);

for (const m of job.models) {
  const t0 = Date.now();
  const n = await page.evaluate(u => window.loadModel(u), m.url);
  console.log(`loaded ${m.url}: ${n} children in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  if (m.steps && m.steps.length !== n) console.log(`WARNING: steps length ${m.steps.length} != children ${n}`);
  for (const s of m.shots) {
    const t1 = Date.now();
    const size = s.size || [W, H];
    const info = await page.evaluate(({ s, steps, size }) => {
      window.setSize(size[0], size[1]);
      window.setBackground(s.bg === undefined ? null : s.bg);
      if (s.shadows !== undefined) window.enableShadows(!!s.shadows);
      if (s.only && s.step !== undefined && s.step !== null) window.showSteps(steps, s.step, s.only);
      else if (s.only) window.showOnly(s.only);
      else if (s.step === undefined || s.step === null) window.showAll();
      else window.showStep(steps, s.step, s.mode || 'fade');
      window.frame(s.yaw ?? 35, s.pitch ?? 30, s.pad ?? 1.06, s.focus || null, s.fov ?? 30, !!s.focusHidden);
      const png = window.renderPNG(s.fmt);
      const box = s.boxOf ? window.projectBox(s.boxOf) : null;
      return { png, box };
    }, { s, steps: m.steps, size });
    fs.mkdirSync(path.dirname(s.out), { recursive: true });
    fs.writeFileSync(s.out, Buffer.from(info.png.split(',')[1], 'base64'));
    if (s.fmt === 'jpg' && !s.out.endsWith('.jpg')) console.log('warn: jpg data in', s.out);
    if (s.boxOut) fs.writeFileSync(s.boxOut, JSON.stringify(info.box));
    if (!process.env.QUIET) console.log(`  ${path.basename(s.out)} ${((Date.now() - t1) / 1000).toFixed(1)}s`);
  }
}
await browser.close();
