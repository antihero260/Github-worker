# Edit rythmé « POV : tu crées des sites avec l'IA » (vidéo 18)

Premier **edit** de la chaîne : aucune voix, **aucun texte** (demande de l'utilisateur, pour cette vidéo seulement),
tout est calé image par image sur le son de la vidéo de référence qu'il a envoyée. **30,3 s**, en boucle.

- Son : extrait 25,130 → 55,438 s de la vidéo de référence (48 temps ≈ 94,8 BPM : drop au temps 8, trou des basses au
  temps 39, 2ᵉ drop au temps 40) ; `tools/temps.json` (temps et kicks repérés avec librosa). Voir `assets/music/SOURCES.md`.
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

v4 (« plus de sites, beaucoup plus de vidéos, 30 secondes ») : **100 plans**, 76 vidéos différentes dont **30 vrais sites**
(23 grands sites filmés en direct avec Playwright : Apple, Stripe, Vercel, Figma, Notion, Webflow, Nike, Spline, Bolt, v0,
Cursor, Raycast, Locomotive, Cuberto, Midjourney, Shopify, Duolingo, Wix, Squarespace, Bruno Simon… + Framer, Spline AI,
café, VOLT) et 19 nouvelles vidéos Mixkit (skate, feux d'artifice, boxe, basket, foot, hologrammes, danse). Le montage est
construit automatiquement sur les temps : un plan en mouvement sur chaque temps, un site sur chaque demi-temps, une rafale
de 4 plans à la fin de chaque phrase de 8 temps, deux drops.

v5 (« seulement le 1 est intéressant, une edit de malade, encore plus de vidéos, une montée en tension ») : musique libre
« Phonk Drift Racing Montage » d'Alex Morgan (CC BY 4.0), 34,5 s. **146 plans, 110 vidéos différentes dont 30 sites** (38 nouvelles
vidéos Mixkit : rally, drift, karting, motos, voitures, foules en concert, éclairs, fumée, explosions, boxe, snowboard).
**Montée en tension** sur 10 s : image sombre et désaturée qui reprend ses couleurs, un plan tous les 2 temps → chaque temps →
demi-temps → quart de temps, caméra qui avance, secousses et flashs de plus en plus forts, cœur qui bat, roulement, riser,
noir, DROP. Coupure des basses au milieu avec une 2ᵉ petite montée, 2ᵉ drop avec un plan par demi-temps.

v6 (« prends le 5… montée en tension constante, pas de vidéo cuisine, cinématique, beaucoup plus de vidéos et de sites, calé
sur chaque image, des effets dignes de Premiere Pro ») : « Montagem Rugada » (cape, son TikTok non libre), 29,7 s.
108 plans + 3 écrans partagés, 95 vidéos différentes dont 38 vrais sites. Effets : étalonnage cinéma (froid et désaturé
pendant la montée → bleu-orange chaud au drop), bandes cinémascope qui se resserrent jusqu'à une fente puis s'ouvrent au drop,
grain de film, vignette, vraies fuites de lumière, aberration chromatique RGB (filtre SVG), zoom traversant, rotation, filé,
stutter, écran partagé en 3, vrais ralentis avec accélération, stroboscope, flashs, inversion, glitch, secousses sur les kicks.

v7 / vidéo 19 (« le 12, toujours plus de travail et d'expertise », + extraits de films) : « AVANGARD (Slowed) » de LONOWN,
29,8 s. 94 plans + 1 écran partagé, 93 vidéos différentes dont 35 sites, **extraits de films libres** (Tears of Steel, Sintel
– Blender Foundation, CC BY) et **vidéos NASA** (domaine public). Nouveaux effets : fondus enchaînés (intro et outro),
arrêts sur image sur les attaques et le triple kick, traînées de mouvement (echo), effet miroir, ouverture en iris,
bascule 3D, flou de zoom radial au drop, micro-éclairs sur les caisses claires, outro couleur pellicule.
Crédit obligatoire en description : « Tears of Steel, Sintel (CC) Blender Foundation ».
