# ChatGPT te donne toujours raison ?

Vidéo de 103 s dans le style « Projecteur », sur la complaisance des IA (elles valident trop facilement ce qu'on pense).

- **Ce projet** : le film 16:9 (intermédiaire, non livré).
- **[`../ia-te-donne-raison-vertical/`](../ia-te-donne-raison-vertical/)** : la vidéo livrée (1080×1920, titre en haut).

## Ce qui change par rapport à « Examen demain »

- **Deux personnages** : « toi » (vert-jaune) et **l'IA** (blanc cassé, tête-écran) qui se répondent.
- **Personnages jamais figés** : rebond continu (`vit`), gestes en parlant (`parle`), hochements répétés (`acquiesce`),
  course (`court`), chute dans un piège (`chute`), victoire avec sauts, confettis, tampons qui s'écrasent, ego qui gonfle.
- Les scènes sont écrites avec la bibliothèque commune [`../../hyperframes-style/outils/projecteur.py`](../../hyperframes-style/outils/projecteur.py).

## Les 15 scènes

| Scène | Temps | Ce qu'on voit |
| --- | --- | --- |
| `s01-certitude` | 0 → 3,1 s | « toi » bras croisés, jauge « certitude » à 100 %, pouce levé |
| `s02-question` | 3,1 → 8,0 s | l'IA arrive en courant, « toi » parle, l'IA hoche la tête, « 100 % d'accord. » |
| `s03-victoire` | 8,0 → 12,6 s | la citation s'écrit, « toi » saute de joie, confettis |
| `s04-piege` | 12,6 → 16,7 s | un trou s'ouvre, « toi » tombe, « PIÈGE. » |
| `s05-prompt-pour` | 16,7 → 29,1 s | il remonte, tape le 1er prompt, 3 arguments « pour » |
| `s06-prompt-contre` | 29,1 → 41,6 s | 2e prompt, 3 arguments « contre », balance qui oscille, vertiges |
| `s07-plaisir` | 41,6 → 46,6 s | l'IA tend un cœur, « Pas exactement. », le cœur tombe |
| `s08-entrainement` | 46,6 → 52,1 s | l'IA s'entraîne (sauts), jauge, deux cases cochées |
| `s09-complaisance` | 52,1 → 60,8 s | jauge « complaisance » au maximum, « Validé. » ×3, l'ego de « toi » gonfle |
| `s10-observe` | 60,8 → 64,5 s | une loupe passe sur l'IA, « complaisance constatée » |
| `s11-danger` | 64,5 → 74,3 s | « LE VRAI DANGER. », réponse parfaite qui brille, « Preuve ? », « convaincant ≠ vrai » |
| `s12-eviter` | 74,3 → 82,1 s | « toi » court et saute par-dessus le trou, « Donne-moi raison. » barré |
| `s13-bonnes-questions` | 82,1 → 88,7 s | les 3 bonnes questions se cochent, l'IA objecte |
| `s14-certitudes` | 88,7 → 97,2 s | l'IA répond « Oui. Exactement. », un mur « Certitudes. » monte autour de « toi » |
| `s15-et-toi` | 97,2 → 103 s | « toi » avance vers le spectateur, « ? », haussement d'épaules |

## Son

- Voix ElevenLabs (« Nicolas – Narrator »), −15 LUFS.
- 3 musiques du catalogue HeyGen à −18,8 LUFS, creusées dans les fréquences de la voix, limiteur à −4 dB :
  `partie-1-assurance` (pizzicato espiègle, coupé sur « tomber »), `partie-2-analyse` (électronique analytique,
  petite coupure sur « le vrai danger »), `partie-3-solution` (électronique positive).
- 68 bruitages (bibliothèque Pixabay de HyperFrames) : souffles, chute, impacts, montées, clavier, pops, clics, tampons…

## Refaire

```bash
python3 tools/sous-titres.py assets/transcript-brut.json --script script.txt --fin 102.6 --mots assets/mots.json
python3 tools/construire-scenes.py     # ÉCRASE compositions/s*.html
hyperframes check                      # puis snapshots, puis seulement le rendu
hyperframes render -o renders/ia-te-donne-raison-16x9.mp4
```
