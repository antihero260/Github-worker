# « 5 sites de business à créer avec l'IA et à vendre » : le film 16:9

Douzième vidéo (74,7 s). Voix off et texte fournis par l'utilisateur. Demande : « Tu sais comment les choquer encore plus ».

Livrable : la version verticale, [`../sites-business-vertical/`](../sites-business-vertical/) : titre + ce film + les 5 métiers
sous le film (« 5 sites à vendre »).

## Ce qui est nouveau

- **Encore plus de vraies vidéos** : rafale de fond qui change tous les 1–2 mots dans chaque scène (≈ 70 vidéos Mixkit
  différentes, 13 photos Unsplash de plats, maisons, salons et salles de sport).
- **Hook** : 5 vidéos verticales des 5 métiers qui claquent l'une après l'autre, un « 5 » géant, puis 15 plans en rafale.
- **Un vrai site pour chaque métier** (`site_metier()`), qui défile et ouvre ses fonctions une par une au moment où la voix
  les cite : CHEZ LINA (réservation, commande), NOVA IMMO (visite 360°, filtres, contact agent), STUDIO ÉCLAT (tarifs,
  créneaux, tampon « Fini les messages ! »), MAX COACHING (suivi client, formules), PRO DÉPANNAGE (avis, demande de devis).
- Bruitages propres aux métiers : poêle qui grésille, perceuse, marteau, clé à molette, trousseau de clés, buzzer de sport.
- 264 bruitages, 3 musiques hip-hop/trap Mixkit (voir `assets/music/SOURCES-mixkit.md`).

## Refaire la vidéo

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py
python3 tools/simuler-mix.py /tmp/sim.wav
hyperframes lint && hyperframes check          # 0 erreur, puis regarder les images
hyperframes render ../sites-business -o renders/sites-business-16x9.mp4   # commande séparée
```
