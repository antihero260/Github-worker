# Consignes pour Claude dans ce dépôt

Ce dépôt contient le worker vocal Edge TTS de LeCodeIA (`worker.py`, workflow GitHub Actions) **et** la
production de vidéos avec HyperFrames (`hyperframes-style/`, `videos/`, `scripts/install-hyperframes.sh`).

**Avant toute chose, lire :**
- [`SUIVI.md`](SUIVI.md) : où on en est, décisions prises, prochaines étapes.
- [`hyperframes-style/PROCESSUS-VIDEO.md`](hyperframes-style/PROCESSUS-VIDEO.md) : la marche à suivre pour faire une vidéo.

## Exigences de l'utilisateur (à respecter sans qu'il ait à les redire)

- Répondre en **français**, simplement et directement.
- **Livrable vidéo = une seule vidéo verticale 1080×1920** : titre-promesse blanc en haut, film 16:9 dans un
  bandeau au centre (format de ses vidéos de référence). Ne jamais envoyer le film 16:9 intermédiaire.
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
- **Des vraies vidéos qui choquent visuellement TOUT AU LONG de la vidéo, pas seulement dans le hook** (demande pour la vidéo 11 : « pour empêcher les gens de partir, il faut aussi les choquer visuellement avec beaucoup de vidéos tout au long ») : derrière chaque scène, une rafale de vraies vidéos/photos qui change tous les 1–2 mots (`rafale_mots()`), les éléments (panneaux, personnage, textes) par-dessus.
- **Du mystère, révélation progressive** (demande pour la vidéo 13) : ne jamais montrer toute la liste d'un coup. Les points
  restent cachés (cases verrouillées « ? » sous le film, cartes floutées) et se dévoilent un par un, au moment où la voix les
  annonce, avec un bruitage de révélation.
- **Plus de suivi de caméra** (vidéo 13) : la caméra suit le personnage et les éléments qui bougent (panoramiques qui accompagnent
  les déplacements, recadrages successifs), pas seulement des zooms fixes.
- **Exception de la vidéo 18 seulement** (edit rythmé « POV : l'IA a codé mon site ») : aucun texte dans le film, pas de voix, son choisi par l'utilisateur (vidéo de référence). Après cette vidéo, **tout redevient comme d'habitude** (voix, sous-titres, mots qui claquent, cases mystère, musiques Mixkit).
- Le style peut varier d'une vidéo à l'autre si l'utilisateur le demande (vidéo 7 : style « Alerte », voir `videos/site-conforme/README.md`), en gardant le format vertical, les personnages qui bougent et les recadrages.
- **Tout vérifier et corriger avant de lancer un rendu** : `hyperframes check` sans erreur, puis regarder les
  images clés. Ne jamais lancer le rendu dans la même commande que le contrôle.
- **Nouvelle niche depuis novembre 2026 : vulgarisation financière** (l'utilisateur a une formation d'actuaire, mais **ne jamais le dire publiquement** : ni en bio, ni dans les vidéos, ni dans les textes). Exemples en FCFA, petits constats chiffrés, chaque chiffre vérifié à la source (INS, BCEAO) ; jamais de conseil d'investissement personnalisé. **Ne jamais montrer de jeux d'argent (casino, paris, tickets de pari), même pour les critiquer : la vidéo 2 sur les paris sportifs a reçu un avertissement TikTok et a été supprimée.** Les sites web sont arrêtés pour l'instant. Même outil (HyperFrames). **Couleur de la chaîne finance « Lefinancier » : bleu ciel #38BDF8 sur bleu nuit #0B1220, plus de jaune citron ni de vert** (personnage en bleu ciel, pièces dorées).
- Mettre à jour `SUIVI.md` à chaque étape importante.
