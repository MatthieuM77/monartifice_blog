#!/usr/bin/env python3
"""Monte un Reel a partir des rushes, avec titres incrustes aux couleurs de la marque.

Les titres sont rendus en HTML par Chromium (fond transparent) pour recuperer
exactement la typographie et la palette des visuels, puis composites par ffmpeg.
Le son d'ambiance des rushes est conserve : pas de musique ajoutee ici, elle se
pose dans Instagram pour rester sous licence.
"""
import json
import pathlib
import subprocess

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

RAC = pathlib.Path(__file__).resolve().parents[2]
RUSHES = pathlib.Path("/home/user/rushes")
TRAVAIL = pathlib.Path("/tmp/claude-0/-home-user-monartifice-blog/"
                       "57e78697-be58-5808-bc0a-6310eaa79157/scratchpad/reel")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
L, H = 1080, 1920

VERT, MAGENTA, BLANC = "#AEDA4A", "#F5399B", "#FFFFFF"

# plan : (fichier, debut, duree, texte, style)
MONTAGE = [
    ("T3.MP4",         3.0, 2.4, ("De la caisse\nau dispositif", "titre")),
    ("M6.MP4",         3.5, 2.2, None),
    ("M7.MP4",         5.2, 1.8, None),
    ("M8A-Angle1.MP4", 4.0, 2.6, ("Le calage, c'est ce que\ntout le monde néglige", "sous")),
    ("M8B-Angle2.MP4", 5.0, 2.2, None),
    ("T5.MP4",         3.5, 2.4, ("Chaque départ\na son fil", "sous")),
    ("T2.MP4",         1.5, 2.0, None),
    ("M11.MP4",        9.0, 2.2, ("On vérifie. Deux fois.", "sous")),
    ("M12.MP4",        4.0, 2.0, None),
    ("M13.MP4",        1.0, 4.0, ("3 heures\npour 3 minutes", "fin")),
]


def html_titre(texte, style):
    br = texte.replace("\n", "<br>")
    if style == "titre":
        corps = (f'<div class="eyebrow">Coulisses</div><h1>{br}</h1>'
                 '<div class="rule"></div>')
    elif style == "fin":
        corps = ('<div class="voile"></div>'
                 f'<div class="bloc-fin"><h1 class="fin">{br}</h1>'
                 '<div class="marque">Mon Artifice<span>by Ciels en Fête</span></div></div>')
    else:
        corps = f'<div class="sous">{br}</div>'
    pos = "flex-end" if style == "sous" else "center"
    pad = "0 70px 300px" if style == "sous" else "0 70px"
    return f"""<!doctype html><html><head><meta charset="utf-8">
<style>
html,body{{margin:0;width:{L}px;height:{H}px;background:transparent}}
body{{display:flex;flex-direction:column;justify-content:{pos};padding:{pad};box-sizing:border-box}}
h1{{font-family:'Anton','Arial Narrow',Impact,sans-serif;font-weight:400;text-transform:uppercase;
   font-size:104px;line-height:.94;color:{BLANC};margin:0;letter-spacing:.01em;
   text-shadow:0 4px 40px rgba(0,0,0,.85),0 2px 8px rgba(0,0,0,.7)}}
h1.fin{{font-size:118px}}
.eyebrow{{font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;font-weight:600;font-size:30px;
  letter-spacing:.34em;text-transform:uppercase;color:{VERT};margin-bottom:22px;
  text-shadow:0 2px 14px rgba(0,0,0,.9)}}
.rule{{width:150px;height:7px;background:{MAGENTA};margin-top:30px;border-radius:2px}}
.sous{{font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;font-weight:600;font-size:52px;line-height:1.28;
  color:{BLANC};background:rgba(8,8,15,.74);padding:22px 28px;border-left:7px solid {VERT};
  border-radius:3px;align-self:flex-start;max-width:900px}}
.voile{{position:absolute;inset:0;background:linear-gradient(180deg,
  rgba(8,8,15,.06) 0%,rgba(8,8,15,.62) 42%,rgba(8,8,15,.84) 100%)}}
.bloc-fin{{position:relative}}
.marque{{font-family:'Anton','Arial Narrow',Impact,sans-serif;font-size:46px;color:{BLANC};margin-top:44px;
  text-transform:uppercase;letter-spacing:.03em;text-shadow:0 2px 20px rgba(0,0,0,.9)}}
.marque span{{display:block;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;font-size:22px;
  letter-spacing:.2em;color:{VERT};margin-top:8px}}
</style></head><body>{corps}</body></html>"""


def rendre_titres():
    TRAVAIL.mkdir(parents=True, exist_ok=True)
    titres = {}
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={"width": L, "height": H})
        for i, (_, _, _, t) in enumerate(MONTAGE):
            if not t:
                continue
            f = TRAVAIL / f"titre{i:02d}.png"
            pg.set_content(html_titre(*t))
            pg.wait_for_timeout(700)
            pg.screenshot(path=str(f), omit_background=True)
            titres[i] = f
        b.close()
    return titres


def couper(i, fichier, debut, duree, titre):
    """Extrait un plan, le recadre en 9:16 et y incruste son titre s'il en a un."""
    sortie = TRAVAIL / f"plan{i:02d}.mp4"
    vf = (f"scale={L}:{H}:force_original_aspect_ratio=increase,"
          f"crop={L}:{H},fps=30,format=yuv420p")
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-ss", str(debut), "-t", str(duree),
           "-i", str(RUSHES / fichier)]
    if titre:
        cmd += ["-i", str(titre),
                "-filter_complex", f"[0:v:0]{vf}[v];[v][1:v]overlay=0:0[out]",
                "-map", "[out]"]
    else:
        cmd += ["-vf", vf, "-map", "0:v:0"]
    cmd += ["-map", "0:a:0?", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", str(sortie)]
    subprocess.run(cmd, check=True)
    return sortie


def main():
    TRAVAIL.mkdir(parents=True, exist_ok=True)
    titres = rendre_titres()
    plans = [couper(i, f, d, du, titres.get(i))
             for i, (f, d, du, _) in enumerate(MONTAGE)]

    liste = TRAVAIL / "plans.txt"
    liste.write_text("".join(f"file '{p}'\n" for p in plans), encoding="utf-8")

    sortie = RAC / "social/video/reel-20-09-de-la-caisse-au-dispositif.mp4"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(liste),
                    # le son brut saute d'un plan a l'autre : on l'aplanit
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=out:st=22.5:d=1.3",
                    # Instagram re-encode de toute facon : au-dela de ~10 Mbps on transporte du
                    # poids sans gagner d'image
                    "-c:v", "libx264", "-preset", "slow", "-crf", "21",
                    "-maxrate", "9M", "-bufsize", "18M", "-profile:v", "high", "-level", "4.1",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    "-map", "0:v:0", "-map", "0:a:0", str(sortie)], check=True)
    print(f"→ {sortie.relative_to(RAC)}  ({sortie.stat().st_size // 1024} Ko)")
    return sortie


if __name__ == "__main__":
    main()
