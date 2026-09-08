/**
 * Screenshot every project's live demo into assets/shots/<slug>.png.
 *
 * Runs weekly in CI (.github/workflows/screenshots.yml) and can be run by hand:
 *
 *     npm install playwright && npx playwright install --with-deps chromium
 *     node tools/shoot.mjs            # all projects
 *     node tools/shoot.mjs stargazer  # just one
 *
 * The site works without these files — cards fall back to a branded tile and a
 * click-to-load live preview. Screenshots just make the gallery read faster.
 */

import { chromium } from 'playwright';
import { readFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const OUT = path.join(ROOT, 'assets', 'shots');
const { projects } = JSON.parse(readFileSync(path.join(ROOT, 'data', 'projects.json'), 'utf8'));

const only = process.argv.slice(2);
const targets = projects.filter(p => p.demo && (!only.length || only.includes(p.slug)));

mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width: 1280, height: 800 },
  deviceScaleFactor: 1,
  reducedMotion: 'reduce',
});

let ok = 0, failed = [];

for (const p of targets) {
  const page = await ctx.newPage();
  try {
    await page.goto(p.demo, { waitUntil: 'networkidle', timeout: 45000 });
    // Give canvas/3D/font work a beat to settle, then dismiss anything modal.
    await page.waitForTimeout(p.shotDelay ?? 3500);
    await page.keyboard.press('Escape').catch(() => {});
    await page.screenshot({ path: path.join(OUT, `${p.slug}.png`), animations: 'disabled' });
    console.log(`  ok   ${p.slug}`);
    ok++;
  } catch (err) {
    console.log(`  FAIL ${p.slug} — ${err.message.split('\n')[0]}`);
    failed.push(p.slug);
  } finally {
    await page.close();
  }
}

await browser.close();
console.log(`\n${ok}/${targets.length} captured.` + (failed.length ? ` Failed: ${failed.join(', ')}` : ''));
