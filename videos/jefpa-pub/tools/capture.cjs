// Filme le site jefpa-site.pages.dev image par image, à 30 i/s, avec une horloge contrôlée (Playwright clock) :
// les animations GSAP/ScrollTrigger et le défilement sont exacts et fluides, quelle que soit la vitesse de la machine.
// Un pointeur de souris dessiné est ajouté dans la page (il se déplace, survole et clique).
//
// Usage : node tools/capture.cjs tools/plan-capture.json [nom-de-clip ...]
// Sortie : assets/captures/<nom>.mp4 (2880×1620, mise en page 1440×810 en densité 2).
// Le formulaire de contact n'est jamais envoyé : on tape seulement un exemple dans deux champs.
const {chromium} = require('playwright');
const fs = require('fs'), path = require('path'), {execFileSync} = require('child_process');

const ICI = path.resolve(__dirname, '..');
const BASE = 'https://jefpa-site.pages.dev';
const FPS = 30, DT = 1000 / FPS, W = 1440, H = 810;
const plan = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const choix = process.argv.slice(3);

const CURSEUR = `(() => {
  const poser = () => {
    if (document.getElementById('cap-curseur')) return;
    const c = document.createElement('div');
    c.id = 'cap-curseur';
    c.innerHTML = '<svg viewBox="0 0 28 36" width="28" height="36"><path d="M3 2 L3 29 L10 22.5 L14.8 33.5 L20 31.3 L15.3 20.6 L24.5 20.6 Z" fill="#fff" stroke="#05070d" stroke-width="2.2" stroke-linejoin="round"/></svg><i></i>';
    c.style.cssText = 'position:fixed;left:0;top:0;z-index:2147483647;pointer-events:none;transform:translate(-200px,-200px);filter:drop-shadow(0 4px 8px rgba(0,0,0,.35))';
    const st = document.createElement('style');
    st.textContent = '#cap-curseur i{position:absolute;left:-22px;top:-22px;width:44px;height:44px;border-radius:50%;border:3px solid #1f4bff;opacity:0;transform:scale(.3)}';
    document.documentElement.append(st, c);
  };
  window.__curseur = (x, y, anneau) => {
    poser();
    const c = document.getElementById('cap-curseur');
    c.style.transform = 'translate(' + x + 'px,' + y + 'px)';
    const i = c.querySelector('i');
    i.style.opacity = anneau > 0 ? String(1 - anneau) : '0';
    i.style.transform = 'scale(' + (0.3 + anneau * 1.2) + ')';
  };
  if (document.readyState !== 'loading') poser(); else addEventListener('DOMContentLoaded', poser);
})();`;

const ease = {
  lin: t => t,
  in: t => t * t * t,
  out: t => 1 - Math.pow(1 - t, 3),
  inout: t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
};

async function cible(p, a) {
  // position de défilement visée : nombre, sélecteur CSS ou texte d'un titre (+ décalage)
  if (typeof a.to === 'number') return a.to;
  const y = await p.evaluate(({sel, texte}) => {
    let el = null;
    if (sel) el = document.querySelector(sel);
    if (!el && texte) el = [...document.querySelectorAll('h1,h2,h3,p,span,strong,a,button')].find(e => e.textContent.replace(/\s+/g, ' ').includes(texte));
    return el ? el.getBoundingClientRect().top + scrollY : null;
  }, {sel: a.sel, texte: a.texte});
  if (y === null) throw new Error('cible introuvable : ' + JSON.stringify(a));
  return Math.max(0, Math.round(y + (a.offset || 0)));
}

async function clip(b, c) {
  const dossier = path.join(ICI, 'assets/captures', c.nom + '-img');
  fs.rmSync(dossier, {recursive: true, force: true});
  fs.mkdirSync(dossier, {recursive: true});
  const ctx = await b.newContext({viewport: {width: W, height: H}, deviceScaleFactor: 2});
  await ctx.addInitScript(CURSEUR);
  const p = await ctx.newPage();
  await p.clock.install({time: new Date('2026-11-13T10:00:00')});
  await p.goto(BASE + c.url, {waitUntil: 'networkidle', timeout: 90000});
  await p.evaluate(() => document.fonts.ready);
  // état initial : défilement de départ, pointeur
  let y = c.depart ? await cible(p, c.depart) : 0;
  if (y) await p.evaluate(y => scrollTo(0, y), y);
  let cx = c.curseur ? c.curseur[0] : -200, cy = c.curseur ? c.curseur[1] : -200, anneau = 0;
  await p.evaluate(([x, y]) => window.__curseur(x, y, 0), [cx, cy]);
  for (let i = 0; i < (c.prechauffe ?? 0) * FPS; i++) await p.clock.runFor(DT);  // laisser jouer l'entrée de page avant de filmer
  let n = 0;
  const image = async () => {
    await p.screenshot({path: path.join(dossier, String(n++).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 90});
  };
  for (const a of c.actions) {
    const k = Math.max(1, Math.round((a.d || 0) * FPS));
    if (a.t === 'attente') {
      for (let i = 0; i < k; i++) { await p.clock.runFor(DT); await image(); }
    } else if (a.t === 'defile') {
      const y0 = y, y1 = await cible(p, a), e = ease[a.ease || 'inout'];
      for (let i = 1; i <= k; i++) {
        y = Math.round(y0 + (y1 - y0) * e(i / k));
        await p.evaluate(y => scrollTo(0, y), y);
        await p.clock.runFor(DT); await image();
      }
    } else if (a.t === 'souris') {
      const x0 = cx, y0 = cy, e = ease[a.ease || 'inout'];
      for (let i = 1; i <= k; i++) {
        const u = e(i / k);
        cx = x0 + (a.x - x0) * u; cy = y0 + (a.y - y0) * u;
        // légère courbe pour un geste naturel
        const arc = Math.sin(u * Math.PI) * (a.arc ?? 30);
        await p.evaluate(([x, y]) => window.__curseur(x, y, 0), [cx, cy - arc]);
        await p.mouse.move(cx, cy - arc);
        await p.clock.runFor(DT); await image();
      }
    } else if (a.t === 'clic') {
      for (let i = 0; i < k; i++) {
        anneau = i / k;
        await p.evaluate(([x, y, r]) => window.__curseur(x, y, r), [cx, cy, anneau]);
        if (i === 2 && a.vraiClic) await p.mouse.click(cx, cy);
        await p.clock.runFor(DT); await image();
      }
      await p.evaluate(([x, y]) => window.__curseur(x, y, 0), [cx, cy]);
    } else if (a.t === 'tape') {
      // tape un exemple dans un champ (jamais d'envoi du formulaire)
      await p.focus(a.sel);
      const lettres = [...a.texte];
      for (let i = 0; i < k; i++) {
        const avant = Math.floor(lettres.length * i / k), apres = Math.floor(lettres.length * (i + 1) / k);
        if (apres > avant) await p.keyboard.insertText(lettres.slice(avant, apres).join(''));
        await p.clock.runFor(DT); await image();
      }
    } else if (a.t === 'clicDom') {
      await p.evaluate(sel => document.querySelector(sel)?.click(), a.sel);
    } else throw new Error('action inconnue ' + a.t);
  }
  await ctx.close();
  const sortie = path.join(ICI, 'assets/captures', c.nom + '.mp4');
  execFileSync('ffmpeg', ['-nostdin', '-v', 'error', '-y', '-framerate', String(FPS), '-i', path.join(dossier, '%05d.jpg'),
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', sortie]);
  fs.rmSync(dossier, {recursive: true, force: true});
  console.log(c.nom, n, 'images', (n / FPS).toFixed(2) + ' s');
}

(async () => {
  const b = await chromium.launch();
  for (const c of plan) if (!choix.length || choix.includes(c.nom)) await clip(b, c);
  await b.close();
})();
