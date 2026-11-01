# Suivi du travail

Dernière mise à jour : 1er novembre 2026, 19 h 40 UTC.

## État actuel

| Sujet | État |
| --- | --- |
| Installation de HyperFrames | Faite (dans le conteneur cloud, temporaire). Script permanent : `scripts/install-hyperframes.sh`. |
| Charte de style « Projecteur » | Faite : `hyperframes-style/frame.md` + `ANALYSE.md`. |
| Projets modèles | Faits : `hyperframes-style/modele/` (film 16:9) et `modele-vertical/` (titre + bandeau). |
| Vidéo « Réviser en une nuit avec ChatGPT » | Version 4 envoyée à 17 h 45 (musique +3 dB). Pas encore de retour. |
| Vidéo « ChatGPT te donne toujours raison ? » | Demandée « beaucoup plus dynamique, surtout le perso ». 15 scènes, 2 personnages animés, 3 musiques, 68 bruitages. **Envoyée** à 19 h 40 (1080×1920, 103 s, −16,5 LUFS, crête −1,5 dBTP). Titre proposé, à valider. En attente des retours. |
| Pull request | [#2](https://github.com/antihero260/Github-worker/pull/2) ouverte vers `main`, surveillée. Branche : `ccr-e6530603-mcler7`. |

## Prochaines étapes

1. Recueillir les retours sur « ChatGPT te donne toujours raison ? »
   (`videos/ia-te-donne-raison-vertical/renders/chatgpt-te-donne-toujours-raison.mp4`, non versionné) et faire valider le titre.
2. Recueillir les retours de l'utilisateur sur la version 4 de « Réviser… »
   (`videos/examen-demain-vertical/renders/reviser-en-une-nuit-avec-chatgpt.mp4`, non versionné : 1080×1920, 120 s,
   −15,6 LUFS, crête −1,5 dBFS).
3. Corriger d'après ses retours (en suivant `hyperframes-style/PROCESSUS-VIDEO.md`).
4. Mettre à jour `hyperframes-style/frame.md`, `ANALYSE.md` et les modèles avec ce qui a été appris sur cette
   vidéo (personnage articulé, recadrages, niveaux de musique) : les modèles n'ont pas encore ces améliorations.
5. Rendre l'installation permanente : l'utilisateur doit fusionner la PR #2 puis ajouter
   `cd Github-worker && bash scripts/install-hyperframes.sh` au script de démarrage de l'environnement cloud.

## Décisions prises

- **Format** : 7 vidéos de référence sur 9 sont un film 16:9 dans un bandeau sous un titre blanc. C'est le format
  livré. La vidéo verticale est fabriquée à partir du film 16:9 (`videos/<nom>-vertical/`).
- **Titre de la vidéo actuelle** : « Réviser en une nuit avec ChatGPT » (choisi par l'utilisateur).
- **Musique** : catalogue HeyGen (l'utilisateur a choisi cette source ; compte HeyGen connecté).
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

## À savoir sur le son

- À la fin du rendu, HyperFrames baisse **tout** le mixage pour que les crêtes restent sous −1 dBTP (2,5 dB sur la
  version 4, voir « lowered by … dB » dans le journal du rendu). Le volume global reste donc vers −15,6 LUFS même si
  on remonte la musique ; c'est l'écart musique/voix qui change.

## Environnement cloud (limites connues)

- Ce qui est installé hors du dépôt disparaît à la fin de la session : HyperFrames, venv Python
  (`/root/.venvs/hyperframes`), commande `heygen` (`~/.local/bin/heygen`), connexion HeyGen.
- Bloqués depuis le conteneur : Edge TTS (certificat du proxy), Openverse, Freesound, Pixabay.
  Accessibles : catalogue HeyGen (après `hyperframes auth login --device`), incompetech.com.
- `HYPERFRAMES_PYTHON=/root/.venvs/hyperframes/bin/python` est nécessaire pour la voix Kokoro (déjà dans `~/.bashrc`).
