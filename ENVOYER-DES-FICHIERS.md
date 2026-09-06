# Envoyer des fichiers — photos, vidéos, documents

## En résumé

| Quoi | Où | Pourquoi |
|---|---|---|
| **Photos** | GitHub, dossier `social/photos/2026-09/` | Quelques Mo, sans conséquence |
| **Rushes vidéo** | **Google Drive ou disque dur** | Plusieurs Go — jamais dans Git |
| **Reel monté** | Directement sur Instagram | Il n'a rien à faire dans un dépôt |
| **Documents, CSV** | GitHub | Du texte, c'est ce pour quoi Git est fait |

## Pourquoi pas la vidéo dans Git

Git garde **toutes les versions de tout, pour toujours**. Sur un fichier texte il
ne stocke que les lignes changées ; sur un binaire il réécrit le fichier entier à
chaque modification. Une vidéo de 500 Mo retouchée trois fois, c'est 1,5 Go dans
l'historique — que chaque clone retélécharge, définitivement.

Git LFS contourne le problème mais ne le supprime pas :

- **Le quota gratuit de GitHub est d'environ 1 Go** de stockage et autant de
  transfert mensuel. Une minute de 4K au téléphone pèse ~350 Mo.
- Au-delà, c'est payant, par tranches.
- **Le transfert compte aussi** : chaque clone qui télécharge le fichier consomme
  du quota.
- Un fichier déjà poussé sans LFS y reste. L'en sortir demande de **réécrire
  l'historique** — force-push, et tout le monde reclone.

Pour trois Reels de 25 à 30 plans chacun, le quota saute dès la première séquence.

## Si vous devez quand même pousser une vidéo

Le dépôt est déjà configuré : `.gitattributes` route `.mp4`, `.mov`, `.avi` et
`.zip` vers LFS. Il reste à installer LFS sur votre machine.

**1. Installer Git LFS**

GitHub Desktop l'embarque en général. Sinon : <https://git-lfs.com>.

**2. L'activer une fois**

Dans GitHub Desktop : menu *Repository* → *Open in Terminal* (ou
*Open in Command Prompt* sous Windows), puis :

```bash
git lfs install
```

**3. Vérifier que le suivi est actif**

```bash
git lfs track
```

La liste doit afficher `*.mp4`, `*.mov`, etc. Si elle est vide, c'est que
`.gitattributes` n'est pas dans la branche courante.

**4. Déposer le fichier, puis committer normalement**

GitHub Desktop s'occupe du reste. Au push, la barre de progression est plus lente :
c'est le fichier qui part sur le serveur LFS, séparément.

**5. Contrôler ce qui est bien passé en LFS**

```bash
git lfs ls-files
```

> ⚠️ **L'ordre compte.** `.gitattributes` doit être committé **avant** le fichier
> qu'il concerne. S'il arrive après, le fichier est déjà dans l'historique en Git
> ordinaire, et l'en sortir demande `git lfs migrate import` — qui réécrit
> l'historique.

## Le dépôt ne contient plus les fichiers régénérables

Les maquettes HTML, les JPEG d'export et les CSV ne sont plus versionnés : ils
pesaient 20 Mo sur 27, et chaque retouche de photo en réécrivait la totalité,
parce que les images y sont encodées en base64.

Pour les refabriquer :

```bash
python3 social/visuels/build_visuels.py        # les maquettes
python3 social/visuels/export_visuels.py       # les JPEG 1080×1350
python3 social/data/build_calendrier_csv.py    # les CSV d'import
python3 social/data/build_calendrier_md.py     # le tableau du calendrier
```

Les vraies sources — textes, photos, logo, scripts — pèsent 6,5 Mo.

## Stabilisation : Gyroflow, sur votre machine

**Une passe vidstab a ete essayee ici, puis retiree.** Sur un ultra grand-angle
elle plaque une transformation affine globale par-dessus la distorsion en
barillet de l'objectif : les bords respirent, l'image s'etire, et le resultat
donne mal au coeur. Les chiffres etaient pourtant bons — deplacement image a
image ramene de 1,40 a 0,76 px. **La mesure ne voyait pas le defaut qu'elle
creait.**

Gyroflow ne souffre pas de ce probleme : il lit le **log IMU embarque dans le
fichier** et corrige image par image en tenant compte du profil de l'objectif,
au lieu de deviner le mouvement en comparant les images.

### Les donnees gyro sont bien la

Verifie sur vos rushes : chaque fichier porte une piste `dbgi` d'environ 2 Mo,
c'est le log de la centrale inertielle. Gyroflow connait l'Osmo Action 5 Pro —
il embarque plus de 12 000 profils d'objectifs.

### Pourquoi ca ne peut pas tourner ici

Gyroflow a besoin d'un backend de calcul GPU (OpenCL, CUDA ou wgpu). Le
conteneur n'en a aucun : le binaire Linux se lance, charge les profils, parse
le gyro — puis plante au rendu. Un OpenCL logiciel (pocl) ne suffit pas non plus.

**C'est de toute facon la bonne place** : vous avez les fichiers d'origine et une
machine avec une carte graphique.

### La marche a suivre

1. Ouvrir les rushes dans Gyroflow, verifier que le profil d'objectif est
   detecte automatiquement.
2. Exporter en **1080 x 1920**, sans audio — la bande-son est refaite ici.
3. Deposer les fichiers stabilises dans un dossier Drive `video-stab/`, en
   **gardant les memes noms** (`M6.MP4`, `T5.MP4`…).
4. Me le dire : je repointe le montage dessus et je relance. Rien d'autre a
   changer, le tableau des plans reste valable.

En ligne de commande, pour traiter le dossier d'un coup :

```bash
gyroflow *.MP4 -f -t "" \
  -p "{'codec':'x264','bitrate':40,'audio':false,'output_width':1080,'output_height':1920}"
```

Gyroflow a aussi un mode `--watch <dossier>` qui traite automatiquement tout
fichier depose dedans.
