# « Ton site crie "fait par l'IA" » : le film 16:9

Vingt-et-unième vidéo (47,6 s), un **conseil** (pilier « expertise », publication du matin). Voix ElevenLabs « Nicolas – Narrator »
de l'utilisateur, script dans `script.txt`.

- **Idée** : un même faux site (IRON CLUB, salle de boxe à Cocody) corrigé point par point :
  violet générique « Révolutionnez votre business » → palette imposée (noir, crème + accent rouge) → vrais textes
  (offre, clients, prix) → nouvelle structure inspirée d'un site qu'on aime (Locomotive).
- Scènes : hook (rafale d'outils IA, mur de 12 vrais sites IA violets identiques, tampon « Fait par l'IA », compteur
  « visiteurs en direct » qui s'effondre, 3 cases « ? ») → 01 Couleurs → 02 Textes → 03 Structure (squelette titre /
  3 cartes / avis qui s'allume, « Copié-collé », site de référence avec ce qu'il faut garder) → avant / après + « Commente PROMPT ».
- Sous le film (vertical) : 3 cases « ? » « Les 3 signes d'un site IA » (Couleurs, Textes, Structure) dévoilées au moment
  où la voix les annonce, validées quand le conseil est donné.
- Fonds : vraies vidéos (outils IA filmés, Mixkit) qui changent tous les 1–2 mots ; captures `site-ia-*` (vrais sites
  générés par IA) reprises de `skills-design`.
- Musiques Mixkit (Need for Speed, Hip Hop 02, Complicated), ≈ 5,6 dB sous la voix ; 162 bruitages.

**Après la publication** : répondre aux commentaires « PROMPT » avec le prompt complet (couleurs + vraies infos + site de référence).

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py /tmp/corelink
hyperframes check
hyperframes render . -o renders/site-fait-par-ia-16x9.mp4   # commande séparée
```
