#!/usr/bin/env python3
"""Genere le fichier HTML multi-pages importable dans Canva.

Chaque page porte data-document-role="page" (une page Canva), un data-label date
pour le classement, et la legende Instagram en speaker notes.
Source unique de verite pour les textes : social/posts/AAAA/MM/*.md
"""
import html
import math
import pathlib
import random
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
random.seed(77)

# --- Direction artistique Mon Artifice -------------------------------------
# Couleurs relevees dans le SVG du logo fourni le 30/08/2026.
# Le lettrage du logo est blanc : le logo est concu pour un fond sombre,
# ce qui valide le parti pris du fond nuit.
NUIT, NUIT2 = "#08080F", "#17172E"
VERT, VERT_CLAIR = "#8DBB20", "#AEDA4A"
MAGENTA, MAGENTA_CLAIR = "#D50175", "#F5399B"
BLANC, GRIS = "#FFFFFF", "#C8CBD4"
PALETTE = (VERT, MAGENTA, VERT_CLAIR, MAGENTA_CLAIR)


def burst(cx, cy, r, rays=26, seed=0):
    """Gerbe pyrotechnique : halo + rayons + points, aux couleurs de la marque."""
    rnd = random.Random(seed)
    out = [
        f'<radialGradient id="g{seed}"><stop offset="0%" stop-color="{VERT_CLAIR}" '
        f'stop-opacity=".16"/><stop offset="55%" stop-color="{MAGENTA}" stop-opacity=".06"/>'
        f'<stop offset="100%" stop-color="{MAGENTA}" stop-opacity="0"/></radialGradient>',
        f'<circle cx="{cx}" cy="{cy}" r="{r * 1.15:.0f}" fill="url(#g{seed})"/>',
    ]
    for i in range(rays):
        ang = (360 / rays) * i + rnd.uniform(-4, 4)
        length = r * rnd.uniform(0.55, 1.0)
        rad = math.radians(ang)
        x2, y2 = cx + length * math.cos(rad), cy + length * math.sin(rad)
        col = rnd.choice(PALETTE)
        out.append(f'<line x1="{cx:.0f}" y1="{cy:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
                   f'stroke="{col}" stroke-width="{rnd.uniform(1.2, 3.0):.1f}" '
                   f'stroke-linecap="round" opacity="{rnd.uniform(.35, .9):.2f}"/>')
        out.append(f'<circle cx="{x2:.0f}" cy="{y2:.0f}" r="{rnd.uniform(2, 5):.1f}" '
                   f'fill="{col}" opacity="{rnd.uniform(.5, 1):.2f}"/>')
    return "".join(out)


def sparks(n, seed=0):
    rnd = random.Random(seed)
    return "".join(
        f'<circle cx="{rnd.randint(0, 1080)}" cy="{rnd.randint(0, 1350)}" '
        f'r="{rnd.uniform(.8, 2.2):.1f}" fill="{rnd.choice([VERT_CLAIR, BLANC, MAGENTA_CLAIR])}" '
        f'opacity="{rnd.uniform(.10, .42):.2f}"/>' for _ in range(n))


def logo_mark():
    """Rappel du logo : deux gerbes, une verte une magenta, avec tige et point."""
    def mini(cx, cy, r, col, rays=13, seed=1):
        rnd = random.Random(seed)
        s = "".join(
            f'<line x1="{cx}" y1="{cy}" x2="{cx + r * math.cos(math.radians(a)):.1f}" '
            f'y2="{cy + r * math.sin(math.radians(a)):.1f}" stroke="{col}" '
            f'stroke-width="1.6" stroke-linecap="round"/>'
            for a in [(360 / rays) * i + rnd.uniform(-6, 6) for i in range(rays)])
        return s
    return ('<svg width="76" height="46" viewBox="0 0 76 46">'
            + mini(24, 15, 13, VERT, seed=3)
            + f'<path d="M24 15 Q14 32 7 40" stroke="{VERT}" stroke-width="1.6" fill="none"/>'
            + f'<circle cx="6" cy="41" r="3.4" fill="{VERT}"/>'
            + mini(56, 24, 10, MAGENTA, rays=11, seed=9)
            + f'<path d="M56 24 Q49 34 43 40" stroke="{MAGENTA}" stroke-width="1.6" fill="none"/>'
            + f'<circle cx="42" cy="41" r="3" fill="{MAGENTA}"/></svg>')


CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#1b1b1b;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif}}
.page{{position:relative;width:1080px;height:1350px;overflow:hidden;
  background:radial-gradient(ellipse at 50% 20%,{NUIT2} 0%,{NUIT} 62%,#040409 100%);
  color:{BLANC};margin:0 auto 48px}}
.bg{{position:absolute;inset:0}}
.inner{{position:relative;height:100%;display:flex;flex-direction:column;
  justify-content:flex-end;padding:92px 88px 152px}}
.inner.mid{{justify-content:center}}
.photo{{position:absolute;left:64px;right:64px;top:64px;height:560px;
  border:2px dashed rgba(141,187,32,.45);border-radius:6px;
  display:flex;align-items:center;justify-content:center}}
.photo span{{font-size:24px;letter-spacing:.26em;color:rgba(141,187,32,.68);
  text-transform:uppercase;font-weight:700}}
.eyebrow{{font-size:30px;letter-spacing:.30em;text-transform:uppercase;
  color:{VERT};font-weight:700;margin-bottom:26px}}
.badge{{display:inline-block;align-self:flex-start;background:{MAGENTA};color:{BLANC};
  font-size:27px;font-weight:800;letter-spacing:.20em;text-transform:uppercase;
  padding:13px 30px;margin-bottom:34px}}
h1{{font-family:'Anton','Arial Narrow',Impact,'Helvetica Neue',sans-serif;
  font-size:112px;line-height:.94;letter-spacing:-.015em;text-transform:uppercase;
  font-weight:900;color:{BLANC}}}
h1.sm{{font-size:90px}}
h1.xs{{font-size:76px}}
.sub{{font-size:37px;line-height:1.35;color:{GRIS};margin-top:32px;max-width:830px}}
.rule{{width:132px;height:5px;background:{VERT};margin-top:42px}}
.pills{{display:flex;flex-wrap:wrap;gap:16px;margin-top:44px}}
.pill{{border:2px solid {VERT};color:{VERT_CLAIR};font-size:27px;font-weight:700;
  letter-spacing:.10em;text-transform:uppercase;padding:14px 28px;border-radius:999px}}
.pill.m{{border-color:{MAGENTA};color:{MAGENTA_CLAIR}}}
.opts{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;
  margin-top:46px;max-width:680px}}
.opt{{background:rgba(141,198,63,.10);border:2px solid rgba(141,198,63,.5);
  color:{BLANC};font-size:40px;font-weight:800;letter-spacing:.05em;
  padding:24px 34px;border-radius:14px;text-align:center}}
.cta{{display:flex;justify-content:space-between;align-items:flex-end;
  margin-top:54px;padding-top:28px;border-top:1px solid rgba(141,187,32,.26)}}
.cta-txt{{font-size:29px;color:{GRIS};letter-spacing:.04em;max-width:560px}}
.brand{{display:flex;align-items:center;gap:14px}}
.brand-name{{font-family:'Anton','Arial Narrow',Impact,sans-serif;font-size:32px;
  letter-spacing:.22em;color:{BLANC};text-transform:uppercase}}
.foot{{position:absolute;left:88px;bottom:56px;font-size:22px;letter-spacing:.20em;
  color:rgba(200,203,212,.45);text-transform:uppercase}}
"""

# --- Septembre 2026 : phase de PRE-LANCEMENT --------------------------------
# La boutique n'est pas en ligne : aucun post produit, aucun CTA vers le site.
# Pilier dominant : coulisses metier (photos reelles a shooter).
CTA_DM = "Une question ? Écrivez-nous en message privé"

PAGES = [
    dict(n="01", date="02/09", kind="coulisses", eyebrow="Expertise",
         title="Compact ou éventail ?", sub="Même durée. Rendu totalement différent."),
    dict(n="02", date="04/09", kind="silence", title="Le silence juste avant"),
    dict(n="03", date="06/09", kind="communaute",
         title="Votre feu idéal dure combien de temps ?", size="xs",
         opts=["30 sec", "1 min 30", "3 min", "5 min"]),
    dict(n="04", date="07/09", kind="pedago", badge="À savoir",
         title="Faut-il prévenir la mairie ?",
         sub="Ça dépend de trois choses. On vous explique.", cta=CTA_DM),
    dict(n="05", date="09/09", kind="coulisses", photo="E1", eyebrow="Mon Artifice",
         title="Artificiers de métier", sub="On se présente, puisque ce compte commence.",
         cta=CTA_DM),
    dict(n="06", date="11/09", kind="emotion", photo="I1",
         title="Le moment où tout le monde lève la tête", size="sm"),
    dict(n="07", date="13/09", kind="coulisses", photo="A1", eyebrow="Coulisses",
         title="Le méchage", sub="3 heures de travail pour 3 minutes de spectacle."),
    dict(n="08", date="14/09", kind="pedago", badge="Sécurité",
         title="8 mètres ou 25 mètres ?", sub="La différence n'est pas un détail.",
         pills=["F2 · 8 m", "F3 · 25 m"]),
    dict(n="09", date="16/09", kind="coulisses", photo="B1", eyebrow="Coulisses",
         title="La mise d'inflammateur", size="sm",
         sub="Chaque départ a son fil. Chaque fil a son numéro."),
    dict(n="10", date="18/09", kind="emotion", photo="H3",
         title="Il a dit oui. Le ciel aussi.", cta=CTA_DM),
    dict(n="11", date="20/09", kind="coulisses", photo="C3", eyebrow="Coulisses",
         title="De la caisse au dispositif", size="sm",
         sub="Un feu d'artifice, ça ne se pose pas. Ça se monte."),
    dict(n="12", date="21/09", kind="pedago", badge="Réglementation",
         title="F2 ou F3 ?", sub="C'est ce qui détermine où vous pourrez tirer.",
         pills=["F2 · 8 m", "F3 · 25 m"]),
    dict(n="13", date="23/09", kind="coulisses", photo="D1", eyebrow="Coulisses",
         title="Le tableau de tir", sub="Une ligne = un départ = une seconde précise."),
    dict(n="14", date="25/09", kind="emotion", photo="H2", eyebrow="Mariage",
         title="Les mariages de septembre",
         sub="ont quelque chose que les autres n'ont pas.", cta=CTA_DM),
    dict(n="15", date="27/09", kind="communaute", photo="I3",
         title="Montrez-nous votre été", sub="On republie les plus belles."),
    dict(n="16", date="28/09", kind="pedago", badge="Météo", title="Et s'il pleut ?",
         sub="La pluie n'est pas le pire ennemi. Le vent, si."),
    dict(n="17", date="30/09", kind="coulisses", photo="F2", eyebrow="Coulisses",
         title="Ce qu'il reste après", size="sm",
         sub="On repart quand le terrain est plus propre qu'à l'arrivée."),
]


def captions():
    """Legende Instagram de chaque post : les fichiers posts/ font foi."""
    out = []
    for f in sorted((ROOT / "posts/2026/09").glob("*.md")):
        m = re.search(r"## Texte Instagram\n(.*?)\n## Texte Facebook",
                      f.read_text(encoding="utf-8"), re.S)
        out.append(m.group(1).strip() if m else "")
    return out


def render(p, caption, idx):
    kind, size = p["kind"], p.get("size", "")
    seed = idx * 17 + 3
    n_sparks = 150 if kind in ("emotion", "silence") else 100

    svg = f'<svg class="bg" viewBox="0 0 1080 1350">{sparks(n_sparks, seed)}'
    if kind == "silence":
        pass
    elif p.get("photo"):
        # La vraie photo porte le visuel : pas de gerbe, elle chevaucherait le titre.
        pass
    elif kind == "emotion":
        svg += burst(700, 400, 330, 30, seed)
    elif kind == "pedago":
        svg += burst(880, 250, 215, 20, seed)
    else:
        svg += burst(770, 330, 290, 26, seed) + burst(300, 235, 150, 16, seed + 1)
    svg += "</svg>"

    photo = (f'<div class="photo"><span>Photo {html.escape(p["photo"])}</span></div>'
             if p.get("photo") else "")

    body = []
    if p.get("badge"):
        body.append(f'<div class="badge">{html.escape(p["badge"])}</div>')
    if p.get("eyebrow"):
        body.append(f'<div class="eyebrow">{html.escape(p["eyebrow"])}</div>')
    body.append(f'<h1 class="{size}">{html.escape(p["title"])}</h1>')
    if p.get("sub"):
        body.append(f'<p class="sub">{html.escape(p["sub"])}</p>')
    if p.get("pills"):
        body.append('<div class="pills">' + "".join(
            f'<span class="pill{" m" if i else ""}">{html.escape(x)}</span>'
            for i, x in enumerate(p["pills"])) + "</div>")
    if p.get("opts"):
        body.append('<div class="opts">' + "".join(
            f'<span class="opt">{html.escape(x)}</span>' for x in p["opts"]) + "</div>")
    if not p.get("pills") and not p.get("opts") and not p.get("sub"):
        body.append('<div class="rule"></div>')

    body.append(f'<div class="cta"><span class="cta-txt">{html.escape(p.get("cta", ""))}</span>'
                f'<span class="brand">{logo_mark()}'
                f'<span class="brand-name">Mon Artifice</span></span></div>')

    label = f'{p["n"]} · {p["date"]} · {p["title"]}'
    if p.get("photo"):
        label += f' · photo {p["photo"]}'
    mid = " mid" if p["kind"] == "silence" else ""
    return (f'<div class="page" data-document-role="page" '
            f'data-label="{html.escape(label, quote=True)}" '
            f'data-speaker-notes="{html.escape(caption, quote=True)}">'
            f'{svg}{photo}<div class="inner{mid}">{"".join(body)}</div>'
            f'<div class="foot">Septembre 2026 · {p["date"]}</div></div>')


def main():
    caps = captions()
    assert len(caps) == len(PAGES), f"{len(caps)} légendes pour {len(PAGES)} pages"
    pages = "\n".join(render(p, c, i) for i, (p, c) in enumerate(zip(PAGES, caps)))
    doc = ('<!doctype html><html lang="fr"><head><meta charset="utf-8">'
           f'<title>Mon Artifice — Septembre 2026</title><style>{CSS}</style></head>'
           f'<body>{pages}</body></html>')
    out = ROOT / "visuels/2026/09/septembre-2026.html"
    out.write_text(doc, encoding="utf-8")
    print(f"{out.name} — {len(PAGES)} pages, {len(doc) // 1024} Ko")


if __name__ == "__main__":
    main()
