# « Ton épargne ne te rendra pas riche » : le film 16:9 (Lefinancier, vidéo 1)

Première vidéo de la chaîne finance **Lefinancier** (80,6 s). Voix ElevenLabs « Nicolas – Narrator » et texte de l'utilisateur
(`script.txt`). Couleurs de la chaîne : **bleu ciel #38BDF8 sur bleu nuit #0B1220** (plus de vert), personnage en bleu ciel,
pièces dorées.

- Scènes : hook (24 vraies vidéos en 12,8 s, « Ton épargne / ne te rendra pas riche », compteur 0 → 1 000 000 FCFA, carte
  « Compte Wave » qui se grise, tampon « Plus pauvre », années qui défilent) → panier de courses 100 000 → 105 000 FCFA (+5 %, chaque
  article augmente) → même solde, rien perdu, rien volé, un article barré → « Bienvenue dans le monde de l'inflation », étiquettes de
  prix qui montent, jauge du pouvoir d'achat 100 → 82 %, « Erreur », « Argent sur un compte = Richesse » barré → courbes prix ↑ /
  valeur réelle ↓ + vrai chiffre (+22 % de prix en Côte d'Ivoire entre 2019 et 2024, Banque mondiale) → coussin de sécurité
  (santé, panne, imprévus), cartes « Épargner ≠ Investir », piles de pièces qui grandissent → carte du compte LeFinancier,
  clic « S'abonner », « Fais travailler ton argent ».
- Sous le film (vertical) : « 3 choses à comprendre » (Inflation, Pouvoir d'achat, Investir), cachées puis dévoilées.
- 62 vraies vidéos (Mixkit), 3 musiques Mixkit (Waka Floka Type, Trapanomics, Never Going Broke) ≈ 5–6 dB sous la voix, 229 bruitages.
- La carte « Compte Wave » est dessinée (sans logo ni interface de Wave).

```bash
python3 tools/construire-scenes.py && python3 tools/mixage.py /tmp/corelink
hyperframes check
hyperframes render . -o renders/epargne-inflation-16x9.mp4   # commande séparée
```
