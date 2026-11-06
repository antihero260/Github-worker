# « Je parle, le site se construit » : le film 16:9

Seizième vidéo (29,3 s). Demande : « fais quelque chose que personne n'a fait dans ce domaine ». Idée : **toute la voix est le
prompt** ; chaque phrase dite à voix haute modifie le site à l'instant où elle est prononcée.

- `site-lecodeur/index.html` : le vrai site de la chaîne Lecodeur (fond noir, titre énorme, sous-titre, vidéo en fond,
  3 cartes avec de vraies images des vidéos 13, 14 et 15, bouton jaune, animations au défilement, adapté au téléphone).
  Avec `#construction`, il part d'une page blanche et `window.etape(...)` applique chaque instruction.
- `PHRASES.txt` : les phrases à envoyer aux gens qui commentent « VOIX ».
- Scènes : hook « 0 ligne de code » → « Je parle. » + micro « À l'écoute… » + onde qui suit la **vraie** voix (niveau calculé
  sur `voix.wav`) ; la vraie prise du navigateur, calée sur la voix, avec « Tu dis : … » à gauche, la caméra qui suit le titre,
  le texte, les cartes et le bouton, puis le téléphone ; « Voilà », « Site complet », « Commente VOIX ».
- Sous le film (vertical) : 8 cases verrouillées (Fond, Titre, Texte, Vidéo, Cartes, Bouton, Anim., Mobile) dévoilées une
  par une. Miniature : `miniature/miniature-je-parle-le-site-se-construit.jpg`.
- Musiques orchestrales à cordes (demande « type violon »), voir `assets/music/SOURCES-mixkit.md`.

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py
hyperframes check
hyperframes render ../site-voix -o renders/site-voix-16x9.mp4   # commande séparée
```
