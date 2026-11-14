# « Ce site ressemble à un jeu vidéo » : le film 16:9

Onzième vidéo (70 s). Voix off et texte fournis par l'utilisateur. Demande : « en plus d'un excellent hook, pour empêcher
les gens de partir il faut aussi les choquer visuellement avec beaucoup de vidéos tout au long de la vidéo ».

Livrable : la version verticale, [`../site-3d-vertical/`](../site-3d-vertical/) : titre + ce film + les 4 étapes sous le film.

## Ce qui est nouveau

- **Une rafale de vraies vidéos derrière CHAQUE scène** (`fond()` → `rafale_mots()`), une nouvelle tous les 1–2 mots,
  avec un voile sombre et les éléments par-dessus : environ 90 plans pour 70 s (≈ 60 vidéos Mixkit différentes, 10 photos
  Unsplash, 3 vraies pages filmées).
- Vraies pages filmées : framer.com/ai, spline.design et spline.design/ai (la galerie d'objets 3D générés par l'IA).
- Logos : Framer (theSVG), Spline (icône officielle du site).

## Refaire la vidéo

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py
python3 tools/simuler-mix.py /tmp/sim.wav
hyperframes lint && hyperframes check          # 0 erreur, puis regarder les images
hyperframes render ../site-3d -o renders/site-3d-16x9.mp4   # commande séparée
```
