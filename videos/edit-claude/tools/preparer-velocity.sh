#!/bin/bash
# Prépare les plans « velocity » de l'edit façon anime (à lancer depuis le dossier du projet).
# vel-<nom>.mp4 : 0,4 s en accéléré (×4) puis 1,2 s au ralenti fondu (×0,25)  →  la claque puis le ralenti.
# rap-<nom>.mp4 : le plan en accéléré ×2 (3 s) pour les coupes rapides du drop.
set -e
cd "$(dirname "$0")/.."
for n in "$@"; do
  s="assets/video/$n.mp4"; [ -f "$s" ] || s="assets/captures/$n.mp4"
  ffmpeg -nostdin -v error -y -i "$s" -filter_complex \
    "[0:v]fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,split[a][b];[a]trim=0.5:2.1,setpts=(PTS-STARTPTS)/4[f];[b]trim=2.1:2.4,setpts=(PTS-STARTPTS)*4,minterpolate=fps=30:mi_mode=blend[l];[f][l]concat=n=2:v=1:a=0[v]" \
    -map "[v]" -an -c:v libx264 -crf 22 -preset veryfast -pix_fmt yuv420p "assets/vel/vel-$n.mp4"
  ffmpeg -nostdin -v error -y -i "$s" -vf "fps=30,setpts=PTS/2,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" -t 3 -an -c:v libx264 -crf 22 -preset veryfast -pix_fmt yuv420p "assets/vel/rap-$n.mp4"
done
