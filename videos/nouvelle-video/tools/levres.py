#!/usr/bin/env python3
"""Repère le contour exact des lèvres image par image (MediaPipe Face Landmarker, 478 points du visage) sur la personne
détourée (assets/perso.webm). Modèle : assets/modeles/face_landmarker.task (téléchargé depuis storage.googleapis.com/mediapipe-models).
Sortie : assets/levres.json {"ext": [[x,y]×20 par image], "int": [[x,y]×20]} en pixels 1080×1920 (null si visage non trouvé).
Sert à tools/bouche.py (retouche lèvres et dents)."""
import json, subprocess
from pathlib import Path
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

ICI = Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30
EXT = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185]
INT = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 415, 310, 311, 312, 13, 82, 81, 80, 191]
det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=str(ICI / "assets/modeles/face_landmarker.task")),
    running_mode=vision.RunningMode.VIDEO, num_faces=1, min_face_detection_confidence=0.3, min_tracking_confidence=0.3))
p = subprocess.Popen(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", str(ICI / "assets/perso.webm"),
                      "-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)
ext, inn, k = [], [], 0
while True:
    b = p.stdout.read(W * H * 4)
    if len(b) < W * H * 4:
        break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 4)
    a = f[..., 3:4].astype(np.float32) / 255
    rgb = (f[..., :3] * a + 128 * (1 - a)).astype(np.uint8)
    r = det.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)), int(k * 1000 / FPS))
    if r.face_landmarks:
        L = r.face_landmarks[0]
        ext.append([[L[i].x * W, L[i].y * H] for i in EXT]); inn.append([[L[i].x * W, L[i].y * H] for i in INT])
    else:
        ext.append(None); inn.append(None)
    k += 1
    if k % 300 == 0:
        print(k, "images", flush=True)
p.wait()
manque = sum(e is None for e in ext)
print("terminé :", k, "images,", manque, "sans visage")
(ICI / "assets/levres.json").write_text(json.dumps({"ext": ext, "int": inn}))
