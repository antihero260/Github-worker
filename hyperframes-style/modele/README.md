# Modèle HyperFrames — style « Projecteur » : le film 16:9

Projet de départ pour toutes nos vidéos : le **film 16:9 au format YouTube** (1920×1080, 30 i/s). Il applique la
charte [`../frame.md`](../frame.md) et contient une vidéo de test de 16 s (« Ça, c'est toi. Un dev normal… »).

La version TikTok / Shorts / Reels (titre en haut, ce film dans un bandeau au centre) se fait ensuite avec
[`../modele-vertical/`](../modele-vertical/README.md).

## Ce qu'il contient

| Fichier | Rôle |
| --- | --- |
| `index.html` | Composition principale : variables de marque (couleurs), styles partagés `pj-*` (pictogrammes, projecteur, étiquettes, autocollants, papiers, mots-chocs, serif, chiffres, éclair), montage des scènes et du son. |
| `compositions/cadre.html` | Cadre technique sur toute la vidéo : croix, lignes de grille, vignettage et grain (composants du catalogue `vignette` et `grain-overlay`). Masqué sur les cartes plein écran. |
| `compositions/sous-titres.html` | Sous-titres mot à mot, **générés** par `tools/sous-titres.py` : ne pas modifier à la main. |
| `compositions/s1-…s6-*.html` | Les six scènes de l'exemple, une par étape du script : accroche, scène vécue, choc, mécanisme, « Retiens ça », appel à l'action. |
| `tools/sous-titres.py` | Transforme une transcription en sous-titres du style. |
| `assets/fonts/` | Anton et Instrument Serif (licence OFL, fichiers de licence inclus). JetBrains Mono et Inter sont fournies par HyperFrames. |
| `assets/audio/` | Voix de test (Kokoro, voix `ff_siwis`), nappe grave, impact et souffle générés avec ffmpeg (aucun son externe). |

## Faire une nouvelle vidéo

1. **Copier le dossier** `modele/` sous un nouveau nom.
2. **Écrire `script.txt`** en suivant la structure de `../ANALYSE.md` (§ 8) : ~230 mots/min, phrases courtes, tutoiement, une métaphore concrète.
3. **Voix off** (exemple local, voix française de Kokoro) :
   ```bash
   hyperframes tts --text-file script.txt --voice ff_siwis --speed 1.2 -o voix-brute.wav
   ffmpeg -i voix-brute.wav -af loudnorm=I=-14:TP=-1.5:LRA=7 -ar 44100 assets/audio/voix.wav
   ```
   Pour une voix plus naturelle : `/media-use` (HeyGen).
4. **Transcription mot à mot** puis **sous-titres** :
   ```bash
   hyperframes transcribe assets/audio/voix.wav --json   # écrit assets/transcript.json
   python3 tools/sous-titres.py assets/transcript.json --script script.txt --fin <durée - 0,6>
   ```
5. **Scènes** : caler chaque scène sur les temps des mots (`assets/transcript.json`), un changement visuel toutes les ~2 s.
   Réutiliser les classes `pj-*` ; les temps dans un fichier de scène sont locaux (0 = début de la scène).
6. **Son** : ajuster les `<audio>` d'impact et de souffle dans `index.html` sur les mots-chocs et les transitions ;
   couper la nappe sur le moment dur (voir la commande ffmpeg ci-dessous).
7. **Contrôle et rendu** :
   ```bash
   hyperframes check
   hyperframes snapshot --at 0.1,2,4,6
   hyperframes render -o renders/film-16x9.mp4
   ```
8. **Version verticale** : copier `renders/film-16x9.mp4` dans `../modele-vertical/assets/` et suivre son README.

### Régénérer la nappe musicale

La coupure se règle avec les deux temps de l'expression `volume` (ici 6,1 s et 7,95 s) :

```bash
ffmpeg -f lavfi -i "aevalsrc='0.34*sin(2*PI*41.2*t)+0.24*sin(2*PI*55*t)+0.10*sin(2*PI*82.4*t)*(0.6+0.4*sin(2*PI*0.25*t))+0.05*sin(2*PI*164.8*t)*(0.5+0.5*sin(2*PI*0.5*t))':s=44100:d=16" \
  -f lavfi -i "anoisesrc=color=brown:amplitude=0.25:d=16:r=44100:seed=7" \
  -filter_complex "[1]lowpass=f=180[n];[0][n]amix=inputs=2:weights='1 0.6':normalize=0,volume='1-0.92*clip((t-6.1)/0.06,0,1)*clip((7.95-t)/0.15,0,1)':eval=frame,afade=t=in:d=0.3,afade=t=out:st=14.6:d=1.4,aformat=channel_layouts=stereo,loudnorm=I=-20:TP=-2" \
  -ar 44100 assets/audio/musique.wav
```

## Résultat du test

- `hyperframes check` : réussi, 0 erreur. Il reste 5 avertissements « texte affiché moins de 1 à 1,5 s » :
  c'est le rythme rapide voulu par le style (les sous-titres portent le texte).
- Rendu : 1920×1080, 30 i/s, 16 s.
- Positions mesurées sur les références (croix à 58 px des bords, sous-titres centrés à 915 px) ; la hauteur des
  sous-titres se règle avec `--caption-y` dans `index.html`.

## Limites connues

- Les décors sont en 2,5D (dégradés, pictogrammes SVG), pas en vraie 3D comme les références.
- La voix Kokoro est correcte mais synthétique ; prévoir une meilleure voix pour publier.
- Le grain rend le fichier lourd (~27 Mo pour 16 s en 1080p) ; baisser son opacité dans `cadre.html` si besoin.
