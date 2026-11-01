# « Crée ton agent IA sans coder » : le film 16:9

Quatrième vidéo dans le style « Projecteur ». Voix off fournie par l'utilisateur (129 s, ElevenLabs « Nicolas –
Narrator ») : créer un agent IA de recherche avec n8n et Telegram, en 5 étapes. `script.txt` est le texte envoyé par
l'utilisateur ; il correspond à la voix.

Livrable : la version verticale, [`../agent-ia-n8n-vertical/`](../agent-ia-n8n-vertical/) (titre « Crée ton agent IA
sans coder » + ce film dans le bandeau). Le film 16:9 seul n'est pas livré.

## Retours de l'utilisateur appliqués (après la vidéo 3, qu'il a « adorée »)

- **« Baisse très légèrement le volume du son »** : bruitages 2 dB plus bas (`VOL_SFX = 0.8` dans
  `tools/construire-scenes.py`). Musique au même niveau que la vidéo 3 (≈ −19 LUFS, sans baisse automatique).
- **« Prends des sons sur Internet, surtout quand tu en prends plusieurs »** : 99 bruitages Mixkit différents
  (58 de la vidéo 3 + 41 nouveaux : clavier d'ordinateur, souris, robots, pages, déverrouillage, fusée, pièces…),
  211 sons placés.
- **« Beaucoup plus d'illustrations, surtout les vidéos »** : 21 vraies vidéos Mixkit (contre 4), 6 logos officiels
  (n8n, Telegram, Google, OpenAI…), et des interfaces animées : fenêtre n8n avec pointeur de souris qui clique,
  workflow dont les nœuds se branchent et qu'une impulsion parcourt, conversations Telegram (BotFather, test).

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `tools/construire-scenes.py` | Écrit les 27 scènes, le montage et les sons de `index.html`, le cadre. Vérifie qu'aucun élément ne porte l'identifiant de sa scène. |
| `tools/mixage.py` | Carve des musiques (creux de fréquences seulement) + limiteur −4 dB. |
| `tools/simuler-mix.py` | Simule le mixage avant le rendu. |
| `assets/*/SOURCES*.md` | Origine et licence de chaque musique, bruitage, vidéo et logo. |

## Refaire la vidéo

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py
python3 tools/simuler-mix.py /tmp/sim.wav
hyperframes lint && hyperframes check          # 0 erreur, puis regarder les images
hyperframes render ../agent-ia-n8n -o renders/agent-ia-n8n-16x9.mp4   # commande séparée
```
