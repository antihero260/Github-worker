#!/usr/bin/env python3
"""Vidéo de base « studio » : la personne (assets/montage/parole-net.mp4 + détourage assets/montage/personne.webm),
éclairée et étalonnée par tools/studio.py, posée sur un fond de studio uni et sombre qui change à chaque passage
(fondu de 0,4 s). Sortie : assets/montage/studio.mp4 (opaque, 30 i/s), découpé en 4 morceaux traités en parallèle.
Les passages sont lus dans assets/montage/passages.json ([[début, nom_du_fond], …]), écrit par tools/construire3.py."""
import json, subprocess, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np

ICI = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ICI / "tools"))
import studio  # noqa: E402

H, W, FPS = 1920, 1080, 30
SRC, ALPHA, OUT = ICI / "assets/montage/parole-net.mp4", ICI / "assets/montage/personne.webm", ICI / "assets/montage"
PASSAGES = json.loads((OUT / "passages.json").read_text())
DUREE = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(SRC)], capture_output=True, text=True).stdout)
N = int(round(DUREE * FPS))


def fond_a(t, cache):
    def get(k):
        if k not in cache:
            cache[k] = studio.fond_studio(PASSAGES[k][1], k)
        return cache[k]
    k = max(i for i, p in enumerate(PASSAGES) if p[0] <= t + 1e-6)
    f = get(k)
    if k + 1 < len(PASSAGES) and t > PASSAGES[k + 1][0] - 0.2:  # fondu vers le fond suivant
        m = (t - (PASSAGES[k + 1][0] - 0.2)) / 0.4
        return f * (1 - m) + get(k + 1) * m
    if k > 0 and t < PASSAGES[k][0] + 0.2:
        m = 0.5 + (t - PASSAGES[k][0]) / 0.4
        return get(k - 1) * (1 - m) + f * m
    return f


def morceau(args):
    q, i0, i1 = args
    t0 = i0 / FPS
    lire = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t0:.4f}", "-i", str(SRC), "-frames:v", str(i1 - i0), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                            stdout=subprocess.PIPE)
    lire_a = subprocess.Popen(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-ss", f"{t0:.4f}", "-i", str(ALPHA), "-frames:v", str(i1 - i0),
                               "-vf", "alphaextract", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    sortie = OUT / f".tmp-studio-{q}.mp4"
    ecrire = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                               "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", str(sortie)], stdin=subprocess.PIPE)
    cache, prec = {}, None
    for i in range(i0, i1):
        b = lire.stdout.read(W * H * 3)
        ba = lire_a.stdout.read(W * H)
        if len(b) < W * H * 3:
            break
        rgb = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        al = np.frombuffer(ba, np.uint8).reshape(H, W) if len(ba) == W * H else np.zeros((H, W), np.uint8)
        out, prec = studio.composer(rgb, al, fond_a(i / FPS, cache), prec)
        ecrire.stdin.write((out * 255 + 0.5).astype(np.uint8).tobytes())
        if (i - i0) % 100 == 0:
            print(f"morceau {q} : image {i - i0}/{i1 - i0}", flush=True)
    ecrire.stdin.close(); ecrire.wait(); lire.kill(); lire_a.kill()
    return sortie


if __name__ == "__main__":
    bornes = np.linspace(0, N, 5).astype(int)
    with Pool(4) as p:
        parts = p.map(morceau, [(q, bornes[q], bornes[q + 1]) for q in range(4)])
    (OUT / ".tmp-liste.txt").write_text("".join(f"file '{x.name}'\n" for x in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(OUT / ".tmp-liste.txt"), "-c", "copy", str(OUT / "studio.mp4")], check=True)
    for x in parts:
        x.unlink()
    print("studio.mp4 :", N, "images")
