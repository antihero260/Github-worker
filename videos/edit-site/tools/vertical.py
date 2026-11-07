#!/usr/bin/env python3
"""Écrit ../edit-site-vertical/index.html : le format bandeau de l'utilisateur (1080×1920), titre blanc en haut, le film 16:9
au centre, et dessous 6 cases verrouillées « ? » qui se dévoilent chacune sur le temps où le bloc arrive dans le site."""
import json
import re
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
V = ICI.parent / "edit-site-vertical"
SRC = ICI.parent / "site-mot-secret-vertical/index.html"
TEMPS = json.loads((ICI / "tools/temps.json").read_text())
B, FIN = TEMPS["beats"], TEMPS["fin"]
TITRE = "POV : l’IA a codé mon site en 1 prompt"
CASES = [("Menu", B[9]), ("Titre", B[10]), ("Photo", B[11]), ("Bouton", B[12]), ("Produits", B[14]), ("Mobile", B[17])]

h = SRC.read_text()
h = h.replace("Ce site cache un mot secret", TITRE).replace("24.58", str(FIN)).replace("assets/site-mot-secret-16x9.mp4", "assets/edit-site-16x9.mp4")
h = h.replace("width: 248px;", f"width: {round((1028 - 12 * (len(CASES) - 1)) / len(CASES))}px;")
h = h.replace("font-size: 96px;\n        line-height: 1;\n        color: #dcfc1c;", "font-size: 76px;\n        line-height: 1;\n        color: #dcfc1c;")
h = h.replace("font-size: 30px;\n        line-height: 1;\n        white-space: nowrap;", "font-size: 27px;\n        line-height: 1;\n        white-space: nowrap;")
gabarit = re.search(r'          <div id="ck-0" class="ck-case">.*?</div>\n', h).group(0)
cases = "".join(gabarit.replace('id="ck-0"', f'id="ck-{k}"').replace("<b>1</b>", f"<b>{k + 1}</b>").replace("ck-q0", f"ck-q{k}")
                .replace('id="ck-n0" class="ck-nom" style="opacity: 0">?', f'id="ck-n{k}" class="ck-nom" style="opacity: 0">{nom}')
                .replace("ck-c0", f"ck-c{k}").replace("ck-v0", f"ck-v{k}") for k, (nom, _) in enumerate(CASES))
h = re.sub(r'          <div id="ck-0" class="ck-case">.*?(?=        </div>\n      </div>\n      <!-- check : fin -->)', cases, h, flags=re.S)
h = h.replace("Le mot secret · 4 lettres", "Mon site · bloc par bloc")
h = h.replace('data-track-index="3" style="opacity: 0"', 'data-track-index="3"')
js = []
for k, (nom, g) in enumerate(CASES):
    js += [f'tl.to("#ck-{k}", {{ rotationY: 360, transformPerspective: 3000, duration: 0.28, ease: "power3.inOut" }}, {round(g - 0.14, 3)});',
           f'tl.set("#ck-q{k}", {{ opacity: 0 }}, {g});', f'tl.set("#ck-c{k}", {{ opacity: 0 }}, {g});', f'tl.set("#ck-n{k}", {{ opacity: 1 }}, {g});',
           f'tl.set("#ck-{k}", {{ backgroundImage: "none" }}, {g});',
           f'tl.to("#ck-{k}", {{ borderColor: "#DCFC1C", backgroundColor: "#DCFC1C", color: "#0C0C0C", scale: 1.12, duration: 0.1 }}, {g});',
           f'tl.to("#ck-{k}", {{ scale: 1, duration: 0.18, ease: "power2.out" }}, {round(g + 0.1, 3)});',
           f'tl.fromTo("#ck-v{k}", {{ opacity: 0, scale: 2 }}, {{ opacity: 1, scale: 1, duration: 0.12, ease: "power4.in", immediateRender: false }}, {round(g + 0.08, 3)});']
js.append(f'tl.to(".ck-case", {{ keyframes: [{{ y: -22, duration: 0.1 }}, {{ y: 0, duration: 0.16 }}], stagger: 0.05 }}, {B[18]});')
for x in (B[21] + (B[22] - B[21]) / 2, B[22], B[23]):
    js.append(f'tl.to(".ck-case", {{ keyframes: [{{ scale: 1.06, duration: 0.07 }}, {{ scale: 1, duration: 0.14 }}] }}, {round(x, 3)});')
h = re.sub(r'(const tl = gsap\.timeline\(\{ paused: true \}\);\n).*?(\s*window\.__timelines\["main"\] = tl;)', lambda m: m.group(1) + "\n".join("      " + l for l in js) + m.group(2), h, flags=re.S)
# Demande de l'utilisateur pour l'edit : pas de texte → titre seul, sans les cases sous le film
h = re.sub(r"\s*<!-- check : début -->.*?<!-- check : fin -->", "", h, flags=re.S)
h = re.sub(r'(const tl = gsap\.timeline\(\{ paused: true \}\);\n).*?(\s*window\.__timelines\["main"\] = tl;)', lambda m: m.group(1) + m.group(2).lstrip("\n"), h, flags=re.S)
(V / "index.html").write_text(h, encoding="utf-8")
json.dump({"id": "edit-site-vertical", "name": "edit-site-vertical", "createdAt": "2026-11-07T01:00:00.000Z"}, open(V / "meta.json", "w"), indent=2)
print("vertical écrit :", len(CASES), "cases")
