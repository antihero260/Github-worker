# Vidéo 14, version test TikTok plein écran 9:16 (25,5 s)

Demande de l'utilisateur (ses vidéos restent vers 190 vues sur TikTok) : tester une version **plein écran 9:16 native**,
**plus courte** (25,5 s au lieu de 37,7 s), avec **la promesse en très gros dès la première image**. Il garde **les mêmes
musiques** (il les préfère aux sons tendance de TikTok).

- Scènes construites directement en 1080×1920 (pas un recadrage du film 16:9) : `tools/construire-scenes.py`, fonction
  `en_vertical()` à la fin (tailles de l'index, des scènes, volets, cadre, sous-titres à 1 420 px).
- Voix raccourcie : passage « Traduis automatiquement… design » et « Et voilà… trois sites différents » retiré
  (coupe de 18,09 s à 30,27 s dans la voix d'origine).
- Zones sûres TikTok respectées : rien d'important dans les 150 px du haut, sous les icônes à droite, ni sous 1 500 px.
- 5 scènes : hook (3 villes FR/EN/ES + promesse « Ton site en 3 langues en 1 clic » + rafale de vraies vidéos + clic géant
  + site qui change de langue), démonstration du sélecteur, demande à l'IA mot à mot, attention, plus de visiteurs.

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py
hyperframes check
hyperframes render ../site-multilingue-9x16 -o renders/brut.mp4   # commande séparée, puis mastering à −14 LUFS
```
