#!/usr/bin/env python3
"""Genere le CSV d'import de l'outil de programmation, au format du modele fourni.

Format : point-virgule, UTF-8 avec BOM, fins de ligne LF.
En-tete : date;heure;fuseau;compte;type;legende;medias;lien;commentaire;campagne

Deux lignes par publication — une par compte — parce que les textes Facebook et
Instagram sont differents : Facebook porte une version plus narrative et trois
hashtags, Instagram une version plus courte et quatorze hashtags. Les fusionner
sur une seule ligne perdrait la moitie du travail d'ecriture.

Les Reels sont exclus : ils demandent une video, qui n'existe pas encore.
"""
import csv
import importlib.util
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
FUSEAU = "Europe/Paris"
CAMPAGNE = "Mon Artifice — Septembre 2026"
FB = "Mon Artifice (facebook)"
IG = "Mon Artifice (instagram)"

spec = importlib.util.spec_from_file_location("bv", ROOT / "visuels/build_visuels.py")
bv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bv)


def nettoie(txt):
    """Retire le balisage markdown : Facebook et Instagram publient du texte brut,
    un **gras** y apparaitrait tel quel, asterisques comprises."""
    txt = re.sub(r"\*\*(.+?)\*\*", r"\1", txt, flags=re.S)   # gras
    txt = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", txt, flags=re.S)  # italique
    txt = re.sub(r"^#+ ", "", txt, flags=re.M)                 # titres residuels
    txt = re.sub(r"^> ?", "", txt, flags=re.M)                 # citations
    return txt.strip()


def section(txt, titre, brut=False):
    """Contenu d'une section markdown, jusqu'au titre de niveau 2 suivant.

    brut=True rend le markdown intact : utile quand il faut encore y chercher un
    marqueur que nettoie() effacerait.
    """
    m = re.search(rf"^## {titre}\n(.*?)(?=\n## |\Z)", txt, re.S | re.M)
    if not m:
        return ""
    return m.group(1).strip() if brut else nettoie(m.group(1))


def lire(md):
    """Extrait l'heure, les deux legendes et les deux premiers commentaires.

    Le premier commentaire Instagram, ce sont les hashtags : on les sort de la legende
    pour la garder lisible. Celui de Facebook est une relance ecrite, parce que Facebook
    ne fait presque rien des hashtags mais pousse les fils de commentaires.
    """
    txt = md.read_text(encoding="utf-8")
    h = re.search(r"^# \d+ · .+? · (\d+) h (\d+)", txt, re.M)
    heure = f"{int(h.group(1)):02d}:{h.group(2)}" if h else ""

    ig = section(txt, "Texte Instagram")
    lignes = ig.rstrip().split("\n")
    if lignes and lignes[-1].lstrip().startswith("#"):
        com_ig = lignes[-1].strip()
        ig = "\n".join(lignes[:-1]).rstrip()
    else:
        com_ig = ""

    # la section porte un bloc de consigne en citation puis "**Facebook :**" : on ne
    # garde que ce qui suit ce marqueur, avant de retirer le balisage
    brut = section(txt, "Premier commentaire", brut=True)
    com_fb = nettoie(brut.split("**Facebook :**", 1)[1]) if "**Facebook :**" in brut else ""

    return heure, ig, section(txt, "Texte Facebook"), com_ig, com_fb


def main():
    posts_md = sorted((ROOT / "posts/2026/09").glob("*.md"))
    assert len(posts_md) == len(bv.POSTS), "posts et slides desynchronises"

    lignes, exclus = [], []
    for post, md in zip(bv.POSTS, posts_md):
        if post["fmt"] == "Reel":
            exclus.append(f'{post["date"]} — {post["titre"]}')
            continue
        heure, ig, fb, com_ig, com_fb = lire(md)
        date = f'2026-09-{post["date"][:2]}'
        n = len(post["slides"])
        typ = "carousel" if n > 1 else "photo"
        # visuels exportes, s'ils existent : le nom de fichier remplit la colonne medias
        exp = ROOT / "visuels/export/2026-09"
        if n > 1:
            fics = [f"{md.stem}-{i:02d}.jpg" for i in range(1, n + 1)]
        else:
            fics = [f"{md.stem}.jpg"]
        medias = ",".join(f for f in fics if (exp / f).exists())
        for compte, legende, com in ((FB, fb, com_fb), (IG, ig, com_ig)):
            lignes.append([date, heure, FUSEAU, compte, typ, legende,
                           medias, "", com, CAMPAGNE])

    entete = ["date", "heure", "fuseau", "compte", "type", "legende",
              "medias", "lien", "commentaire", "campagne"]

    def ecrire(chemin, rows):
        with chemin.open("w", encoding="utf-8-sig", newline="\n") as f:
            w = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL,
                           lineterminator="\n")
            w.writerow(entete)
            w.writerows(rows)

    out = ROOT / "calendrier/import-septembre-2026.csv"
    ecrire(out, lignes)

    # semaine 1 : tout ce qui ne depend d'aucune photo a prendre le 5
    s1 = [l for l in lignes if l[0] <= "2026-09-09"]
    ecrire(ROOT / "calendrier/import-semaine1.csv", s1)

    pub = len(lignes) // 2
    car = sum(1 for l in lignes if l[4] == "carousel") // 2
    print(f"{out.relative_to(ROOT.parent)}")
    print(f"  {pub} publications × 2 comptes = {len(lignes)} lignes")
    print(f"  {car} carrousels · {pub - car} posts simples")
    print(f"  {len(exclus)} Reels exclus : " + " · ".join(exclus))
    avec = sum(1 for l in lignes if l[6]) // 2
    print(f"  {avec} publications avec leurs visuels renseignes")
    print(f"  semaine 1 : {len(s1)} lignes → calendrier/import-semaine1.csv")


if __name__ == "__main__":
    main()
