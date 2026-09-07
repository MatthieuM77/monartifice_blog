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
A_FAIRE = ["13/09", "16/09", "20/09", "27/09"]      # 20/09 est le Reel


def bloc(md, post):
    txt = md.read_text(encoding="utf-8")
    a, mo, j = map(int, md.stem.split("-")[:3])
    heure, ig, fb, cig, cfb = bcc.lire(md)
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

    return f"""## {j} septembre · {JOURS[datetime.date(a, mo, j).weekday()]} {heure.replace(":00", " h").replace(":", " h ")} — {post["titre"]}

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

**Quatre publications prêtes.** Tout le reste du mois est soit déjà programmé, soit bloqué
faute d'image.

| Date | Publication | Format | Comment |
|---|---|---|---|
| 13/09 · dim 11 h | Le méchage | Carrousel 5 images | import ou à la main |
| 16/09 · mer 12 h 30 | La mise d'inflammateur | Carrousel 4 images | import ou à la main |
| **20/09 · dim 11 h** | **De la caisse au dispositif** | **Reel 22 s** | **à la main, avec la vidéo** |
| 27/09 · dim 11 h | Montrez-nous votre été | Post simple | import ou à la main |

> **Instagram et Facebook portent des textes différents.** Ne copiez pas l'un dans l'autre.
> Le premier commentaire part automatiquement juste après la publication : sur Instagram ce
> sont les hashtags, sur Facebook une relance qui ouvre le fil.

> ⚠️ **Ne jamais sponsoriser.** Meta interdit la publicité payante sur les feux d'artifice.

---
"""]
    for md, post in zip(sorted((RAC / "social/posts/2026/09").glob("*.md")), bv.POSTS):
        if post["date"] in A_FAIRE:
            out.append(bloc(md, post))

    out.append("""## Ce qui reste bloqué

| Date | Publication | Il manque |
|---|---|---|
| 11/09 | L'autre côté du feu | Reel · plan `T8` — vous de dos au pupitre, de nuit |
| 18/09 | Il a dit oui. Le ciel aussi. | Reel · plan `T10` — le feu seul, plein cadre |
| 23/09 | Le tableau de tir | photo `D2` — **vous l'avez en archive** : le tableau à l'heure bleue |
| 25/09 | Les mariages de septembre | photo `H2` — le feu large, avec le lieu dans le cadre |
| 30/09 | Ce qu'il reste après | photos `F1` et `F2` — le site vide, le ramassage |

**Le 23/09 est le plus rapide à débloquer.** Cette photo existe déjà, elle ne m'est jamais
parvenue. Déposez-la sur le Drive nommée `D2-quelque-chose.jpg` : le générateur reconnaît le
code et remplit la slide tout seul.

## À vérifier

Les publications du **1er, 2, 4 et 6 septembre** sont passées. Sont-elles bien sorties ?
Si le post d'ouverture « Artificiers de métier » n'a pas été publié, tout le reste arrive
sans présentation — mieux vaut le sortir maintenant, daté d'aujourd'hui, avant les autres.
""")
    f = RAC / "social/calendrier/A-PROGRAMMER.md"
    f.write_text("\n".join(out), encoding="utf-8")
    print(f"{f.relative_to(RAC)} · {len(A_FAIRE)} publications")


if __name__ == "__main__":
    main()
