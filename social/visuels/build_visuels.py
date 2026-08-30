#!/usr/bin/env python3
"""Genere le fichier HTML multi-pages importable dans Canva.

Chaque page porte data-document-role="page" (une page Canva), un data-label date
pour le classement, et la legende Instagram en speaker notes.
Source unique de verite pour les textes : social/posts/AAAA/MM/*.md
"""
import base64
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
MAGENTA, MAGENTA_CLAIR = "#D50174", "#F5399B"
BLANC, GRIS = "#FFFFFF", "#C8CBD4"
PALETTE = (VERT, MAGENTA, VERT_CLAIR, MAGENTA_CLAIR)


def logo_uri():
    """Logo officiel, encode une seule fois dans le CSS et partage par les 17 pages."""
    p = ROOT / "brand/logo-mon-artifice.png"
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def photo_uri(nom):
    """Encode la photo en data URI. Le fichier HTML doit rester autonome :
    l'import Canva ne recupere qu'une seule URL, pas les images liees."""
    p = ROOT / "photos/2026-09" / nom
    if not p.exists():
        return None
    return "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode()


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


LOGO = logo_uri()
LOGO_H = 192

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
.shot{{position:absolute;inset:0;background-size:cover;background-position:center}}
.shot.wide{{inset:0 0 auto 0;height:660px;background-position:center 42%}}
.veil{{position:absolute;inset:0;background:linear-gradient(to bottom,
  rgba(8,8,15,.34) 0%,rgba(8,8,15,.14) 22%,rgba(8,8,15,.58) 42%,
  rgba(8,8,15,.90) 62%,rgba(8,8,15,.98) 78%)}}
.veil.wide{{background:linear-gradient(to bottom,rgba(8,8,15,.18) 0%,
  rgba(8,8,15,.05) 34%,rgba(8,8,15,.90) 46%,{NUIT} 54%)}}
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
.brand{{width:296px;height:{LOGO_H}px;background:url({LOGO}) no-repeat right center;
  background-size:contain;flex:none}}
.foot{{position:absolute;left:88px;bottom:56px;font-size:22px;letter-spacing:.20em;
  color:rgba(200,203,212,.45);text-transform:uppercase}}
"""

# --- Styles additionnels pour les slides de carrousel ---------------------
CSS += f"""
.num{{font-family:'Anton','Arial Narrow',Impact,sans-serif;font-size:150px;line-height:.8;
  color:{VERT};opacity:.85;margin-bottom:26px}}
h2{{font-family:'Anton','Arial Narrow',Impact,sans-serif;font-size:86px;line-height:.96;
  text-transform:uppercase;color:{BLANC};letter-spacing:-.01em}}
h2.sm{{font-size:70px}}
.quote{{font-family:'Anton','Arial Narrow',Impact,sans-serif;font-size:96px;line-height:1.02;
  text-transform:uppercase;color:{BLANC};letter-spacing:-.01em}}
.quote.sm{{font-size:76px}}
.qmark{{font-size:150px;line-height:.5;color:{MAGENTA};margin-bottom:10px}}
.fig{{font-family:'Anton','Arial Narrow',Impact,sans-serif;font-size:230px;line-height:.82;
  color:{BLANC}}}
.fig small{{font-size:88px;color:{VERT}}}
.tag{{display:inline-block;align-self:flex-start;border:2px solid {MAGENTA};color:{MAGENTA_CLAIR};
  font-size:30px;font-weight:800;letter-spacing:.2em;padding:12px 26px;margin-bottom:30px}}
.tag.v{{border-color:{VERT};color:{VERT_CLAIR}}}
.save{{display:flex;align-items:center;gap:16px;margin-top:40px;font-size:32px;color:{VERT_CLAIR};
  font-weight:700}}
.grid6{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:40px}}
.grid6 div{{aspect-ratio:1;border:2px dashed rgba(141,187,32,.42);border-radius:4px;
  display:flex;align-items:center;justify-content:center;font-size:22px;
  color:rgba(141,187,32,.6);letter-spacing:.2em}}
.diag{{position:absolute;left:0;right:0;top:96px;height:620px}}
"""


def schema_distance(actif, couleur, rayon):
    """Vue de dessus a l'echelle. Les deux perimetres sont traces : celui dont
    parle la slide en couleur, l'autre en fantome. La comparaison se voit alors
    sur chaque slide, et le petit cercle ne parait plus perdu."""
    cx, cy = 540, 310
    autre = 281 if rayon == 90 else 90
    public = "".join(
        f'<circle cx="{cx + (rayon + 40) * math.cos(math.radians(a)):.0f}" '
        f'cy="{cy + (rayon + 40) * math.sin(math.radians(a)) * .55:.0f}" r="8" '
        f'fill="{GRIS}" opacity=".7"/>' for a in range(-60, 62, 12))
    return (f'<svg class="diag" viewBox="0 0 1080 640">'
            f'<circle cx="{cx}" cy="{cy}" r="{autre}" fill="none" stroke="{GRIS}" '
            f'stroke-width="2" stroke-dasharray="8 10" opacity=".22"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{rayon}" fill="{couleur}" fill-opacity=".08" '
            f'stroke="{couleur}" stroke-width="3" stroke-dasharray="14 12"/>'
            f'<rect x="{cx - 22}" y="{cy - 22}" width="44" height="44" fill="{couleur}"/>'
            f'<line x1="{cx}" y1="{cy}" x2="{cx + rayon}" y2="{cy}" stroke="{BLANC}" stroke-width="3"/>'
            f'<text x="{cx + rayon / 2}" y="{cy - 18}" fill="{BLANC}" font-size="40" '
            f'font-family="Helvetica,Arial" font-weight="700" text-anchor="middle">{actif}</text>'
            f'{public}</svg>')



# --- Septembre 2026 : phase de PRE-LANCEMENT --------------------------------
# La boutique n'est pas en ligne : aucun post produit, aucun CTA vers le site.
# Chaque publication porte ses slides. `img` = photo disponible,
# `shot` = plan a shooter (cadre reserve nomme).
CTA_DM = "Une question ? Écrivez-nous en message privé"
SAVE = "Enregistrez ce post"

POSTS = [
 dict(n="01", date="02/09", fmt="Reel", titre="Compact ou éventail ?", slides=[
   dict(k="cover", eyebrow="Expertise", t="Compact ou éventail ?",
        sub="Même durée. Rendu totalement différent.")]),

 dict(n="02", date="04/09", fmt="Post", titre="Le silence juste avant", slides=[
   dict(k="cover", style="silence", t="Le silence juste avant")]),

 dict(n="03", date="06/09", fmt="Sondage", titre="Votre feu idéal dure combien de temps ?", slides=[
   dict(k="cover", t="Votre feu idéal dure combien de temps ?", size="xs",
        opts=["30 sec", "1 min 30", "3 min", "5 min"])]),

 dict(n="04", date="07/09", fmt="Carrousel", titre="Faut-il prévenir la mairie ?", slides=[
   dict(k="cover", badge="À savoir", t="Faut-il prévenir la mairie ?",
        sub="Ça dépend de trois choses."),
   dict(k="point", i="01", t="La catégorie du produit",
        sub="Toutes les catégories ne sont pas soumises aux mêmes obligations."),
   dict(k="point", i="02", t="Le lieu",
        sub="Un terrain privé et un espace public, ce n'est pas la même chose."),
   dict(k="point", i="03", t="La taille de l'événement",
        sub="Un feu entre amis dans un jardin n'est pas un feu de village."),
   dict(k="end", t="Dans le doute, appelez votre mairie.",
        sub="C'est gratuit et ça prend cinq minutes.", save=True, cta=CTA_DM)]),

 dict(n="05", date="09/09", fmt="Post épinglé", titre="Artificiers de métier", slides=[
   dict(k="cover", eyebrow="Qui sommes-nous", t="Artificiers de métier",
        sub="On se présente, puisque ce compte commence.",
        img="E1-artificier-obus.jpg", cta=CTA_DM)]),

 dict(n="06", date="11/09", fmt="Reel", titre="Le moment où tout le monde lève la tête", slides=[
   dict(k="cover", t="Le moment où tout le monde lève la tête", size="sm", shot="I1")]),

 dict(n="07", date="13/09", fmt="Carrousel", titre="Le méchage", slides=[
   dict(k="cover", eyebrow="Coulisses", t="Le méchage",
        sub="Ce que personne ne voit.", img="A1-mechage-rack-meches.jpg"),
   dict(k="quote", t="3 heures de travail pour 3 minutes de spectacle."),
   dict(k="photo", shot="A2", legende="Le détail d'un raccord."),
   dict(k="photo", shot="A3", legende="Le dispositif méché, prêt à tirer."),
   dict(k="end", t="On est artificiers.", sub="C'est notre métier, pas notre passe-temps.")]),

 dict(n="08", date="14/09", fmt="Carrousel", titre="8 mètres ou 25 mètres ?", slides=[
   dict(k="cover", badge="Sécurité", t="8 mètres ou 25 mètres ?",
        sub="La différence n'est pas un détail.", pills=["F2 · 8 m", "F3 · 25 m"]),
   dict(k="stat", tag="Catégorie F2", fig="8", unit="mètres", schema=(VERT, 90, "8 m"),
        sub="Ça passe dans la majorité des jardins."),
   dict(k="stat", tag="Catégorie F3", fig="25", unit="mètres", schema=(MAGENTA, 281, "25 m"),
        sub="Il vous faut un vrai terrain dégagé."),
   dict(k="point", i="!", t="Dans toutes les directions",
        sub="Pas seulement face au public. Derrière et sur les côtés aussi."),
   dict(k="end", t="Vent, arbres, fils, toitures.",
        sub="La distance ne suffit pas à elle seule. La notice du produit fait foi.", save=True)]),

 dict(n="09", date="16/09", fmt="Carrousel", titre="La mise d'inflammateur", slides=[
   dict(k="cover", eyebrow="Coulisses", t="La mise d'inflammateur", size="sm",
        img="B1-mise-inflammateur-mains.jpg"),
   dict(k="photo", shot="B2", legende="Le câblage, fil par fil."),
   dict(k="quote", t="Chaque départ a son fil. Chaque fil a son numéro.", size="sm"),
   dict(k="end", t="On décide à la milliseconde.",
        sub="C'est ce qui permet de synchroniser un feu sur une musique.")]),

 dict(n="10", date="18/09", fmt="Reel", titre="Il a dit oui. Le ciel aussi.", slides=[
   dict(k="cover", t="Il a dit oui. Le ciel aussi.", shot="H3", cta=CTA_DM)]),

 dict(n="11", date="20/09", fmt="Reel", titre="De la caisse au dispositif", slides=[
   dict(k="cover", eyebrow="Coulisses", t="De la caisse au dispositif", size="sm",
        sub="Un feu d'artifice, ça ne se pose pas. Ça se monte.",
        img="C5-dispositif-monte-complet.jpg", wide=True)]),

 dict(n="12", date="21/09", fmt="Carrousel", titre="F2 ou F3 ?", slides=[
   dict(k="cover", badge="Réglementation", t="F2 ou F3 ?",
        sub="C'est ce qui détermine où vous pourrez tirer."),
   dict(k="stat", tag="F2", fig="8", unit="mètres", schema=(VERT, 90, "8 m"),
        sub="La majorité des jardins."),
   dict(k="stat", tag="F3", fig="25", unit="mètres", schema=(MAGENTA, 281, "25 m"),
        sub="Terrain dégagé nécessaire. Plus puissant, plus haut."),
   dict(k="end", t="La catégorie est sur le produit.",
        sub="Regardez-la en premier. Avant la durée, avant le nombre de coups.", save=True)]),

 dict(n="13", date="23/09", fmt="Carrousel", titre="Le tableau de tir", slides=[
   dict(k="cover", eyebrow="Coulisses", t="Le tableau de tir",
        img="D1-tableau-de-tir.jpg"),
   dict(k="photo", shot="D2", legende="Les lignes numérotées."),
   dict(k="quote", t="Une ligne = un départ = une seconde précise.", size="sm"),
   dict(k="end", t="Ce n'est pas de l'improvisation.",
        sub="C'est une partition. Et la clé de sécurité est la dernière barrière.")]),

 dict(n="14", date="25/09", fmt="Post", titre="Les mariages de septembre", slides=[
   dict(k="cover", eyebrow="Mariage", t="Les mariages de septembre",
        sub="ont quelque chose que les autres n'ont pas.", shot="H2", cta=CTA_DM)]),

 dict(n="15", date="27/09", fmt="Appel UGC", titre="Montrez-nous votre été", slides=[
   dict(k="cover", t="Montrez-nous votre été", sub="On republie les plus belles.", grid=True)]),

 dict(n="16", date="28/09", fmt="Carrousel", titre="Et s'il pleut ?", slides=[
   dict(k="cover", badge="Météo", t="Et s'il pleut ?",
        sub="La réponse surprend souvent."),
   dict(k="point", i="01", t="La pluie n'est pas le pire ennemi",
        sub="Une pluie fine est gérable si le produit est resté au sec et protégé."),
   dict(k="point", i="02", t="Le vent est le vrai facteur limitant",
        sub="C'est lui qui décide si le feu part ou non. Pas la pluie."),
   dict(k="end", t="L'orage : on ne tire pas.",
        sub="Jamais. Un feu se reporte très bien. Ça ne s'improvise pas.", save=True)]),

 dict(n="17", date="30/09", fmt="Carrousel", titre="Ce qu'il reste après", slides=[
   dict(k="cover", eyebrow="Coulisses", t="Ce qu'il reste après", size="sm", shot="F1"),
   dict(k="photo", shot="F2", legende="Le ramassage, un reliquat après l'autre."),
   dict(k="quote", t="On repart quand le terrain est plus propre qu'à l'arrivée.", size="sm"),
   dict(k="end", t="En octobre, on vous présente nos feux.",
        sub="Un par un, avec leurs vraies caractéristiques.")]),
]


def captions():
    """Legende Instagram de chaque publication : les fichiers posts/ font foi."""
    out = []
    for f in sorted((ROOT / "posts/2026/09").glob("*.md")):
        m = re.search(r"## Texte Instagram\n(.*?)\n## Texte Facebook",
                      f.read_text(encoding="utf-8"), re.S)
        out.append(m.group(1).strip() if m else "")
    return out


def fond(sl, seed):
    """Fond de slide : photo reelle, cadre reserve, ou gerbes."""
    uri = photo_uri(sl["img"]) if sl.get("img") else None
    if uri:
        w = " wide" if sl.get("wide") else ""
        return (f'<div class="shot{w}" style="background-image:url({uri})"></div>'
                f'<div class="veil{w}"></div>'), ""
    svg = f'<svg class="bg" viewBox="0 0 1080 1350">{sparks(110, seed)}'
    k = sl["k"]
    if sl.get("style") == "silence" or sl.get("shot"):
        pass                                    # ciel vide, ou photo a venir
    elif k in ("point", "end"):
        svg += burst(880, 235, 200, 20, seed)
    elif k == "quote":
        svg += burst(760, 330, 300, 28, seed)
    elif k != "stat":
        svg += burst(770, 320, 285, 26, seed) + burst(300, 230, 150, 16, seed + 1)
    svg += "</svg>"
    cadre = (f'<div class="photo"><span>Photo {html.escape(sl["shot"])}</span></div>'
             if sl.get("shot") else "")
    return svg + cadre, ""


def corps(sl):
    k, out = sl["k"], []
    if sl.get("badge"):
        out.append(f'<div class="badge">{html.escape(sl["badge"])}</div>')
    if sl.get("eyebrow"):
        out.append(f'<div class="eyebrow">{html.escape(sl["eyebrow"])}</div>')
    if sl.get("tag"):
        cls = "tag v" if sl["tag"].startswith(("F2", "Catégorie F2")) else "tag"
        out.append(f'<div class="{cls}">{html.escape(sl["tag"])}</div>')
    if k == "point":
        out.append(f'<div class="num">{html.escape(sl["i"])}</div>')
        out.append(f'<h2 class="{sl.get("size", "")}">{html.escape(sl["t"])}</h2>')
    elif k == "stat":
        out.append(f'<div class="fig">{sl["fig"]} <small>{html.escape(sl["unit"])}</small></div>')
    elif k == "quote":
        out.append('<div class="qmark">“</div>')
        out.append(f'<div class="quote {sl.get("size", "")}">{html.escape(sl["t"])}</div>')
    elif k == "end":
        out.append(f'<h2 class="{sl.get("size", "")}">{html.escape(sl["t"])}</h2>')
    elif k == "photo":
        out.append(f'<h2 class="sm">{html.escape(sl.get("legende", ""))}</h2>')
    else:                                        # cover
        out.append(f'<h1 class="{sl.get("size", "")}">{html.escape(sl["t"])}</h1>')
    if sl.get("sub"):
        out.append(f'<p class="sub">{html.escape(sl["sub"])}</p>')
    if sl.get("pills"):
        out.append('<div class="pills">' + "".join(
            f'<span class="pill{" m" if i else ""}">{html.escape(x)}</span>'
            for i, x in enumerate(sl["pills"])) + "</div>")
    if sl.get("opts"):
        out.append('<div class="opts">' + "".join(
            f'<span class="opt">{html.escape(x)}</span>' for x in sl["opts"]) + "</div>")
    if sl.get("grid"):
        out.append('<div class="grid6">' + '<div>VOTRE VIDÉO</div>' * 6 + "</div>")
    if sl.get("save"):
        out.append(f'<div class="save">🔖 {SAVE}</div>')
    if not any(sl.get(x) for x in ("sub", "pills", "opts", "grid", "save")) and k != "photo":
        out.append('<div class="rule"></div>')
    return "".join(out)


def render(post, sl, idx, total, note, seed):
    bg, _ = fond(sl, seed)
    schema = schema_distance(sl["schema"][2], sl["schema"][0], sl["schema"][1]) \
        if sl.get("schema") else ""
    cta = (f'<div class="cta"><span class="cta-txt">{html.escape(sl.get("cta", ""))}</span>'
           f'<span class="brand"></span></div>')
    mid = " mid" if sl.get("style") == "silence" else ""
    pos = f'{idx}/{total}'
    label = f'{post["n"]} · {post["date"]} · {post["titre"]} · {pos}'
    if sl.get("shot"):
        label += f' · photo {sl["shot"]}'
    return (f'<div class="page" data-document-role="page" '
            f'data-label="{html.escape(label, quote=True)}" '
            f'data-speaker-notes="{html.escape(note, quote=True)}">'
            f'{bg}{schema}<div class="inner{mid}">{corps(sl)}{cta}</div>'
            f'<div class="foot">{post["fmt"]} · {post["date"]} · {pos}</div></div>')


def main():
    caps = captions()
    assert len(caps) == len(POSTS), f"{len(caps)} légendes pour {len(POSTS)} publications"
    pages, seed = [], 0
    for post, cap in zip(POSTS, caps):
        n = len(post["slides"])
        for i, sl in enumerate(post["slides"], 1):
            seed += 17
            note = cap if i == 1 else f'{post["titre"]} — slide {i}/{n}. Légende sur la slide 1.'
            pages.append(render(post, sl, i, n, note, seed))
    doc = ('<!doctype html><html lang="fr"><head><meta charset="utf-8">'
           f'<title>Mon Artifice — Septembre 2026</title><style>{CSS}</style></head>'
           f'<body>{"".join(pages)}</body></html>')
    out = ROOT / "visuels/2026/09/septembre-2026.html"
    out.write_text(doc, encoding="utf-8")
    print(f'{out.name} — {len(POSTS)} publications, {len(pages)} pages, {len(doc)//1024} Ko')


if __name__ == "__main__":
    main()
