#!/usr/bin/env python3
"""Génère compositions/sous-titres.html (sous-titres mot à mot du style « Projecteur »,
film 16:9 en 1920×1080 : bandeau centré à 915 px, 85 % de la hauteur).

Usage :
  python3 tools/sous-titres.py assets/transcript.json [--script script.txt] [--fin 16]

- transcript.json : sortie de `hyperframes transcribe` ([{"text", "start", "end"}, …]).
- --script : le texte lu par la voix. Ses mots (orthographe et ponctuation exactes) sont alignés
  sur les temps de la transcription, même quand celle-ci contient des erreurs.
- --fin : seconde où disparaît le dernier groupe (défaut : dernier mot + 0,4 s).

Règles (frame.md, composant caption) : chaque mot apparaît à l'instant où il est dit et
s'ajoute au groupe ; le groupe repart de zéro après une ponctuation, ou au-delà de
4 mots / 26 caractères.
"""
from __future__ import annotations

import argparse
import difflib
import html
import json
import re
import unicodedata
from pathlib import Path

MAX_MOTS = 4
MAX_CARACTERES = 26
PONCTUATION_FIN = re.compile(r"[.,;:!?…]$")


def mots_du_script(chemin: Path) -> list[str]:
    jetons = chemin.read_text(encoding="utf-8").split()
    mots: list[str] = []
    prefixe = ""
    for jeton in jetons:
        if jeton == "«":  # guillemet ouvrant : collé au mot suivant
            prefixe = "«\u00a0"
            continue
        if re.fullmatch(r"[.,;:!?…»\"'—–-]+", jeton):
            if mots:  # ponctuation isolée (« ça : ») : on la colle au mot précédent,
                # avec l'espace insécable de la typographie française devant ? ! : ; »
                mots[-1] += ("\u00a0" if jeton[0] in "?!:;»" else "") + jeton
            continue
        mots.append(prefixe + jeton)
        prefixe = ""
    return mots


def normaliser(texte: str) -> str:
    sans_accents = unicodedata.normalize("NFKD", texte.lower())
    return "".join(c for c in sans_accents if c.isalnum())


def aligner(du_script: list[str], transcription: list[dict]) -> list[dict]:
    """Donne à chaque mot du script le temps du mot transcrit correspondant.

    La transcription automatique se trompe sur certains mots (« TchadGPT », mots anglais) ou les
    découpe autrement (« 23h17 » / « 23 h 17 ») : on aligne les deux suites (difflib), puis on répartit
    régulièrement le temps des passages qui ne correspondent pas.
    """
    a = [normaliser(m) for m in du_script]
    b = [normaliser(m["text"]) for m in transcription]
    sortie: list[dict] = [{"affiche": m.upper(), "start": None, "end": None} for m in du_script]
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op == "equal":
            for k in range(i2 - i1):
                sortie[i1 + k]["start"] = transcription[j1 + k]["start"]
                sortie[i1 + k]["end"] = transcription[j1 + k]["end"]
        elif op in ("replace", "delete") and j2 > j1:
            debut, fin = transcription[j1]["start"], transcription[j2 - 1]["end"]
            pas = (fin - debut) / (i2 - i1)
            for k in range(i2 - i1):
                sortie[i1 + k]["start"] = debut + k * pas
                sortie[i1 + k]["end"] = debut + (k + 1) * pas
    # mots du script sans correspondant : entre le mot précédent et le suivant
    for k, mot in enumerate(sortie):
        if mot["start"] is None:
            avant = next((sortie[x]["end"] for x in range(k - 1, -1, -1) if sortie[x]["end"] is not None), 0.0)
            apres = next((sortie[x]["start"] for x in range(k + 1, len(sortie)) if sortie[x]["start"] is not None), avant + 0.2)
            mot["start"], mot["end"] = avant, max(avant, apres)
    for mot in sortie:
        mot["start"], mot["end"] = round(mot["start"], 3), round(mot["end"], 3)
    return sortie


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
    parser.add_argument("--mots", type=Path, help="écrit aussi les mots du script avec leurs temps (JSON), pour caler les scènes")
    args = parser.parse_args()

    brut = json.loads(args.transcript.read_text(encoding="utf-8"))
    brut = brut["words"] if isinstance(brut, dict) else brut
    mots = [m for m in brut if re.search(r"\w", m["text"])]

    if args.script:
        mots = aligner(mots_du_script(args.script), mots)
    else:
        for mot in mots:
            mot["affiche"] = mot["text"].upper()
    if args.mots:
        args.mots.write_text(json.dumps(
            [{"i": i, "text": m["affiche"], "start": m["start"], "end": m["end"]} for i, m in enumerate(mots)],
            ensure_ascii=False, indent=0), encoding="utf-8")

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
