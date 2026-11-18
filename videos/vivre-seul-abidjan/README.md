# Lefinancier : « Combien ça coûte vraiment de vivre seul à Abidjan ? »

Version longue et approfondie (2 min 10), format vertical natif 1080×1920, même méthode que `videos/enveloppes`.

- **Texte et voix.** Texte écrit par une autre IA avec le prompt approfondi `finance/prompt-vivre-seul-abidjan.txt`,
  voix MiniMax de l'utilisateur (`assets/audio/voix-brute.mp3`, normalisée à −15 LUFS dans `voix.mp3`).
  `script.txt` = le texte lu (orthographe corrigée), aligné mot à mot sur la transcription Parakeet → `assets/mots.json`.
- **Chiffres de la voix (vérification du 18 nov. 2026).**
  - SMIG 75 000 F : correct.
  - « La loi encadre ces sommes. Deux mois de loyer au total » : **inexact**. La loi plafonne à 2 mois de caution ET
    2 mois d'avance (Fratmat, Koaci). À l'écran : « CAUTION + AVANCE, ENCADRÉES PAR LA LOI », sans « 2 mois ».
  - « 114 000 F de revenu moyen chez les jeunes salariés d'Abidjan (OIT) » : **source introuvable** ; la Banque mondiale
    donne environ 120 000 F de salaire moyen en Côte d'Ivoire.
  - « 196 000 à Cocody » : **erreur de calcul** (300 000 − 114 000 = 186 000).
  - Correction proposée à l'utilisateur (voix MiniMax à régénérer) ; montage fait avec la voix reçue.
- **Scènes (13).** Hook en vraies vidéos plein cadre + carte-sujet « VIVRE SEUL À ABIDJAN / COMBIEN ÇA COÛTE VRAIMENT ? » ;
  studio à louer (Lucas, bulle de pensée) ; deux quartiers avec écrans et prix qui défilent (65 000 / 110 000) ;
  caution et avance (propriétaire, bulle, bail, matelas) ; commission du démarcheur, liste d'achats cochée mot à mot,
  cases mystère du coût d'entrée (400 000 / 550 000) ; signature puis factures CIE, eau, gaz qui tombent ; dépenses de
  chaque mois (écran qui change sur chaque mot) ; barres budget / SMIG, « il manque » ; repère salarial et « pas garanti » ;
  coût d'entrée + coût du mois ; totaux 210 000 / 300 000 ; carte « À RETENIR / À FAIRE » ; abonnement et question.
- **Médias.** 71 vraies vidéos (21 nouvelles Mixkit sur le logement, le reste repris des vidéos précédentes par liens
  durs), musiques Mixkit « Hip Hop 02 », « Complicated », « Sweet September » (≈ 5–6 dB sous la voix, carve sans baisse
  automatique), 211 bruitages.

```bash
python3 tools/construire-scenes.py
python3 tools/mixage.py /tmp/corelink
npx hyperframes@0.8.226 check        # puis snapshots, puis rendu (jamais dans la même commande)
```
