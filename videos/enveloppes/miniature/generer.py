"""Miniature verticale (1080x1920) de « La méthode des enveloppes » (Lefinancier, vidéo 7)."""
import subprocess, pathlib
ICI = pathlib.Path(__file__).parent.resolve()
ENV = [("LOYER", "#38BDF8", "#0B1220"), ("VIVRE", "#7DD3FC", "#0B1220"), ("ÉPARGNE", "#F2B705", "#0B1220"), ("LOISIRS", "#0284C7", "#F1F5F9")]


def env(lab, coul, txt, x, y, r):
    return (f'<div class="env" style="left:{x}px;top:{y}px;background:{coul};transform:rotate({r}deg)"><b style="color:{txt}">{lab}</b></div>')


envs = "".join(env(l, c, t, x, y, r) for (l, c, t), (x, y, r) in zip(ENV, [(60, 820, -12), (300, 760, -4), (560, 760, 4), (800, 820, 12)]))
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Anton;src:url(Anton-Regular.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;background:#0B1220;position:relative}}
.a{{font-family:Anton;position:absolute;text-transform:uppercase;line-height:1.05;left:0;right:0;text-align:center;-webkit-text-stroke:12px #0B1220;paint-order:stroke fill}}
.env{{position:absolute;width:230px;height:155px;border:8px solid #0B1220;border-radius:18px;overflow:hidden;display:flex;align-items:flex-end;justify-content:center;padding-bottom:14px;box-shadow:0 24px 60px rgba(0,0,0,.6)}}
.env::before{{content:"";position:absolute;left:-8px;right:-8px;top:-8px;height:62%;background:rgba(11,18,32,.2);clip-path:polygon(0 0,100% 0,50% 100%)}}
.env b{{position:relative;font-family:Anton;font-weight:400;font-size:34px}}
</style></head><body>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,18,32,.55),rgba(11,18,32,.25) 45%,rgba(11,18,32,.92) 80%),url(fond.jpg) center/cover"></div>
<div class="a" style="top:200px;font-size:118px;color:#fff">Fin du mois<br><span style="color:#FF6B6B">sans argent ?</span></div>
{envs}
<div class="a" style="top:1080px;font-size:132px;color:#38BDF8">La méthode<br>des enveloppes</div>
<div class="a" style="top:1480px;font-size:76px;color:#0B1220;-webkit-text-stroke:0"><span style="background:#F2B705;padding:12px 30px 2px">Chaque franc a une mission</span></div>
</body></html>'''
(ICI / "miniature.html").write_text(html)
js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
await p.goto('file://{ICI}/miniature.html');await p.waitForTimeout(500);await p.screenshot({{path:'{ICI}/miniature-enveloppes.jpg',type:'jpeg',quality:92}});await b.close();}})();"""
subprocess.run(["node", "-e", js], check=True)
print("ok")
