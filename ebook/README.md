# Ebook « Crée tes vidéos TikTok avec l'IA »

Formation grand public (28 pages A5, français), centrée sur ce que fait le lecteur et sur plus de 40 prompts prêts à copier ; GitHub seulement pour le téléphone. Texte relu avec le skill Humanizer (github.com/blader/humanizer, installé dans ~/.claude/skills/humanizer) : pas de tirets longs, pas de formules « pas X mais Y », peu de gras décoratif tirée du document Claude Docs « Formation : créer tes vidéos avec Claude Opus 5.5 ».

- `ebook.tex` : la source (XeLaTeX, polices Inter + Anton, encadrés tcolorbox, schéma TikZ).
- `images/` : captures annotées (cercles rouges + pastilles numérotées) et images de la vidéo 21.
- `captures-brutes/` + `annoter.py` : captures d'origine (Playwright) et script d'annotation.
- `polices/` : Anton (SIL OFL) convertie en TTF.
- Livrable : `Cree-tes-videos-TikTok-avec-l-IA.pdf`.

Compiler : `xelatex ebook.tex` deux fois (sommaire). Dépend de `texlive-xetex texlive-latex-extra texlive-lang-french fonts-inter`.
Crédits : GitHub Docs (CC BY 4.0) pour les 2 images GitHub ; GitHub, la page de connexion Claude et TikTok bloquent les robots :
pas de contournement, d'où les images de la documentation GitHub.
