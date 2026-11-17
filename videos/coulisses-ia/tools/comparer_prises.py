#!/usr/bin/env python3
"""Compare toutes les versions de chaque phrase du script de base dans les prises et note chacune.
Critères : fidélité au script (mots), fluidité (répétitions, trous), son (niveau de voix / bruit), image (netteté et lumière du visage).
Sortie : assets/montage/comparaison.json + tableau imprimé."""
import difflib, json, re, subprocess, unicodedata
from pathlib import Path
import numpy as np

ICI = Path(__file__).resolve().parent.parent
PR, TR = ICI / "assets/prises", ICI / "assets/transcripts"

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.findall(r"[a-z0-9]+", s.replace("'", " ").replace("’", " "))

# phrase du script de base -> candidats (prise, début, fin) en temps de mots des transcriptions
PHRASES = [
 ("Certains d'entre vous m'ont demandé comment je faisais mes vidéos avec l'IA.",
  [("161444", 9.44, 13.52), ("161514", 0.24, 4.08), ("162024", 5.28, 9.92), ("162912", 0.00, 4.72)]),
 ("Alors, généralement, j'utilise Claude, notamment Opus 5.5. Mais il n'y a pas que Claude : ChatGPT, Gemini, Grok et bien d'autres peuvent aussi le faire.",
  [("161444", 14.40, 24.24), ("161514", 5.12, 14.96), ("162024", 10.80, 21.36), ("162912", 5.60, 13.52)]),
 ("Le véritable game changer, c'est une skill qui s'appelle HyperFrames.",
  [("161514", 28.24, 31.68), ("161514", 43.04, 46.32), ("162024", 21.92, 26.00), ("162912", 14.00, 17.28)]),
 ("Pourquoi ? Parce que les modèles que je viens de citer ne sont pas spécialement conçus pour créer des vidéos. En revanche, ils sont extrêmement performants pour écrire du code.",
  [("162024", 27.28, 35.60), ("161514", 60.15, 71.43), ("162912", 18.56, 35.04)]),
 ("Et c'est exactement là qu'HyperFrames intervient",
  [("161514", 75.83, 78.47), ("161514", 79.19, 81.35), ("162024", 53.36, 56.16)]),
 ("il permet de créer des vidéos à partir de références visuelles et de code.",
  [("161514", 94.11, 97.79), ("162024", 68.09, 72.57), ("162024", 59.92, 63.52)]),
 ("Pour l'installation, tu as plusieurs possibilités.",
  [("162024", 73.29, 74.09), ("161514", 98.47, 100.31)]),
 ("Tu peux utiliser Claude avec un abonnement à 20 dollars pour commencer, ou opter pour une formule plus puissante.",
  [("161514", 118.02, 123.06), ("161514", 109.51, 112.63), ("162024", 76.97, 82.49), ("162912", 122.42, 129.34)]),
 ("Tu peux aussi installer la skill directement dans ton environnement de chatbot.",
  [("161514", 140.66, 143.70), ("161514", 127.30, 131.46), ("162024", 86.17, 90.97)]),
 ("Mais attention, l'outil ne fait pas tout :",
  [("161514", 144.90, 147.14), ("161514", 150.18, 151.94), ("162024", 112.25, 115.45)]),
 ("le modèle utilisé change énormément le résultat.",
  [("162024", 115.93, 120.09), ("161514", 157.46, 161.46), ("162912", 133.90, 138.14)]),
 ("C'est pour ça qu'Opus 5.5 est très intéressant, mais je pense que Fable 5.2 peut même faire mieux sur certaines créations.",
  [("161514", 172.41, 180.41), ("161514", 185.37, 190.97), ("162024", 136.56, 143.36)]),
 ("Je peux faire de la 3D, de la 2D, de la 3D isométrique et ainsi de suite.",
  [("162912", 145.10, 152.38), ("161514", 191.77, 198.33)]),
 ("Abonne-toi, parce que dans la prochaine vidéo, je vais te montrer comment reproduire le style visuel d'un autre créateur avec cette méthode.",
  [("161514", 208.65, 216.01), ("162912", 161.82, 169.82), ("162024", 144.08, 150.88)]),
]

def mots(p):
    return json.loads((TR / f"20261116_{p}.json").read_text())

def audio(p, a, b):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.2f}", "-i", str(PR / f"20261116_{p}.mp4"), "-t", f"{b - a:.2f}",
                          "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    n = len(x) // 320
    db = 10 * np.log10((x[: n * 320].reshape(n, 320) ** 2).mean(1) + 1e-10)
    return float(np.percentile(db, 90)), float(np.percentile(db, 90) - np.percentile(db, 10))

def image(p, a, b):
    """netteté (variance du laplacien) et luminance moyenne d'une zone visage, sur 3 images"""
    nets, lums = [], []
    for t in np.linspace(a + 0.2, b - 0.2, 3):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(PR / f"20261116_{p}.mp4"), "-frames:v", "1",
                              "-vf", "scale=540:960,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
        g = np.frombuffer(raw, dtype=np.uint8).reshape(960, 540).astype(np.float32)
        z = g[330:620, 150:390]  # visage et haut du buste
        lap = z[1:-1, 1:-1] * 4 - z[:-2, 1:-1] - z[2:, 1:-1] - z[1:-1, :-2] - z[1:-1, 2:]
        nets.append(lap.var()); lums.append(z.mean())
    return float(np.median(nets)), float(np.mean(lums))

res = []
for k, (texte, cands) in enumerate(PHRASES):
    ref = norm(texte)
    ligne = []
    for p, a, b in cands:
        ws = [w for w in mots(p) if a - 0.01 <= w["start"] <= b + 0.01]
        dit = norm(" ".join(w["text"] for w in ws))
        fid = difflib.SequenceMatcher(None, ref, dit).ratio()
        rep = sum(1 for i in range(1, len(dit)) if dit[i] == dit[i - 1]) + sum(
            1 for i in range(2, len(dit) - 1) if dit[i:i + 2] == dit[i - 2:i])
        trous = sum(max(0, ws[i]["start"] - ws[i - 1]["end"] - 0.45) for i in range(1, len(ws)))
        voix, snr = audio(p, a, ws[-1]["end"])
        net, lum = image(p, a, ws[-1]["end"])
        ligne.append(dict(prise=p, debut=a, fin=b, fidelite=round(fid, 2), repetitions=rep, trous=round(trous, 2),
                          voix_db=round(voix, 1), snr_db=round(snr, 1), nettete=round(net, 1), lumiere=round(lum, 1), dit=" ".join(dit)))
    # note : fidélité 50 %, fluidité 25 %, son 10 %, image 15 % (normalisés dans la phrase)
    def nz(v, inv=False):
        lo, hi = min(v), max(v)
        r = [(x - lo) / (hi - lo) if hi > lo else 1.0 for x in v]
        return [1 - x for x in r] if inv else r
    F = [c["fidelite"] for c in ligne]
    FL = nz([c["repetitions"] * 1.0 + c["trous"] for c in ligne], inv=True)
    SN = nz([c["snr_db"] for c in ligne]); NE = nz([c["nettete"] for c in ligne]); LU = nz([c["lumiere"] for c in ligne])
    for i, c in enumerate(ligne):
        c["note"] = round(100 * (0.5 * F[i] + 0.25 * FL[i] + 0.10 * SN[i] + 0.10 * NE[i] + 0.05 * LU[i]), 1)
    best = max(range(len(ligne)), key=lambda i: ligne[i]["note"])
    res.append(dict(phrase=texte, candidats=ligne, choix=best))
    print(f"\n{k + 1}. {texte}")
    for i, c in enumerate(ligne):
        print(f"  {'→' if i == best else ' '} {c['prise']} {c['debut']:7.2f}  note {c['note']:5.1f}  fid {c['fidelite']:.2f} rép {c['repetitions']} trous {c['trous']:.1f}s "
              f"snr {c['snr_db']:.0f} net {c['nettete']:.0f} lum {c['lumiere']:.0f} | {c['dit'][:90]}")
(ICI / "assets/montage/comparaison.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
