#!/usr/bin/env python3
"""Genere le fichier HTML multi-pages importable dans Canva.

Chaque page porte data-document-role="page" (une page Canva), un data-label
date pour le classement, et la legende Instagram en speaker notes.
Source unique de verite pour les textes : social/posts/AAAA/MM/*.md
"""
import html
import pathlib
import random
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
random.seed(77)

# --- Direction artistique Mon Artifice -------------------------------------
NUIT, NUIT2 = "#050814", "#0D1330"
OR, OR_CLAIR = "#F5A623", "#FFD166"
ROUGE, BLANC, ARGENT = "#E63946", "#FFF8E7", "#C9CCD5"


def burst(cx, cy, r, rays=26, palette=(OR, OR_CLAIR, ROUGE), seed=0):
    """Gerbe pyrotechnique en SVG : rayons + points en bout de course."""
    rnd = random.Random(seed)
    out = [
        f'<radialGradient id="g{seed}"><stop offset="0%" stop-color="{OR_CLAIR}" '
        f'stop-opacity=".22"/><stop offset="55%" stop-color="{OR}" stop-opacity=".07"/>'
        f'<stop offset="100%" stop-color="{OR}" stop-opacity="0"/></radialGradient>',
        f'<circle cx="{cx}" cy="{cy}" r="{r*1.15:.0f}" fill="url(#g{seed})"/>',
    ]
    for i in range(rays):
        ang = (360 / rays) * i + rnd.uniform(-4, 4)
        length = r * rnd.uniform(0.55, 1.0)
        rad = ang * 3.14159265 / 180
        x2 = cx + length * __import__("math").cos(rad)
        y2 = cy + length * __import__("math").sin(rad)
        col = rnd.choice(palette)
        out.append(
            f'<line x1="{cx:.0f}" y1="{cy:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
            f'stroke="{col}" stroke-width="{rnd.uniform(1.2, 3.0):.1f}" '
            f'stroke-linecap="round" opacity="{rnd.uniform(0.35, 0.9):.2f}"/>'
        )
        out.append(
            f'<circle cx="{x2:.0f}" cy="{y2:.0f}" r="{rnd.uniform(2, 5):.1f}" '
            f'fill="{col}" opacity="{rnd.uniform(0.5, 1.0):.2f}"/>'
        )
    return "".join(out)


def sparks(n, w=1080, h=1350, seed=0):
    rnd = random.Random(seed)
    return "".join(
        f'<circle cx="{rnd.randint(0, w)}" cy="{rnd.randint(0, h)}" '
        f'r="{rnd.uniform(0.8, 2.2):.1f}" fill="{rnd.choice([OR_CLAIR, BLANC, ARGENT])}" '
        f'opacity="{rnd.uniform(0.10, 0.45):.2f}"/>'
        for _ in range(n)
    )


CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#1b1b1b;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif}}
.page{{position:relative;width:1080px;height:1350px;overflow:hidden;
  background:radial-gradient(ellipse at 50% 22%,{NUIT2} 0%,{NUIT} 62%,#02030A 100%);
  color:{BLANC};margin:0 auto 48px}}
.bg{{position:absolute;inset:0}}
.inner{{position:relative;height:100%;display:flex;flex-direction:column;
  justify-content:flex-end;padding:96px 88px 158px}}
.inner.mid{{justify-content:center}}
.frame{{position:absolute;inset:44px;border:2px solid rgba(245,166,35,.42)}}
.eyebrow{{font-size:30px;letter-spacing:.30em;text-transform:uppercase;
  color:{OR};font-weight:700;margin-bottom:28px}}
.badge{{display:inline-block;align-self:flex-start;background:{OR};color:{NUIT};
  font-size:27px;font-weight:800;letter-spacing:.20em;text-transform:uppercase;
  padding:13px 30px;margin-bottom:36px}}
h1{{font-family:'Anton','Arial Narrow',Impact,'Helvetica Neue',sans-serif;
  font-size:112px;line-height:.94;letter-spacing:-.015em;text-transform:uppercase;
  font-weight:900;color:{BLANC}}}
h1.sm{{font-size:88px}}
h1.xs{{font-size:74px}}
.sub{{font-size:38px;line-height:1.35;color:{ARGENT};margin-top:34px;max-width:820px}}
.rule{{width:132px;height:5px;background:{OR};margin:44px 0 0}}
.pills{{display:flex;flex-wrap:wrap;gap:16px;margin-top:46px}}
.pill{{border:2px solid {OR};color:{OR_CLAIR};font-size:27px;font-weight:700;
  letter-spacing:.10em;text-transform:uppercase;padding:14px 28px;border-radius:999px}}
.opts{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin-top:48px;max-width:660px}}
.opt{{background:rgba(245,166,35,.12);border:2px solid rgba(245,166,35,.55);
  color:{BLANC};font-size:40px;font-weight:800;letter-spacing:.06em;
  padding:24px 40px;border-radius:14px;text-align:center}}
.cta{{display:flex;justify-content:space-between;align-items:flex-end;
  margin-top:58px;padding-top:30px;border-top:1px solid rgba(245,166,35,.28)}}
.cta-txt{{font-size:29px;color:{ARGENT};letter-spacing:.05em}}
.logo{{font-family:'Anton','Arial Narrow',Impact,sans-serif;font-size:34px;
  letter-spacing:.24em;color:{OR};text-transform:uppercase}}
.foot{{position:absolute;left:88px;bottom:58px;font-size:22px;letter-spacing:.20em;
  color:rgba(201,204,213,.5);text-transform:uppercase}}
"""

# --- Definition des 17 pages de septembre 2026 -----------------------------
PAGES = [
    dict(n="01", date="02/09", kind="produit", eyebrow="Champs-Élysées® Mariage Prestige",
         title="5 minutes sur votre musique", size="",
         pills=["5 min", "Musical", "Prêt à l'emploi"], cta="Fiche complète sur le site"),
    dict(n="02", date="04/09", kind="emotion",
         title="Le moment où tout le monde lève la tête", size="sm"),
    dict(n="03", date="06/09", kind="coulisses", eyebrow="Coulisses",
         title="Les 30 minutes avant le feu", size="sm",
         sub="30 minutes de préparation pour 3 minutes de spectacle."),
    dict(n="04", date="07/09", kind="pedago", badge="À savoir",
         title="Faut-il prévenir la mairie ?", size="",
         sub="Ça dépend de trois choses. On vous explique."),
    dict(n="05", date="09/09", kind="produit", eyebrow="Champs-Élysées® 100 % éventaillé",
         title="202 coups en une minute", size="",
         pills=["202 coups", "1 min", "Éventaillé"], cta="Fiche complète sur le site"),
    dict(n="06", date="11/09", kind="emotion", eyebrow="Mariage",
         title="Les mariages de septembre", size="",
         sub="ont quelque chose que les autres n'ont pas."),
    dict(n="07", date="13/09", kind="communaute",
         title="Votre feu idéal dure combien de temps ?", size="xs",
         opts=["1 min 30", "3 min", "5 min", "8 min"]),
    dict(n="08", date="14/09", kind="pedago", badge="Sécurité",
         title="La distance de sécurité, simplement", size="sm",
         sub="Trois choses que beaucoup ignorent."),
    dict(n="09", date="16/09", kind="produit", eyebrow="Portable® de proximité",
         title="Pas de grand terrain ? Pas de problème.", size="xs",
         pills=["1 min 30", "Proximité", "Petits espaces"], cta="Fiche complète sur le site"),
    dict(n="10", date="18/09", kind="emotion",
         title="Il a dit oui. Le ciel aussi.", size=""),
    dict(n="11", date="20/09", kind="coulisses", eyebrow="Expertise",
         title="Compact ou éventail ?", size="",
         sub="Même durée. Rendu totalement différent."),
    dict(n="12", date="21/09", kind="pedago", badge="Réglementation",
         title="F1 F2 F3 F4 : qu'est-ce que ça veut dire ?", size="xs",
         sub="Ces lettres sur les boîtes, ce n'est pas du marketing."),
    dict(n="13", date="23/09", kind="produit", eyebrow="Champs-Élysées® 4MN",
         title="4 minutes. La durée d'une vraie soirée.", size="xs",
         pills=["4 min", "Soirée", "Spectacle"], cta="Fiche complète sur le site"),
    dict(n="14", date="25/09", kind="silence",
         title="Le silence juste avant", size=""),
    dict(n="15", date="27/09", kind="communaute",
         title="Montrez-nous votre été", size="",
         sub="On republie les plus belles."),
    dict(n="16", date="28/09", kind="pedago", badge="Météo",
         title="Et s'il pleut ?", size="",
         sub="La pluie n'est pas le pire ennemi. Le vent, si."),
    dict(n="17", date="30/09", kind="produit", eyebrow="Mad Fire Box®",
         title="100 coups de folie", size="",
         pills=["100 coups", "Intense"], cta="Fiche complète sur le site"),
]


def captions():
    """Extrait la legende Instagram de chaque fichier post (source de verite)."""
    out = []
    for f in sorted((ROOT / "posts/2026/09").glob("*.md")):
        txt = f.read_text(encoding="utf-8")
        m = re.search(r"## Texte Instagram\n(.*?)\n## Texte Facebook", txt, re.S)
        out.append(m.group(1).strip() if m else "")
    return out


def render(p, caption, idx):
    kind, size = p["kind"], p.get("size", "")
    seed = idx * 17 + 3

    if kind in ("emotion", "silence"):
        bg = (f'<svg class="bg" viewBox="0 0 1080 1350">{sparks(150, seed=seed)}'
              + ("" if kind == "silence" else burst(700, 400, 330, 30, seed=seed))
              + "</svg>")
        frame = ""
    elif kind == "produit":
        bg = (f'<svg class="bg" viewBox="0 0 1080 1350">{sparks(110, seed=seed)}'
              f'{burst(760, 360, 290, 26, seed=seed)}'
              f'{burst(300, 250, 150, 16, seed=seed + 1)}</svg>')
        frame = '<div class="frame"></div>'
    else:
        bg = (f'<svg class="bg" viewBox="0 0 1080 1350">{sparks(90, seed=seed)}'
              f'{burst(880, 250, 210, 20, seed=seed)}</svg>')
        frame = ""

    body = []
    if p.get("badge"):
        body.append(f'<div class="badge">{html.escape(p["badge"])}</div>')
    if p.get("eyebrow"):
        body.append(f'<div class="eyebrow">{html.escape(p["eyebrow"])}</div>')
    body.append(f'<h1 class="{size}">{html.escape(p["title"])}</h1>')
    if p.get("sub"):
        body.append(f'<p class="sub">{html.escape(p["sub"])}</p>')
    if p.get("pills"):
        body.append('<div class="pills">'
                    + "".join(f'<span class="pill">{html.escape(x)}</span>' for x in p["pills"])
                    + "</div>")
    if p.get("opts"):
        body.append('<div class="opts">'
                    + "".join(f'<span class="opt">{html.escape(x)}</span>' for x in p["opts"])
                    + "</div>")
    if not p.get("pills") and not p.get("opts"):
        body.append('<div class="rule"></div>')

    cta = (f'<div class="cta"><span class="cta-txt">{html.escape(p["cta"])}</span>'
           f'<span class="logo">Mon Artifice</span></div>') if p.get("cta") else \
          '<div class="cta"><span class="cta-txt"></span><span class="logo">Mon Artifice</span></div>'

    label = f'{p["n"]} · {p["date"]} · {p["title"]}'
    mid = " mid" if kind == "silence" else ""
    return (
        f'<div class="page" data-document-role="page" '
        f'data-label="{html.escape(label, quote=True)}" '
        f'data-speaker-notes="{html.escape(caption, quote=True)}">'
        f'{bg}{frame}<div class="inner{mid}">{"".join(body)}{cta}</div>'
        f'<div class="foot">Septembre 2026 · {p["date"]}</div></div>'
    )


def main():
    caps = captions()
    assert len(caps) == len(PAGES), f"{len(caps)} legendes pour {len(PAGES)} pages"
    pages = "\n".join(render(p, c, i) for i, (p, c) in enumerate(zip(PAGES, caps)))
    doc = (f'<!doctype html><html lang="fr"><head><meta charset="utf-8">'
           f'<title>Mon Artifice — Septembre 2026</title><style>{CSS}</style></head>'
           f'<body>{pages}</body></html>')
    out = ROOT / "visuels/2026/09/septembre-2026.html"
    out.write_text(doc, encoding="utf-8")
    print(f"{out.relative_to(ROOT.parent)} — {len(PAGES)} pages, {len(doc)//1024} Ko")


if __name__ == "__main__":
    main()
