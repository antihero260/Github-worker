# Suivi du travail

Dernière mise à jour : 1er novembre 2026, 22 h 30 UTC.

## État actuel

| Sujet | État |
| --- | --- |
| Installation de HyperFrames | Faite (dans le conteneur cloud, temporaire). Script permanent : `scripts/install-hyperframes.sh`. |
| Charte de style « Projecteur » | Faite : `hyperframes-style/frame.md` + `ANALYSE.md`. |
| Projets modèles | Faits : `hyperframes-style/modele/` (film 16:9) et `modele-vertical/` (titre + bandeau). |
| Vidéo « Réviser en une nuit avec ChatGPT » | Version 4 envoyée à 17 h 45 (musique +3 dB). Pas encore de retour. |
| Vidéo « ChatGPT te donne toujours raison ? » | Demandée « beaucoup plus dynamique, surtout le perso ». 15 scènes, 2 personnages animés, 3 musiques, 68 bruitages. **Envoyée** à 19 h 40 (1080×1920, 103 s, −16,5 LUFS, crête −1,5 dBTP). Titre proposé, à valider. En attente des retours. |
| Vidéo « L’IA cachée dans ton clavier » (vidéo 3) | Voix off sur le clavier prédictif (le script fourni parlait de n8n : **la voix fait foi**, confirmé par l'utilisateur). 16 scènes, vraies vidéos et logos, téléphone animé, 3 musiques et 58 bruitages Mixkit (155 placés). Contrôle réussi (0 erreur), images revues. **Envoyée** à 21 h (`videos/clavier-ia-vertical/renders/L-IA-cachee-dans-ton-clavier.mp4`, non versionné : 1080×1920, 96 s, −13,9 LUFS, crête −1,4 dBFS ; volume final monté avec ffmpeg, image copiée telle quelle). Titre proposé, à valider. **Retour : l'utilisateur l'a adorée** (« juste baisse très légèrement le volume du son »). Titre non commenté. |
| Vidéo « Crée ton agent IA sans coder » (vidéo 4, n8n + Telegram) | L'utilisateur a **adoré la vidéo 3**. Ses demandes : baisser très légèrement « le son » (compris : les bruitages, −2 dB), encore plus de sons d'Internet et variés, **beaucoup plus d'illustrations, surtout des vidéos**. 27 scènes, 21 vidéos Mixkit, 6 logos, interface n8n et Telegram animées, 99 bruitages (211 placés). Contrôle réussi, images revues. Rendu en cours. Titre proposé, à valider. |
| Pull request | [#2](https://github.com/antihero260/Github-worker/pull/2) ouverte vers `main`, surveillée. Branche : `ccr-e6530603-mcler7`. |

## Prochaines étapes

1. Envoyer « Crée ton agent IA sans coder » (vertical) et recueillir les retours (niveau des bruitages, titre).
2. Recueillir les retours sur « ChatGPT te donne toujours raison ? »
   (`videos/ia-te-donne-raison-vertical/renders/chatgpt-te-donne-toujours-raison.mp4`, non versionné) et faire valider le titre.
3. Recueillir les retours de l'utilisateur sur la version 4 de « Réviser… »
   (`videos/examen-demain-vertical/renders/reviser-en-une-nuit-avec-chatgpt.mp4`, non versionné : 1080×1920, 120 s,
   −15,6 LUFS, crête −1,5 dBFS).
4. Corriger d'après ses retours (en suivant `hyperframes-style/PROCESSUS-VIDEO.md`).
5. Mettre à jour `hyperframes-style/frame.md`, `ANALYSE.md` et les modèles avec ce qui a été appris sur cette
   vidéo (personnage articulé, recadrages, niveaux de musique) : les modèles n'ont pas encore ces améliorations.
6. Rendre l'installation permanente : l'utilisateur doit fusionner la PR #2 puis ajouter
   `cd Github-worker && bash scripts/install-hyperframes.sh` au script de démarrage de l'environnement cloud.

## Décisions prises

- **Format** : 7 vidéos de référence sur 9 sont un film 16:9 dans un bandeau sous un titre blanc. C'est le format
  livré. La vidéo verticale est fabriquée à partir du film 16:9 (`videos/<nom>-vertical/`).
- **Titre de la vidéo actuelle** : « Réviser en une nuit avec ChatGPT » (choisi par l'utilisateur).
- **Vidéo 3 : sons sur Internet** (demande de l'utilisateur) : Mixkit (musiques, bruitages, vidéos ; gratuit, usage
  commercial, crédit non obligatoire). Le site bloque vite les robots (Cloudflare, erreur 429) mais les fichiers
  restent accessibles directement : `https://assets.mixkit.co/active_storage/sfx/<n>/<n>.wav` (le nom du son est
  dans l'en-tête `content-disposition`), `https://assets.mixkit.co/music/<n>/<n>.mp3`,
  `https://assets.mixkit.co/videos/<n>/<n>-1080.mp4` (ou `-720`). Les numéros des vidéos se trouvent avec WebFetch
  sur une page de recherche Mixkit (vignettes `…/videos/<n>/<n>-thumb-360-0.jpg`).
- **Vidéo 3 : beaucoup plus de bruitages** (demande de l'utilisateur) : un son de rush à chaque recadrage (`zoom()`
  dans `construire-scenes.py`), souffle à chaque transition, risers avant les moments forts, pops, frappe, pluie…
  Chaque son est calé sur son pic (`assets/sfx/pics.json`).
- **Musique** : catalogue HeyGen pour les vidéos 1 et 2 (l'utilisateur a choisi cette source ; compte HeyGen connecté), Mixkit pour la vidéo 3.
  - Partie 1 « tension » : `bgm_002` (nappe tendue avec tic-tac), temps fort sur « tu ouvres ChatGPT ».
  - Partie 2 « méthode » : `bgm_005` (enquête rythmée, 128 BPM), bouclé sur 14 mesures.
  - Partie 3 « élan » : `bgm_007` (montée cinématique), à partir de 83,3 s.
  - Niveaux (version 4) : musiques −18/−19 LUFS sous une voix à −16 (3–4 dB dessous) ; creusées dans les
    fréquences de la voix (carve 0,5) ; limiteur à −4 dB en fin de chaîne pour éviter la saturation.
- **Bruitages** : bibliothèque Pixabay de HyperFrames (pas de crédit obligatoire) + battement de cœur et
  frappe continue fabriqués avec ffmpeg.
- **Voix off** : fournie par l'utilisateur (ElevenLabs, « Nicolas – Narrator »).
- **Bibliothèque commune** : `hyperframes-style/outils/projecteur.py` (personnages « toi » et « IA », gestes, scènes) ;
  chaque vidéo a son `tools/construire-scenes.py` qui l'utilise.
- **Dynamisme exigé** (retour de l'utilisateur) : personnages qui bougent en permanence (`vit`), un geste ou une
  réaction à chaque groupe de mots, deux personnages qui se répondent quand c'est possible.

## Erreurs déjà faites (à ne pas refaire)

- Modèle construit d'abord en vertical plein écran au lieu du format 16:9 + titre des références.
- Personnages statiques alors que ceux des références marchent et gesticulent.
- Musique réglée 12–14 dB sous la voix : inaudible pour l'utilisateur. Même 6–7 dB était encore trop bas pour lui.
- Rendu lancé alors que le contrôle signalait un chevauchement (« REC » sur « 23:17 » pendant un zoom).
- Identifiant d'élément égal à l'identifiant de sa scène (`s5-carte`, `s11-prof`) : masquait toute la scène.
- Le signe « ≠ » n'existe pas dans la police Anton : il faut le dessiner.
- Commandes lancées en parallèle (création du projet vertical + rendu) : le rendu est parti dans le mauvais dossier.
  Toujours passer le dossier du projet à `hyperframes render <dossier>` et enchaîner les étapes dans l'ordre.

- **Musique trop basse dans les vidéos 1 et 2 : vraie cause trouvée.** Le carve (`carve.mjs`, force 0,5) ajoute,
  en plus des creux de fréquences, une **baisse de niveau automatique** (nœud « gain » + courbe) qui vise une musique
  **12 dB sous la voix** et la baisse jusqu'à −12 dB dès que la voix parle (−9 dB en moyenne). Les niveaux « 3–4 dB
  sous la voix » des fichiers n'étaient donc pas ceux entendus. Désormais `tools/mixage.py` retire cette baisse et
  garde seulement les creux de fréquences (vidéo 3). Les vidéos 1 et 2 ont encore la baisse : à corriger si
  l'utilisateur veut les refaire.
- Vidéo 4 : identifiant égal à la scène refait (`s15-agir`, `s22-voila` : scène vide par moments). Le générateur
  vérifie maintenant automatiquement qu'aucun élément ne porte l'identifiant de sa scène.
- Caractères absents d'Anton (⇄, ⌕, ◆) : les remplacer par du texte ou un petit SVG.
- Snapshots : quand on demande beaucoup d'images d'un coup, certaines sortent floues/vides (scène prise à son état
  de départ). Relancer ces instants seuls pour vérifier avant de conclure à un bug.
- Apostrophe droite `'` dans le titre du projet vertical : casse l'attribut `data-composition-variables='…'`.
  Utiliser l'apostrophe typographique `’`.

## À savoir sur le son

- Volume final : après le rendu, monter le fichier livré vers −14 LUFS sans toucher l'image :
  `ffmpeg -i in.mp4 -c:v copy -af "volume=<gain>dB,alimiter=limit=0.83:attack=3:release=60:level=false" -c:a aac -b:a 256k out.mp4`.

- À la fin du rendu, HyperFrames baisse **tout** le mixage pour que les crêtes restent sous −1 dBTP (2,5 dB sur la
  version 4, voir « lowered by … dB » dans le journal du rendu). Le volume global reste donc vers −15,6 LUFS même si
  on remonte la musique ; c'est l'écart musique/voix qui change.

## Environnement cloud (limites connues)

- Ce qui est installé hors du dépôt disparaît à la fin de la session : HyperFrames, venv Python
  (`/root/.venvs/hyperframes`), commande `heygen` (`~/.local/bin/heygen`), connexion HeyGen.
- Bloqués depuis le conteneur : Edge TTS (certificat du proxy), Openverse, Freesound, Pixabay.
  Accessibles : catalogue HeyGen (après `hyperframes auth login --device`), incompetech.com.
- `HYPERFRAMES_PYTHON=/root/.venvs/hyperframes/bin/python` est nécessaire pour la voix Kokoro (déjà dans `~/.bashrc`).
