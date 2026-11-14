# « 5 points à vérifier avant de publier ton site IA » : le film 16:9

Septième vidéo. Voix off fournie par l'utilisateur (52 s, ElevenLabs « Nicolas – Narrator ») ; `script.txt` est son
texte exact. Demande : « un autre style dynamique », avec un hook visuel fort dès le début (l'utilisateur a aimé la
rafale de la vidéo 6).

Livrable : la version verticale, [`../site-conforme-vertical/`](../site-conforme-vertical/) : titre + ce film dans le
bandeau + **la check-list des 5 points sous le film**, qui se coche au fil de la vidéo. Le film 16:9 seul n'est pas livré.

## Style « Alerte » (variante dynamique du style « Projecteur »)

- Accent **orange signal** `#FF5A1F` (au lieu du vert-jaune), coches **vertes** `#2FE38A` pour ce qui est validé.
- Fond « plan technique » : bleu nuit avec une grille fine, sans projecteurs.
- **Volet rayé** orange et bleu nuit qui balaie l'image à chaque coupe (`compositions/volets.html`).
- Mots-chocs en **glitch** (décalage cyan/rouge), **secousses de caméra** sur les impacts, **rubans de chantier**
  « ATTENTION », pop-ups d'erreur, numéros géants « 01 » à « 05 » qui se rangent à côté du titre.
- Sous-titres : bandeau blanc penché avec une ombre orange.
- Hook : une vidéo plein cadre qui se découpe en 2, 4, 9 puis 16 vidéos sur les premiers mots, puis le site, le bouton
  « Publier » cliqué et une fusée qui décolle. Le drop de la musique tombe sur « Attention ! ».

## Contenu vérifié

Chaque point est illustré par la vraie page officielle correspondante, filmée (Service Public Entreprendre, CNIL,
Your Europe) : voir [`assets/video/SOURCES.md`](assets/video/SOURCES.md).

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `tools/construire-scenes.py` | Écrit les 9 scènes, les volets, la check-list de la version verticale, le montage et les sons. |
| `tools/mixage.py` | Carve des musiques (creux de fréquences seulement) + limiteur −4 dB. |
| `tools/simuler-mix.py` | Simule le mixage avant le rendu. |

## Refaire la vidéo

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py
python3 tools/simuler-mix.py /tmp/sim.wav
hyperframes lint && hyperframes check          # 0 erreur, puis regarder les images
hyperframes render ../site-conforme -o renders/site-conforme-16x9.mp4   # commande séparée
```
