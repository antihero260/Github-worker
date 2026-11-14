"""Génère une voix française avec Chatterbox Multilingual (MIT) à partir d'une voix de référence.
Usage : python cloner.py <reference.wav> <texte.txt> <sortie.wav> [exaggeration] [cfg]
Le texte est découpé en phrases (le modèle est meilleur sur des morceaux courts). Les silences du début et de la fin de
chaque phrase sont retirés (avec une marge pour ne jamais couper un mot), puis les phrases sont recollées avec une pause
courte (PAUSE, 0,07 s par défaut : variable d'environnement PAUSE pour la changer)."""
import os, re, sys, time
import torch, torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

ref, src, out = sys.argv[1:4]
exa = float(sys.argv[4]) if len(sys.argv) > 4 else 0.6
cfg = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
torch.set_num_threads(4)
PAUSE = float(os.environ.get("PAUSE", "0.07"))


def rogne(w, sr, seuil_db=-42, avant=0.04, apres=0.07):
    """Retire le silence au début et à la fin d'une phrase, en gardant une marge."""
    a = w[0].abs()
    n = int(sr * 0.01)
    env = torch.nn.functional.max_pool1d(a[None, None], n, n)[0, 0]
    seuil = env.max() * (10 ** (seuil_db / 20))
    idx = torch.nonzero(env > seuil).flatten()
    if len(idx) == 0:
        return w
    d = max(0, int(idx[0]) * n - int(sr * avant))
    f = min(w.shape[-1], (int(idx[-1]) + 1) * n + int(sr * apres))
    return w[:, d:f]

t0 = time.time()
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
print(f"modèle chargé en {time.time() - t0:.0f} s", flush=True)
texte = open(src, encoding="utf-8").read().strip()
phrases = [p.strip() for p in re.split(r"(?<=[.!?…])\s+", texte) if p.strip()]
morceaux = []
for i, p in enumerate(phrases):
    t1 = time.time()
    torch.manual_seed(42 + i)
    w = m.generate(p, language_id="fr", audio_prompt_path=ref, exaggeration=exa, cfg_weight=cfg)
    w = rogne(w, m.sr)
    morceaux += [w, torch.zeros(1, int(m.sr * PAUSE))]
    print(f"{i + 1}/{len(phrases)} {w.shape[-1] / m.sr:.1f} s audio en {time.time() - t1:.0f} s", flush=True)
ta.save(out, torch.cat(morceaux, dim=-1), m.sr)
print("écrit", out, f"total {time.time() - t0:.0f} s")
