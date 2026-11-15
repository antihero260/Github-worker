# Consignes pour Claude dans ce dépôt

Ce dépôt contient le worker vocal Edge TTS de LeCodeIA (`worker.py`, workflow GitHub Actions) **et** la
production de vidéos avec HyperFrames (`hyperframes-style/`, `videos/`, `scripts/install-hyperframes.sh`).

**Avant toute chose, lire :**
- [`SUIVI.md`](SUIVI.md) : où on en est, décisions prises, prochaines étapes.
- [`hyperframes-style/PROCESSUS-VIDEO.md`](hyperframes-style/PROCESSUS-VIDEO.md) : la marche à suivre pour faire une vidéo.

## Exigences de l'utilisateur (à respecter sans qu'il ait à les redire)

- Répondre en **français**, simplement et directement.
- **Livrable vidéo = une seule vidéo verticale 1080×1920.** Depuis la vidéo 4 de Lefinancier (13 nov. 2026 : « je veux des
  vidéos verticales, plus d'horizontal »), **tout est composé directement en 1080×1920**, sans film 16:9 dans un bandeau.
  Titre blanc en haut, sous-titres vers y = 1400. Modèle : `videos/tontine-epargne` (générateur autonome + `tools/styles.css`).
- **Scènes de Lefinancier depuis la vidéo 4** : personnages **verticaux et bleus** (bleu ciel, bleu clair, bleu profond,
  distingués par chignon, casquette, mèche), **décors dessinés** (rue, chambre, cercle de la tontine), **bulles de dialogue**,
  éléments dans la scène (téléphone avec messages, appels entrants, calendrier, caisse, cartes de compte, cases mystère).
  **Plus de vidéos en arrière-plan des personnages** : une vraie vidéo se montre DANS la scène (écran vertical, télé,
  bulle de pensée, panneau) et **la caméra zoome dessus** jusqu'à remplir l'image, puis ressort.
- Style « Projecteur » : [`hyperframes-style/frame.md`](hyperframes-style/frame.md).
- **Les personnages doivent bouger** (marcher, pointer, lever les bras, réagir) et la caméra doit recadrer
  pendant les scènes. Des pictogrammes figés ne sont pas acceptables.
- **Musique bien audible mais pas trop** : 3 morceaux (un par partie). Réglage validé : environ **5–6 dB sous la
  voix** (musique ≈ −21 LUFS pour une voix à −15 ; `data-volume` 0,63 sur des fichiers à −16,9). Historique : 12 dB
  = inaudible ; 3–4 dB (vidéo 3) = un peu trop fort, « c'est la musique qu'il faut baisser » ; les bruitages, eux, sont bons. **Retirer la baisse automatique du carve**
  (voir `videos/clavier-ia/tools/mixage.py` et `SUIVI.md`) : sinon la musique tombe 9–12 dB sous la voix.
- **Bruitages obligatoires et nombreux** : un rush/souffle à chaque recadrage et transition, impacts, risers, clavier,
  clics, pops, apparitions… (vidéo 3 : environ 150 sons pour 96 s).
- **Beaucoup d'illustrations, surtout de vraies vidéos** (demande après la vidéo 3) : vidéo 4 = 21 vidéos Mixkit pour
  130 s, plus logos et interfaces animées (fenêtre d'application, pointeur de souris, workflow, conversations).
- **Musiques à la mode et libres de droits** (retour sur la vidéo 5 : « les musiques ne sont pas du tout bonnes ») :
  prendre les morceaux **les plus téléchargés** de Mixkit et des styles actuels (hip-hop urbain, trap, house), pas des
  morceaux choisis seulement d'après leur nom. NCS est tendance mais impose un crédit en description : à proposer
  seulement si l'utilisateur l'accepte.
- **Sons et images téléchargés sur Internet** quand c'est possible (demande de l'utilisateur) : Mixkit (gratuit,
  sans crédit) pour musiques, bruitages et vraies vidéos ; logos officiels avec `media-use resolve --type logo`.
- **Hook visuel fort dès la première seconde** (retour sur la vidéo 6 : « un hook visuel est très important, captiver visuellement dès le début c'est fort ») : rafale ou mosaïque de vraies vidéos qui change sur chaque mot, gros bruitages.
- **Le hook doit être plein de vraies vidéos et images d'Internet** (retour sur la vidéo 9 : « ton dernier hook ne me plaisait pas trop… mets les vidéos, ça ne manque pas sur Internet, et les images ; d'ailleurs augmente ») : pas un hook fait seulement d'interfaces dessinées ou codées. Au moins 15–20 vraies vidéos/photos dans les premières secondes, une par mot.
- **Des vraies vidéos qui choquent visuellement TOUT AU LONG de la vidéo, pas seulement dans le hook** (demande pour la vidéo 11 : « pour empêcher les gens de partir, il faut aussi les choquer visuellement avec beaucoup de vidéos tout au long ») : derrière chaque scène, une rafale de vraies vidéos/photos qui change tous les 1–2 mots (`rafale_mots()`), les éléments (panneaux, personnage, textes) par-dessus. **Remplacé pour Lefinancier depuis la vidéo 4** : les vraies vidéos restent nombreuses mais dans des écrans de la scène avec zoom (voir plus haut) ; le hook garde une rafale plein cadre.
- **Du mystère, révélation progressive** (demande pour la vidéo 13) : ne jamais montrer toute la liste d'un coup. Les points
  restent cachés (cases verrouillées « ? » sous le film, cartes floutées) et se dévoilent un par un, au moment où la voix les
  annonce, avec un bruitage de révélation.
- **Plus de suivi de caméra** (vidéo 13) : la caméra suit le personnage et les éléments qui bougent (panoramiques qui accompagnent
  les déplacements, recadrages successifs), pas seulement des zooms fixes.
- **Exception de la vidéo 18 seulement** (edit rythmé « POV : l'IA a codé mon site ») : aucun texte dans le film, pas de voix, son choisi par l'utilisateur (vidéo de référence). Après cette vidéo, **tout redevient comme d'habitude** (voix, sous-titres, mots qui claquent, cases mystère, musiques Mixkit).
- Le style peut varier d'une vidéo à l'autre si l'utilisateur le demande (vidéo 7 : style « Alerte », voir `videos/site-conforme/README.md`), en gardant le format vertical, les personnages qui bougent et les recadrages.
- **Tout vérifier et corriger avant de lancer un rendu** : `hyperframes check` sans erreur, puis regarder les
  images clés. Ne jamais lancer le rendu dans la même commande que le contrôle.
- **Nouvelle niche depuis novembre 2026 : vulgarisation financière** (l'utilisateur a une formation d'actuaire, mais **ne jamais le dire publiquement** : ni en bio, ni dans les vidéos, ni dans les textes). Exemples en FCFA, petits constats chiffrés, chaque chiffre vérifié à la source (INS, BCEAO) ; jamais de conseil d'investissement personnalisé. **Ne jamais montrer de jeux d'argent (casino, paris, tickets de pari), même pour les critiquer : la vidéo 2 sur les paris sportifs a reçu un avertissement TikTok et a été supprimée.** Les sites web sont arrêtés pour l'instant. Même outil (HyperFrames). **Scripts en mode storytelling** (demande du 12 nov. 2026) : raconter une histoire avec des personnages inventés aux **prénoms non africains** (ex. Emma et Julie, Tom et Hugo ; demande de l'utilisateur), un mystère et une chute, plutôt qu'une explication directe. **Couleur de la chaîne finance « Lefinancier » : bleu ciel #38BDF8 sur bleu nuit #0B1220, plus de jaune citron ni de vert** (personnage en bleu ciel, pièces dorées).
- **Scripts de Lefinancier écrits par une autre IA** (depuis le 13 nov. 2026, l'utilisateur trouve mon storytelling faible) : il utilise `finance/prompt-storytelling.txt` (page pour copier en un clic : `finance/prompt-storytelling.html`) et m'envoie le texte et sa voix ; je fais le montage.
- **Clarté avant tout** (retour du 14 nov. 2026 : « à part le titre c'est difficile de savoir de quoi parle la vidéo », « trop de chiffres », « pas de sujet qui cartonne ») : dans le montage, **le sujet doit être écrit en clair à l'écran dans les 3 premières secondes** (carte-sujet), **3 chiffres au maximum affichés** (pas de tableaux de calculs), **la règle à retenir écrite à l'écran à la fin**. Les sujets viennent de `finance/sujets-qui-cartonnent.txt` (des sujets vécus : arnaques, fin du mois, crédit téléphone, tontine…). Prompt version 3 : `finance/prompt-storytelling.txt`.
- **Fin claire : on doit savoir quoi retenir** (demande du 15 nov. 2026, après la vidéo 6) : le prompt v3 impose une fin en 4 temps (réponse à la question du début → « Retiens ça : » + règle de 12 mots maximum, affirmative, sans « pas toujours » → « À faire : » + un geste simple, gratuit, faisable aujourd'hui → abonne-toi + question). Dans le montage, **carte de fin à deux blocs « À RETENIR » / « À FAIRE »**, chaque phrase écrite mot pour mot comme dans la voix, révélée au moment où la voix la dit et **tenue au moins 3 s** (elle peut rester sous la carte d'abonnement).
- Mettre à jour `SUIVI.md` à chaque étape importante.
