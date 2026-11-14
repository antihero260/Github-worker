# « Ce site ? Un seul prompt » : le film 16:9

Quinzième vidéo (26,2 s). Premier sujet de la nouvelle stratégie d'engagement : montrer un **vrai** site fait avec **un seul
prompt**, puis finir par « Commente PROMPT ».

- `PROMPT.txt` : le prompt exact, à envoyer aux gens qui commentent « PROMPT ».
- `site-cafe/index.html` : le site **réellement généré** à partir de ce prompt (Café Aurore), sans retouche à la main ensuite.
  Il a été filmé avec Playwright (ordinateur 1280×720 et iPhone 13) : `assets/video/cafe-*.mp4`.
- Scènes : le vrai site net dès la 1ʳᵉ image + « 1 seul prompt / 0 ligne de code » ; le prompt collé dans l'IA, le code qui
  s'écrit, le site qui sort ; les vraies prises (accueil, animations, sections, formulaire, téléphone) au rythme de la voix ;
  « le secret c'est le prompt » (ChatGPT, Claude, Gemini grisés) et chaque partie du prompt allumée avec ce qu'elle produit ;
  la fin « Commente PROMPT » avec des commentaires qui arrivent.
- Sous le film (vertical) : « Ce que dit le prompt », 4 cases verrouillées dévoilées une par une.
- 130 bruitages, 3 musiques hip-hop Mixkit populaires jamais utilisées (voir `assets/music/SOURCES-mixkit.md`).

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py
hyperframes check
hyperframes render ../site-un-prompt -o renders/site-un-prompt-16x9.mp4   # commande séparée
```
