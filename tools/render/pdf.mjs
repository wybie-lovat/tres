// Print an HTML booklet to PDF (A4 landscape) with headless Chromium: node pdf.mjs in.html out.pdf
import { createRequire } from 'module';
import path from 'path';
const require = createRequire(process.env.PLAYWRIGHT_REQUIRE || '/opt/node22/lib/node_modules/');
const { chromium } = require('playwright');
const [,, inp, out] = process.argv;
const browser = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const page = await browser.newPage();
await page.goto('file://' + path.resolve(inp), { waitUntil: 'load' });
await page.pdf({ path: out, format: 'A4', landscape: true, printBackground: true, margin: { top: 0, bottom: 0, left: 0, right: 0 } });
await browser.close();
console.log('wrote', out);
