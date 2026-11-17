#!/usr/bin/env python3
"""Coupe la meilleure prise de chaque phrase (temps mot à mot des transcriptions) et les colle bout à bout.
Sortie : assets/montage/parole.mp4 (1080×1920, 30 i/s) + assets/montage/segments.json (début de chaque phrase dans le montage)."""
import json
import subprocess

import numpy as np
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
PR, TR, OUT = ICI / "assets/prises", ICI / "assets/transcripts", ICI / "assets/montage"
OUT.mkdir(parents=True, exist_ok=True)
# (prise, temps du 1er mot, temps du dernier mot, recadrage : zoom, centre y du visage dans l'image d'origine)
EDL = [  # choix faits avec tools/comparer_prises.py (fidélité au script, fluidité, son, image) ; voir assets/montage/comparaison.json
    ("20261116_161444", 9.44, 13.52, "certains d'entre vous"),
    ("20261116_161444", 14.40, 24.24, "Claude et les autres"),
    ("20261116_161514", 28.24, 31.68, "game changer HyperFrames"),
    ("20261116_162024", 27.28, 35.60, "pourquoi : le code"),
    ("20261116_162024", 53.36, 56.16, "HyperFrames intervient"),
    ("20261116_161514", 94.11, 97.79, "références visuelles et code"),
    ("20261116_162024", 73.29, 74.09, "plusieurs possibilités"),
    ("20261116_161514", 118.02, 123.06, "abonnements"),
    ("20261116_161514", 140.66, 147.14, "chatbot + attention"),
    ("20261116_162024", 115.93, 120.09, "tout se joue sur le modèle"),
    ("20261116_161514", 172.41, 180.41, "Opus 5.5 et Fable 5.2"),
    ("20261116_161514", 193.77, 198.33, "3D, 2D, isométrique"),
    ("20261116_161514", 208.65, 216.01, "abonne-toi"),
]
DEBUT_FORCE = {("20261116_161444", 9.44): 9.20}  # le « Cer- » de « certains » commence avant le temps du mot : on le garde
FIN_FORCEE = {("20261116_162024", 27.28): 35.80}  # couper avant « comme Gemini Omni »
RECADRE = {"20261116_162912": (1.35, 1140)}  # prise filmée de plus loin : on resserre pour garder la même taille de visage
segs, t = [], 0.0
FICHIERS, COUPES = [], []
for k, (p, a, b, note) in enumerate(EDL):
    mots = json.loads((TR / f"{p}.json").read_text())
    i0 = min(range(len(mots)), key=lambda i: abs(mots[i]["start"] - a))
    i1 = min(range(len(mots)), key=lambda i: abs(mots[i]["start"] - b))
    debut = max(0.0, mots[i0]["start"] - 0.08)
    if i0 > 0:
        debut = max(debut, mots[i0 - 1]["end"] + 0.02)
    fin = mots[i1]["end"] + 0.18
    if i1 + 1 < len(mots):
        fin = min(fin, mots[i1 + 1]["start"] - 0.04)
    if (p, a) in DEBUT_FORCE:
        debut = DEBUT_FORCE[(p, a)]
    if (p, a) in FIN_FORCEE:
        fin = FIN_FORCEE[(p, a)]
    d = round(fin - debut, 3)
    z, cy = RECADRE.get(p, (1.0, 1000))
    if z > 1:
        w, h = round(1080 / z / 2) * 2, round(1920 / z / 2) * 2
        y = int(min(max(cy - 1000 / z, 0), 1920 - h))
        vf = f"crop={w}:{h}:{(1080 - w) // 2}:{y},scale=1080:1920,fps=30"
    else:
        vf = "scale=1080:1920,fps=30"
    # parties parlées : énergie par tranches de 20 ms, seuil = bruit de fond + 12 dB, pauses > 0,25 s supprimées
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{debut:.3f}", "-i", str(PR / f"{p}.mp4"), "-t", f"{d:.3f}", "-vn", "-ac", "1", "-ar", "16000",
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    n = len(x) // 320
    db = 10 * np.log10((x[: n * 320].reshape(n, 320) ** 2).mean(1) + 1e-10)
    seuil = np.percentile(db, 10) + 12
    parle = db > seuil
    zones, i = [], 0
    while i < n:
        if parle[i]:
            j = i
            while j < n and parle[j]:
                j += 1
            zones.append([i * 0.02, j * 0.02])
            i = j
        else:
            i += 1
    fus = []
    for z in zones:
        if fus and z[0] - fus[-1][1] < 0.25:
            fus[-1][1] = z[1]
        else:
            fus.append(z)
    fus = [z for z in fus if z[1] - z[0] > 0.08]
    morceaux = [(max(0.0, z[0] - 0.07), min(d, z[1] + 0.09)) for z in fus]
    seg_t0 = t
    for m, (u0, u1) in enumerate(morceaux):
        f = OUT / f"seg{k:02d}-{m:02d}.mp4"
        du = round(u1 - u0, 3)
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{debut + u0:.3f}", "-i", str(PR / f"{p}.mp4"), "-t", f"{du:.3f}",
                        "-vf", vf, "-af", f"afade=t=in:d=0.015,afade=t=out:st={max(0, du - 0.03):.3f}:d=0.03,aresample=48000",
                        "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(f)], check=True)
        FICHIERS.append(f.name)
        COUPES.append({"t": round(t, 3), "phrase": k})
        t += du
    segs.append({"k": k, "prise": p, "note": note, "debut_montage": round(seg_t0, 3), "duree": round(t - seg_t0, 3), "morceaux": len(morceaux),
                 "texte": " ".join(m["text"] for m in mots[i0:i1 + 1])})
(OUT / "liste.txt").write_text("".join(f"file '{f}'\n" for f in FICHIERS))
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(OUT / "liste.txt"), "-c:v", "libx264", "-crf", "12",
                "-preset", "medium", "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-15:TP=-1.5:LRA=9", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                str(OUT / "parole.mp4")], check=True)
(OUT / "segments.json").write_text(json.dumps({"phrases": segs, "coupes": COUPES}, indent=1, ensure_ascii=False))
for s in segs:
    print(f'{s["debut_montage"]:6.2f} +{s["duree"]:.2f} ({s["morceaux"]} morceaux)  {s["texte"][:70]}')
print("total", round(t, 2))
