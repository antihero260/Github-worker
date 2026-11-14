# Modèle HyperFrames — style « Projecteur » : la version verticale

Version TikTok / Shorts / Reels (1080×1920) du film 16:9, comme dans les références : fond noir,
**titre-promesse** blanc en haut, film dans un bandeau 1080×608 centré (de 656 à 1264 px).
Valeurs : [`../frame.md`](../frame.md) (`hook-title`, `band-top`, `hook-bottom`).

## Faire la version verticale d'une vidéo

1. Rendre le film dans [`../modele/`](../modele/README.md) : `hyperframes render -o renders/film-16x9.mp4`.
2. Le copier ici : `assets/film-16x9.mp4` (ce fichier n'est pas versionné).
3. Écrire le titre : variable `titre` (panneau Variables du Studio) ou texte de `#titre` dans `index.html`.
   1 à 3 lignes ; le bas du titre reste à 581 px, un titre plus long monte.
4. Ajuster `data-duration` (racine, fond, titre, vidéo) à la durée du film.
5. Contrôler et rendre :
   ```bash
   hyperframes check
   hyperframes render -o renders/vertical-9x16.mp4
   ```

Si tu préfères ajouter le titre directement dans TikTok, publie le film 16:9 tel quel : TikTok le place
de lui-même au centre de l'écran, et le titre se pose au-dessus avec l'outil texte de l'application.

## Résultat du test

- `hyperframes check` : réussi, 0 erreur, 0 avertissement.
- Rendu : 1080×1920, 30 i/s, 16 s, ~11 Mo. Comparé à une référence, le titre, le bandeau, les croix et les
  sous-titres tombent aux mêmes positions.
- Le titre utilise Inter 600 : c'est la police la plus proche de celle des références (texte de TikTok), pas l'originale.
