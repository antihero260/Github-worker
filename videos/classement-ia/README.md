# « Je classe les IA de S à C » : le film 16:9

Cinquième vidéo dans le style « Projecteur ». Voix off de l'utilisateur (120 s, ElevenLabs « Nicolas – Narrator ») et
texte fourni par lui (`script.txt`) : classement des IA populaires par catégorie (conversation, images, vidéos,
audio), rangs S, A, B, C.

Livrable : la version verticale, [`../classement-ia-vertical/`](../classement-ia-vertical/) (titre proposé « Je classe
les IA de S à C »). Le film 16:9 seul n'est pas livré.

## Ce qu'il contient

- **Tableau de classement animé** (`Tableau` dans `tools/construire-scenes.py`) : rangs S, A, B, C ; chaque logo tombe
  dans son rang au moment où la voix le nomme (chute + rebond, souffle + impact), le rang concerné s'allume, la caméra
  zoome dessus. Récapitulatif final avec les 16 outils et le rang C laissé vide.
- **16 logos officiels** (theSVG) : ChatGPT, Claude, Gemini, DeepSeek, Perplexity, Grok, Midjourney, Nano Banana
  (logo Gemini), ChatGPT Images, Adobe Firefly, Recraft, Kling, Seedance (logo ByteDance), Runway, ElevenLabs, Suno.
- **15 vraies vidéos Mixkit** : une carte plein cadre par catégorie (ordinateur, peinture, tournage, micro) et des
  panneaux pour chaque explication.
- Téléphone dont les applis IA tremblent puis disparaissent (« n'en garder qu'une seule »), ondes sonores, notes de
  musique, personnages qui réagissent à chaque placement.
- Son : 3 nouvelles musiques Mixkit (≈ −21 LUFS, 5–6 dB sous la voix, réglage validé), 166 bruitages.

## Transcription

La transcription automatique Parakeet dérivait vers l'anglais : la voix a été retranscrite avec Whisper `medium`
forcé en français (`hyperframes transcribe --engine whisper --model medium --language fr`), puis alignée sur le texte
de l'utilisateur.

## Refaire la vidéo

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py
python3 tools/simuler-mix.py /tmp/sim.wav
hyperframes lint && hyperframes check          # 0 erreur, puis regarder les images
hyperframes render ../classement-ia -o renders/classement-ia-16x9.mp4   # commande séparée
```
