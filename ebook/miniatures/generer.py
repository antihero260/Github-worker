"""Génère les miniatures verticales (1080x1920) de l'ebook : HTML puis capture Playwright."""
import subprocess, pathlib
ICI = pathlib.Path(__file__).parent

def perso(g=0, d=0, couleur="#DCFC1C", h=300):
    w = h * 120 / 270
    return f'''<svg width="{w:.0f}" height="{h}" viewBox="-10 -10 120 270" style="overflow:visible">
<g fill="{couleur}" stroke="#000" stroke-width="10" stroke-linejoin="round">
<rect x="24" y="136" width="24" height="112" rx="8"/><rect x="52" y="136" width="24" height="112" rx="8"/>
<rect x="22" y="52" width="56" height="94" rx="12"/>
<rect x="2" y="54" width="18" height="86" rx="8" transform="rotate({g} 11 62)"/>
<rect x="80" y="54" width="18" height="86" rx="8" transform="rotate({d} 89 62)"/>
<circle cx="50" cy="24" r="22"/></g></svg>'''

BASE = '''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Anton;src:url(src/Anton-Regular.woff2)}
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1920px;overflow:hidden;background:#0C0C0C;font-family:Inter,sans-serif;position:relative}
.abs{position:absolute}
.anton{font-family:Anton;text-transform:uppercase;line-height:.92;letter-spacing:.5px}
.fond{position:absolute;inset:0;background-size:cover;background-position:center}
.nav{background:#1b1b1f;border-radius:22px;overflow:hidden;border:3px solid #333;box-shadow:0 30px 80px rgba(0,0,0,.7)}
.nav .barre{height:46px;background:#2a2a30;display:flex;align-items:center;gap:12px;padding-left:20px}
.nav .barre i{width:16px;height:16px;border-radius:50%;background:#555;display:block}
.nav img{display:block;width:100%}
.ombre{text-shadow:0 8px 0 #000,0 0 40px rgba(0,0,0,.8)}
.contour{-webkit-text-stroke:10px #000;paint-order:stroke fill}
.etiq{background:#DCFC1C;color:#0C0C0C;padding:10px 26px 4px}
.case{width:150px;height:170px;border:8px solid #DCFC1C;border-radius:16px;background:#0C0C0C;display:flex;align-items:center;justify-content:center;color:#DCFC1C;font-family:Anton;font-size:120px;box-shadow:0 0 40px rgba(220,252,28,.55)}
</style></head><body>'''

M = {}

# 1. Ton site crie «&nbsp;fait par l'IA&nbsp;»
M["m1-site-ia"] = BASE + f'''
<div class="fond" style="background-image:url(src/frustree.jpg);background-position:62% center;filter:brightness(.55) saturate(1.1)"></div>
<div class="fond" style="background:linear-gradient(180deg,#0C0C0C 0%,rgba(12,12,12,.2) 38%,rgba(12,12,12,.15) 70%,#0C0C0C 100%)"></div>
<div class="abs anton ombre" style="top:250px;left:0;right:0;text-align:center;color:#fff;font-size:150px">Ton site</div>
<div class="abs anton contour" style="top:390px;left:0;right:0;text-align:center;color:#DCFC1C;font-size:300px">crie</div>
<div class="abs nav" style="top:760px;left:110px;width:860px;transform:rotate(-4deg)"><div class="barre"><i></i><i></i><i></i></div><img src="src/siteia0.jpg"></div>
<svg class="abs" style="top:770px;left:180px" width="720" height="260"><ellipse cx="360" cy="125" rx="330" ry="95" fill="none" stroke="#E8112D" stroke-width="12" transform="rotate(-4 360 125)"/></svg>
<div class="abs anton" style="top:1210px;left:130px;transform:rotate(-7deg);background:#E8112D;color:#fff;font-size:120px;padding:18px 40px 8px;box-shadow:0 20px 50px rgba(0,0,0,.6);border:6px solid #fff">Fait par l'IA</div>
<div class="abs" style="top:1440px;left:160px;display:flex;gap:30px"><div class="case">?</div><div class="case">?</div><div class="case">?</div></div>
<div class="abs anton" style="top:1640px;left:160px;color:#fff;font-size:64px">Les <span style="color:#DCFC1C">3 signes</span></div>
<div class="abs" style="top:1300px;right:70px">{perso(0,-150,h=380)}</div>
'''

# 2. Ce site est un jeu vidéo
M["m2-jeu-video"] = BASE + f'''
<div class="fond" style="background-image:url(src/neon.jpg);filter:brightness(.8) hue-rotate(-10deg)"></div>
<div class="fond" style="background:linear-gradient(180deg,rgba(12,12,12,.95) 0%,rgba(12,12,12,.3) 30%,rgba(12,12,12,.1) 60%,rgba(12,12,12,.9) 100%)"></div>
<div class="abs anton ombre" style="top:240px;left:0;right:0;text-align:center;color:#fff;font-size:130px">Ce site est un</div>
<div class="abs anton contour" style="top:380px;left:0;right:0;text-align:center;color:#DCFC1C;font-size:250px;text-shadow:0 0 60px rgba(220,252,28,.8)">jeu vidéo</div>
<div class="abs nav" style="top:700px;left:90px;width:900px;transform:rotate(3deg);border-color:#3cf;box-shadow:0 0 90px rgba(60,200,255,.7)"><div class="barre"><i></i><i></i><i></i></div><img src="src/nebula-site.jpg"></div>
<div class="abs" style="top:1180px;left:70px;width:620px;height:470px;border-radius:28px;overflow:hidden;border:8px solid #DCFC1C;transform:rotate(-4deg);box-shadow:0 30px 70px rgba(0,0,0,.8)"><img src="src/joueur.jpg" style="height:100%;margin-left:-150px"></div>
<div class="abs anton" style="top:1190px;right:90px;transform:rotate(8deg);font-size:150px;color:#0C0C0C;background:#fff;padding:14px 34px 4px;border-radius:14px;box-shadow:0 20px 50px rgba(0,0,0,.6)">3D</div>
<div class="abs" style="top:1380px;right:110px">{perso(150,-150,h=340)}</div>
'''

# 3. Introuvable sur Google
M["m3-google"] = BASE + f'''
<div class="fond" style="background-image:url(src/desert.jpg);background-position:40% center;filter:brightness(.9) saturate(1.2)"></div>
<div class="fond" style="background:linear-gradient(180deg,rgba(12,12,12,.9) 0%,rgba(12,12,12,.2) 35%,rgba(12,12,12,0) 60%,rgba(12,12,12,.85) 100%)"></div>
<div class="abs anton ombre" style="top:250px;left:0;right:0;text-align:center;color:#fff;font-size:140px">Ton site est</div>
<div class="abs anton contour" style="top:400px;left:0;right:0;text-align:center;color:#DCFC1C;font-size:200px">introuvable</div>
<div class="abs" style="top:720px;left:80px;width:920px;background:#fff;border-radius:40px;padding:40px 50px;box-shadow:0 30px 80px rgba(0,0,0,.55)">
  <img src="src/logo-google.svg" style="height:80px;display:block;margin-bottom:28px">
  <div style="border:3px solid #dfe1e5;border-radius:60px;padding:24px 36px;font-size:46px;color:#202124;display:flex;align-items:center;gap:22px"><svg width="44" height="44" viewBox="0 0 24 24"><circle cx="10" cy="10" r="7" fill="none" stroke="#5f6368" stroke-width="2.5"/><path d="M15 15l6 6" stroke="#5f6368" stroke-width="2.5"/></svg>ton-site.fr</div>
  <div style="margin-top:30px;font-size:44px;font-weight:700;color:#E8112D">Aucun résultat</div>
</div>
<div class="abs" style="top:1010px;left:620px;transform:rotate(12deg);width:330px;height:330px;border-radius:50%;border:12px solid #E8112D;display:flex;align-items:center;justify-content:center;font-family:Anton;font-size:210px;color:#E8112D;background:rgba(255,255,255,.92)">0</div>
<div class="abs" style="top:1300px;left:90px;width:470px;height:360px;border-radius:26px;overflow:hidden;border:8px solid #fff;transform:rotate(-5deg);box-shadow:0 30px 70px rgba(0,0,0,.7)"><img src="src/perdu.jpg" style="height:100%;margin-left:-120px"></div>
<div class="abs" style="top:1360px;left:640px">{perso(0,-95,h=330)}</div>
'''

# 4. Un site à 5 000 € en un prompt
M["m4-5000"] = BASE + f'''
<div class="fond" style="background:radial-gradient(circle at 50% 55%,#2c3a05 0%,#0C0C0C 60%)"></div>
<div class="abs" style="top:0;left:0;right:0;height:560px;overflow:hidden;opacity:.55"><img src="src/billets.jpg" style="width:100%;margin-top:-80px;filter:saturate(1.3)"></div>
<div class="fond" style="background:linear-gradient(180deg,rgba(12,12,12,.2) 0%,#0C0C0C 34%)"></div>
<div class="abs anton ombre" style="top:250px;left:0;right:0;text-align:center;color:#fff;font-size:120px">Il a l'air de coûter</div>
<div class="abs anton" style="top:380px;left:0;right:0;text-align:center;color:#fff;font-size:250px"><span style="position:relative">5 000 €<span style="position:absolute;left:-30px;right:-30px;top:48%;height:30px;background:#E8112D;transform:rotate(-8deg);border-radius:10px"></span></span></div>
<div class="abs nav" style="top:700px;left:60px;width:960px;transform:rotate(-3deg);border-color:#DCFC1C;box-shadow:0 0 80px rgba(220,252,28,.45)"><div class="barre"><i></i><i></i><i></i></div><img src="src/elegant-site.jpg"></div>
<div class="abs anton etiq" style="top:1290px;left:90px;font-size:170px;transform:rotate(-4deg);box-shadow:0 20px 50px rgba(0,0,0,.6)">1 prompt</div>
<div class="abs anton" style="top:1520px;left:100px;color:#fff;font-size:76px">Fait avec <span style="color:#DCFC1C">Claude</span></div>
<div class="abs" style="top:1280px;right:90px">{perso(0,-150,h=400)}</div>
'''


# ---- Style d'un autre créateur (fictif) : éditorial crème, titres à empattement, mot surligné orange
CREME = BASE.replace("background:#0C0C0C;font-family", "background:#F2EBDD;font-family") + """<style>
@font-face{font-family:Serif;src:url(src/InstrumentSerif-Italic.woff2)}
.serif{font-family:Serif;font-style:italic;color:#1d1a16;line-height:1}
.photo{position:absolute;border-radius:36px;overflow:hidden;border:4px solid #1d1a16}
.photo img{width:100%;height:100%;object-fit:cover}
.st{position:absolute;left:0;right:0;text-align:center;font-size:58px;font-weight:600;color:#1d1a16;letter-spacing:-.5px}
.st b{background:#FF6A3D;color:#fff;padding:2px 16px;border-radius:10px}
.num{position:absolute;top:110px;left:80px;font-size:34px;letter-spacing:6px;color:#8a7f70;font-weight:600}
</style>"""

def creme(num, titre, img, st, pos="center", extra=""):
    return CREME + f"""
<div class="num">{num}</div>
<div class="abs serif" style="top:250px;left:80px;right:80px;font-size:132px">{titre}</div>
<div class="photo" style="top:760px;left:80px;width:920px;height:680px"><img src="src/{img}" style="object-position:{pos}"></div>
<div class="st" style="top:1530px">{st}</div>{extra}"""

M["s1-autre-a"] = creme("N°12 · FORME", "3 habitudes pour garder la forme", "sport-cordes.jpg", "chaque <b>matin</b>, dix minutes")
M["s2-autre-b"] = creme("N°12 · FORME", "1. Bouger avant le café", "sport-velo.jpg", "même <b>cinq</b> minutes suffisent")
M["s3-toi-a"] = creme("N°21 · SITES WEB", "Ton site crie «&nbsp;fait par l'IA&nbsp;»", "siteia0.jpg", "les <b>3 signes</b> qui te trahissent", "top",
    f'<div class="abs" style="top:1190px;right:40px">{perso(0,-150,h=270)}</div>')
M["s4-toi-b"] = creme("N°21 · SITES WEB", "1. Les couleurs violettes", "revol-site.jpg", "le <b>violet</b> partout, ça se voit", "center",
    f'<div class="abs" style="top:1190px;right:95px">{perso(0,-95,h=270)}</div>')

for nom, html in M.items():
    (ICI / f"{nom}.html").write_text(html + "</body></html>")

js = """const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
for (const n of %s){await p.goto('file://%s/'+n+'.html');await p.waitForTimeout(400);await p.screenshot({path:'%s/'+n+'.jpg',type:'jpeg',quality:92});}
await b.close();})();""" % (list(M), ICI.resolve(), ICI.resolve())
(ICI / "capture.js").write_text(js)
subprocess.run(["node", str(ICI / "capture.js")], check=True)
print("ok", list(M))
