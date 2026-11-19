# « 5 skills GitHub pour un design unique » : le film 16:9

Sixième vidéo dans le style « Projecteur ». Voix off et texte de l'utilisateur (60 s). Livrable : la version verticale,
[`../skills-design-vertical/`](../skills-design-vertical/). Le film 16:9 seul n'est pas livré.

## Demandes de l'utilisateur et ce qui a été fait

- **Intro : « plusieurs vidéos qui se superposent dans tous les sens, très vite »** : 16 vidéos (10 faux sites
  « générés par IA » + 6 vidéos Mixkit de gens qui naviguent) arrivent de 8 directions toutes les 0,24 s
  (`rafale()`), avec un son à chaque arrivée et un choc toutes les quatre. Puis un mur de 30 sites identiques
  (« mêmes structures, mêmes cartes, mêmes dégradés ») et un mur de 63 où « ton site se noie ».
- **Les faux sites** : écrits pour l'occasion (même héros en dégradé violet, mêmes 3 cartes, même CTA)
  et filmés avec Playwright ; aucun site réel copié.
- **Skills vérifiés sur GitHub** (recherche GitHub, novembre 2026) et **filmés sur leurs vraies pages** (Playwright,
  thème sombre, capture + vidéo du défilement) :

| Skill | Dépôt officiel | Étoiles | Captures |
| --- | --- | --- | --- |
| Frontend Design | `anthropics/skills` → `skills/frontend-design` | 187 k | page du dossier, `SKILL.md` |
| UI/UX Pro Max | `nextlevelbuilder/ui-ux-pro-max-skill` | 146 k | dépôt, site uupm.cc |
| shadcn | `shadcn-ui/ui` → `skills/shadcn` | 127 k | `SKILL.md`, site ui.shadcn.com |
| Taste Skill | `Leonxlnx/taste-skill` | 111 k | dépôt, site tasteskill.dev |
| Emil Design Engineering | `emilkowalski/skills` → `skills/emil-design-eng` | 54 k | `SKILL.md`, site emilkowal.ski |

- **Effets sonores**, surtout au début : 108 bruitages Mixkit disponibles (nouveaux : scratch, glitchs, parasites,
  déclencheur photo), 118 placés.
- **Musiques rythmées** parmi les plus téléchargées de Mixkit : « Hazy After Hours », « House 02 », « Trap Electro
  Vibes » (`assets/music/SOURCES-mixkit.md`), au niveau validé (≈ −21 LUFS, 5–6 dB sous la voix).

## Refaire la vidéo

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py
hyperframes lint && hyperframes check          # 0 erreur, puis regarder les images
hyperframes render ../skills-design -o renders/skills-design-16x9.mp4   # commande séparée
```
