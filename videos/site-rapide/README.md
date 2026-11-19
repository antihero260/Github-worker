# « Ton site met 10 secondes à charger ? » : le film 16:9

Neuvième vidéo. Voix off fournie par l'utilisateur (44 s) ; `script.txt` est son texte exact. Demande : « surpasse-toi
encore, surtout dans le hook » et « améliore en laissant des traces » (compris comme des **traînées de mouvement** sur ce
qui va vite ; tout est aussi noté dans `SUIVI.md`).

Livrable : la version verticale, [`../site-rapide-vertical/`](../site-rapide-vertical/) : titre + ce film + les 4
solutions sous le film (Web Perf, React BP, 3 astuces, PageSpeed).

## Ce qui est nouveau

- Hook : le beau site LUMEN (vidéo 8)… qui se fige sur « mais » (scratch) et devient une page blanche qui charge : squelettes,
  roue, barre bloquée, **chronomètre 0,0 → 10,0 s** qui vire au rouge, visiteurs qui s'en vont, onglet fermé. Sur
  « Heureusement », drop de la musique, plongée en hyperespace, le site s'affiche en 0,8 s.
- **Traînées** : `course_trace()` (le personnage court suivi de copies de plus en plus transparentes) et `slam_trace()`
  (mot qui arrive avec une traînée d'ombres qui se résorbe).
- Les 2 skills vérifiés et filmés sur GitHub ; cascade de chargement, suggestions de corrections, scripts inutiles barrés,
  jauge de score façon Lighthouse ; les 3 astuces animées (poids qui fond, chargement différé, JavaScript allégé) ;
  PageSpeed Insights filmé.

## Refaire la vidéo

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py
python3 tools/simuler-mix.py /tmp/sim.wav
hyperframes lint && hyperframes check          # 0 erreur, puis regarder les images
hyperframes render ../site-rapide -o renders/site-rapide-16x9.mp4   # commande séparée
```
