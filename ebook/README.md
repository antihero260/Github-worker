# Ebook « Crée tes vidéos TikTok avec l'IA »

Formation grand public v2.0 (36 pages A5, français) : Claude Code + Opus 5.5 (abonnement obligatoire), application mobile (menu Code), installation d'HyperFrames et de Humanizer par prompt, notre style avec le personnage vert, copier un style, vidéos libres qui collent au texte, plus de 50 prompts, bilan à chaque chapitre, dépannage. Texte relu avec Humanizer.

- `ebook.tex` : la source (XeLaTeX, polices Inter + Anton, encadrés tcolorbox, schéma TikZ).
- `images/` : captures annotées (cercles rouges + pastilles numérotées) et images de la vidéo 21.
- `captures-brutes/` + `annoter.py` : captures d'origine (Playwright) et script d'annotation.
- `polices/` : Anton (SIL OFL) convertie en TTF.
- Livrable : `Cree-tes-videos-TikTok-avec-l-IA.pdf`.

Compiler : `xelatex ebook.tex` deux fois (sommaire). Dépend de `texlive-xetex texlive-latex-extra texlive-lang-french fonts-inter`.
Crédits : GitHub Docs (CC BY 4.0) pour les 2 images GitHub ; GitHub, la page de connexion Claude et TikTok bloquent les robots :
pas de contournement, d'où les images de la documentation GitHub.
