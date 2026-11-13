"""Miniature verticale (1080x1920) de « Tontine ou compte épargne ? » (Lefinancier, vidéo 4 : Tom et Emma en bleu)."""
import subprocess, pathlib
ICI = pathlib.Path(__file__).parent.resolve()

def perso(coul, genre, g=0, d=0, h=420, bouche="M41 32 Q50 40 59 32"):
    w = h * 120 / 270
    acc = ('<circle cx="50" cy="-8" r="13" fill="#0B1220"/><path d="M27 18 Q28 -2 50 -2 Q72 -2 73 18 Q64 6 50 7 Q36 6 27 18 Z" fill="#0B1220"/>' if genre == "emma" else
           '<path d="M28 12 Q34 -6 50 -4 Q66 -6 72 12 Q62 4 50 6 Q38 4 28 12 Z" fill="#0B1220"/>' if genre == "tom" else
           '<circle cx="41" cy="20" r="9" fill="none" stroke="#0B1220" stroke-width="2.6"/><circle cx="59" cy="20" r="9" fill="none" stroke="#0B1220" stroke-width="2.6"/>')
    return f'''<svg width="{w:.0f}" height="{h}" viewBox="-10 -20 120 280" style="overflow:visible"><g fill="{coul}" stroke="#000" stroke-width="10" stroke-linejoin="round">
<rect x="24" y="136" width="24" height="112" rx="8"/><rect x="52" y="136" width="24" height="112" rx="8"/><rect x="22" y="52" width="56" height="94" rx="12"/>
<rect x="2" y="54" width="18" height="86" rx="8" transform="rotate({g} 11 62)"/><rect x="80" y="54" width="18" height="86" rx="8" transform="rotate({d} 89 62)"/>
<circle cx="50" cy="24" r="22"/></g>{acc}<circle cx="41" cy="20" r="6.5" fill="#fff"/><circle cx="59" cy="20" r="6.5" fill="#fff"/><circle cx="42" cy="21" r="3" fill="#0B1220"/><circle cx="60" cy="21" r="3" fill="#0B1220"/>
<path d="{bouche}" fill="none" stroke="#0B1220" stroke-width="3.5" stroke-linecap="round"/></svg>'''

html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Anton;src:url(Anton-Regular.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;background:#0B1220;position:relative;font-family:Inter,sans-serif}}
.a{{font-family:Anton;position:absolute;text-transform:uppercase;line-height:.95;left:0;right:0;text-align:center}}
.contour{{-webkit-text-stroke:10px #0B1220;paint-order:stroke fill}}
.m{{position:absolute;top:0;width:540px;height:1920px;background-size:cover;background-position:center}}
.carte{{position:absolute;width:440px;padding:20px 26px;background:#0f1b33;border:6px solid;border-radius:26px;font-family:Anton;color:#fff;text-align:center;box-shadow:0 30px 80px rgba(0,0,0,.7)}}
.carte span{{display:block;font-size:40px;color:#b9c7d8;text-transform:uppercase}} .carte b{{font-weight:400;font-size:96px;line-height:1.05}}
</style></head><body>
<div class="m" style="left:0;background-image:linear-gradient(180deg,rgba(56,189,248,.25),rgba(11,18,32,.75)),url(g.jpg)"></div>
<div class="m" style="left:540px;background-image:linear-gradient(180deg,rgba(125,211,252,.3),rgba(11,18,32,.75)),url(d.jpg)"></div>
<div style="position:absolute;left:530px;top:-60px;width:20px;height:2100px;background:#fff;transform:rotate(3deg);box-shadow:0 0 40px rgba(0,0,0,.9)"></div>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,#0B1220 0%,rgba(11,18,32,0) 22%,rgba(11,18,32,0) 80%,#0B1220 100%)"></div>
<div class="a contour" style="top:250px;font-size:150px;color:#fff">Tontine<br>ou compte ?</div>
<div class="a contour" style="top:580px;font-size:110px;color:#F2B705">Qui gagne vraiment ?</div>
<div style="position:absolute;left:170px;top:800px">{perso("#38BDF8","tom",0,0,440,"M41 38 Q50 30 59 38")}</div>
<div style="position:absolute;left:720px;top:800px">{perso("#7DD3FC","emma",150,-150,440)}</div>
<div class="carte" style="left:50px;top:1290px;border-color:#38BDF8"><span>Tom · tontine</span><b>0 F</b></div>
<div class="carte" style="left:590px;top:1290px;border-color:#7DD3FC"><span>Emma · compte</span><b style="color:#F2B705">+4 000 F</b></div>
<div class="a" style="top:1540px;font-size:86px;color:#0B1220"><span style="background:#fff;padding:12px 30px 2px">Tu préfères quoi ?</span></div>
</body></html>'''
(ICI / "miniature.html").write_text(html)
js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
await p.goto('file://{ICI}/miniature.html');await p.waitForTimeout(500);await p.screenshot({{path:'{ICI}/miniature-tontine-epargne.jpg',type:'jpeg',quality:92}});await b.close();}})();"""
subprocess.run(["node", "-e", js], check=True)
print("ok")
