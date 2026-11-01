# Faire une vidéo dans le style « Projecteur »

Marche à suivre complète, de la voix off au fichier livré. Exemple réel : [`../videos/examen-demain/`](../videos/examen-demain/README.md).

## 1. Entrées

- Le **script** (texte exact lu par la voix) → `script.txt`.
- La **voix off** (fournie par l'utilisateur, ex. ElevenLabs) → `assets/audio/voix.mp3`, normalisée à −15 LUFS :
  `ffmpeg -i voix.mp3 -af loudnorm=I=-15:TP=-1.5:LRA=9 voix.wav` puis encodage MP3.
- Le **titre** de la version verticale : court et simple, validé par l'utilisateur.

## 2. Mots et temps

```bash
hyperframes transcribe voix.wav --json            # temps de chaque mot (fautes possibles dans le texte)
python3 tools/sous-titres.py assets/transcript-brut.json --script script.txt --fin <durée-0,4> --mots assets/mots.json
```

`sous-titres.py` aligne l'orthographe exacte du script sur les temps de la transcription et écrit les sous-titres
mot à mot. `assets/mots.json` sert ensuite à caler chaque animation sur son mot.

## 3. Scènes

- Une scène par idée (6 à 16 s), un **changement visuel toutes les ~2 s**.
- Écrire `tools/construire-scenes.py` avec la bibliothèque [`outils/projecteur.py`](outils/projecteur.py)
  (exemple complet : `videos/ia-te-donne-raison/tools/construire-scenes.py`). Elle contient :
  - `perso(id, x, pieds, taille, "toi" | "ia")` : **pictogrammes articulés** (tête, tronc, bras, jambes) ;
  - les gestes `vit` (rebond continu, à mettre partout), `parle`, `acquiesce`, `marche`, `court`, `chute`, `remonte`,
    `pose`, `tape`, `non`, `saut`, `victoire`, `pouce`, `bras_croises`, `grossit`, `panique`, `gratte`, `haussement`,
    `vertiges`, `dort` ; et `bulle`, `tampon`, `confettis` ;
  - `s.recadre(...)` : gros plan filé sur un détail, puis retour au plan large.
- **Le personnage doit jouer chaque phrase** : il marche vers ce dont on parle, pointe, réagit (tête, bras, saut).
  Jamais figé : `vit` sur toute la scène, un geste à chaque groupe de mots, et un deuxième personnage (l'IA) qui
  répond quand le sujet s'y prête.
- Identifiants : préfixés par la scène, et **jamais égaux à l'identifiant de la scène elle-même**.
- Ne pas utiliser de caractère absent d'Anton (ex. « ≠ ») : le dessiner.

## 4. Son

- **3 musiques, une par partie** (catalogue HeyGen : `hyperframes media-use resolve --type bgm --intent "..."`),
  choisies d'après leur description et leur courbe d'énergie, coupées et bouclées sur des mesures entières.
- **Niveaux** : voix −15/−16 LUFS ; musiques **−18 à −19 LUFS** (3–4 dB dessous, limiteur à −4 dB en fin de chaîne) ; puis carve sur chaque musique :
  `node <skill media-use>/audio/scripts/carve.mjs --comp index.html --bed musique-N --strength 0.5 --core <core>`.
- **Bruitages** (volume 0,2–0,4) : souffle à chaque transition, impact grave sur les mots-chocs, montée avant un
  mot-choc, clavier pendant un texte tapé, clic par case cochée, pop par apparition, son « barré », ping sur les chiffres.
- Simuler le mixage avec ffmpeg avant le rendu : crête sous −1 dBFS, total autour de −15 LUFS.

## 5. Contrôle AVANT tout rendu

1. `hyperframes lint` puis `hyperframes check` : **0 erreur**. Corriger chaque chevauchement signalé.
2. `hyperframes snapshot --at ...` : regarder **au moins une image par scène**, plus chaque moment animé ou zoomé.
3. Corriger, recommencer 1 et 2. **Ne lancer le rendu qu'ensuite**, jamais dans la même commande que le contrôle.

## 6. Rendu et livraison

```bash
cd videos/<nom> && hyperframes render -o renders/<nom>-16x9.mp4          # film intermédiaire (non livré)
cp renders/<nom>-16x9.mp4 ../<nom>-vertical/assets/
cd ../<nom>-vertical && hyperframes check && hyperframes render -o renders/<titre>.mp4
```

- Vérifier le fichier final : `ffprobe` (1080×1920, durée), loudness (`ebur128`), quelques images extraites.
- **Envoyer uniquement la vidéo verticale.**
- Mettre à jour `SUIVI.md` et commiter.
