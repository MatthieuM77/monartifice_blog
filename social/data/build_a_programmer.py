#!/usr/bin/env python3
"""Genere A-PROGRAMMER.md : ce qui reste a mettre en ligne, en clair.

Le CSV sert a l'import automatique ; ce fichier sert a programmer a la main.
Memes donnees, lues aux memes endroits — les fichiers de publication.
"""
import datetime
import importlib.util
import pathlib

RAC = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("bcc", RAC / "social/data/build_calendrier_csv.py")
bcc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bcc)
bv = bcc.bv

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
# Tout ce qui etait ecrit est sorti. Les quatre creneaux vides de fin septembre
# recoivent des publications neuves, ecrites dans le registre client vise pour
# octobre : l'occasion et le conseil d'achat plutot que le metier.
RATTRAPAGE = {}
A_FAIRE = ["2026-09-18-emotion-le-lendemain",
           "2026-09-23-choisir-combien-invites",
           "2026-09-25-occasion-anniversaire",
           "2026-09-30-communaute-octobre"]


def bloc(md, post):
    txt = md.read_text(encoding="utf-8")
    a, mo, j = map(int, md.stem.split("-")[:3])
    heure, ig, fb, cig, cfb = bcc.lire(md)
    report = RATTRAPAGE.get(post["date"])
    reel = post["fmt"] == "Reel"
    ns = len(post["slides"])

    if reel:
        media = """**Reel, 22 s, 1080 × 1920.** Il se poste **à la main**, avec le fichier vidéo —
pas par import CSV.

- Le montage est le `.mp4` envoyé dans la conversation. **Récupérez-le** : il n'est pas dans
  le dépôt, et le poste de travail qui l'a produit est temporaire.
- La musique est déjà dedans. Si vous préférez une piste de la bibliothèque Instagram —
  meilleur pour la portée — prenez-en une **autour de 128 BPM** : les coupes tomberont sur
  les temps."""
    else:
        fics = ([f"{md.stem}-{i:02d}.jpg" for i in range(1, ns + 1)] if ns > 1
                else [f"{md.stem}.jpg"])
        media = (f'**{post["fmt"]} · {ns} image{"s" if ns > 1 else ""}**, dans cet ordre :\n\n'
                 + "\n".join(f"{i}. `{f}`" for i, f in enumerate(fics, 1)))

    if report:
        quand, jour, note = report
        entete = (f'## {quand[:2]} septembre · {jour} — {post["titre"]}\n\n'
                  f'> **Rattrapage.** Cette publication était prévue le {post["date"]} et n\'est '
                  f'jamais sortie. {note}')
    else:
        jour = JOURS[datetime.date(a, mo, j).weekday()]
        entete = (f'## {j} septembre · {jour} '
                  f'{heure.replace(":00", " h").replace(":", " h ")} — {post["titre"]}')

    return f"""{entete}

{media}

### Instagram — légende
```
{ig}
```

### Instagram — premier commentaire
```
{cig}
```

### Facebook — légende
```
{fb}
```

### Facebook — premier commentaire
```
{cfb}
```

### Story
{bcc.section(txt, "Story associée") or "—"}

---
"""


def main():
    out = ["""# À programmer — septembre 2026

**Tout ce qui était écrit est sorti.** Restaient quatre créneaux vides — les 18, 23, 25 et 30 —
et six jours de silence entre le 21 et le 27, le pire moment pour disparaître sur un compte
qui démarre. Voici quatre publications neuves pour les combler.

Elles sont écrites dans le **registre client** prévu pour octobre : l'occasion et le conseil
d'achat plutôt que le métier. Elles préparent le basculement.

| Date | Publication | Format | État |
|---|---|---|---|
| 16/09 · mer 12 h 30 | La mise d'inflammateur | Carrousel 4 | ✅ programmée |
| **18/09 · ven 18 h 30** | **Le lendemain** | Post simple | 🆕 **à programmer** |
| 20/09 · dim 11 h | De la caisse au dispositif | Reel 22 s | ✅ programmée |
| 21/09 · lun 19 h | F2 ou F3 ? | Carrousel 4 | ✅ programmée |
| **23/09 · mer 12 h 30** | **Combien d'invités ?** | Carrousel 5 | 🆕 **à programmer** |
| **25/09 · ven 18 h 30** | **Pas que pour les mariages** | Carrousel 4 | 🆕 **à programmer** |
| 27/09 · dim 11 h | Montrez-nous votre été | Post simple | ✅ programmée |
| 28/09 · lun 19 h | Et s'il pleut ? | Carrousel 4 | ⚠️ programmée **à 9 h 00** |
| **30/09 · mer 12 h 30** | **En octobre, on passe à la suite** | Carrousel 4 | 🆕 **à programmer** |

> ⚠️ **Le 28 septembre est programmé à 9 h 00, pas 19 h 00.** Toutes les autres publications
> du lundi sont à 19 h. C'est très probablement un 1 oublié à la saisie — à corriger, sinon
> le carrousel sort un lundi matin, le pire moment de la semaine.

> **Instagram et Facebook portent des textes différents.** Ne copiez pas l'un dans l'autre.
> Le premier commentaire part automatiquement juste après la publication : sur Instagram ce
> sont les hashtags, sur Facebook une relance qui ouvre le fil.

> ⚠️ **Ne jamais sponsoriser.** Meta interdit la publicité payante sur les feux d'artifice.

---
"""]
    # trier sur la date de diffusion, pas sur le nom du fichier : une publication
    # rattrapee sort a une autre date que celle qui la nomme
    # apparier par nom de fichier, jamais par position : deux publications peuvent
    # partager une date et l'ordre alphabetique ne suit pas celui de POSTS
    prevues = [(RATTRAPAGE.get(post["date"], (post["date"],))[0],
                RAC / f'social/posts/2026/09/{post["md"]}.md', post)
               for post in bv.POSTS if post["md"] in A_FAIRE]
    for _, md, post in sorted(prevues, key=lambda x: int(x[0][:2])):
        out.append(bloc(md, post))

    out.append("""## Ce qui reste bloqué

| Date | Publication | Il manque |
|---|---|---|
| 11/09 | L'autre côté du feu | Reel · plan `T8` — vous de dos au pupitre, de nuit |
| 18/09 | Il a dit oui. Le ciel aussi. | Reel · plan `T10` — le feu seul, plein cadre |
| Le tableau de tir | photo `D2` — **vous l'avez en archive** : le tableau à l'heure bleue |
| Les mariages de septembre | photo `H2` — le feu large, avec le lieu dans le cadre |
| Ce qu'il reste après | photos `F1` et `F2` — le site vide, et **la caisse de reliquats** |

Ces trois-là **basculent sur octobre** : leurs créneaux de septembre sont repris par les
rattrapages ci-dessus. Un créneau qui porte une publication vaut mieux qu'un créneau qui
attend une photo.

**Deux sont à portée de main.** `D2` et `F2`, vous me les avez déjà montrées — le tableau à
l'heure bleue et la caisse de reliquats éclairée à la frontale. Les fichiers ne me sont jamais
parvenus. Déposez-les sur le Drive nommés `D2.jpg` et `F2.jpg` : le générateur reconnaît le
code et remplit la slide tout seul.

## ⚠️ Des astérisques sont visibles sur cinq publications en ligne

Les textes Facebook des **1er, 2, 4, 6 et 7 septembre** — et le texte Instagram du 2 —
contiennent des `**` qui auraient dû disparaître. Ils encadrent les passages en gras dans mes
fichiers de travail ; Facebook et Instagram ne les interprètent pas et les affichent tels quels.

**C'est mon erreur.** La première version de la fiche de la semaine 1 livrait les textes sans
retirer ce balisage. Elle a été corrigée le 31 août, ce qui explique que tout soit propre à
partir du 9 septembre.

Les légendes se modifient après publication, sur les deux réseaux. Il suffit de supprimer les
`**` : aucune raison de republier, le contenu est bon.
""")
    f = RAC / "social/calendrier/A-PROGRAMMER.md"
    f.write_text("\n".join(out), encoding="utf-8")
    print(f"{f.relative_to(RAC)} · {len(A_FAIRE)} publications")


if __name__ == "__main__":
    main()
