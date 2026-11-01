# Examen demain : utilise ChatGPT comme un prof

Vidéo de 2 min (120 s) dans le style « Projecteur » ([`../../hyperframes-style/frame.md`](../../hyperframes-style/frame.md)).

- **Ce projet** : le film 16:9, version YouTube (1920×1080, 30 i/s).
- **[`../examen-demain-vertical/`](../examen-demain-vertical/)** : la version TikTok, Shorts et Reels, avec le titre-promesse au-dessus du film.

## Sources

| Fichier | Contenu |
| --- | --- |
| `script.txt` | Le script, tel que lu par la voix. |
| `assets/audio/voix.wav` | La voix off ElevenLabs (« Nicolas – Narrator »), normalisée à −15 LUFS. |
| `assets/transcript-brut.json` | La transcription automatique (temps justes, mais avec des fautes de mots). |
| `assets/mots.json` | Les mots exacts du script, alignés sur ces temps. Sert aux sous-titres et aux scènes. |
| `assets/audio/musique.wav` | Nappe grave générée avec ffmpeg, coupée sur « oublié la moitié » et « le piège ». |

## Les 12 scènes

| Scène | Temps | Ce qu'on voit |
| --- | --- | --- |
| `s1-heure` | 0 → 7,3 s | « toi » au bureau, 23:17, 40 pages qui s'empilent, jauge « mémorisé 3 % » |
| `s2-panique` | 7,3 → 15,5 s | pouls qui s'emballe, pages 01 et 02, 23:27, moitié des lignes qui s'effacent, « OUBLIÉ. » |
| `s3-chatgpt` | 15,5 → 23,1 s | fenêtre ChatGPT, « Résume mes 40 pages. » barré, « MISSION. » |
| `s4-prompt1` | 23,1 → 39,5 s | le premier prompt tapé mot à mot avec la voix, mots clés surlignés, « consignes 0/5 → 5/5 » |
| `s5-carte` | 39,5 → 49,8 s | carte de révision, « ATTENTION. », « lire un résumé ≠ connaître son cours », « ÉTAPE 02 » |
| `s6-prompt2` | 49,8 → 63,8 s | le deuxième prompt (le professeur), « règles 0/4 → 4/4 » |
| `s7-rappel` | 63,8 → 73,4 s | relire (passif) / se souvenir (actif), « RAPPEL ACTIF. » |
| `s8-examen` | 73,4 → 81,5 s | 5 questions Q1 à Q5 et leur maîtrise, mini-examen, chrono, notes barrées |
| `s9-piege` | 81,5 → 91,9 s | « LE PIÈGE. », « vérité absolue » barrée, vérifications cochées, document original |
| `s10-heures` | 91,9 → 102,2 s | temps restant, cible « notions essentielles » et lacunes, belles fiches barrées, « APPRENDRE. DORMIR. » |
| `s11-prof` | 102,2 → 110,6 s | « réviser à ta place » barré, « PROFESSEUR », bulles de questions |
| `s12-question` | 110,6 → 120 s | « dis-moi… », choix A « Résumer » / B « T'interroger », « ? », réponse en commentaire |

## Refaire ou retoucher

```bash
# sous-titres (mot à mot, orthographe du script)
python3 tools/sous-titres.py assets/transcript-brut.json --script script.txt --fin 119.6 --mots assets/mots.json
# scènes : ÉCRASE compositions/s*.html, à n'utiliser que pour repartir de zéro
python3 tools/construire-scenes.py
hyperframes check
hyperframes render -o renders/examen-demain-16x9.mp4
```

Pour la version verticale : copier le rendu dans `../examen-demain-vertical/assets/`, puis y lancer `hyperframes render`.
