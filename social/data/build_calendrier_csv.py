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


def lire(md):
    """Extrait l'heure, la legende Instagram et la legende Facebook d'un fichier post."""
    txt = md.read_text(encoding="utf-8")
    h = re.search(r"^# \d+ · .+? · (\d+) h (\d+)", txt, re.M)
    heure = f"{int(h.group(1)):02d}:{h.group(2)}" if h else ""
    ig = re.search(r"## Texte Instagram\n(.*?)\n## Texte Facebook", txt, re.S)
    fb = re.search(r"## Texte Facebook\n(.*?)\n## Story associée", txt, re.S)
    return heure, nettoie(ig.group(1)) if ig else "", nettoie(fb.group(1)) if fb else ""


def main():
    posts_md = sorted((ROOT / "posts/2026/09").glob("*.md"))
    assert len(posts_md) == len(bv.POSTS), "posts et slides desynchronises"

    lignes, exclus = [], []
    for post, md in zip(bv.POSTS, posts_md):
        if post["fmt"] == "Reel":
            exclus.append(f'{post["date"]} — {post["titre"]}')
            continue
        heure, ig, fb = lire(md)
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
        for compte, legende in ((FB, fb), (IG, ig)):
            lignes.append([date, heure, FUSEAU, compte, typ, legende,
                           medias, "", "", CAMPAGNE])

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
