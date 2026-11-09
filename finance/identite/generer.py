"""Photos de profil TikTok de la chaîne finance (1080x1080, affichées en rond)."""
import subprocess, pathlib
ICI = pathlib.Path(__file__).parent.resolve()
FONT = ICI.parents[1] / "ebook" / "miniatures" / "src" / "Anton-Regular.woff2"

def perso(g=0, d=0, h=300):
    w = h * 120 / 270
    return f'''<svg width="{w:.0f}" height="{h}" viewBox="-10 -10 120 270" style="overflow:visible">
<g fill="#DCFC1C" stroke="#000" stroke-width="10" stroke-linejoin="round">
<rect x="24" y="136" width="24" height="112" rx="8"/><rect x="52" y="136" width="24" height="112" rx="8"/>
<rect x="22" y="52" width="56" height="94" rx="12"/>
<rect x="2" y="54" width="18" height="86" rx="8" transform="rotate({g} 11 62)"/>
<rect x="80" y="54" width="18" height="86" rx="8" transform="rotate({d} 89 62)"/>
<circle cx="50" cy="24" r="22"/></g></svg>'''

def page(corps):
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Anton;src:url({FONT})}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1080px;overflow:hidden;background:#111;position:relative}}
.a{{font-family:Anton;position:absolute;line-height:1}}
</style></head><body>{corps}</body></html>'''

piece = '''<div style="position:absolute;left:{x}px;top:{y}px;width:{d}px;height:{d}px;border-radius:50%;
background:radial-gradient(circle at 35% 30%,#FFE98A,#F2B705 55%,#B07D00);border:{b}px solid #000;
box-shadow:0 20px 50px rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center">
<div style="width:78%;height:78%;border-radius:50%;border:{b2}px solid rgba(120,80,0,.55);display:flex;align-items:center;justify-content:center;
font-family:Anton;font-size:{f}px;color:#7A5200">F</div></div>'''

# A : le personnage vert et une grosse pièce FCFA
A = page(f'''
<div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 55%,#33420a 0%,#111 68%)"></div>
<div style="position:absolute;left:250px;top:230px">{perso(150,-95,610)}</div>
''' + piece.format(x=580, y=310, d=360, b=14, b2=10, f=210))

# B : le personnage pointe une courbe qui monte
B = page(f'''
<div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 55%,#33420a 0%,#111 68%)"></div>
<svg style="position:absolute;left:0;top:0" width="1080" height="1080">
<rect x="520" y="640" width="90" height="180" rx="10" fill="#DCFC1C"/>
<rect x="650" y="520" width="90" height="300" rx="10" fill="#DCFC1C"/>
<rect x="780" y="380" width="90" height="440" rx="10" fill="#DCFC1C"/>
<polyline points="500,600 640,470 760,500 900,250" fill="none" stroke="#fff" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/>
<polygon points="900,250 830,262 888,318" fill="#fff" stroke="#fff" stroke-width="18" stroke-linejoin="round"/>
</svg>
<div style="position:absolute;left:150px;top:260px">{perso(0,-95,600)}</div>
''')

# C : monogramme « LF » et pièce
C = page('''
<div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,#2a3608 0%,#111 70%)"></div>
<div class="a" style="left:0;right:0;top:250px;text-align:center;font-size:560px;color:#DCFC1C;letter-spacing:-10px">LF</div>
''' + piece.format(x=700, y=640, d=230, b=10, b2=7, f=130))

for nom, html in [("profil-A-perso-piece", A), ("profil-B-perso-courbe", B), ("profil-C-monogramme", C)]:
    (ICI / f"{nom}.html").write_text(html)
    js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1080}}}});
await p.goto('file://{ICI}/{nom}.html');await p.waitForTimeout(400);await p.screenshot({{path:'{ICI}/{nom}.png'}});await b.close();}})();"""
    subprocess.run(["node", "-e", js], check=True)
print("ok")
