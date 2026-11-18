#!/usr/bin/env bash
# v12 : coupe les 2,64 premières secondes du rendu (« Certains d'entre vous m'ont contacté pour me demander »),
# la vidéo commence sur « comment je faisais mes vidéos avec l'IA » ; puis mastering −14 LUFS (deux passes), 1080×1920.
# Usage : tools/finaliser.sh renders/v12-brut.mp4 renders/Comment-je-cree-mes-videos-avec-l-IA-v12-1080p.mp4
set -euo pipefail
ENTREE="$1"; SORTIE="$2"; S=2.64
MES=$(ffmpeg -hide_banner -ss "$S" -i "$ENTREE" -vn -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
v() { echo "$MES" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -hide_banner -v error -y -ss "$S" -i "$ENTREE" \
  -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=$(v input_i):measured_TP=$(v input_tp):measured_LRA=$(v input_lra):measured_thresh=$(v input_thresh):offset=$(v target_offset):linear=true,aresample=48000" \
  -c:v libx264 -preset slow -crf 15 -profile:v high -pix_fmt yuv420p -r 30 -movflags +faststart -c:a aac -b:a 256k "$SORTIE"
