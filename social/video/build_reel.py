#!/usr/bin/env python3
"""Monte le Reel du 20/09 a partir des rushes du 5 septembre.

Partis pris, tous demandes par le client :

- **Le son des rushes est jete** : on y parle technique entre artificiers.
  La bande-son vient de `musique.py`, ecrite sur mesure donc libre de droits.
- **Pas de bandeaux de sous-titres.** A la place, un reperage d'etape discret en
  haut de l'image : numero, titre, une ligne d'explication. Il tient sur toute
  la duree de l'etape au lieu de clignoter a chaque plan.
- **Stabilisation.** Les plans sortent d'une Osmo Action 5 Pro : RockSteady a
  deja fait le gros du travail, il reste un flottement de main. Passe vidstab en
  deux temps sur une image agrandie de 10 %, pour que le recadrage du
  stabilisateur mange la marge et non l'image finale. Mesure sur M8A : le
  deplacement image a image tombe de 1,40 a 0,76 px, les a-coups (p90) de 3,0 a 1,0.

- **Etalonnage.** Les rushes sortent tres plats — saturation moyenne 0,17,
  noirs leves a 35/255. La chaine ci-dessous les remonte a ~0,32 et redescend
  les noirs vers 4, avec un leger virage chaud dans les hautes lumieres pour
  retrouver l'heure doree.

Les coupes tombent sur la grille du morceau (128 BPM) : les durees sont donnees
en temps, jamais en secondes, donc un plan change toujours sur un temps.
"""
import base64
import pathlib
import subprocess

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

import musique

RAC = pathlib.Path(__file__).resolve().parents[2]
RUSHES = pathlib.Path("/home/user/rushes")
TRAVAIL = pathlib.Path("/tmp/claude-0/-home-user-monartifice-blog/"
                       "57e78697-be58-5808-bc0a-6310eaa79157/scratchpad/reel")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
LOGO = RAC / "social/brand/logo-mon-artifice.png"
L, H = 1080, 1920
TEMPS = musique.TEMPS

VERT, MAGENTA, BLANC = "#AEDA4A", "#F5399B", "#FFFFFF"

# on travaille 10 % plus grand que la sortie : la marge absorbe le recadrage
# du stabilisateur
LS, HS = 1188, 2112
PRE = (f"scale={LS}:{HS}:force_original_aspect_ratio=increase,"
       f"crop={LS}:{HS},fps=30")

ETALONNAGE = (
    "curves="
    "r='0/0 0.22/0.18 0.5/0.53 0.78/0.82 1/1':"
    "g='0/0 0.22/0.175 0.5/0.505 0.78/0.79 1/1':"
    "b='0/0.015 0.22/0.185 0.5/0.475 0.78/0.745 1/0.975',"
    "eq=saturation=1.30:contrast=1.05:gamma=0.99,"
    "vignette=PI/6,unsharp=5:5:0.42"
)

# (fichier, entree, temps, etape, nouvelle_etape)
# etape = (numero, titre, explication) — None sur les cartes
MONTAGE = [
    ("T3.MP4",         3.0, 4, "ouverture", True),
    ("M12.MP4",        6.0, 4, ("01", "Le terrain",
                                "On repère, on mesure, on place les jalons"), True),
    ("M6.MP4",         4.0, 2, ("02", "Positionnement",
                                "Chaque rack a sa place, définie au plan de tir"), True),
    ("M7.MP4",         5.2, 2, ("02", "Positionnement",
                                "Chaque rack a sa place, définie au plan de tir"), False),
    ("M8A-Angle1.MP4", 4.0, 4, ("03", "Calage",
                                "Un rack qui bouge, c'est un départ de travers"), True),
    ("M8B-Angle2.MP4", 5.0, 2, ("03", "Calage",
                                "Un rack qui bouge, c'est un départ de travers"), False),
    ("T5.MP4",         3.5, 2, ("04", "Inflammateurs",
                                "Un fil par départ. Chaque fil est numéroté"), True),
    ("T5.MP4",         7.0, 4, ("04", "Inflammateurs",
                                "Un fil par départ. Chaque fil est numéroté"), False),
    ("T2.MP4",         1.5, 2, ("05", "Les chandelles",
                                "Bâchées jusqu'au dernier moment"), True),
    # M11 ne montre le pupitre qu'a partir de ~9 s : avant, c'est un plan large.
    # Le repere "tableau de tir" arrivait donc une coupe trop tot.
    ("T2.MP4",         4.0, 2, ("05", "Les chandelles",
                                "Bâchées jusqu'au dernier moment"), False),
    ("M11.MP4",        9.5, 4, ("06", "Le tableau de tir",
                                "Une ligne, un départ, une seconde précise"), True),
    ("M12.MP4",        9.0, 2, ("07", "On recule",
                                "Une fois la clé tournée, plus personne côté dispositif"), True),
    ("M13.MP4",        1.0, 4, ("07", "On recule",
                                "Une fois la clé tournée, plus personne côté dispositif"), False),
    ("M13.MP4",        3.0, 8, "fin", True),
]
DUREE = sum(m[2] for m in MONTAGE) * TEMPS


def logo_uri():
    return "data:image/png;base64," + base64.b64encode(LOGO.read_bytes()).decode()


def html_calque(etape):
    if etape == "ouverture":
        corps = ('<div class="centre"><div class="eyebrow">Coulisses</div>'
                 '<h1>De la caisse<br>au dispositif</h1><div class="rule"></div></div>')
    elif etape == "fin":
        corps = ('<div class="voile"></div><div class="centre bas">'
                 '<h1 class="fin">13 minutes<br>de show</h1>'
                 f'<img class="logo" src="{logo_uri()}" alt="Mon Artifice"></div>')
    else:
        num, titre, expl = etape
        corps = (f'<div class="etape"><div class="ligne"><span class="num">{num}</span>'
                 f'<span class="titre">{titre}</span></div>'
                 f'<div class="expl">{expl}</div></div>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:{L}px;height:{H}px;background:transparent;overflow:hidden}}
body{{position:relative;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif}}
.voile{{position:absolute;inset:0;background:linear-gradient(180deg,
  rgba(8,8,15,0) 0%,rgba(8,8,15,.28) 34%,rgba(8,8,15,.80) 72%,rgba(8,8,15,.93) 100%)}}
.centre{{position:absolute;inset:0;display:flex;flex-direction:column;
  justify-content:center;padding:0 74px;box-sizing:border-box}}
.centre.bas{{justify-content:flex-end;padding-bottom:210px}}
h1{{font-family:'Anton','Arial Narrow',Impact,sans-serif;font-weight:400;
  text-transform:uppercase;font-size:112px;line-height:.93;color:{BLANC};margin:0;
  letter-spacing:.012em;text-shadow:0 4px 44px rgba(0,0,0,.9),0 2px 8px rgba(0,0,0,.75)}}
h1.fin{{font-size:126px}}
.eyebrow{{font-weight:700;font-size:31px;letter-spacing:.36em;text-transform:uppercase;
  color:{VERT};margin-bottom:24px;text-shadow:0 2px 16px rgba(0,0,0,.95)}}
.rule{{width:158px;height:8px;background:{MAGENTA};margin-top:32px;border-radius:2px}}
.logo{{width:430px;margin-top:52px;display:block;filter:drop-shadow(0 3px 26px rgba(0,0,0,.9))}}

/* reperage d'etape : en haut, sans cartouche, juste une ombre portee */
.etape{{position:absolute;top:196px;left:70px;right:70px}}
.ligne{{display:flex;align-items:baseline;gap:20px}}
.num{{font-family:'Anton','Arial Narrow',Impact,sans-serif;font-size:74px;color:{VERT};
  line-height:1;text-shadow:0 3px 22px rgba(0,0,0,.95)}}
.titre{{font-family:'Anton','Arial Narrow',Impact,sans-serif;font-size:74px;
  text-transform:uppercase;color:{BLANC};line-height:1;letter-spacing:.012em;
  text-shadow:0 3px 26px rgba(0,0,0,.95),0 1px 5px rgba(0,0,0,.85)}}
.expl{{margin-top:14px;padding-left:4px;font-size:38px;font-weight:600;line-height:1.3;
  color:{BLANC};max-width:820px;border-left:5px solid {MAGENTA};padding-left:18px;
  text-shadow:0 2px 18px rgba(0,0,0,.98),0 1px 4px rgba(0,0,0,.9)}}
</style></head><body>{corps}</body></html>"""


def rendre_calques():
    TRAVAIL.mkdir(parents=True, exist_ok=True)
    vus, calques = {}, {}
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={"width": L, "height": H})
        for i, (_, _, _, etape, _) in enumerate(MONTAGE):
            cle = etape if isinstance(etape, str) else etape[0]
            if cle not in vus:
                f = TRAVAIL / f"calque-{cle}.png"
                pg.set_content(html_calque(etape))
                pg.wait_for_timeout(600)
                pg.screenshot(path=str(f), omit_background=True)
                vus[cle] = f
            calques[i] = vus[cle]
        b.close()
    return calques


def stabiliser(fichier, debut, duree):
    """Premiere passe vidstab : releve les transformations du plan.

    Une passe par extrait, pas par fichier : un meme rush sert a plusieurs plans
    a des points d'entree differents, et le fichier de transformations est
    indexe sur les images de l'extrait.
    """
    trf = TRAVAIL / f"stab-{pathlib.Path(fichier).stem}-{debut}-{duree}.trf"
    if not trf.exists():
        subprocess.run([FFMPEG, "-y", "-loglevel", "error",
                        "-ss", str(debut), "-t", str(duree), "-i", str(RUSHES / fichier),
                        "-vf", f"{PRE},vidstabdetect=shakiness=7:accuracy=15:"
                               f"result={trf}", "-f", "null", "-"], check=True)
    return trf


def couper(i, fichier, debut, temps, calque, fondu):
    sortie = TRAVAIL / f"plan{i:02d}.mp4"
    duree = temps * TEMPS
    trf = stabiliser(fichier, debut, duree)
    base = (f"{PRE},"
            f"vidstabtransform=input={trf}:smoothing=20:optzoom=1:interpol=bicubic,"
            f"scale={L}:{H},{ETALONNAGE},format=yuv420p")
    # -loop : un PNG n'a qu'une image, sans lui le fondu alpha la fige a zero
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-ss", str(debut), "-t", str(duree),
           "-i", str(RUSHES / fichier),
           "-loop", "1", "-framerate", "30", "-t", str(duree), "-i", str(calque),
           "-filter_complex",
           f"[0:v:0]{base}[v];"
           + (f"[1:v]format=rgba,fade=t=in:st=0:d=0.30:alpha=1[c];" if fondu
              else "[1:v]format=rgba[c];")
           + "[v][c]overlay=0:0[out]",
           "-map", "[out]", "-an",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", str(sortie)]
    subprocess.run(cmd, check=True)
    return sortie


def main():
    TRAVAIL.mkdir(parents=True, exist_ok=True)
    calques = rendre_calques()
    plans = [couper(i, f, d, t, calques[i], nouv)
             for i, (f, d, t, _, nouv) in enumerate(MONTAGE)]

    liste = TRAVAIL / "plans.txt"
    liste.write_text("".join(f"file '{p}'\n" for p in plans), encoding="utf-8")
    muet = TRAVAIL / "muet.mp4"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(liste), "-c", "copy", str(muet)], check=True)

    lit = TRAVAIL / "lit.wav"
    musique.composer(DUREE, str(lit))

    sortie = RAC / "social/video/reel-20-09-de-la-caisse-au-dispositif.mp4"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(muet), "-i", str(lit),
                    "-c:v", "libx264", "-preset", "slow", "-crf", "21",
                    "-maxrate", "9M", "-bufsize", "18M", "-profile:v", "high",
                    "-level", "4.1", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    "-map", "0:v:0", "-map", "1:a:0", "-shortest", str(sortie)],
                   check=True)
    print(f"→ {sortie.relative_to(RAC)}  {DUREE:.2f} s  {len(MONTAGE)} plans  "
          f"({sortie.stat().st_size // 1024} Ko)")


if __name__ == "__main__":
    main()
