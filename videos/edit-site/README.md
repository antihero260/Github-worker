# Edit rythmé « POV : l'IA a codé mon site » (vidéo 18)

Premier **edit sans voix off** de la chaîne : tout le montage est calé image par image sur les temps d'une phonk.
15,2 s, en boucle (la dernière image retombe sur la première).

- Musique (v2) : le son de la vidéo de référence de l'utilisateur, extrait 25,130 → 40,281 s (drop à 30,174 s), voir `assets/music/SOURCES.md`.
  `tools/temps.json` : temps et kicks repérés avec librosa.
- **Aucun texte** dans le film (demande de l'utilisateur, pour cette vidéo seulement).
- Temps 0 à 7 (intro) : une vraie vidéo par temps (puis demi-temps, puis quart de temps), la caméra fonce vers le drop.
- Temps 8 (drop) : flash, glitch, secousse, le navigateur s'écrase ; le site VOLT (vidéo 17) s'assemble **un bloc par temps**
  (menu, titre, photo, bouton, produits, panier, version mobile), la caméra suit chaque bloc ; confettis.
- Temps 19 à 24 : un café, une chaîne, la boutique ; la caméra tourne autour du site, flashs, la boucle repart.
- Coups de zoom sur chaque temps, petites secousses sur les kicks, personnage qui bat la mesure ; 69 bruitages.
- Version verticale (`../edit-site-vertical`) : titre seul au-dessus du film, sans cases (choix de l'utilisateur).

```bash
python3 tools/construire-edit.py && python3 tools/vertical.py
hyperframes check
hyperframes render . -o renders/edit-site-16x9.mp4   # commande séparée
```
