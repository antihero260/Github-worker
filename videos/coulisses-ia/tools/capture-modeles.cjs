// Filme les pages d'accueil publiques des modèles (vignettes de la liste qui suit le doigt).
// Usage : node tools/capture-modeles.cjs ; sortie : assets/captures/modele-<nom>.mp4 (960×540, 12 i/s, 3 s).
const {chromium} = require('playwright');
const fs = require('fs'), path = require('path'), {execFileSync} = require('child_process');
const ICI = path.resolve(__dirname, '..');
const PLAN = [
  {nom: 'chatgpt', url: 'https://openai.com/chatgpt/overview/'},
  {nom: 'gemini', url: 'https://gemini.google.com/'},
  {nom: 'grok', url: 'https://grok.com/'},
];
(async () => {
  const b = await chromium.launch();
  for (const c of PLAN) {
    const p = await b.newPage({viewport: {width: 1280, height: 720}, deviceScaleFactor: 1});
    try { await p.goto(c.url, {waitUntil: 'domcontentloaded', timeout: 40000}); } catch (e) { console.log('lent', c.nom); }
    await p.waitForTimeout(5000);
    for (const t of ['Accept all', 'Tout accepter', 'Accept', 'Reject all', 'Stay logged out', 'Got it']) {
      const btn = p.getByRole('button', {name: t}).first();
      if (await btn.isVisible().catch(() => false)) { await btn.click().catch(() => {}); await p.waitForTimeout(800); }
    }
    const dir = path.join(ICI, '.cap', c.nom); fs.rmSync(dir, {recursive: true, force: true}); fs.mkdirSync(dir, {recursive: true});
    // on tape une question dans la zone de saisie si elle existe (la page vit)
    const zone = p.locator('textarea, [contenteditable="true"]').first();
    const q = 'Fais-moi une vidéo animée';
    const ok = await zone.isVisible().catch(() => false);
    if (ok) await zone.click().catch(() => {});
    for (let i = 0; i < 36; i++) {
      if (ok && i % 2 === 0 && i / 2 < q.length) await p.keyboard.type(q[i / 2]).catch(() => {});
      await p.screenshot({path: path.join(dir, String(i).padStart(4, '0') + '.jpg'), type: 'jpeg', quality: 85});
    }
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', '12', '-i', path.join(dir, '%04d.jpg'), '-vf', 'scale=960:540', '-c:v', 'libx264', '-crf', '22', '-pix_fmt', 'yuv420p',
      '-g', '12', path.join(ICI, 'assets/captures', 'modele-' + c.nom + '.mp4')]);
    console.log('ok', c.nom, ok ? 'saisie' : 'sans saisie');
    await p.close();
  }
  await b.close();
})();
