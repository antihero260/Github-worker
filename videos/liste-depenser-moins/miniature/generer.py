"""Miniature verticale (1080x1920) de « 10 techniques pour dépenser moins » (Lefinancier, vidéo 8, format liste)."""
import subprocess, pathlib
ICI = pathlib.Path(__file__).parent.resolve()
IM = ["pas-rue", "marche-fruits", "bouteille-parc", "couple-cuisine", "prix-etiquettes", "grillade-rue"]
tuiles = "".join(f'<div class="t" style="left:{(k % 2) * 540}px;top:{(k // 2) * 640}px;background-image:url({f}.jpg)"></div>' for k, f in enumerate(IM))
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Anton;src:url(Anton-Regular.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;background:#0B1220;position:relative}}
.t{{position:absolute;width:540px;height:640px;background-size:cover;background-position:center;filter:saturate(1.15)}}
.a{{font-family:Anton;position:absolute;text-transform:uppercase;line-height:.95;left:0;right:0;text-align:center;-webkit-text-stroke:14px #0B1220;paint-order:stroke fill}}
</style></head><body>
{tuiles}
<div style="position:absolute;inset:0;background:radial-gradient(ellipse 80% 55% at 50% 48%,rgba(11,18,32,.88),rgba(11,18,32,.35))"></div>
<div class="a" style="top:480px;font-size:560px;color:#F1F5F9;text-shadow:0 0 80px rgba(56,189,248,.7)">10</div>
<div class="a" style="top:1010px;font-size:150px;color:#38BDF8">techniques</div>
<div class="a" style="top:1170px;font-size:104px;color:#fff">pour dépenser moins</div>
<div class="a" style="top:1330px;font-size:84px;color:#0B1220;-webkit-text-stroke:0"><span style="background:#F2B705;padding:12px 30px 2px">sans te priver</span></div>
</body></html>'''
(ICI / "miniature.html").write_text(html)
js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
await p.goto('file://{ICI}/miniature.html');await p.waitForTimeout(500);await p.screenshot({{path:'{ICI}/miniature-10-techniques.jpg',type:'jpeg',quality:92}});await b.close();}})();"""
subprocess.run(["node", "-e", js], check=True)
print("ok")
