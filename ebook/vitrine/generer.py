"""Vignette (1200x1200) et bannière (2106x780) de la boutique Chariow."""
import subprocess, pathlib
ICI = pathlib.Path(__file__).parent.resolve()
IMG = ICI.parent / "images"
FONT = ICI.parent / "miniatures" / "src" / "Anton-Regular.woff2"

def perso(g=0, d=0, h=300):
    w = h * 120 / 270
    return f'''<svg width="{w:.0f}" height="{h}" viewBox="-10 -10 120 270" style="overflow:visible">
<g fill="#DCFC1C" stroke="#000" stroke-width="10" stroke-linejoin="round">
<rect x="24" y="136" width="24" height="112" rx="8"/><rect x="52" y="136" width="24" height="112" rx="8"/>
<rect x="22" y="52" width="56" height="94" rx="12"/>
<rect x="2" y="54" width="18" height="86" rx="8" transform="rotate({g} 11 62)"/>
<rect x="80" y="54" width="18" height="86" rx="8" transform="rotate({d} 89 62)"/>
<circle cx="50" cy="24" r="22"/></g></svg>'''

def tel(img, w, rot, x, y, z=1):
    return f'''<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;transform:rotate({rot}deg);z-index:{z};background:#000;border:5px solid #fff;border-radius:{w*0.09:.0f}px;padding:{w*0.025:.0f}px;box-shadow:0 25px 60px rgba(0,0,0,.7)"><img src="{IMG/img}" style="width:100%;display:block;border-radius:{w*0.06:.0f}px"></div>'''

def page(w, h, corps):
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Anton;src:url({FONT})}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:{w}px;height:{h}px;overflow:hidden;background:#111;position:relative;font-family:Inter,sans-serif}}
.a{{font-family:Anton;text-transform:uppercase;line-height:.95;color:#fff;position:absolute}}
.lime{{background:#DCFC1C;color:#111;padding:10px 20px 2px;display:inline-block;margin-top:18px}}
</style></head><body>{corps}</body></html>'''

vignette = page(1200, 1200, f'''
<div style="position:absolute;inset:0;background:radial-gradient(circle at 78% 55%,rgba(220,252,28,.35) 0%,rgba(17,17,17,0) 45%)"></div>
<div class="a" style="left:80px;top:80px;font-size:150px">Crée tes<br>vidéos<br><span class="lime">avec l'IA</span></div>
<div style="position:absolute;left:80px;top:640px;font-size:40px;color:#fff;line-height:1.35;width:520px">La méthode pas à pas pour faire tes vidéos <b>TikTok</b>, Reels et Shorts.</div>
<div class="a lime" style="left:80px;top:900px;font-size:50px;padding:14px 24px 8px;margin-top:0">53 prompts prêts à copier</div>
{tel("resultat-6.6.jpg", 330, 7, 740, 200, 2)}
<div style="position:absolute;left:990px;top:830px;z-index:3">{perso(150,-150,300)}</div>
<div class="a" style="right:70px;top:80px;font-size:46px">Lecodeur</div>
''')

banniere = page(2106, 780, f'''
<div style="position:absolute;inset:0;background:radial-gradient(ellipse at 72% 60%,rgba(220,252,28,.33) 0%,rgba(17,17,17,0) 50%)"></div>
<div class="a" style="left:140px;top:90px;font-size:150px">Crée tes vidéos<br><span class="lime">avec l'IA</span></div>
<div style="position:absolute;left:140px;top:480px;font-size:40px;color:#fff;line-height:1.35;width:760px">La méthode pas à pas pour TikTok, Reels et Shorts.</div>
<div class="a lime" style="left:140px;top:600px;font-size:48px;padding:12px 22px 6px;margin-top:0">53 prompts prêts à copier</div>
{tel("galerie/attention.jpg", 210, -12, 1130, 210, 1)}
{tel("galerie/mot-secret.jpg", 240, -5, 1340, 150, 2)}
{tel("galerie/jeu-video.jpg", 270, 0, 1560, 100, 3)}
{tel("galerie/skills.jpg", 240, 6, 1790, 150, 2)}
<div style="position:absolute;left:1000px;top:470px;z-index:4">{perso(150,-150,250)}</div>
<div class="a" style="right:60px;bottom:40px;font-size:40px;z-index:5">Lecodeur</div>
''')

for nom, html, (w, h) in [("vignette", vignette, (1200, 1200)), ("banniere", banniere, (2106, 780))]:
    (ICI / f"{nom}.html").write_text(html)
    js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:{w},height:{h}}}}});
await p.goto('file://{ICI}/{nom}.html');await p.waitForTimeout(400);await p.screenshot({{path:'{ICI}/{nom}.jpg',type:'jpeg',quality:92}});await b.close();}})();"""
    subprocess.run(["node", "-e", js], check=True)
print("ok")
