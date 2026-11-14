"""Miniature verticale (1080x1920) de « Ton salaire disparaît avant le 15 ? » (Lefinancier, vidéo 6 : Lucas, les petites dépenses oubliées)."""
import subprocess, pathlib
ICI = pathlib.Path(__file__).parent.resolve()

ICONES = {
    "cafe": '<path d="M18 38 H70 V62 Q70 84 44 84 Q18 84 18 62 Z" fill="#F1F5F9" stroke="#0B1220" stroke-width="6"/><path d="M70 46 Q88 46 88 58 Q88 70 70 70" fill="none" stroke="#0B1220" stroke-width="6"/>',
    "taxi": '<path d="M14 60 L24 36 H76 L86 60 Z" fill="#F2B705" stroke="#0B1220" stroke-width="6" stroke-linejoin="round"/><rect x="8" y="58" width="84" height="20" rx="6" fill="#F2B705" stroke="#0B1220" stroke-width="6"/><circle cx="28" cy="80" r="9" fill="#0B1220"/><circle cx="72" cy="80" r="9" fill="#0B1220"/>',
    "credit": '<rect x="28" y="8" width="44" height="84" rx="10" fill="#0B1220" stroke="#F1F5F9" stroke-width="4"/><rect x="34" y="20" width="32" height="56" rx="3" fill="#38BDF8"/>',
    "livraison": '<path d="M14 34 L50 18 L86 34 L86 74 L50 90 L14 74 Z" fill="#c08a4a" stroke="#0B1220" stroke-width="6" stroke-linejoin="round"/><path d="M14 34 L50 50 L86 34 M50 50 V90" fill="none" stroke="#0B1220" stroke-width="6"/>',
}
ico = lambda n, x, y, r: (f'<div style="position:absolute;left:{x}px;top:{y}px;width:170px;height:170px;border-radius:50%;background:#F1F5F9;border:7px solid #0B1220;'
                          f'display:flex;align-items:center;justify-content:center;transform:rotate({r}deg);box-shadow:0 20px 50px rgba(0,0,0,.6)">'
                          f'<svg viewBox="0 0 100 100" width="120" height="120">{ICONES[n]}</svg></div>')

html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Anton;src:url(Anton-Regular.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;background:#0B1220;position:relative}}
.a{{font-family:Anton;position:absolute;text-transform:uppercase;line-height:.95;left:0;right:0;text-align:center;-webkit-text-stroke:12px #0B1220;paint-order:stroke fill}}
</style></head><body>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,18,32,.2),rgba(11,18,32,.15) 40%,rgba(11,18,32,.9) 85%),url(fond.jpg) center/cover"></div>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,#0B1220 0%,rgba(11,18,32,0) 30%)"></div>
<div class="a" style="top:150px;font-size:150px;line-height:1.08;color:#fff">Ton salaire<br><span style="color:#38BDF8">disparaît</span></div>
<div style="position:absolute;left:340px;top:520px;width:400px;height:420px;background:#F1F5F9;border:10px solid #0B1220;border-radius:30px;overflow:hidden;text-align:center;transform:rotate(-5deg);box-shadow:0 40px 100px rgba(0,0,0,.7)">
<div style="height:110px;background:#38BDF8;border-bottom:10px solid #0B1220;font-family:Anton;font-size:76px;line-height:110px;color:#0B1220">AVANT LE</div>
<div style="font-family:Anton;font-size:250px;line-height:290px;color:#0B1220">15</div></div>
<svg style="position:absolute;left:330px;top:640px" width="440" height="300"><ellipse cx="215" cy="150" rx="195" ry="120" fill="none" stroke="#FF6B6B" stroke-width="16" transform="rotate(-5 215 150)"/></svg>
{ico("cafe", 60, 1180, -10)}{ico("taxi", 300, 1260, 6)}{ico("credit", 610, 1260, -6)}{ico("livraison", 850, 1180, 10)}
<div class="a" style="top:1500px;font-size:92px;color:#0B1220;-webkit-text-stroke:0"><span style="background:#fff;padding:14px 30px 4px">Les dépenses oubliées</span></div>
</body></html>'''
(ICI / "miniature.html").write_text(html)
js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
await p.goto('file://{ICI}/miniature.html');await p.waitForTimeout(500);await p.screenshot({{path:'{ICI}/miniature-salaire-15.jpg',type:'jpeg',quality:92}});await b.close();}})();"""
subprocess.run(["node", "-e", js], check=True)
print("ok")
