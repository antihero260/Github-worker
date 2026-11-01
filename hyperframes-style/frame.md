---
version: 1
name: Projecteur — style maison (vidéo verticale)
description: >
  Explication en voix off rapide, racontée en pictogrammes sous des projecteurs, dans un décor gris
  presque noir. Une seule couleur d'accent, un vert-jaune électrique, réservée au héros (« toi ») et à
  l'information clé. Sous-titres mot à mot en capitales condensées sur un bandeau blanc, habillage
  d'interface technique (croix de cadrage, étiquettes en monospace, compteurs) et phrases dites en
  serif italique. Les valeurs marquées [mesuré] viennent des 9 vidéos de référence ; [estimé] = lu à
  l'œil, à confirmer.
unit: "1080×1920 à 30 i/s (format A, natif vertical). Format B : film 16:9 dans un bandeau au centre."
principle: un seul accent · la caméra ne s'arrête jamais · un changement visuel toutes les 2 s

colors:
  ground: "#0C0C0C"          # [mesuré] fond des décors (#080808 à #141414)
  void: "#000000"            # [mesuré] noir pur : cartes plein écran, bandes du format B
  accent: "#DCFC1C"          # [mesuré] vert-jaune éclairé : « toi », chiffres clés, autocollants
  accent-shade: "#98AC18"    # [mesuré] le même accent dans l'ombre (hors du projecteur)
  accent-glow: "rgba(220,252,28,0.35)"  # [estimé] halo des mots-chocs
  light: "#ECECE8"           # [mesuré] « elle », texte serif, papiers
  caption-box: "#EEEEEA"     # [mesuré] bandeau des sous-titres
  caption-ink: "#0A0A06"     # [mesuré] texte des sous-titres
  grey-900: "#1A1A1A"        # [estimé] rampe de gris du décor, de l'ombre…
  grey-700: "#2E2E2E"
  grey-500: "#4A4A4A"
  grey-300: "#7A7A7A"
  grey-100: "#A8A8A8"        # …à la lumière du projecteur
  hud-grey: "#9A9A9A"        # [estimé] 2e ligne des étiquettes techniques
  cross: "#D9D9D9"           # [estimé] croix de cadrage
  hairline: "rgba(255,255,255,0.06)"  # [estimé] lignes de grille quasi invisibles

typography:
  # cqw = % de la largeur de l'image (1 cqw = 10,8 px en 1080 de large)
  caption:  { fontFamily: "Anton", cqw: 7.8, weight: 400, upper: true, lineHeight: 1.0 }   # [mesuré] hauteur de capitale 6,7 cqw ; police [estimé]
  impact:   { fontFamily: "Anton", cqw: 30, weight: 400, upper: true, lineHeight: 0.9 }    # mot-choc plein écran, ~75 % de la largeur [mesuré]
  sticker:  { fontFamily: "Anton", cqw: 6.5, weight: 400, upper: true }                    # [estimé]
  stat:     { fontFamily: "JetBrains Mono", cqw: 7, weight: 700 }                          # chiffres et compteurs [estimé]
  voice:    { fontFamily: "Instrument Serif", cqw: 8.5, style: italic, weight: 400, lineHeight: 1.1 }  # [estimé] hauteur d'x mesurée 4,3 cqw
  bubble:   { fontFamily: "Instrument Serif", cqw: 4, style: italic, weight: 400 }        # [estimé]
  label:    { fontFamily: "JetBrains Mono", cqw: 2.4, weight: 700, upper: true, tracking: "0.15em" }  # [estimé] capitale mesurée 1,75 cqw
  hook:     { fontFamily: "Inter", cqw: 4.8, weight: 600, lineHeight: 1.2 }                # titre du format B [estimé]

spacing:
  frame-x: "60px"          # [mesuré] croix de cadrage à 5,6 % des bords gauche/droit
  frame-top: "141px"       # [mesuré] 7,3 % de la hauteur
  frame-bottom: "1558px"   # [mesuré] 81,2 % de la hauteur : rien d'important en dessous
  label-x: "84px"          # [mesuré]
  label-top: "206px"       # [mesuré]
  caption-center-y: "1511px"  # [mesuré] 78,7 % de la hauteur
  band-top: "656px"        # [mesuré] format B : bandeau 1080×608 centré verticalement
  band-height: "608px"

components:
  caption:
    box: "{colors.caption-box}, coins carrés, hauteur 103 px [mesuré], marge interne 15 px × 19 px"
    text: "{typography.caption} en {colors.caption-ink}"
    placement: "centré horizontalement, centre à {spacing.caption-center-y} ; format B : en bas du bandeau"
    behavior: >
      Mot à mot : chaque mot apparaît à l'image où il est prononcé (à ±2 images près) et s'ajoute au groupe ;
      le bandeau s'élargit d'un coup, sans animation. Le groupe repart de zéro à la ponctuation ou au-delà de
      4 à 5 mots / 26 caractères [mesuré]. La ponctuation est gardée (« CE QUI SE PASSE. »).
  frame-guides:
    crosses: "4 croix « + » aux coins du cadre {spacing.frame-x} / {spacing.frame-top} / {spacing.frame-bottom}, branches de 20 px, trait de 2 px, {colors.cross}"
    hairlines: "lignes de 1 px {colors.hairline} passant par les croix, sur toute la hauteur et la largeur"
    description: "Présentes sur presque tous les plans ; absentes des cartes plein écran."
  hud-label:
    left: "2 lignes en haut à gauche : catégorie en {colors.accent} (« ANALYSE · IMAGE FIGÉE ») + donnée en {colors.hud-grey} (« DURÉE : 00:00,1 »)"
    right: "statut en haut à droite : « POV : ELLE » avec un œil, « REC ● », « 100 % », « COMPARAISON… »"
    typography: "{typography.label}"
  characters:
    toi: "pictogramme plein {colors.accent}, contour noir de 4 px ; le seul personnage en couleur"
    elle: "pictogramme {colors.light} en robe (silhouette de signalétique)"
    les-autres: "pictogrammes noirs à contour blanc de 3 px ; la foule = les mêmes en petit, répétés"
    faces: "aucun trait, sauf un sourire ou des yeux fermés quand le texte en parle"
  spotlight:
    description: >
      Cône de lumière blanche venant du haut (10 à 20 % d'opacité, bords flous) et tache elliptique au sol
      sous le sujet. Le sujet est toujours sous un projecteur ; le reste tombe dans le noir.
  set:
    description: >
      Décors 3D en gris désaturés (café, couloir, porte, escalier, scène), flous en arrière-plan
      (profondeur de champ), vignettage et grain. Saturation moyenne 0,05 à 0,08 [mesuré].
  sticker:
    shape: "rectangle {colors.accent}, incliné de −3° à −6°, texte {typography.sticker} noir avec point final (« COUPÉE. », « OUBLIÉ. », « PRÊT. »)"
    motion: "arrive en 6 à 8 images avec dépassement (back.out)"
  callout:
    description: "trait fin {colors.accent} terminé par un point sur le sujet + étiquette {typography.label} (« TA TÊTE / ? ? ? »)"
  viewfinder:
    description: "4 équerres {colors.accent} de 3 px autour du sujet (mise au point), parfois avec une jauge (« ASSURANCE 29 % »)"
  voice-line:
    description: >
      Phrase prononcée ou pensée, en {typography.voice} {colors.light}, en haut à gauche, qui s'écrit mot à
      mot avec la voix. Un mot clé souligné ou barré d'un trait {colors.accent}.
  bubble:
    description: "petit rectangle blanc avec une pointe, texte {typography.bubble} noir (« salut ! t'es d'ici ? »)"
  paper:
    description: "document blanc cassé (CV, tableau Excel, notification, téléphone) : titre en Anton, détails en monospace ; barré d'une grande croix {colors.accent} quand il a tort"
  stat:
    description: "chiffre clé en {typography.stat} {colors.accent} qui défile jusqu'à sa valeur (« 17 % », « 8 412 977 », « 00:00 »), avec une étiquette au-dessus"
  split:
    description: "deux panneaux empilés à bord gris de 2 px, « ▶ PRISE 01 · TOI » / « ▶ PRISE 02 · L'AUTRE », titre « COMPARAISON… »"
  impact-card:
    description: >
      Fond {colors.void}, un seul mot en {typography.impact} {colors.accent} avec halo {colors.accent-glow}
      (« NON. », « RETIENS ÇA. »), ou blanc. Variante : mot blanc en relief 3D qui s'écrase, avec 1 à 3
      images entièrement {colors.accent}, des débris et des traînées verticales vert-jaune.
  hook-title:
    description: "format B seulement : titre-promesse blanc {typography.hook} sur 2 à 3 lignes, centré, juste au-dessus du bandeau"
---

# Projecteur — style maison

## Ce que le style doit produire

Une démonstration qui avance aussi vite que la voix : chaque phrase a son image, chaque idée a son objet.
Le spectateur se reconnaît dans le pictogramme vert-jaune (« toi ») et comprend un mécanisme invisible
grâce à une métaphore matérielle (un bouclier, une porte, une zone grise, une barre de réseau).

## À faire

- Le pictogramme « toi » est à l'écran dès l'image 0, sous un projecteur.
- Une seule couleur d'accent ; elle couvre environ 1,5 % de l'image en médiane et 5 % au plus (90e centile) [mesuré]. Une image sur cinq n'en contient pas.
- La caméra bouge toujours : lente avancée sur chaque plan, recul rapide ou panoramique filé pour passer au plan suivant.
- Chaque mot dit s'affiche à l'instant où il est dit.
- Les mots-chocs (« Non. », « Rien. », « Retiens ça. ») ont une carte plein écran.
- Les chiffres sont précis et défilent (« 8 412 977 », « 04,29 s »), même quand ils sont imaginaires : c'est l'esthétique « tableau de bord ».

## À ne pas faire

- Pas de deuxième couleur vive, pas de dégradé coloré, pas de photo en couleur.
- Pas de visage réaliste : uniquement des pictogrammes.
- Pas de plan fixe de plus de 3 s sans mouvement ni nouvel élément.
- Pas de texte de lecture en dehors des sous-titres, des étiquettes techniques et des phrases en serif.
- Pas de silence : la voix commence à l'image 0 et la musique ne s'arrête que pour souligner un moment.
- Ne pas reprendre le filigrane TikTok ni l'écran de fin TikTok vus dans les références : la plateforme les ajoute elle-même.
