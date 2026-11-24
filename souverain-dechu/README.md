# Souverain Déchu

Beat'em up de cultivation en 2,5D (personnages et décors en 3D, gameplay sur un plan 2D), jouable dans le navigateur. Inspiré des récits de xianxia où un maître démoniaque trahi renaît dans un corps faible. Les personnages, les noms et l'histoire sont originaux.

## Lancer le jeu

Ouvre `index.html` dans un navigateur récent. Une connexion est nécessaire pour charger Three.js (cdnjs) et les polices Google Fonts. Aucune installation, aucun build.

## Commandes

| Action | Clavier | Tactile |
| --- | --- | --- |
| Se déplacer | ← → ou Q D | croix à gauche |
| Sauter / double saut | Espace, ↑, Z | 跃 |
| Attaque (combo 3 coups, combo aérien) | J | 攻 |
| Paume lourde / plongeon en l'air | K | 重 |
| Esquive (invulnérable) | L ou Maj | 闪 |
| Paume des Neuf Abîmes (25 Qi) | U | 掌 |
| Dévoreur d'âmes (45 Qi, royaume 筑基) | I | 噬 |
| Éveil du Souverain (Démon intérieur plein, royaume 金丹) | O | 皇 |
| Pause | Échap ou P | bouton II |

## Contenu

- 3 chapitres : la Cour du Clan Su, la Forêt des Bêtes Spirituelles, le Pic du Givre Éternel.
- 3 boss avec des attaques annoncées : Hu Ba (charge, saut fracassant, rage à 50 %), l'Ancienne Mei (pétales, lotus, téléportation), Yan Shuang (ruées, vagues de glace, pluie d'épées, phase 2 avec dialogue).
- 4 royaumes de cultivation (炼气 → 筑基 → 金丹 → 元婴). L'essence des ennemis vaincus fait percer au royaume suivant, ce qui augmente la vie et les dégâts et débloque des techniques.
- Jauge du Démon intérieur : elle se remplit au combat et déclenche l'Éveil du Souverain (dégâts ×1,8, armure, vagues de sang).
- Sauvegarde locale du chapitre atteint (bouton Continuer) et reprise au boss après une défaite.

## Images générées (facultatif)

Le jeu peut afficher des décors peints, des portraits de dialogue, une illustration d'écran titre et des textures de sol. Les prompts et les noms de fichiers sont dans [`PROMPTS-IMAGES.md`](PROMPTS-IMAGES.md). Dépose les images dans `assets/` : chaque image absente laisse le rendu procédural en place.

## Technique

Un seul fichier HTML. Three.js r128 pour le rendu toon avec contours, les ombres et les particules. Les personnages sont construits à partir de primitives et animés de façon procédurale. Les sons et la musique pentatonique sont synthétisés avec Web Audio. Aucun fichier image ou son externe.

Le bloc entre `<!-- ARTIFACT-START -->` et `<!-- ARTIFACT-END -->` est le contenu publié tel quel comme page Artifact.
