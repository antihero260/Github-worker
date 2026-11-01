# Consignes pour Claude dans ce dépôt

Ce dépôt contient le worker vocal Edge TTS de LeCodeIA (`worker.py`, workflow GitHub Actions) **et** la
production de vidéos avec HyperFrames (`hyperframes-style/`, `videos/`, `scripts/install-hyperframes.sh`).

**Avant toute chose, lire :**
- [`SUIVI.md`](SUIVI.md) : où on en est, décisions prises, prochaines étapes.
- [`hyperframes-style/PROCESSUS-VIDEO.md`](hyperframes-style/PROCESSUS-VIDEO.md) : la marche à suivre pour faire une vidéo.

## Exigences de l'utilisateur (à respecter sans qu'il ait à les redire)

- Répondre en **français**, simplement et directement.
- **Livrable vidéo = une seule vidéo verticale 1080×1920** : titre-promesse blanc en haut, film 16:9 dans un
  bandeau au centre (format de ses vidéos de référence). Ne jamais envoyer le film 16:9 intermédiaire.
- Style « Projecteur » : [`hyperframes-style/frame.md`](hyperframes-style/frame.md).
- **Les personnages doivent bouger** (marcher, pointer, lever les bras, réagir) et la caméra doit recadrer
  pendant les scènes. Des pictogrammes figés ne sont pas acceptables.
- **Musique bien audible** : 3 morceaux (un par partie), environ 3–4 dB sous la voix (demandé après la version 3,
  puis « encore plus fort » pour la vidéo 3), jamais 12 dB. **Retirer la baisse automatique du carve**
  (voir `videos/clavier-ia/tools/mixage.py` et `SUIVI.md`) : sinon la musique tombe 9–12 dB sous la voix.
- **Bruitages obligatoires et nombreux** : un rush/souffle à chaque recadrage et transition, impacts, risers, clavier,
  clics, pops, apparitions… (vidéo 3 : environ 150 sons pour 96 s).
- **Sons et images téléchargés sur Internet** quand c'est possible (demande de l'utilisateur) : Mixkit (gratuit,
  sans crédit) pour musiques, bruitages et vraies vidéos ; logos officiels avec `media-use resolve --type logo`.
- **Tout vérifier et corriger avant de lancer un rendu** : `hyperframes check` sans erreur, puis regarder les
  images clés. Ne jamais lancer le rendu dans la même commande que le contrôle.
- Mettre à jour `SUIVI.md` à chaque étape importante.
