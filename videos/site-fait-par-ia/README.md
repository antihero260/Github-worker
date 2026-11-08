# « Ce site cache un mot secret » : le film 16:9

Dix-septième vidéo (24,6 s). Nouveau type d'appel à l'action : **un jeu**. Un vrai site e-commerce (VOLT, sneakers) généré
avec un seul prompt cache le mot **NÉON** pendant une demi-seconde ; le premier qui l'écrit en commentaire reçoit le prompt
complet (`PROMPT.txt`). But : faire revoir la vidéo (rétention) et faire commenter (engagement).

- `site-volt/index.html` : le site (menu, titre animé, 4 produits, panier latéral, bandeau promo, adapté au téléphone).
  Au survol du bouton de la VOLT Pastel, « Ajouter » devient « NÉON » en rose néon pendant 500 ms.
  `#tournage` ajoute le voile noir de calage (`window.top_depart()`) et un pointeur visible.
- Scènes : hook (rafale, site < 1 minute, nuit + flou sur « cache », « Un mot secret », 4 cases « ? ») → visite filmée avec la
  caméra qui suit le menu, les produits et le panier (NÉON passe à 8,45–8,85 s) → rembobinage (bande de vignettes, tête de
  lecture, « ? ? ? ? » flou, « 0,5 s ») → « 1er gagne le prompt », faux commentaires barrés, carte « Le prompt complet »,
  « Indice » avec la loupe sur les boutons → « Abonne-toi à Gausscode », « Prochain défi ».
- Sous le film (vertical) : 4 cases « ? » (« Le mot secret · 4 lettres ») qui ne se dévoilent jamais : la réponse reste
  dans les commentaires.
- Miniature : `miniature/miniature-ce-site-cache-un-mot-secret.jpg`.
- Musiques : trap Mixkit (Arulo), voir `assets/music/SOURCES-mixkit.md`.

**Après la publication** : répondre au premier commentaire « NÉON » avec le prompt (`PROMPT.txt`) et épingler cette réponse.

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py
hyperframes check
hyperframes render ../site-mot-secret -o renders/site-mot-secret-16x9.mp4   # commande séparée
```
