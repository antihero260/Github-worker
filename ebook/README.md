# Ebook « Crée tes vidéos TikTok avec l'IA »

Formation grand public v3 (37 pages A5) : fabrication de vidéos avec Claude Code + HyperFrames, Opus 5.5 en effort « Élevé », 52 prompts. Charte : Inter (texte) + Anton (titres), interligne 1,2, titres de section à 17 pt, palette noir / violet / jaune citron, encadré « Dans ce chapitre » en tête de chaque étape. Couverture refaite (titre géant, personnage vert vectoriel, téléphone), testée en miniature 150 px et en niveaux de gris ; image de couverture : couverture-ebook.jpg. Texte relu avec le skill Humanizer (non mentionné dans l'ebook).

- `ebook.tex` : la source (XeLaTeX, polices Inter + Anton, encadrés tcolorbox, schéma TikZ).
- `images/` : captures annotées (cercles rouges + pastilles numérotées) et images de la vidéo 21.
- `captures-brutes/` + `annoter.py` : captures d'origine (Playwright) et script d'annotation.
- `polices/` : Anton (SIL OFL) convertie en TTF.
- Livrable : `Cree-tes-videos-TikTok-avec-l-IA.pdf`.

Compiler : `xelatex ebook.tex` deux fois (sommaire). Dépend de `texlive-xetex texlive-latex-extra texlive-lang-french fonts-inter`.
Crédits : GitHub Docs (CC BY 4.0) pour les 2 images GitHub ; GitHub, la page de connexion Claude et TikTok bloquent les robots :
pas de contournement, d'où les images de la documentation GitHub.
