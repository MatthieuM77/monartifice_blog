# Import CSV — Septembre 2026

Fichier : **`import-septembre-2026.csv`**
Généré par `social/data/build_calendrier_csv.py` depuis les fichiers `posts/2026/09/`.

## Ce que contient le fichier

**28 lignes = 14 publications × 2 comptes.**

Une ligne par compte, et non une ligne pour les deux, parce que **les textes Facebook et
Instagram sont différents** : Facebook porte une version plus narrative avec 3 hashtags,
Instagram une version plus courte avec 14 hashtags. Les fusionner perdrait la moitié du travail.

| | |
|---|---|
| Format | Point-virgule, UTF-8 avec BOM, fins de ligne LF — identique au modèle fourni |
| Colonnes | `date;heure;fuseau;compte;type;legende;medias;lien;commentaire;campagne` |
| Campagne | `Mon Artifice — Septembre 2026` |
| Fuseau | `Europe/Paris` |

## ⚠️ Deux points à vérifier avant l'import

**1. Le libellé des comptes.** J'ai repris exactement les intitulés de votre liste :
`Mon Artifice (facebook)` et `Mon Artifice (instagram)`. Si l'outil attend le nom sans le
suffixe de plateforme, un rechercher-remplacer suffit.

**2. La colonne `medias` est vide.** Les visuels ne sont pas encore exportés de Canva. C'est
volontaire : une URL inventée ferait échouer l'import. Complétez-la après export, ou importez
en brouillon et ajoutez les images à la main.

## Ce qui n'est pas dans le fichier

**Les 3 Reels sont exclus**, comme demandé : 11/09, 18/09 et 20/09. Ils demandent une vidéo
à tourner et monter — voir `REELS.md`.

**Aucun lien** dans la colonne `lien` : la boutique n'est pas en ligne, et un lien mort coûte
plus cher qu'une absence de lien.

## Correspondance images ↔ publications

44 images à exporter au total.

| Date | Publication | Type | Images | Design Canva | Photos à venir |
|---|---|---|---|---|---|
| 02/09 | Compact ou éventail ? | carousel | **4** | [ouvrir](https://www.canva.com/d/aBIs83LEDoBiE-6) | — |
| 04/09 | Le silence juste avant | photo | **1** | [ouvrir](https://www.canva.com/d/LJ8hF3yHd5fwxWo) | — |
| 06/09 | Votre feu idéal dure combien de temps ? | photo | **1** | [ouvrir](https://www.canva.com/d/nFcdoc9uEgIuMWJ) | — |
| 07/09 | Faut-il prévenir la mairie ? | carousel | **5** | [ouvrir](https://www.canva.com/d/pgLpz6sZmk9KPwQ) | — |
| 09/09 | Artificiers de métier | photo | **1** | [ouvrir](https://www.canva.com/d/wXLKqc1daviP8W_) | — |
| 13/09 | Le méchage | carousel | **5** | [ouvrir](https://www.canva.com/d/-ri5_CoOMpqcnUt) | `A2` · `A3` |
| 14/09 | 8 mètres ou 25 mètres ? | carousel | **5** | [ouvrir](https://www.canva.com/d/D4tmjTPJHZaQCZq) | — |
| 16/09 | La mise d'inflammateur | carousel | **4** | [ouvrir](https://www.canva.com/d/aiXm5uUT0zRtlSb) | `B2` |
| 21/09 | F2 ou F3 ? | carousel | **4** | [ouvrir](https://www.canva.com/d/p6mEMmjBuJQmQfr) | — |
| 23/09 | Le tableau de tir | carousel | **4** | [ouvrir](https://www.canva.com/d/-GKbwRWYViSFRdN) | `D2` |
| 25/09 | Les mariages de septembre | photo | **1** | [ouvrir](https://www.canva.com/d/beLDKt3DbgM3-nE) | `H2` |
| 27/09 | Montrez-nous votre été | photo | **1** | [ouvrir](https://www.canva.com/d/oqqIw1KksRwU6pX) | — |
| 28/09 | Et s'il pleut ? | carousel | **4** | [ouvrir](https://www.canva.com/d/6okqjzRceVRIxLV) | — |
| 30/09 | Ce qu'il reste après | carousel | **4** | [ouvrir](https://www.canva.com/d/63Qacpc_5HIXq5y) | `F1` · `F2` |

Les codes de la dernière colonne sont les plans à rapporter du feu du 5 septembre
(voir `COULISSES-PLAN-PHOTO.md`). Les publications sans code sont complètes.

## Régénérer

```bash
python3 social/data/build_calendrier_csv.py
```

Le CSV est reconstruit depuis les fichiers `posts/`. **Modifier un texte dans `posts/`, pas
dans le CSV** : le CSV est écrasé à chaque exécution.


## La colonne `commentaire`

L'outil de programmation publie ce texte **en premier commentaire, juste après la publication**.
Les deux comptes ne l'utilisent pas pour la même chose.

| Compte | Contenu | Pourquoi |
|---|---|---|
| **Instagram** | Les 14 hashtags, **retirés de la légende** | La portée est identique, mais la légende reste lisible. Les quatre premières lignes sont tout ce qu'on voit avant « plus » : autant ne pas les gâcher. |
| **Facebook** | Une **relance écrite**, jamais des hashtags | Facebook ne fait presque rien des hashtags, mais il pousse les publications qui ouvrent un fil de commentaires. |

Les relances Facebook sont écrites une par une dans les fichiers de publication, section
`## Premier commentaire`. Le commentaire Instagram, lui, est **généré** : le script détache la
dernière ligne de la légende quand elle commence par un `#`. Rien à saisir à la main.

> Une relance n'est pas un remplissage. Elle doit appeler une réponse, sinon elle occupe le
> premier commentaire pour rien — et c'est la place la plus visible de la publication.
