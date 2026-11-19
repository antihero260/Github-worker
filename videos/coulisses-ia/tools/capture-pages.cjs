// Filme des pages publiques officielles (défilement doux, image par image) pour l'edit Claude.
// Usage : node tools/capture-pages.cjs ; sortie : assets/captures/<nom>.mp4 (1920×1080, 30 i/s).
const {chromium} = require('playwright');
const fs = require('fs'), path = require('path'), {execFileSync} = require('child_process');
const ICI = path.resolve(__dirname, '..');
const PLAN = [
  {nom: 'hyperframes-accueil', url: 'https://hyperframes.heygen.com/', de: 0, a: 1400, d: 5},
];
const _ANCIEN = [
  {nom: 'docs-modeles-haut', url: 'https://platform.claude.com/docs/en/about-claude/models/overview', de: 0, a: 900, d: 4},
  {nom: 'docs-modeles-tableau', url: 'https://platform.claude.com/docs/en/about-claude/models/overview', texte: 'All models', de: -100, a: 1300, d: 5},
  {nom: 'claude-accueil', url: 'https://claude.com/', de: 0, a: 1100, d: 4.5},
  {nom: 'anthropic-news', url: 'https://www.anthropic.com/news', de: 0, a: 1500, d: 5},
  {nom: 'anthropic-claude', url: 'https://www.anthropic.com/claude', de: 0, a: 1400, d: 5},
];
const ease = t => t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
(async () => {
  const b = await chromium.launch();
  for (const c of PLAN) {
    const p = await b.newPage({viewport: {width: 1280, height: 720}, deviceScaleFactor: 1});
    try {
      await p.goto(c.url, {waitUntil: 'domcontentloaded', timeout: 45000});
    } catch (e) { console.log('lent', c.nom); }
    await p.waitForTimeout(2500);
    // fermer les bandeaux de cookies éventuels
    for (const t of ['Accept all', 'Accept All Cookies', 'Accept', 'Reject all', 'Got it']) {
      const btn = p.getByRole('button', {name: t}).first();
      if (await btn.isVisible().catch(() => false)) { await btn.click().catch(() => {}); await p.waitForTimeout(500); break; }
    }
    let base = 0;
    if (c.texte) base = await p.evaluate(t => { const el = [...document.querySelectorAll('h1,h2,h3')].find(e => e.textContent.trim().startsWith(t)); return el ? el.getBoundingClientRect().top + scrollY : 0; }, c.texte);
    const dir = path.join(ICI, '.cap', c.nom); fs.rmSync(dir, {recursive: true, force: true}); fs.mkdirSync(dir, {recursive: true});
    const n = Math.round(c.d * 30);
    for (let i = 0; i < n; i++) {
      const y = base + c.de + (c.a - c.de) * ease(i / (n - 1));
      await p.evaluate(y => window.scrollTo(0, y), y);
      await p.waitForTimeout(25);
      await p.screenshot({path: path.join(dir, String(i).padStart(4, '0') + '.jpg'), type: 'jpeg', quality: 88});
    }
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', '30', '-i', path.join(dir, '%04d.jpg'), '-vf', 'scale=1920:1080', '-c:v', 'libx264', '-crf', '22', '-pix_fmt', 'yuv420p', path.join(ICI, 'assets/captures', c.nom + '.mp4')]);
    fs.rmSync(dir, {recursive: true, force: true});
    console.log('ok', c.nom);
    await p.close();
  }
  await b.close();
})();
