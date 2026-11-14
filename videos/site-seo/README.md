# « Ton site est introuvable sur Google ? » : le film 16:9

Dixième vidéo. Voix off fournie par l'utilisateur (47 s) ; `script.txt` est son texte exact. Retour de l'utilisateur sur la
vidéo 9 : « ton dernier hook ne me plaisait pas trop… mets les vidéos, ça ne manque pas sur Internet, et les images ;
d'ailleurs augmente ».

Livrable : la version verticale, [`../site-seo-vertical/`](../site-seo-vertical/) : titre + ce film + les 5 étapes sous
le film (SEO Audit, Schema, Architecture, Astuces, Seobility).

## Ce qui est nouveau

- **Hook = 28 vraies vidéos et photos en 6,4 s, une par mot** (`rafale_mots()`) : ordinateur, code, IA, Google (téléphone,
  enseigne, page), barre de recherche « Aucun résultat », personnes perdues devant l'écran, vitrine et rayons vides,
  panneaux « Open », boutiques, puis désert (survol, dunes, van) et la boutique posée au milieu des dunes, « Visiteurs : 0 ».
- Photos réelles d'Unsplash (gratuites, sans crédit) en plus des vidéos Mixkit ; une vraie vidéo en fond de chaque skill.
- Les 3 skills vérifiés (dépôt `coreyhaines31/marketingskills`, 58,8 k ★) et filmés sur GitHub ; Seobility filmé.

## Refaire la vidéo

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py
python3 tools/simuler-mix.py /tmp/sim.wav
hyperframes lint && hyperframes check          # 0 erreur, puis regarder les images
hyperframes render ../site-seo -o renders/site-seo-16x9.mp4   # commande séparée
```
