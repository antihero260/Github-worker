# Suivi du travail

Dernière mise à jour : 1er novembre 2026, 16 h 25 UTC.

## État actuel

| Sujet | État |
| --- | --- |
| Installation de HyperFrames | Faite (dans le conteneur cloud, temporaire). Script permanent : `scripts/install-hyperframes.sh`. |
| Charte de style « Projecteur » | Faite : `hyperframes-style/frame.md` + `ANALYSE.md`. |
| Projets modèles | Faits : `hyperframes-style/modele/` (film 16:9) et `modele-vertical/` (titre + bandeau). |
| Vidéo « Réviser en une nuit avec ChatGPT » | Version 3 (personnage animé, musiques remontées, bruitages) **rendue, vérifiée et envoyée** à 16 h 25. En attente des retours de l'utilisateur. |
| Pull request | [#2](https://github.com/antihero260/Github-worker/pull/2) ouverte vers `main`, surveillée. Branche : `ccr-e6530603-mcler7`. |

## Prochaines étapes

1. Recueillir les retours de l'utilisateur sur la version 3
   (`videos/examen-demain-vertical/renders/reviser-en-une-nuit-avec-chatgpt.mp4`, non versionné : 1080×1920, 120 s,
   −15,5 LUFS, crête −1,6 dBFS).
2. Corriger et corriger (en suivant `hyperframes-style/PROCESSUS-VIDEO.md`).
3. Mettre à jour `hyperframes-style/frame.md`, `ANALYSE.md` et les modèles avec ce qui a été appris sur cette
   vidéo (personnage articulé, recadrages, niveaux de musique) : les modèles n'ont pas encore ces améliorations.
4. Rendre l'installation permanente : l'utilisateur doit fusionner la PR #2 puis ajouter
   `cd Github-worker && bash scripts/install-hyperframes.sh` au script de démarrage de l'environnement cloud.

## Décisions prises

- **Format** : 7 vidéos de référence sur 9 sont un film 16:9 dans un bandeau sous un titre blanc. C'est le format
  livré. La vidéo verticale est fabriquée à partir du film 16:9 (`videos/<nom>-vertical/`).
- **Titre de la vidéo actuelle** : « Réviser en une nuit avec ChatGPT » (choisi par l'utilisateur).
- **Musique** : catalogue HeyGen (l'utilisateur a choisi cette source ; compte HeyGen connecté).
  - Partie 1 « tension » : `bgm_002` (nappe tendue avec tic-tac), temps fort sur « tu ouvres ChatGPT ».
  - Partie 2 « méthode » : `bgm_005` (enquête rythmée, 128 BPM), bouclé sur 14 mesures.
  - Partie 3 « élan » : `bgm_007` (montée cinématique), à partir de 83,3 s.
  - Niveaux : musiques −20/−22 LUFS sous une voix à −16 ; creusées dans les fréquences de la voix (carve 0,5).
- **Bruitages** : bibliothèque Pixabay de HyperFrames (pas de crédit obligatoire) + battement de cœur et
  frappe continue fabriqués avec ffmpeg.
- **Voix off** : fournie par l'utilisateur (ElevenLabs, « Nicolas – Narrator »).

## Erreurs déjà faites (à ne pas refaire)

- Modèle construit d'abord en vertical plein écran au lieu du format 16:9 + titre des références.
- Personnages statiques alors que ceux des références marchent et gesticulent.
- Musique réglée 12–14 dB sous la voix : inaudible pour l'utilisateur.
- Rendu lancé alors que le contrôle signalait un chevauchement (« REC » sur « 23:17 » pendant un zoom).
- Identifiant d'élément égal à l'identifiant de sa scène (`s5-carte`, `s11-prof`) : masquait toute la scène.
- Le signe « ≠ » n'existe pas dans la police Anton : il faut le dessiner.

## Environnement cloud (limites connues)

- Ce qui est installé hors du dépôt disparaît à la fin de la session : HyperFrames, venv Python
  (`/root/.venvs/hyperframes`), commande `heygen` (`~/.local/bin/heygen`), connexion HeyGen.
- Bloqués depuis le conteneur : Edge TTS (certificat du proxy), Openverse, Freesound, Pixabay.
  Accessibles : catalogue HeyGen (après `hyperframes auth login --device`), incompetech.com.
- `HYPERFRAMES_PYTHON=/root/.venvs/hyperframes/bin/python` est nécessaire pour la voix Kokoro (déjà dans `~/.bashrc`).
