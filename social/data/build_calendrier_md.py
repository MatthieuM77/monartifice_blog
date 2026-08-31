#!/usr/bin/env python3
"""Regenere le tableau du calendrier mensuel a partir des fichiers de publication
et du generateur de visuels. Evite que le tableau derive quand une publication change."""
import re, pathlib, importlib.util, datetime

RACINE = pathlib.Path(__file__).resolve().parents[2]
POSTS_DIR = RACINE / "social/posts/2026/09"
CAL = RACINE / "social/calendrier/2026-09.md"
JOURS = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

spec = importlib.util.spec_from_file_location("bv", RACINE / "social/visuels/build_visuels.py")
bv = importlib.util.module_from_spec(spec); spec.loader.exec_module(bv)
# codes photo par publication, dans l'ordre des slides
codes, titres = {}, {}
for p in bv.POSTS:
    c = [s.get("shot") or (s["img"].split("-")[0] if s.get("img") else None) for s in p["slides"]]
    codes[p["date"]] = [x for x in dict.fromkeys(c) if x]
    titres[p["date"]] = p["titre"]

def champ(txt, nom):
    m = re.search(rf"^\| \*\*{nom}\*\* \| (.+?) \|$", txt, re.M)
    return m.group(1).strip() if m else ""

lignes, pil = [], {}
for f in sorted(POSTS_DIR.glob("*.md")):
    txt = f.read_text(encoding="utf-8")
    h = re.match(r"# (\d+) · .+? · (\d+) h (\d+)", txt)
    n, hh, mm = h.group(1), h.group(2), h.group(3)
    a, mo, j = map(int, f.stem.split("-")[:3])
    d = datetime.date(a, mo, j)
    pilier = champ(txt, "Pilier")
    fmt = re.sub(r"\s*—.*", "", champ(txt, "Format")).replace("**", "")
    ph = codes.get(f"{j:02d}/{mo:02d}", [])
    sujet = titres.get(f"{j:02d}/{mo:02d}", f.stem)
    court = pilier.split(" — ")[1].split(" & ")[0].split(", ")[0] if " — " in pilier else pilier
    num = pilier.split(" — ")[0]
    pil[f"{num} · {court}"] = pil.get(f"{num} · {court}", 0) + 1
    hors = " *(hors grille)*" if n == "00" else ""
    lignes.append(f"| {n} | {j:02d}/{mo:02d} | {JOURS[d.weekday()]}{hors} | {hh}h{mm} | "
                  f"{num} · {court} | {fmt} | {sujet} | "
                  f"{'**' + ', '.join(ph) + '**' if ph else '—'} |")

tableau = ("| # | Date | Jour | H | Pilier | Format | Sujet | Photo |\n"
           "|---|---|---|---|---|---|---|---|\n" + "\n".join(lignes))

txt = CAL.read_text(encoding="utf-8")
txt = re.sub(r"<!--TABLEAU-->.*?<!--/TABLEAU-->",
             f"<!--TABLEAU-->\n{tableau}\n<!--/TABLEAU-->", txt, flags=re.S)
CAL.write_text(txt, encoding="utf-8")
print(f"{len(lignes)} publications ecrites dans {CAL.relative_to(RACINE)}")
for k, v in sorted(pil.items()):
    print(f"  pilier {k} : {v}")
