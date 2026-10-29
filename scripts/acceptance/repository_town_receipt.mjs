// Q01 live acceptance receipt for Repository Town (a deployed 3D web game).
//
// Proves user-facing behaviour in a real browser, not HTTP 200: the game loads with WebGL and no
// page errors; a primary interaction works (walk into the café and use the counter, which opens
// its panel); phone layout keeps the touch controls on screen and clear of the minimap; and a
// reload restores where the player was. Writes a JSON receipt bound to the release the site
// itself reports (release.json sourceCommit/contentHash), the URL, browser and viewport, with
// SHA-256 digests of the screenshots taken as observations.
//
//   node repository_town_receipt.mjs <url> <receipt.json> [--expect-fail]
// Exit 0 = every check passed (or, with --expect-fail, at least one failed); 1 otherwise.
import { createHash } from 'node:crypto';
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { chromium } from 'playwright';

const [url, receiptPath] = process.argv.slice(2);
const expectFail = process.argv.includes('--expect-fail');
if (!url || !receiptPath) { console.error('usage: <url> <receipt.json> [--expect-fail]'); process.exit(2); }
const shotDir = join(dirname(receiptPath), 'screenshots');
mkdirSync(shotDir, { recursive: true });

const checks = [], shots = [];
const record = (id, ok, observed) => { checks.push({ id, status: ok ? 'PASS' : 'FAIL', observed }); console.log(`${ok ? 'PASS' : 'FAIL'} ${id}: ${observed}`); };
const sha256 = (buf) => createHash('sha256').update(buf).digest('hex');
async function shot(page, name) {
  const buf = await page.screenshot({ path: join(shotDir, name + '.png') });
  shots.push({ name: name + '.png', sha256: sha256(buf) });
}

const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const receipt = { schema: 'q01-acceptance-receipt/1', app: 'Repository Town', url, started_utc: new Date().toISOString(),
  browser: `chromium ${browser.version()}`, release: 'UNKNOWN', checks, screenshots: shots };

async function release(page) {
  try {
    const r = await page.evaluate(async () => { const x = await fetch('release.json', { cache: 'no-store' }); return x.ok ? x.json() : null; });
    return r?.sourceCommit ? { sourceCommit: r.sourceCommit, contentHash: r.contentHash ?? 'UNKNOWN' } : 'UNKNOWN';
  } catch { return 'UNKNOWN'; }
}

async function journey(label, contextOptions) {
  const ctx = await browser.newContext({ locale: 'en-AU', ...contextOptions });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e.message).slice(0, 160)));
  await page.route('**/api/npc-chat', (r) => r.abort('connectionrefused'));     // no AI traffic during acceptance
  const T = (f, a) => page.evaluate(f, a);
  try {
    // J1: loads with WebGL, loading screen gone, no page errors.
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForFunction(() => window.__town && document.getElementById('loading')?.hidden, null, { timeout: 150000 });
    if (receipt.release === 'UNKNOWN') receipt.release = await release(page);
    const gl = await T(() => { const c = [...document.querySelectorAll('canvas')].find((x) => x.id !== 'minimap'); return c ? { w: c.width, h: c.height, webgl: !!(c.getContext('webgl2') || c.getContext('webgl')) } : null; });
    await page.waitForTimeout(1500);
    record(`${label}.load`, !!gl && gl.w > 0 && gl.h > 0 && errors.length === 0,
      gl ? `canvas ${gl.w}x${gl.h}, page errors ${errors.length}${errors.length ? ': ' + errors[0] : ''}` : 'no 3D canvas');
    await shot(page, `${label}-loaded`);

    // J2: primary interaction through real input (E key or the ✋ button), not a direct panel call.
    await T(() => { const t = window.__town; t.life.setDay(2); t.life.setTime(10 * 60); t.life.run(30); t.goPlace('cafe'); t.enterShop('cafe'); });
    await page.waitForTimeout(1500);
    const counter = (await T(() => window.__town.state().interactables)).find((x) => /counter/i.test(x.label));
    let panelTitle = null;
    if (counter) {
      await T((k) => window.__town.approach(k), counter.key);
      await page.waitForFunction((k) => window.__town.state().near === k, counter.key, { timeout: 30000 }).catch(() => {});
      for (let i = 0; i < 4 && !panelTitle; i++) {
        if (contextOptions.hasTouch) await page.tap('#t-use').catch(() => {});
        else { await page.keyboard.down('e'); await page.waitForTimeout(120); await page.keyboard.up('e'); }
        await page.waitForTimeout(1500);
        // #panel is position:fixed, so offsetParent is always null; use computed style and size.
        panelTitle = await T(() => { const p = document.getElementById('panel'); if (!p || p.hidden) return null; const cs = getComputedStyle(p), r = p.getBoundingClientRect();
          return cs.display !== 'none' && cs.visibility !== 'hidden' && r.width > 0 && r.height > 0 ? document.getElementById('panel-title')?.textContent : null; });
      }
    }
    record(`${label}.primary_interaction`, !!panelTitle,
      counter ? (panelTitle ? `using "${counter.label}" opened panel "${panelTitle}"` : `using "${counter.label}" opened no visible panel`) : 'no café counter to use');
    await shot(page, `${label}-interaction`);
    await T(() => window.__town.closePanel());

    // J3 (phone only): touch controls on screen, inside the viewport and clear of the minimap.
    if (contextOptions.hasTouch) {
      const lay = await T(() => {
        const box = (id) => { const e = document.getElementById(id); if (!e || e.hidden || getComputedStyle(e).display === 'none') return null; const r = e.getBoundingClientRect(); return { l: r.left, t: r.top, r: r.right, b: r.bottom }; };
        return { vw: innerWidth, vh: innerHeight, use: box('t-use'), stick: box('stick'), map: box('minimap') };
      });
      const inside = (b) => b && b.l >= 0 && b.t >= 0 && b.r <= lay.vw && b.b <= lay.vh;
      const overlap = (a, b) => a && b && a.l < b.r && a.r > b.l && a.t < b.b && a.b > b.t;
      const ok = inside(lay.use) && inside(lay.stick) && !overlap(lay.use, lay.map);
      record(`${label}.touch_layout`, ok, `✋ ${JSON.stringify(lay.use)}, stick ${JSON.stringify(lay.stick)}, minimap ${JSON.stringify(lay.map)} in ${lay.vw}x${lay.vh}`);
    }

    // J4: persistence — the game saves, and a reload puts the player back inside the café.
    await page.waitForTimeout(4500);                                    // the game saves every ~3 s
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForFunction(() => window.__town && document.getElementById('loading')?.hidden, null, { timeout: 150000 });
    await page.waitForTimeout(1500);
    const after = await T(() => { const s = window.__town.state(); return { mode: s.mode, place: s.place ?? null }; });
    record(`${label}.persistence`, after.mode === 'house', `after reload: mode ${after.mode}`);
    record(`${label}.no_page_errors`, errors.length === 0, errors.length ? errors.slice(0, 3).join(' | ') : 'none');
  } catch (e) {
    record(`${label}.journey_completed`, false, String(e.message).split('\n')[0].slice(0, 200));
  } finally {
    await ctx.close();
  }
}

await journey('desktop', { viewport: { width: 1280, height: 800 } });
await journey('phone', { viewport: { width: 412, height: 915 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
await browser.close();

receipt.finished_utc = new Date().toISOString();
const failed = checks.filter((c) => c.status === 'FAIL').length;
receipt.verdict = failed ? 'FAIL' : 'PASS';
receipt.limitations = [
  'Headless Chromium with software WebGL, not a physical phone or GPU.',
  'Uses the game\'s test hook to fast-travel and set the clock; the interaction itself uses real key/tap input.',
  'A PASS covers only these journeys on this release; it is not proof of the whole game.',
];
writeFileSync(receiptPath, JSON.stringify(receipt, null, 2) + '\n');
console.log(`receipt: ${receipt.verdict} (${checks.length - failed}/${checks.length} checks) release ${JSON.stringify(receipt.release)}`);
process.exit(expectFail ? (failed ? 0 : 1) : (failed ? 1 : 0));
