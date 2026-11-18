#!/usr/bin/env python3
"""Refait le mixage audio de la vidéo à partir des pistes déclarées dans index.html (voix, musiques, bruitages),
avec la voix nettement devant (retour de l'utilisateur : « ma voix est trop en bas, on l'entend presque pas »).
Voix : plus énergique (demande du 18 nov.) : bas-médiums −2,5 dB, présence +4 dB vers 3,2 kHz, brillance +3 dB, compression 4:1 rapide, −15 LUFS ; musiques : ~8 dB sous la voix ; bruitages : baissés d'un tiers.
Puis remplace le son de la vidéo rendue (image copiée telle quelle) et masterise à −14 LUFS.
Usage : python3 tools/mixer.py renders/Les-3-niveaux-de-l-IA.mp4"""
import re, subprocess, sys, json
from pathlib import Path

ICI = Path(__file__).resolve().parent.parent
VIDEO = Path(sys.argv[1])
html = (ICI / "index.html").read_text()
pistes = []
for m in re.finditer(r'<audio id="([^"]+)" src="([^"]+)" data-start="([\d.]+)" data-duration="([\d.]+)" data-volume="([\d.]+)"', html):
    pistes.append({"id": m.group(1), "src": m.group(2), "debut": float(m.group(3)), "duree": float(m.group(4)), "vol": float(m.group(5))})
print(len(pistes), "pistes")

# voix plus forte et régulière
voix = ICI / "assets/voix-forte.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ICI / "assets/voix-montage.wav"), "-af",
                "highpass=f=90,equalizer=f=250:width_type=o:w=1.2:g=-2.5,equalizer=f=3200:width_type=o:w=1.3:g=4,treble=g=3:f=7500,acompressor=threshold=-26dB:ratio=4:attack=3:release=70:makeup=3,alimiter=limit=0.89:attack=2:release=40,loudnorm=I=-15:TP=-1.5:LRA=6",
                "-ar", "48000", str(voix)], check=True)
DUCK = json.loads((ICI / "assets/duck.json").read_text()) if (ICI / "assets/duck.json").exists() else []
GAIN = {"voix": 1.0, "musique": 1.55, "sfx": 0.65}   # musique : fichiers à −17 LUFS × 0,30 d'origine → ~ −24 LUFS une fois × 1,55
entrees, filtres, labels = [], [], []
for k, p in enumerate(pistes):
    src = voix if p["id"] == "voix" else ICI / p["src"]
    kind = "voix" if p["id"] == "voix" else ("musique" if p["id"].startswith("musique") else "sfx")
    vol = 1.0 if kind == "voix" else p["vol"] * GAIN[kind]
    entrees += ["-i", str(src)]
    d_ms = int(p["debut"] * 1000)
    duck = ""
    if kind == "musique" and DUCK:   # musique baissée sous certaines phrases (assets/duck.json, écrit par construire.py)
        expr = "*".join(f"(1-{1 - g:.3f}*min(1,max(0,(t-{a0 - p['debut'] - 0.25:.3f})/0.25))*min(1,max(0,({a1 - p['debut']:.3f}-t)/0.25)))" for a0, a1, g in DUCK)
        duck = f",volume='{expr}':eval=frame"
    filtres.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{p['duree']:.3f},asetpts=PTS-STARTPTS,volume={vol:.3f}{duck},adelay={d_ms}|{d_ms}[a{k}]")
    labels.append(f"[a{k}]")
fc = ";".join(filtres) + ";" + "".join(labels) + f"amix=inputs={len(labels)}:normalize=0:dropout_transition=0[m]"
(ICI / "assets/mix-filtre.txt").write_text(fc)
mix = ICI / "assets/mix.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y"] + entrees + ["-filter_complex_script", str(ICI / "assets/mix-filtre.txt"), "-map", "[m]",
                "-ar", "48000", str(mix)], check=True)
# mastering −14 LUFS en deux passes, puis on remplace le son de la vidéo
r = subprocess.run(["ffmpeg", "-nostdin", "-i", str(mix), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
d = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:"
      f"measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true")
sortie = VIDEO.with_name(VIDEO.stem + "-voix-forte.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(VIDEO), "-i", str(mix), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", af,
                "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(sortie)], check=True)
print("→", sortie)
