# Edit rythmé « POV : tu crées des sites avec l'IA » (vidéo 18)

Premier **edit** de la chaîne : aucune voix, **aucun texte** (demande de l'utilisateur, pour cette vidéo seulement),
tout est calé image par image sur le son de la vidéo de référence qu'il a envoyée. 15,2 s, en boucle.

- Son : extrait 25,130 → 40,281 s de la vidéo de référence (8 temps avant le drop des basses à 30,174 s + 16 après,
  ≈ 94,8 BPM) ; `tools/temps.json` (temps et kicks repérés avec librosa). Voir `assets/music/SOURCES.md`.
- v3 (après « tu vas juste présenter un site de chaussures ? C'est un edit ») : **48 plans** très courts pleins de mouvement
  (danse, breakdance, robots, moto, vitesse, VR, hologrammes, tunnels, néons, code) coupés sur les temps, rafales de coupes
  au quart de temps avant et après le drop, vrais sites (Spline, Framer, café, VOLT) seulement en flashs.
- Effets sur le rythme : coup de zoom sur chaque temps, flash blanc puis inversion des couleurs et glitch au drop, flash
  coloré tous les 2 temps, inversion tous les 4, flou de fouet sur les demi-temps, secousses sur les kicks ; la fin
  retombe sur le plan du début (boucle).
- Version verticale (`../edit-site-vertical`) : titre seul au-dessus du film (« POV : tu crées des sites avec l'IA »).

```bash
python3 tools/construire-edit.py && python3 tools/vertical.py
hyperframes check
hyperframes render . -o renders/edit-site-16x9.mp4   # commande séparée
```
