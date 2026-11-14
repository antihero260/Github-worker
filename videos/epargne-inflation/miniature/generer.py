"""Miniature verticale (1080x1920) de « Ton épargne ne te rendra pas riche » (Lefinancier, bleu ciel)."""
import subprocess, pathlib
ICI = pathlib.Path(__file__).parent.resolve()

def perso(g=0, d=0, h=300):
    w = h * 120 / 270
    return f'''<svg width="{w:.0f}" height="{h}" viewBox="-10 -10 120 270" style="overflow:visible"><g fill="#38BDF8" stroke="#000" stroke-width="10" stroke-linejoin="round">
<rect x="24" y="136" width="24" height="112" rx="8"/><rect x="52" y="136" width="24" height="112" rx="8"/><rect x="22" y="52" width="56" height="94" rx="12"/>
<rect x="2" y="54" width="18" height="86" rx="8" transform="rotate({g} 11 62)"/><rect x="80" y="54" width="18" height="86" rx="8" transform="rotate({d} 89 62)"/>
<circle cx="50" cy="24" r="22"/></g></svg>'''

def billet(x, y, r, s=1.0):
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;transform:rotate({r}deg) scale({s});width:300px;height:150px;border-radius:12px;'
            'background:linear-gradient(135deg,#2f7fb8 0%,#38bdf8 45%,#f2b705 100%);border:4px solid #0b1220;box-shadow:0 16px 40px rgba(0,0,0,.6);font-family:Anton;color:#0b1220">'
            '<b style="position:absolute;left:16px;top:12px;font-weight:400;font-size:58px;line-height:1">10 000</b>'
            '<span style="position:absolute;left:18px;bottom:12px;font-size:26px;text-transform:uppercase">Francs CFA</span>'
            '<i style="position:absolute;right:18px;top:26px;width:90px;height:90px;border-radius:50%;border:6px solid rgba(11,18,32,.6);background:rgba(255,255,255,.35)"></i></div>')

html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Anton;src:url(Anton-Regular.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;background:#0B1220;position:relative;font-family:Inter,sans-serif}}
.a{{font-family:Anton;position:absolute;text-transform:uppercase;line-height:.92;left:0;right:0;text-align:center}}
.contour{{-webkit-text-stroke:10px #0B1220;paint-order:stroke fill}}
</style></head><body>
<div style="position:absolute;inset:0;background:url(choc.jpg) 45% center/cover;filter:brightness(.5) saturate(1.1)"></div>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,#0B1220 0%,rgba(11,18,32,.25) 40%,rgba(11,18,32,.25) 62%,#0B1220 100%)"></div>
{billet(40,140,-18,1.1)}{billet(760,120,14,1.0)}{billet(-60,1500,12,1.1)}{billet(800,1560,-10,1.0)}
<div class="a contour" style="top:300px;font-size:170px;color:#fff">Ton épargne</div>
<div class="a contour" style="top:470px;font-size:150px;color:#38BDF8">ne te rendra<br>pas riche</div>
<div style="position:absolute;left:150px;top:880px;width:780px;padding:34px 40px;background:#0f1b33;border:6px solid #38BDF8;border-radius:34px;box-shadow:0 40px 110px rgba(0,0,0,.7);color:#ecece8">
  <div style="font-weight:800;font-size:40px;color:#38BDF8;display:flex;align-items:center;gap:14px"><i style="width:30px;height:30px;border-radius:50%;background:#38BDF8;display:block"></i>Mon épargne</div>
  <div style="display:flex;align-items:baseline;gap:20px;margin-top:10px"><b style="font-family:Anton;font-weight:400;font-size:150px;line-height:1;color:#fff">100 000</b><em style="font-style:normal;font-family:Anton;font-size:64px;color:#38BDF8">FCFA</em></div>
  <div style="font-family:Anton;font-size:60px;color:#FF4D4D;margin-top:6px;white-space:nowrap">Valeur réelle ↓ chaque année</div>
</div>
<div class="a" style="top:1330px;left:150px;right:auto;width:auto;text-align:left;font-size:96px;color:#0B1220;background:#FF4D4D;padding:14px 30px 4px;transform:rotate(-4deg)">L’inflation</div>
<div style="position:absolute;right:110px;top:1260px">{perso(150,-150,360)}</div>
</body></html>'''
(ICI / "miniature.html").write_text(html)
js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
await p.goto('file://{ICI}/miniature.html');await p.waitForTimeout(500);await p.screenshot({{path:'{ICI}/miniature-ton-epargne-ne-te-rendra-pas-riche.jpg',type:'jpeg',quality:92}});await b.close();}})();"""
subprocess.run(["node", "-e", js], check=True)
print("ok")
