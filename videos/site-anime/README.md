# « Un site qui a l’air de coûter des milliers d’euros » : le film 16:9

Huitième vidéo. Voix off fournie par l'utilisateur (34 s) ; `script.txt` est son texte exact. Demande : « là encore tu
dois te surpasser, surtout sur le hook ».

Livrable : la version verticale, [`../site-anime-vertical/`](../site-anime-vertical/) : titre + ce film dans le bandeau
+ les 4 effets (défilement, parallaxe, transitions, survol) sous le film, qui s'allument quand on les montre.

## Ce qui est nouveau

- **Un vrai faux site premium, « LUMEN », construit en HTML/GSAP dans les scènes** (net en 1080p, calé sur la voix) :
  titre dont les lettres montent, halos de couleur, menu, bouton avec reflet, cartes flottantes ; section qui défile
  avec cartes et compteurs ; **parallaxe** sur 5 plans de montagnes + lune + étoiles ; **transitions** (cercle qui
  s'ouvre, volet qui monte) ; **survol** (cartes qui pivotent en 3D sous le pointeur, lumière qui suit, boutons
  aimantés) ; et un contre-exemple « tout bouge dans tous les sens ».
- **Hook** : 5 coupes en 2,2 s, une par groupe de mots, chacune sur une animation différente du site (flash + rush),
  recul qui révèle le navigateur sur « ce site », puis compteur de prix 0 → 15 000 € sur des billets qui tombent.
- Style « Projecteur » (vert-jaune) + les effets dynamiques de la vidéo 7 (volets rayés, glitch, secousses).
- Vraies pages de Claude Code et Cursor filmées, logos officiels.

## Refaire la vidéo

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py
python3 tools/simuler-mix.py /tmp/sim.wav
hyperframes lint && hyperframes check          # 0 erreur, puis regarder les images
hyperframes render ../site-anime -o renders/site-anime-16x9.mp4   # commande séparée
```
