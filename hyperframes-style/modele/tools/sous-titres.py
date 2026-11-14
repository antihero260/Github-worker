#!/usr/bin/env python3
"""Génère compositions/sous-titres.html (sous-titres mot à mot du style « Projecteur »,
film 16:9 en 1920×1080 : bandeau centré à 915 px, 85 % de la hauteur).

Usage :
  python3 tools/sous-titres.py assets/transcript.json [--script script.txt] [--fin 16]

- transcript.json : sortie de `hyperframes transcribe` ([{"text", "start", "end"}, …]).
- --script : le texte lu par la voix. Sa ponctuation remplace celle de la transcription
  (mot par mot, par position) quand les deux ont le même nombre de mots.
- --fin : seconde où disparaît le dernier groupe (défaut : dernier mot + 0,4 s).

Règles (frame.md, composant caption) : chaque mot apparaît à l'instant où il est dit et
s'ajoute au groupe ; le groupe repart de zéro après une ponctuation, ou au-delà de
4 mots / 26 caractères.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

MAX_MOTS = 4
MAX_CARACTERES = 26
PONCTUATION_FIN = re.compile(r"[.,;:!?…]$")


def mots_du_script(chemin: Path) -> list[str]:
    jetons = chemin.read_text(encoding="utf-8").split()
    mots: list[str] = []
    for jeton in jetons:
        if re.fullmatch(r"[.,;:!?…«»\"'—–-]+", jeton):
            if mots:  # ponctuation isolée (« ça : ») : on la colle au mot précédent,
                # avec l'espace insécable de la typographie française devant ? ! : ;
                mots[-1] += (" " if jeton[0] in "?!:;" else "") + jeton
            continue
        mots.append(jeton)
    return mots


def grouper(mots: list[dict]) -> list[list[dict]]:
    groupes: list[list[dict]] = []
    courant: list[dict] = []
    for mot in mots:
        texte = " ".join(m["affiche"] for m in courant + [mot])
        if courant and (len(courant) >= MAX_MOTS or len(texte) > MAX_CARACTERES):
            groupes.append(courant)
            courant = []
        courant.append(mot)
        if PONCTUATION_FIN.search(mot["affiche"]):
            groupes.append(courant)
            courant = []
    if courant:
        groupes.append(courant)
    return groupes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("transcript", type=Path)
    parser.add_argument("--script", type=Path)
    parser.add_argument("--fin", type=float)
    parser.add_argument("--sortie", type=Path, default=Path("compositions/sous-titres.html"))
    args = parser.parse_args()

    brut = json.loads(args.transcript.read_text(encoding="utf-8"))
    brut = brut["words"] if isinstance(brut, dict) else brut
    mots = [m for m in brut if re.search(r"\w", m["text"])]

    textes = [m["text"] for m in mots]
    if args.script:
        du_script = mots_du_script(args.script)
        if len(du_script) == len(mots):
            textes = du_script
        else:
            print(f"Attention : {len(du_script)} mots dans le script, {len(mots)} dans la transcription ;"
                  " ponctuation de la transcription conservée.")
    for mot, texte in zip(mots, textes):
        mot["affiche"] = texte.upper()

    groupes = grouper(mots)
    fin_totale = args.fin if args.fin is not None else mots[-1]["end"] + 0.4

    lignes_html: list[str] = []
    lignes_js: list[str] = []
    n_mot = 0
    for g, groupe in enumerate(groupes):
        debut = max(0.0, round(groupe[0]["start"], 3))
        fin = round(groupes[g + 1][0]["start"], 3) if g + 1 < len(groupes) else round(fin_totale, 3)
        duree = round(fin - debut, 3)
        spans = []
        for mot in groupe:
            mid = f"st-m{n_mot}"
            spans.append(f'<span id="{mid}" class="st-mot">{html.escape(mot["affiche"])}</span>')
            if mot is not groupe[0]:
                lignes_js.append(f'    tl.set("#{mid}", {{ display: "inline-block" }}, {round(mot["start"], 3)});')
            n_mot += 1
        lignes_html.append(
            f'    <div id="st-g{g}" class="clip st-groupe" data-start="{debut}" data-duration="{duree}">'
            f'<span class="st-bandeau">{"".join(spans)}</span></div>'
        )

    sortie = f"""<!-- Généré par tools/sous-titres.py : ne pas modifier à la main, relancer le script. -->
<template>
  <style>
    #root {{
      position: absolute;
      inset: 0;
      pointer-events: none;
    }}
    .st-groupe {{
      position: absolute;
      left: 0;
      width: 100%;
      top: calc(var(--caption-y, 915px) - 47px);
      height: 94px;
      text-align: center;
      overflow: visible;
    }}
    .st-bandeau {{
      display: inline-block;
      background: var(--caption-box, #eeeeea);
      color: var(--caption-ink, #0a0a06);
      font-family: "Anton", "League Gothic", sans-serif;
      font-size: 78px;
      line-height: 0.9;
      padding: 12px 20px 11px;
      text-transform: uppercase;
      white-space: nowrap;
    }}
    .st-mot {{
      display: none;
    }}
    .st-mot:first-child {{
      display: inline-block;
    }}
    .st-mot + .st-mot {{
      margin-left: 0.22em;
    }}
  </style>
  <div id="root" data-composition-id="sous-titres" data-width="1920" data-height="1080">
{chr(10).join(lignes_html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(lignes_js)}
    window.__timelines["sous-titres"] = tl;
  </script>
</template>
"""
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(sortie, encoding="utf-8")
    print(f"{len(groupes)} groupes, {n_mot} mots → {args.sortie}")


if __name__ == "__main__":
    main()
