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
# Cinq publications pretes n'ont jamais ete publiees : leur date est passee sans
# qu'elles soient programmees. Elles reprennent les creneaux restes vides de la
# fin du mois plutot que d'ecrire du contenu neuf. Les publications qui
# occupaient ces creneaux attendent une photo : elles basculent sur octobre.
RATTRAPAGE = {
    "01/09": ("18/09", "vendredi 18 h 30", "**Le post d'ouverture. À épingler** dès publication."),
    "13/09": ("23/09", "mercredi 12 h 30", "Remplace « Le tableau de tir », en attente de la photo `D2`."),
    "04/09": ("25/09", "vendredi 18 h 30", "Remplace « Les mariages de septembre », en attente de `H2`."),
    "02/09": ("30/09", "mercredi 12 h 30", "Remplace « Ce qu'il reste après », en attente de `F1` et `F2`."),
}
A_FAIRE = ["20/09"] + list(RATTRAPAGE)      # 20/09 est le Reel


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

**La fin du mois a quatre créneaux vides**, et six jours de silence entre le 21 et le 27.
Cinq publications prêtes ne sont jamais sorties : elles les remplissent, plutôt que d'écrire
du contenu neuf.

| Date | Publication | Format | État |
|---|---|---|---|
| 16/09 · mer 12 h 30 | La mise d'inflammateur | Carrousel 4 images | ✅ programmée |
| **18/09 · ven 18 h 30** | **Artificiers de métier** | Post simple | 🔁 **rattrapage — à épingler** |
| **20/09 · dim 11 h** | **De la caisse au dispositif** | **Reel 22 s** | **à la main, avec la vidéo** |
| 21/09 · lun 19 h | F2 ou F3 ? | Carrousel 4 images | ✅ programmée |
| **23/09 · mer 12 h 30** | **Le méchage** | Carrousel 5 images | 🔁 rattrapage |
| **25/09 · ven 18 h 30** | **Le silence juste avant** | Post simple | 🔁 rattrapage |
| 27/09 · dim 11 h | Montrez-nous votre été | Post simple | ✅ programmée |
| 28/09 · lun 19 h | Et s'il pleut ? | Carrousel 4 images | ✅ programmée |
| **30/09 · mer 12 h 30** | **Compact ou éventail ?** | Carrousel 4 images | 🔁 rattrapage |

La cinquième — le **sondage « Votre feu idéal dure combien de temps ? »** — n'a plus de
créneau en septembre. Elle ouvrira octobre : un sondage marche mieux quand il y a du monde
pour y répondre.

> **Le post d'ouverture d'abord.** Il dit qui vous êtes et il s'épingle : un visiteur le voit
> en haut du profil quelle que soit sa date de publication. C'est le seul dont l'ordre compte
> plus que la date.

> **Instagram et Facebook portent des textes différents.** Ne copiez pas l'un dans l'autre.
> Le premier commentaire part automatiquement juste après la publication : sur Instagram ce
> sont les hashtags, sur Facebook une relance qui ouvre le fil.

> ⚠️ **Ne jamais sponsoriser.** Meta interdit la publicité payante sur les feux d'artifice.

---
"""]
    # trier sur la date de diffusion, pas sur le nom du fichier : une publication
    # rattrapee sort a une autre date que celle qui la nomme
    prevues = [(RATTRAPAGE.get(post["date"], (post["date"],))[0], md, post)
               for md, post in zip(sorted((RAC / "social/posts/2026/09").glob("*.md")), bv.POSTS)
               if post["date"] in A_FAIRE]
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

## Ce qui a été perdu

Quatre publications prêtes sont passées sans être programmées : celles du 1er, 2, 4 et 6
septembre. Trois sont rattrapées ci-dessus. La quatrième — le sondage sur la durée — ouvrira
octobre.

**Le point à ne pas rater : le post d'ouverture n'est jamais sorti.** Le compte a démarré le
7 septembre avec un carrousel sur la réglementation, donc personne n'a jamais lu qui vous
êtes. C'est ce que le 18 corrige, et c'est pour ça qu'il faut l'épingler.
""")
    f = RAC / "social/calendrier/A-PROGRAMMER.md"
    f.write_text("\n".join(out), encoding="utf-8")
    print(f"{f.relative_to(RAC)} · {len(A_FAIRE)} publications")


if __name__ == "__main__":
    main()
