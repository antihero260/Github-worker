# Analyse du style « Projecteur »

Analyse des 9 vidéos de référence fournies, pour en faire le style de toutes nos vidéos HyperFrames.
La spécification à copier à la racine de chaque projet est [`frame.md`](frame.md) ; ce document explique d'où
viennent ses valeurs et comment les appliquer.

Légende : **[mesuré]** = calculé sur les fichiers (images, son, transcription) ; **[estimé]** = lu à l'œil.

## 1. Le corpus

| Vidéo | Durée | Format | Mots | Débit | Plans (coupes franches) | Durée médiane d'un plan |
| --- | --- | --- | --- | --- | --- | --- |
| v1 « Ça c'est toi… » (accroche) | 2 min 25 | vertical natif | 543 | 235 mots/min | 75 | 1,7 s |
| v2 « Elle a choisi un mec… » | 2 min 14 | vertical natif | 504 | 236 | 51 | 2,2 s |
| v3 « Comment les femmes tombent amoureuses » | 2 min 01 | 16:9 + titre | 437 | 228 | 11 | 4,1 s |
| v4 « Poser des questions » | 1 min 32 | 16:9 + titre | 341 | 239 | 13 | 4,0 s |
| v5 « La faire revenir » | 1 min 40 | 16:9 + titre | 353 | 220 | 8 | 11,3 s |
| v6 « Plus aucune femme ne pourra t'ignorer » | 2 min 26 | 16:9 + titre | 523 | 225 | 17 | 6,4 s |
| v7 « La porte TIRER » | 2 min 21 | 16:9 + titre | 493 | 220 | 29 | 3,2 s |
| v8 « La zone grise » | 2 min 17 | 16:9 + titre | 518 | 227 | 13 | 6,1 s |
| v9 « Complimenter » | 2 min 35 | 16:9 + titre | 556 | 224 | 45 | 1,8 s |

Toutes les vidéos sont en 576×1024 (téléchargement TikTok), 30 i/s, son AAC stéréo [mesuré]. Le filigrane
« TikTok @klauser.app » et l'écran de fin noir-bleu sont ajoutés par la plateforme : ils ne font pas partie du style.

Dans le format principal (16:9 avec titre), la plupart des changements de plan sont des mouvements de caméra ou des éclairs plutôt que
des coupes franches (121 « éclairs » et 7 mouvements rapides détectés au total) : la durée médiane d'un plan
y est donc surestimée. Le rythme réel ressemble à celui du format A.

## 2. Les deux formats

**Format principal — film 16:9 au format YouTube, avec titre (v3 à v9, 7 vidéos sur 9).** Le film est
fait en 16:9. Sur TikTok, il apparaît dans un bandeau de 1080×608 centré verticalement (de y=656 à 1264 px
en 1080×1920) sur fond noir [mesuré]. Au-dessus, un **titre-promesse** blanc de 1 à 3 lignes
(« Comment complimenter une femme ? ») reste affiché toute la vidéo : c'est l'accroche écrite pour ceux qui
regardent sans le son. Son bas reste à ~581 px, l'interligne est de ~84 px et la largeur de ~810 px [mesuré].
Le même film sert donc tel quel pour YouTube.

Dans le film (positions ramenées en 1920×1080) : croix de cadrage à 58 px des bords, à 88 et 992 px de haut,
sous-titres centrés à 915 px (85 % de la hauteur), bandeau de sous-titre de 94 px [mesuré].

**Format secondaire — vertical natif (v1, v2).** Le film occupe tout le 9:16 : croix à 60 px des bords,
à 141 et 1558 px de haut, sous-titres centrés à 1511 px [mesuré].

## 3. La couleur

- **Un seul accent : vert-jaune `#DCFC1C`** [mesuré], qui devient `#98AC18` dans l'ombre [mesuré].
- **Fond** `#0C0C0C` (de `#080808` à `#141414`) [mesuré] ; noir pur pour les cartes plein écran.
- **Neutres** : blanc cassé `#ECECE8` pour « elle », les papiers et la serif ; gris désaturés pour les décors.
- Image très sombre : luminance moyenne 35 à 43 sur 255 en format A, saturation moyenne 0,05 à 0,08 [mesuré].
- **L'accent est rare** : 1,3 à 1,6 % de l'image en médiane, 4,5 à 5,2 % au 90e centile, et environ 20 % des
  images n'en contiennent pas du tout [mesuré]. Il désigne toujours la même chose : toi, ce qui compte, la réponse.
- Exception volontaire : un **éclair plein écran vert-jaune de 1 à 3 images** sur un mot-choc [mesuré sur v2 à 7,33 s].

## 4. La typographie

| Rôle | Police (estimée) | Taille | Exemple |
| --- | --- | --- | --- |
| Sous-titres | Anton, capitales | ~78 px dans le film 1920×1080 (bandeau de 94 px) [mesuré] | « CE QUI SE PASSE. » |
| Mots-chocs, autocollants | Anton, capitales, avec point final | jusqu'à ~75 % de la largeur [mesuré] | « NON. », « COUPÉE. » |
| Phrases dites ou pensées | Instrument Serif italique, minuscules | hauteur d'x 4,3 % de la largeur [mesuré] | « comment je me débarrasse » |
| Habillage technique | JetBrains Mono gras, capitales espacées (~0,15 em) | capitale 1,75 % de la largeur [mesuré] | « ANALYSE · IMAGE FIGÉE » |
| Chiffres | monospace gras, vert-jaune | grand | « 04,29 s », « 17 % » |
| Titre-promesse (version verticale) | sans-serif demi-gras type Inter 600 | ~70 px en 1080, interligne 84 px [mesuré] | « Comment la faire revenir ? » |

Trois voix typographiques, trois rôles : **Anton = ce que dit la voix off**, **serif italique = ce que
disent ou pensent les personnages**, **monospace = la machine qui analyse la scène**.

Anton et Instrument Serif ne sont pas fournies avec HyperFrames : il faut leurs fichiers `.woff2` dans
`assets/fonts/` avec un `@font-face` (licence OFL, Google Fonts). JetBrains Mono et Inter sont fournies.

## 5. Les sous-titres

- Bandeau blanc cassé `#EEEEEA`, coins carrés, texte quasi noir `#0A0A06` [mesuré] : 94 px de haut, centré à 915 px dans le film 16:9 ; 103 px de haut, centré à 1511 px en vertical natif [mesuré].
- **Mot à mot** : chaque mot apparaît dans l'image où il est prononcé (écart observé : 0 à 2 images) et
  s'ajoute aux précédents ; le bandeau s'élargit d'un coup, sans animation [mesuré sur v1, 45,5 à 48,5 s].
- Le groupe repart de zéro à chaque ponctuation, ou après 4 à 5 mots / ~26 caractères [mesuré].
- La ponctuation reste affichée : le point final donne le ton sec du style.
- Toujours présents, du premier au dernier mot.

## 6. La mise en scène

**Les personnages sont des pictogrammes** de signalétique, jamais des humains réalistes :
- **Toi** : plein vert-jaune, contour noir. C'est le seul personnage en couleur ; le spectateur s'y identifie dès « Ça, c'est toi. »
- **Elle** : blanc cassé, silhouette en robe.
- **Les autres** : noirs à contour blanc ; une foule = des dizaines de ces silhouettes.
- Les visages n'apparaissent que si le texte en parle (un sourire, des yeux fermés qui rient).

**Le décor** : des scènes 3D en gris (café, couloir, porte immense, escalier, rayonnages), avec flou
d'arrière-plan, vignettage et grain. Chaque sujet est sous un **cône de projecteur** venant du haut, avec
une tache de lumière au sol ; tout le reste se perd dans le noir.

**Une métaphore matérielle par vidéo**, qui revient d'un bout à l'autre : le dôme-bouclier (v1), la porte
« TIRER » (v7), la barre de réseau (v8), le rayon de dégustation (v9), le CV (v2), l'escalier et les leviers (v3).

**L'habillage technique** donne l'impression d'une analyse en direct :
- étiquettes en haut à gauche (catégorie en vert-jaune, donnée en gris) et statut en haut à droite (« POV : ELLE », « REC ● ») ;
- équerres de mise au point autour du sujet, traits de légende avec point et étiquette (« TA TÊTE ? ? ? ») ;
- jauges segmentées (« INTÉRÊT 81 % »), compteurs qui défilent, chronomètres, courbes (« SIGNAL · ELLE ») ;
- icônes de lecture (« ▶ PRISE 01 · TOI », « ▌▌ PAUSE », « ◀◀ RETOUR AU DÉBUT ») ;
- comparaisons en deux panneaux empilés.

**Les objets du quotidien** deviennent des preuves : CV, tableau Excel, téléphone et messages, notification,
calendrier, thermomètre. Papier blanc cassé, titre en Anton, détails en monospace, grande croix vert-jaune quand c'est faux.

## 7. Le mouvement et le montage

- **Un changement visuel toutes les ~2 s** (plan, nouvel objet, mouvement) [mesuré : plans médians de 1,7 à 2,2 s en format A].
- **Caméra jamais fixe** : lente avancée sur le sujet pendant le plan, puis recul rapide ou panoramique filé avec
  flou de mouvement pour passer au suivant ; mises au point floues utilisées comme transitions [estimé].
- **On coupe sur le mot** : le changement d'image tombe avec le mot qui l'appelle.
- **Entrées sèches** : étiquettes, autocollants et objets arrivent en 6 à 10 images avec un léger dépassement [estimé].
- **La serif s'écrit avec la voix**, mot à mot, comme les sous-titres.
- **Les chiffres défilent** jusqu'à leur valeur.
- **Le choc** : mot en relief qui s'écrase + éclair vert-jaune de 1 à 3 images + débris + traînées verticales [mesuré sur v2, 6,9 à 7,6 s].

## 8. La voix et le texte

- **Voix off seule, du premier au dernier instant** : elle commence à 0,00 s dans les 9 vidéos et ne fait
  quasiment jamais de pause de plus de 0,4 s [mesuré].
- **Débit très rapide : 220 à 239 mots par minute** [mesuré] (un débit de conversation est autour de 150).
- **Phrases courtes** : 6 à 8 mots en médiane [mesuré], beaucoup de phrases d'un mot (« Non. », « Rien. », « Reste. »).
- **Tutoiement direct**, registre oral familier (« t'as », « un mec », « lâche un like »), questions rhétoriques,
  énumérations par trois (« Moins d'argent, moins de projets, moins de tout. »).
- Je n'ai pas pu mesurer de façon fiable le timbre de la voix (la musique gêne l'analyse) : à vérifier à l'écoute.

### La structure, identique d'une vidéo à l'autre [mesuré]

| Temps | Étape | Exemples tirés des références |
| --- | --- | --- |
| 0 à 3 s | **Accroche** : « toi » à l'écran + une phrase qui pique ou un chiffre | « Ça, c'est toi. », « Elle a choisi un mec qui a la moitié de ce que t'as. », « 89 % des mecs ne le savent pas. » |
| 3 à 25 s | **Scène vécue** : le problème joué, souvent contre « un autre » qui réussit | le café, le mec « pas plus beau que toi » |
| 6 à 32 % de la durée | **Relance** : « Reste. Parce que… » + promesse | « Reste. Parce que dans cette vidéo, je t'explique exactement ce qui se passe. » |
| le cœur | **Le mécanisme** : un concept nommé + sa métaphore visuelle, puis « Exemple. » concret | « Moi, j'appelle ça le bouclier. » |
| ~90 % | **« Retiens ça. »** : la règle en une phrase, sur carte plein écran | « Retiens ça. Dans la zone grise, celui qui court après le réseau le perd. » |
| 97 à 100 % | **Appel à l'action** justifié | « Lâche un like, ça la pousse à ceux qui en ont besoin. », « Lien en bio. », « C'est la partie 2. » |

Durée cible : **1 min 30 à 2 min 30**, soit 350 à 550 mots de script.

## 9. Le son

- **Nappe musicale sombre** dominée par des basses profondes continues (20 à 120 Hz), sous la voix [mesuré au spectrogramme].
- **La musique se retire sur les moments durs** : sur v1, les basses tombent de 17,8 à 21,5 s, exactement sur
  « Deux minutes plus tard, il repart avec son numéro. Toi, t'as toujours ton café » [mesuré].
- Bruitages tonals et souffles sur les transitions [estimé].
- Mixage très fort : −10,8 LUFS intégrés sur v1 [mesuré], la voix toujours devant.

## 10. Comment le produire avec HyperFrames

Deux projets modèles prêts à copier appliquent tout ce qui suit : [`modele/`](modele/README.md) (le film 16:9, version YouTube) et [`modele-vertical/`](modele-vertical/README.md) (titre + film en bandeau, version TikTok/Shorts/Reels).

1. **Script d'abord** : suivre la structure du § 8, 230 mots/min, phrases courtes, une métaphore matérielle.
2. **Voix off** : `/media-use` (HeyGen) ou une voix française locale ; caler le débit autour de 230 mots/min.
   Le worker Edge TTS de ce dépôt (`fr-FR-VivienneMultilingualNeural`) peut aussi servir, avec un débit accéléré.
3. **Transcription mot à mot** : `hyperframes transcribe voix.wav` → les temps de chaque mot pilotent les sous-titres,
   la serif qui s'écrit et les coupes.
4. **Projet** : copier `modele/` (film 1920×1080) ; ou `hyperframes init <nom> --resolution landscape`, puis copier `frame.md` à la racine du projet ;
   le skill `/hyperframes` le lit automatiquement.
5. **Décors** : deux options.
   - **2,5D (recommandé pour commencer)** : arrière-plans gris générés ou photographiés, désaturés et floutés
     avec `hyperframes media-treatment`, plans superposés qui avancent à des vitesses différentes, projecteurs
     en dégradés radiaux, pictogrammes en SVG.
   - **3D** : scènes Three.js en matériaux gris mats (voir la référence `runtimes.md` du skill), plus proche des
     références mais beaucoup plus long à produire.
6. **Bibliothèque** : avant de dessiner un effet à la main (éclair, flou de mouvement, grain, sous-titres mot à mot,
   compteurs), chercher dans le catalogue avec `/hyperframes-registry`.
7. **Musique** : `/media-use` pour une nappe sombre à basses profondes ; prévoir les coupures sur les moments durs.
8. **Contrôle** : `hyperframes check`, puis `hyperframes snapshot --at …` à côté d'une référence
   (`--against`) pour comparer.

## 11. Points à trancher

- **Sous-titres et interface TikTok** : dans le format principal, les sous-titres sont dans le film, donc à
  ~1170 px en vertical, au-dessus de la zone où TikTok affiche sa légende : pas de conflit. Le problème ne se
  pose qu'en format vertical natif (sous-titres à 1511 px).
- **Identité propre** : ce style est la signature visuelle d'un autre créateur (@klauser.app). Reprendre sa grammaire
  (rythme, mise en scène, habillage) est sain ; pour être reconnaissable, il vaut mieux poser notre propre marque
  (nom, logo, éventuellement une nuance d'accent différente) et ne jamais reprendre ses contenus ni ses métaphores telles quelles.
- **Polices** : Anton, Instrument Serif et JetBrains Mono sont les plus proches à l'œil ; les originales ne sont pas identifiées avec certitude.
