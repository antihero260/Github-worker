#!/usr/bin/env python3
"""Mixage des musiques, à relancer après tools/construire-scenes.py.

1. carve : creuse chaque musique dans les fréquences de la voix (skill media-use, force 0,5) ;
2. SUPPRIME la baisse de niveau automatique que carve ajoute (nœud « gain » + sa courbe) : à la force 0,5,
   elle vise une musique 12 dB sous la voix et la baisse jusqu'à 12 dB dès que la voix parle, ce qui rendait la
   musique inaudible pour l'utilisateur. On garde seulement les creux de fréquences ;
3. ajoute un limiteur (−4 dB) en fin de chaîne d'effets de chaque musique.
Le niveau de la musique se règle ensuite avec data-volume (MUSIQUES dans construire-scenes.py).
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
CARVE = Path.home() / ".claude/skills/media-use/audio/scripts/carve.mjs"
CORE = sys.argv[1] if len(sys.argv) > 1 else "/tmp/corelink"  # dossier contenant node_modules/@hyperframes/core

index = ICI / "index.html"
ids = re.findall(r'<audio id="(musique-\d+)"', index.read_text(encoding="utf-8"))
for m in ids:
    subprocess.run(["node", str(CARVE), "--comp", str(index), "--bed", m, "--strength", "0.5", "--core", CORE], check=True)

h = index.read_text(encoding="utf-8")


def plafond(m):
    chaine = json.loads(html.unescape(m.group(2)))
    baisse = [n["id"] for n in chaine["nodes"] if n.get("fromCarve") and n["type"] == "gain"]
    BAISSES.extend(baisse)
    chaine["nodes"] = [n for n in chaine["nodes"] if n.get("id") != "plafond" and n["id"] not in baisse]
    chaine["nodes"].append({"type": "limiter", "id": "plafond", "label": "Plafond des crêtes", "params": {"limit": -4}})
    return m.group(1) + html.escape(json.dumps(chaine, ensure_ascii=False, separators=(",", ":")), quote=True) + m.group(3)


def sans_baisse(m):
    auto = json.loads(html.unescape(m.group(2)))
    auto["lanes"] = [la for la in auto["lanes"] if not any(la["target"].startswith(f"fx.{b}.") for b in BAISSES)]
    return m.group(1) + html.escape(json.dumps(auto, ensure_ascii=False, separators=(",", ":")), quote=True) + m.group(3)


BAISSES = []
h, n = re.subn(r'(<audio id="musique-\d+"[^>]*?data-fx-chain=")([^"]*)(")', plafond, h)
h = re.sub(r'(<audio id="musique-\d+"[^>]*?data-automation=")([^"]*)(")', sans_baisse, h)
index.write_text(h, encoding="utf-8")
print(f"carve sur {len(ids)} musiques, baisse automatique retirée ({len(BAISSES)}), limiteur ajouté sur {n}")
