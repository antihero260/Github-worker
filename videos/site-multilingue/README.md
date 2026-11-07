# « Ton site en 3 langues en 1 clic » : le film 16:9

Quatorzième vidéo (37,7 s). Voix off et texte fournis par l'utilisateur. Demande : « surpasse-toi encore, surtout au début ».

Livrable : la version verticale, [`../site-multilingue-vertical/`](../site-multilingue-vertical/) : titre + ce film + la méthode
en 3 étapes sous le film (verrouillées, dévoilées une par une).

## Ce qui est nouveau

- **Hook** : dès la première image, 3 vraies vidéos plein cadre (Paris, Big Ben, Sagrada Família) avec « FR / EN / ES » et
  leurs drapeaux claquent en 0,15 s (flash, secousse) ; puis une vraie vidéo par mot (15 plans en 6 s : Arc de triomphe,
  globe, Times Square, Tower Bridge, drapeaux américain, espagnol, mexicain…), un curseur géant qui clique avec une onde de
  choc, le site qui passe **en direct** de « Bienvenue » à « Welcome » puis « Bienvenidos », des visiteurs du monde entier
  qui affluent, et la caméra qui plonge sur le sélecteur sur « Regarde ! ».
- **Un vrai site traduisible** (`site_boul()`, `lx()`, `bascule()`) : chaque texte existe en 3 langues superposées
  (la mise en page ne bouge jamais) ; le curseur ouvre le sélecteur, choisit EN puis ES, tout le site change.
- La demande à l'IA s'écrit **mot à mot avec la voix** (`prompt_mots()`), FR / EN / ES en surbrillance.
- Textes, boutons, menus, formulaires : chacun est encadré et traduit au moment où la voix le nomme, la caméra suit.
- Attention : « Chausson aux pommes » → « Apple slipper » ✗, la loupe vérifie, corrigé en « Apple turnover » ✓.
- 212 bruitages, 3 musiques trap Mixkit populaires jamais utilisées (voir `assets/music/SOURCES-mixkit.md`).

## Refaire la vidéo

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py
python3 tools/simuler-mix.py /tmp/sim.wav
hyperframes lint && hyperframes check          # 0 erreur, puis regarder les images
hyperframes render ../site-multilingue -o renders/site-multilingue-16x9.mp4   # commande séparée
```

Attention : `hyperframes snapshot` rend parfois une image noire au hasard dans ce projet (relancer la capture : l'image
revient) ; le film rendu est vérifié avec `ffmpeg -vf blackdetect`.
