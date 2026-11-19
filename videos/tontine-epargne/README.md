# Lefinancier, vidéo 4 : « Tontine ou compte épargne ? »

Première vidéo **composée directement en vertical 1080×1920**, sans film 16:9 dans un bandeau.

- Texte écrit par une autre IA (prompt `finance/prompt-storytelling.txt`) et voix ElevenLabs de l'utilisateur (61,8 s).
- Histoire : Tom reçoit 250 000 F grâce à une tontine de 10 personnes à 25 000 F par mois. Il achète une moto, mais
  son salaire tarde, alors il vend son téléphone pour payer sa cotisation. Sa sœur Emma met les mêmes 25 000 F chaque
  mois sur un compte à 3,5 % par an (10 versements, environ 4 000 F d'intérêts bruts).
- Chiffres vérifiés :
  - **3,5 %** : taux fixe des comptes et livrets d'épargne dans l'UMOA (décision BCEAO sur l'épargne réglementée).
  - Intérêts : 25 000 × 3,5 % / 12 × (10 + 9 + … + 1) = **4 010 F**.
  - « Sans frais de tenue chez NSIA » : non vérifié sur une grille officielle. Aucun logo de banque n'est montré, seulement une banque dessinée.

## Construction

```bash
python3 tools/construire-scenes.py      # écrit compositions/s*.html, sous-titres.html et index.html
python3 tools/mixage.py /tmp/corelink   # creux de la voix dans les musiques, sans baisse automatique
npx hyperframes@0.8.226 check           # puis snapshots, puis rendu (jamais dans la même commande)
```

- `tools/styles.css` : décors (rue, chambre), personnages, bulles, écrans, téléphone, pièces, titre.
- Les personnages sont verticaux et bleus : Tom (bleu ciel, mèche), Emma (bleu clair, chignon), Hugo (bleu profond, casquette).
- Les vraies vidéos sont **dans la scène** : bulle de pensée, écran vertical de garage, télé de la chambre, écrans du bilan. La caméra zoome dessus jusqu'à remplir l'image (`zoom_ecran`), puis ressort. Seul le hook est fait de vidéos plein cadre.
- La caméra reste dans le décor (`SV.bornes`) et suit les personnages (`pano`).
- Musiques Mixkit : Waka Floka Type, G-Eazy NBA Type et Try Me, environ 5–6 dB sous la voix. Bruitages : 192, dont sonnerie et moto récupérées sur Mixkit.
