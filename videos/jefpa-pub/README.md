# Pub JE-FPA (horizontal 1920×1080)

Publicité pour le site de la Junior Entreprise de la Filière Professionnalisée Actuariat (UFHB) :
https://jefpa-site.pages.dev/

Demande de l'utilisateur :
- garder la voix de sa vidéo (`assets/reference.mp4`, non versionnée) ;
- faire une vidéo plus captivante, **en format horizontal**, **sans personnage** ;
- une vraie pub qui se « balade » sur le site.

## Fabrication

1. **Voix.** On extrait la voix de la vidéo fournie. Elle contenait encore l'ancienne musique : on la sépare avec `tools/separer-voix.py` (modèle UVR MDX-Net Kim_Vocal_2 en ONNX, exécuté avec onnxruntime ; le fond passe de −43 à −75 dB), puis on la règle à −15 LUFS. Le texte exact est dans `script.txt` ; la transcription automatique mélangeait de l'anglais, donc le texte a été reconstitué à partir du site et des sous-titres de la vidéo de référence. L'alignement mot à mot est dans `assets/mots.json`.
2. **Captures du site** : `node tools/capture.cjs tools/plan-capture.json [clip…]`.
   - La page est filmée image par image à 30 i/s, avec l'horloge de la page contrôlée (Playwright clock). Les animations GSAP et ScrollTrigger et le défilement sont donc exacts et fluides.
   - Le pointeur de souris est dessiné dans la page.
   - Mise en page 1440×810, densité 2, soit 2880×1620, ce qui laisse des zooms nets.
   - Le formulaire de contact n'est jamais envoyé : on tape seulement un exemple dans deux champs.
   - Les fichiers vont dans `assets/captures/`, non versionnés : relancer la capture pour les recréer.
3. **Montage** : `python3 tools/construire.py`, puis `python3 tools/mixage.py /tmp/corelink`.
   - 14 scènes calées sur la voix : captures en plein écran ou dans des fenêtres de navigateur, zooms et panoramiques sur les détails dont parle la voix (logo, 2023, les trois présidents, les cartes L3/M1/M2), et cadres bleus sur ces détails.
   - Intertitres animés aux couleurs du site : Manrope, bleu #1f4bff, encre #05070d. Ils couvrent « un sinistre, une retraite, un avenir », « il y a un pas », la méthode en 4 étapes et la fin.
   - Images du site : UFR, rendus 3D.
   - Sous-titres discrets.
4. **Son.**
   - Musique : « Digital Clouds » (Mixkit, gratuite et sans crédit), environ 6 dB sous la voix.
   - Une centaine de bruitages : souffles aux transitions, zooms, clics, frappe au clavier, impacts.
