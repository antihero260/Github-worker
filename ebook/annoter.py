#!/usr/bin/env python3
"""Entoure en rouge les boutons à cliquer sur les captures et ajoute une pastille numérotée (ebook)."""
from PIL import Image, ImageDraw, ImageFont

ROUGE = (232, 17, 45)
POLICE = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)


def annote(src, dst, cercles, crop=None, echelle=1.0):
    im = Image.open(src).convert("RGB")
    d = ImageDraw.Draw(im)
    for (x, y, w, h, n) in cercles:
        px, py = min(40, max(14, w * 0.12)), min(26, max(12, h * 0.4))
        d.ellipse([x - px, y - py, x + w + px, y + h + py], outline=ROUGE, width=7)
        if n:
            cx, cy = min(im.width - 30, x + w + px - 4), max(30, y - py + 4)
            d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=ROUGE, outline=(255, 255, 255), width=3)
            d.text((cx, cy), str(n), font=POLICE, fill=(255, 255, 255), anchor="mm")
    if crop:
        im = im.crop(crop)
    if echelle != 1.0:
        im = im.resize((round(im.width * echelle), round(im.height * echelle)), Image.LANCZOS)
    im.save(dst, quality=92)


B = "captures-brutes/"
annote(B + "claude-code.png", "images/claude-code.jpg", [(1234, 24, 142, 36, 1), (425, 770, 90, 85, 3), (64, 518, 420, 40, 2)])
annote(B + "ghdoc-repo-create-global-nav-update.png", "images/github-nouveau-depot.jpg", [(300, 20, 100, 52, 1), (44, 108, 258, 52, 2)])
annote(B + "ghdoc-create-repository-name.png", "images/github-nom-depot.jpg", [(362, 150, 1140, 70, 3)])
annote(B + "elevenlabs-tts.png", "images/elevenlabs.jpg", [(752, 160, 560, 80, 2), (164, 366, 246, 38, 1)])
annote(B + "mixkit-musique.png", "images/mixkit-musique.jpg", [(408, 552, 34, 34, 2), (394, 462, 52, 52, 1)], crop=(0, 0, 1440, 640))
annote(B + "mixkit-sons.png", "images/mixkit-sons.jpg", [(1440 - 1440 + 418, 548, 34, 34, 1)], crop=(0, 0, 1440, 640))
annote(B + "tiktok-upload.png", "images/tiktok.jpg", [(560, 425, 325, 52, 1)], crop=(380, 140, 1060, 720))
print("ok")
