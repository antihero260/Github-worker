# Voix clonée (gratuite, sans ElevenLabs)

Voix de l'utilisateur (c'est **sa propre voix**, confirmé le 8 novembre 2026), clonée avec **Chatterbox Multilingual**
(Resemble AI, licence **MIT**, usage commercial autorisé). Les sorties portent le filigrane inaudible « Perth » de Resemble AI.

- `reference-voix.wav` : 12,6 s de référence (extrait propre de sa narration, 24 kHz mono, −18 LUFS).
- `cloner.py` : texte → voix (découpe en phrases, silences de début et de fin de phrase retirés avec une marge, pause de 0,07 s entre les phrases ; `PAUSE=0.15` pour une pause plus longue).
- `essais/` : essai 1 (réglage naturel : exaggeration 0,6, cfg 0,5) et essai 2 (plus énergique : 0,85 / 0,35), plus l'extrait original.

## Installation (machine remise à zéro à chaque session, ~5 min, ~1,5 Go)
```bash
V=/tmp/tts-venv; export UV_NO_CACHE=1
uv venv -q -p 3.11 $V
VIRTUAL_ENV=$V uv pip install -q --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple \
  --index-strategy unsafe-best-match torch==2.6.0 torchaudio==2.6.0 chatterbox-tts "setuptools<81"
$V/bin/python voix-clone/cloner.py voix-clone/reference-voix.wav script.txt voix.wav 0.6 0.5
ffmpeg -i voix.wav -af "highpass=f=70,loudnorm=I=-16:TP=-1.5" -ar 44100 -b:a 192k voix.mp3
```
- Python 3.13 ne marche pas (torch 2.6 absent) : utiliser 3.11. Sans `setuptools<81`, le filigrane plante (`pkg_resources`).
- Vitesse sur le processeur (4 cœurs, sans carte graphique) : ~5× le temps réel (20 s de voix ≈ 1 min 45).
- Toujours vérifier la voix générée avec whisper avant le montage (mots oubliés ou répétés).
- Demande de l’utilisateur (8 nov.) : **enlever les silences**. Un `silenceremove` global coupait des mots (« Et », début de « Ton ») : on rogne donc phrase par phrase dans `cloner.py`.
