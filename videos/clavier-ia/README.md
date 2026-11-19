# « L’IA cachée dans ton clavier » : le film 16:9

Troisième vidéo dans le style « Projecteur » ([`../../hyperframes-style/frame.md`](../../hyperframes-style/frame.md)).
Voix off fournie par l'utilisateur (95 s) : le clavier prédictif du téléphone est une forme d'IA. **La voix fait foi**
(le script envoyé avec elle parlait d'un agent n8n) : `script.txt` est le texte réellement prononcé, reconstitué
depuis la transcription.

Livrable : la version verticale, [`../clavier-ia-vertical/`](../clavier-ia-vertical/) (titre « L’IA cachée dans ton
clavier » + ce film dans le bandeau). Le film 16:9 seul n'est pas livré.

## Ce qui change par rapport aux vidéos 1 et 2

- **Musique vraiment audible** : `tools/mixage.py` retire la baisse automatique que le carve ajoutait
  (−9 à −12 dB dès que la voix parle, voir `SUIVI.md`). Musiques à ≈ −19 LUFS, 4 dB sous la voix, sans baisse.
- **Sons et musiques téléchargés sur Internet** (Mixkit, gratuit, sans crédit obligatoire) : 3 musiques, 58 bruitages
  ([`assets/music/SOURCES-mixkit.md`](assets/music/SOURCES-mixkit.md), [`assets/sfx/SOURCES-mixkit.md`](assets/sfx/SOURCES-mixkit.md)).
- **155 bruitages placés**, dont un son de rush à **chaque** recadrage de caméra (`zoom()`), un souffle à chaque
  transition, des montées (risers) avant les moments forts, des pops, la frappe sur le clavier du téléphone, la pluie
  et le tonnerre sur « pleuvoir ». Chaque son est calé sur son **pic** (`assets/sfx/pics.json`).
- **Vraies images et vidéos** : 4 vidéos Mixkit (mains qui tapent sur un téléphone, gros plan du clavier), une photo
  de ciel de pluie, les logos officiels ChatGPT, Claude et Gemini ([`assets/video/SOURCES.md`](assets/video/SOURCES.md),
  [`assets/img/SOURCES.md`](assets/img/SOURCES.md)).
- Un **téléphone dessiné** (champ de saisie, barre de 3 suggestions, clavier AZERTY dont les touches s'allument) pour
  montrer les suggestions en direct : « Je suis en… » → « retard », « Le ciel est couvert, il va… » → « pleuvoir ».

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `tools/construire-scenes.py` | Écrit les 16 scènes (`compositions/s01…s16`), le montage et les sons de `index.html`, et les masques du cadre. |
| `tools/mixage.py` | À relancer après : carve des musiques (creux de fréquences seulement), limiteur −4 dB. |
| `tools/simuler-mix.py` | Simule le mixage avec ffmpeg pour vérifier les niveaux avant le rendu. |
| `tools/sous-titres.py` | Sous-titres mot à mot et `assets/mots.json`. |

## Refaire la vidéo

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py   # mixage.py a besoin de /tmp/corelink (voir SUIVI.md)
python3 tools/simuler-mix.py /tmp/sim.wav
hyperframes lint && hyperframes check          # 0 erreur, puis regarder les images (hyperframes snapshot --at …)
hyperframes render ../clavier-ia -o renders/clavier-ia-16x9.mp4   # commande séparée
```
