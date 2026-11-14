# « 6 types de sites web : lequel te faut-il ? » : le film 16:9

Treizième vidéo (95,6 s). Voix off et texte fournis par l'utilisateur. Demande : « en plus du mystère, il ne faut pas qu'ils
connaissent tous les types en même temps mais progressivement. De plus, on peut même mettre plus de suivi de caméra. »

Livrable : la version verticale, [`../types-de-sites-vertical/`](../types-de-sites-vertical/) : titre + ce film + les 6 types
sous le film, **verrouillés** (« ? » et cadenas) et dévoilés un par un.

## Ce qui est nouveau

- **Mystère, révélation progressive** (`mystere()`) : après chaque numéro, la voix marque une pause d'environ 1 s. L'image
  plonge dans la nuit, une carte face cachée tombe (« ? », cadenas), tremble, la caméra s'approche lentement, cœur qui bat,
  roulement de tambour ; sur le nom du type, le cadenas saute, la carte se retourne (flash, choc, « révélation »), puis
  s'envole et devient le titre. Dans la scène 2, les 6 cartes restent cachées ; sous le film (vertical), 6 cases « ? »
  verrouillées se retournent une par une. Les 6 types ne sont visibles ensemble qu'à la fin (« pas de la même manière »).
- **Caméra qui suit** (`suit()`, `pano()`) : la caméra accompagne ce qui bouge — le logo, les images puis le bouton du
  site basique ; les 6 cartes qui arrivent ; la fenêtre du site qui entre ; à chaque fonction, elle va vers l'étiquette puis
  vers la fenêtre qui s'ouvre ; la carte de visite, l'entonnoir, « Niveau MAX », les logos Netflix et Airbnb ; elle glisse
  sur la mosaïque des 6 sites, puis s'approche de la question finale.
- Un faux site par type (`site_type()`) : vitrine (ATELIER ÉLISE), e-commerce (URBAN SHOP : produits qui volent dans le
  panier, paiement, suivi de commande), portfolio (LÉA MOREAU), blog (LE MAG DIGITAL : abonnés qui grimpent, trafic),
  landing page (FITPULSE : entonnoir 1 000 visiteurs → 87 clients), plateforme (HUBLO : compte, publication, messages,
  formation ; cartes en vraies vidéos).
- Rafale de vraies vidéos en fond de chaque scène (≈ 90 vidéos Mixkit), 18 photos Unsplash, 426 bruitages dont 10 nouveaux
  sons de suspense Mixkit, 3 musiques hip-hop Mixkit populaires (voir `assets/music/SOURCES-mixkit.md`).

## Refaire la vidéo

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py
python3 tools/simuler-mix.py /tmp/sim.wav
hyperframes lint && hyperframes check          # 0 erreur, puis regarder les images
hyperframes render ../types-de-sites -o renders/types-de-sites-16x9.mp4   # commande séparée
```
