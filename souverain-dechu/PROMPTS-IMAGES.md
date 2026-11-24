# Prompts d'images pour Souverain Déchu

Ce fichier liste les 13 images que le jeu sait afficher, avec un prompt prêt à coller dans ChatGPT pour chacune. Le jeu les charge tout seul depuis le dossier `souverain-dechu/assets/`. Une image absente n'est pas un problème : le jeu garde son rendu actuel pour cet élément, donc tu peux les livrer petit à petit.

## Règles communes

- **Nom de fichier exact** : celui indiqué au-dessus de chaque prompt, en `.png` (ou `.webp` / `.jpg`).
- **Format** : paysage 1536 × 1024 pour les décors et l'écran titre, carré 1024 × 1024 pour les portraits et les textures.
- **Aucun texte** dans l'image : pas de titre, de signature, de logo ni de filigrane.
- **Une conversation ChatGPT par famille d'images** (décors, portraits, textures). Génère le portrait de Lin Ye en premier et garde la même conversation pour les autres portraits : le style restera cohérent.
- Les prompts sont en anglais, car les modèles d'image les suivent plus fidèlement. Tu peux ajouter des précisions en français à la fin.
- Les personnages et l'univers sont originaux. Ne demande pas « dans le style de Magic Emperor » ni le style d'un artiste précis : le jeu doit rester publiable.

**Bloc de style.** Il est déjà inclus dans chaque prompt ci-dessous, ne le colle pas en plus :

> Chinese xianxia manhua illustration, painterly digital art, clean ink linework, cel-shaded lighting, rich atmospheric color, cinematic night scene, high detail

---

## 1. Décors de fond (3 images, 1536 × 1024)

Ces images remplacent le ciel et les montagnes au fond de la scène. Le jeu affiche une **bande horizontale** de l'image, plus ou moins large selon l'écran :

- le **haut de l'image (0 à 40 %)** sert de ciel de réserve, souvent coupé : il doit rester un simple dégradé ;
- **tout l'important** (montagnes, toits, lune) doit tenir entre **40 % et 60 %** de la hauteur, en partant du haut ;
- la **ligne d'horizon** se trouve à **60 %** ;
- le **bas de l'image (60 à 100 %)** est caché par le sol 3D : de la brume unie suffit.

Il ne faut ni personnage ni objet au premier plan, car les décors 3D du jeu se placent devant.

### `bg-cour.png` (Chapitre I, la Cour du Clan Su)

```
Wide background plate for a 2.5D side-scrolling game, 1536x1024, Chinese xianxia manhua illustration, painterly digital art, clean ink linework, cel-shaded lighting, rich atmospheric color, cinematic night scene, high detail. A distant view of an ancient Chinese clan estate at night: layered silhouettes of curved tiled palace roofs, two tall pagodas with warm glowing windows, red paper lanterns tiny in the distance, misty mountains behind them. A large pale full moon sits LOW in the sky, its center at about 45% from the top of the image. Sky is a deep indigo-to-plum gradient with a crimson glow near the horizon. Composition rules: the horizon line is at 60% from the top; all buildings, mountains and the moon must sit between 40% and 60% from the top; the top 40% is only a smooth dark sky gradient with a few stars; the bottom 40% is flat soft purple mist with no objects. No characters, no people, no foreground objects, no text, no watermark.
```

### `bg-foret.png` (Chapitre II, la Forêt des Bêtes Spirituelles)

```
Wide background plate for a 2.5D side-scrolling game, 1536x1024, Chinese xianxia manhua illustration, painterly digital art, clean ink linework, cel-shaded lighting, rich atmospheric color, cinematic night scene, high detail. A distant mystical bamboo forest valley at night: towering bamboo groves fading into layers of mist, steep karst mountains with pines on their ridges, faint cyan spirit lights floating between the stalks, an old stone shrine roof barely visible in the haze. A small pale jade-white moon sits LOW in the sky, its center at about 44% from the top. Palette: deep teal, emerald and silver mist. Composition rules: the horizon line is at 60% from the top; all forest, mountains and the moon must sit between 40% and 60% from the top; the top 40% is only a smooth dark teal sky gradient; the bottom 40% is flat soft green-grey mist with no objects. No characters, no animals, no foreground objects, no text, no watermark.
```

### `bg-pic.png` (Chapitre III, le Pic du Givre Éternel)

```
Wide background plate for a 2.5D side-scrolling game, 1536x1024, Chinese xianxia manhua illustration, painterly digital art, clean ink linework, cel-shaded lighting, rich atmospheric color, cinematic night scene, high detail. A frozen mountain summit range at night under a huge blood-red moon: jagged icy peaks with snow caps, a ruined stone sect gate on a distant ridge, thousands of ancient swords planted in the snow like a graveyard, drifting snow and red embers. The enormous crimson moon sits LOW, its center at about 46% from the top, partly behind the peaks. Palette: black-crimson sky, cold violet snow, icy blue highlights. Composition rules: the horizon line is at 60% from the top; all peaks, ruins and the moon must sit between 40% and 60% from the top; the top 40% is only a smooth dark crimson sky gradient; the bottom 40% is flat soft dusky-violet mist with no objects. No characters, no people, no foreground objects, no text, no watermark.
```

---

## 2. Portraits de dialogue (6 images, 1024 × 1024)

Chaque portrait s'affiche au-dessus de la boîte de dialogue. Les portraits des boss apparaissent aussi en petit à côté de leur jauge de vie.

- **Cadrage** : buste (tête et épaules), visage bien centré dans le carré, regard tourné vers la droite.
- **Fond** : uni, très sombre (#140E1A). Un fond transparent convient aussi.

### `portrait-mo.png` (Mo Tianxie dans le corps de Lin Ye)

```
Head-and-shoulders bust portrait, square 1024x1024, Chinese xianxia manhua illustration, painterly digital art, clean ink linework, cel-shaded lighting, high detail. A slender 16-year-old boy servant possessed by an ancient demon sovereign: pale skin, long black hair tied in a high ponytail with loose strands over the forehead, dark indigo servant robe with crimson trim and crossed collar, crimson sash. His eyes glow crimson, with a cold, arrogant half-smile far too old for his face. A faint crimson and violet demonic aura curls around his shoulders. Three-quarter view, looking toward the right. Plain flat very dark violet background (#140E1A). No text, no frame, no watermark.
```

### `portrait-linye.png` (la voix de Lin Ye, le serment)

```
Same boy as the previous portrait, same face, hairstyle and clothes, head-and-shoulders bust, square 1024x1024, same illustration style. This time he is the gentle original Lin Ye: soft sad dark-brown eyes, worried tender expression, translucent like a spirit memory, faint warm golden glow around him, a few golden motes floating. Three-quarter view, looking toward the right. Plain flat very dark violet background (#140E1A). No text, no frame, no watermark.
```

### `portrait-su.png` (Su Qingyi, jeune maîtresse du clan Su)

```
Head-and-shoulders bust portrait, square 1024x1024, Chinese xianxia manhua illustration, painterly digital art, clean ink linework, cel-shaded lighting, high detail. Su Qingyi, a 16-year-old young lady of a declining noble clan: long black hair half tied up with a jade hairpin, elegant pale jade-green and white hanfu with subtle embroidery, large determined dark eyes, worried but brave expression, warm lantern light on one side of her face. Three-quarter view, looking toward the right. Plain flat very dark violet background (#140E1A). No text, no frame, no watermark.
```

### `portrait-hu.png` (Hu Ba, le Tigre Noir, boss du chapitre I)

```
Head-and-shoulders bust portrait, square 1024x1024, Chinese xianxia manhua illustration, painterly digital art, clean ink linework, cel-shaded lighting, high detail. Hu Ba, a huge brutal bandit chief: shaved head, thick black beard, a scar across one eyebrow, amber eyes, savage toothy grin, burnt-orange vest with black tiger stripes, tiger-fur mantle on massive shoulders, the pole of a heavy guandao glaive resting on his shoulder. Three-quarter view, looking toward the right. Plain flat very dark violet background (#140E1A). No text, no frame, no watermark.
```

### `portrait-mei.png` (l'Ancienne Mei, Secte du Lotus Pourpre, boss du chapitre II)

```
Head-and-shoulders bust portrait, square 1024x1024, Chinese xianxia manhua illustration, painterly digital art, clean ink linework, cel-shaded lighting, high detail. Elder Mei of the Purple Lotus Sect: an ageless, elegant and dangerous woman with very long straight white hair, violet eyes, calm cruel smile, layered violet and lilac robes embroidered with lotus flowers, holding a pink silk folding fan near her chin, a few glowing pink lotus petals floating around her. Three-quarter view, looking toward the right. Plain flat very dark violet background (#140E1A). No text, no frame, no watermark.
```

### `portrait-yan.png` (Yan Shuang, le disciple traître, boss final)

```
Head-and-shoulders bust portrait, square 1024x1024, Chinese xianxia manhua illustration, painterly digital art, clean ink linework, cel-shaded lighting, high detail. Yan Shuang, a beautiful and cold young cultivator around 25 years old: long silver-white hair, piercing ice-blue eyes, faint contemptuous smile, white and pale-blue layered robes with frost patterns, a glowing crystalline ice sword held upright beside his face, frost crystals in the air. Three-quarter view, looking toward the right. Plain flat very dark violet background (#140E1A). No text, no frame, no watermark.
```

---

## 3. Écran titre (1 image, 1536 × 1024)

Le titre et les boutons s'affichent à gauche. La moitié gauche de l'image doit donc rester sombre et vide.

### `titre.png`

```
Key art illustration, 1536x1024, Chinese xianxia manhua illustration, painterly digital art, clean ink linework, cel-shaded lighting, cinematic, high detail. A slender boy servant with a long black ponytail and a dark indigo robe with crimson trim stands on a temple roof at night, seen from a low angle, holding a dark saber. A huge crimson and violet demonic aura shaped like a towering shadow emperor rises behind him, against a giant full moon. Falling plum petals and embers. The character and aura occupy the RIGHT 45% of the image. The LEFT 55% is a dark, almost empty night sky gradient with only faint mist, kept free for the game title. No text, no letters, no logo, no watermark.
```

---

## 4. Textures de sol (3 images, 1024 × 1024, facultatives)

Ces textures sont répétées en mosaïque sur le sol. Elles doivent donc être **raccordables** (seamless), vues de dessus, sans ombre portée ni perspective.

### `texture-pierre.png` (Chapitre I)

```
Seamless tileable top-down texture, 1024x1024, flat orthographic view, no perspective, no shadows: ancient Chinese courtyard paving of large worn grey-violet stone slabs in a staggered pattern, thin dark grout lines, small cracks and a few fallen plum petals, stylized painterly game texture, even lighting, muted night colors.
```

### `texture-mousse.png` (Chapitre II)

```
Seamless tileable top-down texture, 1024x1024, flat orthographic view, no perspective, no shadows: dark mossy forest floor with patches of deep green moss, fallen bamboo leaves and small pebbles, stylized painterly game texture, even lighting, muted teal-green night colors.
```

### `texture-neige.png` (Chapitre III)

```
Seamless tileable top-down texture, 1024x1024, flat orthographic view, no perspective, no shadows: wind-packed mountain snow with soft drifts, small ice crystals and a few dark rocks poking through, stylized painterly game texture, even lighting, cold lavender-grey night colors.
```

---

## Me renvoyer les images

Tu as deux possibilités :

1. **Les joindre directement dans notre conversation.** Je les renomme si besoin, je les compresse en WebP pour que le jeu reste léger, puis je les intègre et je republie la page.
2. **Les déposer toi-même sur GitHub**, dans `souverain-dechu/assets/` sur la branche `ccr-00043135-azvyj9` (bouton *Add file* puis *Upload files*), puis me prévenir.

**Pour tester en local** : les décors et les textures passent par WebGL, qui refuse les images ouvertes en `file://`. Lance un petit serveur dans le dossier du jeu avec `python -m http.server`, puis ouvre `http://localhost:8000`. Les portraits et l'écran titre s'affichent même sans serveur.

## Liste de contrôle

| Fichier | Taille | Où il apparaît |
| --- | --- | --- |
| `bg-cour.png` | 1536 × 1024 | fond du chapitre I et de l'écran titre animé |
| `bg-foret.png` | 1536 × 1024 | fond du chapitre II |
| `bg-pic.png` | 1536 × 1024 | fond du chapitre III |
| `portrait-mo.png` | 1024 × 1024 | dialogues de Mo Tianxie |
| `portrait-linye.png` | 1024 × 1024 | dialogues de la voix de Lin Ye |
| `portrait-su.png` | 1024 × 1024 | dialogues de Su Qingyi |
| `portrait-hu.png` | 1024 × 1024 | dialogues et jauge de Hu Ba |
| `portrait-mei.png` | 1024 × 1024 | dialogues et jauge de l'Ancienne Mei |
| `portrait-yan.png` | 1024 × 1024 | dialogues et jauge de Yan Shuang |
| `titre.png` | 1536 × 1024 | écran titre |
| `texture-pierre.png` | 1024 × 1024 | sol du chapitre I (facultatif) |
| `texture-mousse.png` | 1024 × 1024 | sol du chapitre II (facultatif) |
| `texture-neige.png` | 1024 × 1024 | sol du chapitre III (facultatif) |
