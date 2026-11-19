#!/usr/bin/env python3
"""Simule le mixage de index.html avec ffmpeg (sans les filtres de carve) pour vérifier les niveaux avant le rendu.

Usage : python3 tools/simuler-mix.py <sortie.wav>  → affiche loudness totale, crête, et niveaux voix / musique / bruitages.
"""
import re
import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
h = (ICI / "index.html").read_text(encoding="utf-8")
pistes = []
for m in re.finditer(r'<audio id="([^"]+)" src="([^"]+)"([^>]*)>', h):
    a = m.group(3)
    g = lambda k, d=None: (re.search(rf'{k}="([^"]*)"', a) or [None, d])[1]
    pistes.append((m.group(1), m.group(2), float(g("data-start", 0)), g("data-duration"), float(g("data-volume", 1))))


def mix(sel, sortie):
    ins, fil = [], []
    choisies = [p for p in pistes if sel(p[0])]
    for k, (pid, src, d0, dd, v) in enumerate(choisies):
        ins += ["-i", str(ICI / src)]
        t = f"atrim=0:{dd}," if dd else ""
        fil.append(f"[{k}]{t}aformat=sample_rates=48000:channel_layouts=stereo,volume={v},adelay={int(d0 * 1000)}:all=1[a{k}]")
    fil.append("".join(f"[a{k}]" for k in range(len(choisies))) + f"amix=inputs={len(choisies)}:normalize=0,atrim=0:96[o]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fil), "-map", "[o]", sortie], check=True)
    o = subprocess.run(["ffmpeg", "-nostats", "-i", sortie, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1]
    pk = re.findall(r"Peak:\s+(-?[\d.inf]+) dBFS", o)[-1]
    return I, pk


sortie = sys.argv[1]
for nom, sel in (("voix", lambda i: i == "voix"), ("musiques", lambda i: i.startswith("musique")),
                 ("bruitages", lambda i: i.startswith("sfx")), ("TOTAL", lambda i: True)):
    I, pk = mix(sel, sortie.replace(".wav", f"-{nom}.wav"))
    print(f"{nom:10s} {I:>6} LUFS   crête {pk} dBFS")
