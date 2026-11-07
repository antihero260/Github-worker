# Edit rythmé « POV : l'IA a codé mon site » (vidéo 18)

Premier **edit sans voix off** de la chaîne : tout le montage est calé image par image sur les temps d'une phonk.
15,6 s, en boucle (la dernière image retombe sur la première).

- Musique : « Phonk Remix » de HoliznaCC0 (CC0, aucun crédit), extrait 5,270 → 20,876 s = 24 temps à 92,3 BPM
  (`assets/music/`, `tools/temps.json` : temps et kicks repérés avec librosa). Les autres extraits proposés : `choix-musique/`.
- Temps 0 à 7 (intro) : une vraie vidéo par temps (puis demi-temps, puis quart de temps), un mot qui claque :
  « PAS DE CODE. / PAS DE DEV. / PAS D'AGENCE. / JUSTE… / 1 PROMPT. ».
- Temps 8 (drop) : flash, glitch, secousse, le navigateur s'écrase ; le site VOLT (vidéo 17) s'assemble **un bloc par temps**
  (menu, titre, photo, bouton, produits, panier, version mobile), la caméra suit chaque bloc ; « Site complet ✓ ».
- Temps 19 à 24 : un café, une chaîne, la boutique ; « FAIT PAR L'IA. » ; « COMMENTE SITE ».
- Coups de zoom sur chaque temps, petites secousses sur les kicks, personnage qui bat la mesure ; 69 bruitages.
- Version verticale (`../edit-site-vertical`) : 6 cases « ? » qui se dévoilent sur les temps où chaque bloc arrive.

```bash
python3 tools/construire-edit.py && python3 tools/vertical.py
hyperframes check
hyperframes render . -o renders/edit-site-16x9.mp4   # commande séparée
```
