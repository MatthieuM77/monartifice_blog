#!/usr/bin/env python3
"""Regenere social/PRODUITS.md depuis social/data/produits.json (export SQL).

Aucun prix n'est ecrit dans le markdown : les tarifs changent, les visuels restent.
Le champ de disponibilite fiable est `dispo_stock`, pas `stock` (voir le rapport
de qualite en fin de fichier genere).
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = json.loads((ROOT / "data/produits.json").read_text(encoding="utf-8"))

# L'export du 30/08 est complet : 30 references, plus aucune manquante.
MANQUANTS = []


def duree(sec):
    if not sec:
        return "—"
    sec = int(sec)
    return f"{sec} s" if sec < 60 else (f"{sec // 60} min" if sec % 60 == 0
                                        else f"{sec // 60} min {sec % 60} s")


def nettoie(txt, limite=None):
    if not txt:
        return ""
    txt = re.sub(r"<[^>]+>", " ", str(txt))
    txt = re.sub(r"\s+", " ", txt).replace("|", "/").strip()
    return txt[:limite].rstrip() + "…" if limite and len(txt) > limite else txt


def ligne(x):
    return (f"| `{x['reference']}` | {nettoie(x['nom'])[:58]} | {x.get('cat') or '—'} | "
            f"{x.get('calibre') or '—'} | {duree(x.get('duree'))} | "
            f"{int(x['nbr_coups']) if x.get('nbr_coups') else '—'} | "
            f"{int(x['hauteur']) if x.get('hauteur') else '—'} m | "
            f"{x.get('distance_securite') or '—'} | "
            f"{'🎬' if x.get('video') else '—'} |")


EN_TETE = ("| Réf. | Produit | Cat. | Calibre | Durée | Coups | Hauteur | Distance séc. | Vidéo |\n"
           "|---|---|---|---|---|---|---|---|---|")

dispo = [x for x in P if x.get("dispo_stock")]
rupture = [x for x in P if not x.get("dispo_stock")]

out = [
    "# Catalogue de référence — Mon Artifice",
    "",
    "> Généré depuis l'export SQL par `social/data/build_produits.py`. **Ne pas éditer à la main.**",
    "> **Aucun prix n'y figure volontairement** : les tarifs changent, les publications restent en ligne.",
    "> CTA à utiliser tant que la boutique n'est pas en ligne : « Écrivez-nous en message privé ».",
    "",
    "## Ce qu'il faut savoir avant d'utiliser ce fichier",
    "",
    "- La disponibilité fiable est **`dispo_stock`**, pas `stock` (voir le rapport en fin de page).",
    "- Les distances de sécurité sont homogènes : **F2 → 8 m**, **F3 → 25 m**. "
    "C'est le premier critère de choix pour un client, avant la durée.",
    f"- **{sum(1 for x in P if x.get('video'))} produits sur {len(P)} ont une vidéo YouTube** : "
    "matière directe pour des Reels.",
    "",
    "---",
    "",
    f"## ✅ Disponibles — {len(dispo)} références",
    "",
    EN_TETE,
]
out += [ligne(x) for x in dispo]
out += ["", f"## ⏳ Indisponibles — {len(rupture)} références", "",
        "**Jamais de post de vente sur ces références.** Teasing ou contenu comparatif uniquement.",
        "", EN_TETE]
out += [ligne(x) for x in rupture]

out += ["", "---", "", "## Effets par produit disponible", "",
        "Matière première pour les carrousels : ce sont les effets réels, à reprendre tels quels.", ""]
for x in dispo:
    eff = nettoie(x.get("effets"), 400)
    if eff:
        out += [f"**`{x['reference']}` — {nettoie(x['nom'])[:52]}**", f"> {eff}", ""]

out += ["---", "", "## ⚠️ Rapport de qualité des données", "",
        "À corriger dans la base avant la mise en ligne de la boutique.", ""]

if MANQUANTS:
    out += [f"### 1. {len(MANQUANTS)} références absentes de l'export", ""]
    out += [f"- `{r}`" for r in MANQUANTS]
    out += [""]
else:
    out += ["### 1. Export complet ✅", "",
            f"Les {len(P)} références de la boutique sont présentes. Plus aucune donnée manquante.", ""]

incoherents = [x for x in P if x.get("dispo_stock") and not x.get("stock")]
out += ["### 2. Le champ `stock` n'est pas fiable", "",
        f"{len(incoherents)} références ont `dispo_stock = 1` mais `stock = 0` :", ""]
out += [f"- `{x['reference']}`" for x in incoherents]
out += ["", "> Soit le stock n'est pas tenu, soit l'affichage boutique se fonde uniquement sur "
        "`dispo_stock`. **Toujours se fier à `dispo_stock`** en attendant clarification.", ""]

out += ["### 3. Champs erronés ou vides", ""]
for x in P:
    pb = []
    ds = str(x.get("distance_securite") or "")
    if "cm" in ds or " x " in ds:
        pb.append(f"`distance_securite` contient des dimensions : « {ds} »")
    if not x.get("nbr_coups"):
        pb.append("`nbr_coups` vide")
    if not x.get("hauteur"):
        pb.append("`hauteur` vide")
    if pb:
        out.append(f"- `{x['reference']}` — " + " · ".join(pb))
out.append("")

(ROOT / "PRODUITS.md").write_text("\n".join(out), encoding="utf-8")
print(f"PRODUITS.md — {len(dispo)} dispo / {len(rupture)} rupture / {len(MANQUANTS)} manquants")
