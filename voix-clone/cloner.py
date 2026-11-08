"""Génère une voix française avec Chatterbox Multilingual (MIT) à partir d'une voix de référence.
Usage : python cloner.py <reference.wav> <texte.txt> <sortie.wav> [exaggeration] [cfg]
Le texte est découpé en phrases (le modèle est meilleur sur des morceaux courts), puis recollé avec de petits silences."""
import re, sys, time
import torch, torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

ref, src, out = sys.argv[1:4]
exa = float(sys.argv[4]) if len(sys.argv) > 4 else 0.6
cfg = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
torch.set_num_threads(4)
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
    morceaux += [w, torch.zeros(1, int(m.sr * 0.18))]
    print(f"{i + 1}/{len(phrases)} {w.shape[-1] / m.sr:.1f} s audio en {time.time() - t1:.0f} s", flush=True)
ta.save(out, torch.cat(morceaux, dim=-1), m.sr)
print("écrit", out, f"total {time.time() - t0:.0f} s")
