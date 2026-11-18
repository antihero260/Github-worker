# Ebook « Crée tes vidéos TikTok avec l'IA »

**Version 2.2 (18 nov. 2026)** : la v2.1 simplifiée pour des débutants (principe Gausscode : le lecteur n'a pas besoin de comprendre la technologie pour réussir). On garde seulement les corrections qui évitent un échec ou un problème (dépôt privé, installation HyperFrames en un prompt copiable, « Enregistre tout sur GitHub », télécharger la vidéo par un lien, lire avant d'autoriser, Mixkit Free License dans le prompt, ElevenLabs gratuit non commercial) ; explications sur les branches, le cloud, les compétences et les licences retirées ; une seule phrase de prudence sur les droits (« avant d'utiliser une musique ou une vidéo, vérifie qu'elle est autorisée pour ton usage… ») ; le détail des licences et les liens officiels sont dans la page finale « Pour aller plus loin ». 42 pages, 57 prompts. Livrable : `Gausscode-Cree-tes-videos-avec-l-IA-v2.2.pdf`.

**Version 2.1 (18 nov. 2026, marque Gausscode)** : corrections après une relecture critique faite par une autre IA, chaque point vérifié à la source avant correction. 46 pages, 56 prompts. (PDF v2.1 retiré, voir l'historique git.)
- Licences : « libre de droits » redéfini ; Mixkit Free License / Restricted License (non commercial) ; ElevenLabs gratuit = pas d'usage commercial + crédit, clonage professionnel réservé à sa propre voix ; sons TikTok (bibliothèque générale vs CML, pas d'usage hors TikTok) ; Pexels ; bruitages ; logos et personnes ; fichier `sources.txt` demandé dans les prompts ; tableau « Les licences en bref ».
- Installation HyperFrames refaite (plugin Claude Code `claude plugin marketplace add heygen-com/hyperframes` + `claude plugin install hyperframes@hyperframes`, ou `npx skills add heygen-com/hyperframes` ; Node.js 22+ et FFmpeg, `npx hyperframes doctor`) ; prompt `/style-sampling` retiré (compétence HyperFrames Pro qui fait autre chose).
- Téléphone : dépôt GitHub **privé**, accès de l'app Claude limité au dépôt, fonctionnement des sessions cloud (ordinateur temporaire, branche, pull request facultative), récupération du MP4 (< 100 Mo).
- Autorisations : « accepte » remplacé par « lis, et demande une explication si tu ne comprends pas ».
- Budget et limites d'utilisation, estimation de temps nuancée, ChatGPT présenté comme un choix personnel, vérification des faits avec citation de la source, version YouTube recomposée, version sobre du style, dépannage élargi + méthode en 5 étapes, lexique complété, page « Ressources officielles » avec liens cliquables, crédits GitHub Docs précisés (titre, lien, licence, annotations).

Formation grand public v3.3 (36 pages A5 ; 4 miniatures verticales refaites (dossier miniatures/, générées en HTML + Playwright à partir de vidéos Mixkit) et section « Des miniatures qui donnent envie » ; chapitre 3 illustré par la vidéo d'un autre créateur (exemple inventé, style crème) et la même vidéo refaite dans ce style ; planche de style pleine page au chapitre 2 et personnage en trois couleurs ; relecture complète page par page, aucun débordement ; texte de la voix écrit avec ChatGPT ; page « Ce que tu sauras faire » avec galerie de 5 téléphones et vidéo annotée) : fabrication de vidéos avec Claude Code + HyperFrames, Opus 5.5 en effort « Élevé », 53 prompts. Charte : Inter (texte) + Anton (titres), interligne 1,2, titres de section à 17 pt, palette noir / violet / jaune citron, encadré « Dans ce chapitre » en tête de chaque étape. Couverture refaite (titre géant, personnage vert vectoriel, téléphone), testée en miniature 150 px et en niveaux de gris ; image de couverture : couverture-ebook.jpg. Texte relu avec le skill Humanizer (non mentionné dans l'ebook).

- `ebook.tex` : la source (XeLaTeX, polices Inter + Anton, encadrés tcolorbox, schéma TikZ).
- `images/` : captures annotées (cercles rouges + pastilles numérotées) et images de la vidéo 21.
- `captures-brutes/` + `annoter.py` : captures d'origine (Playwright) et script d'annotation.
- `polices/` : Anton (SIL OFL) convertie en TTF.
- Livrable : `Lecodeur-Cree-tes-videos-avec-l-IA.pdf`.

Compiler : `xelatex ebook.tex` deux fois (sommaire). Dépend de `texlive-xetex texlive-latex-extra texlive-lang-french fonts-inter`.
Crédits : GitHub Docs (CC BY 4.0) pour les 2 images GitHub ; GitHub, la page de connexion Claude et TikTok bloquent les robots :
pas de contournement, d'où les images de la documentation GitHub.
