"""Miniature verticale (1080x1920) de l'edit « Tous les modèles Claude »."""
import subprocess, pathlib
ICI = pathlib.Path(__file__).parent.resolve()
NOMS = ["FABLE 5.2", "OPUS 5.5", "SONNET 5.5", "HAIKU 5.5"]
cartes = "".join(f'<div class="c">{n}</div>' for n in NOMS)
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Anton;src:url(Anton-Regular.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;background:#141413;position:relative}}
.a{{font-family:Anton;position:absolute;left:0;right:0;text-align:center;text-transform:uppercase;line-height:.95;-webkit-text-stroke:14px #141413;paint-order:stroke fill}}
.g{{position:absolute;left:70px;top:1180px;width:940px;display:grid;grid-template-columns:1fr 1fr;gap:26px}}
.c{{background:#F0EEE6;border:8px solid #141413;border-radius:28px;padding:26px 0 16px;text-align:center;font-family:Anton;font-size:84px;color:#141413}}
</style></head><body>
<div style="position:absolute;inset:0;background:radial-gradient(ellipse 80% 60% at 50% 45%,rgba(20,20,19,.35),rgba(20,20,19,.9)),url(fond.jpg) center/cover"></div>
<img src="logo-claude.svg" style="position:absolute;left:340px;top:200px;width:400px;height:400px;filter:drop-shadow(0 0 80px rgba(217,119,87,.9))">
<div class="a" style="top:660px;font-size:250px;color:#F0EEE6">CLAUDE</div>
<div class="a" style="top:920px;font-size:96px;color:#141413;-webkit-text-stroke:0"><span style="background:#D97757;padding:12px 30px 2px;border:7px solid #141413">TOUS SES MODÈLES</span></div>
<div class="g">{cartes}</div>
<div class="a" style="top:1640px;font-size:110px;color:#fff">2023 <span style="color:#D97757">→</span> 2026</div>
</body></html>'''
(ICI / "miniature.html").write_text(html)
js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
await p.goto('file://{ICI}/miniature.html');await p.waitForTimeout(500);await p.screenshot({{path:'{ICI}/miniature-edit-claude.jpg',type:'jpeg',quality:92}});await b.close();}})();"""
subprocess.run(["node", "-e", js], check=True)
print("ok")
