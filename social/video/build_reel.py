#!/usr/bin/env python3
"""Monte un Reel a partir des rushes, sur une grille de tempo.

Trois partis pris, demandes par le client :

- **Le son des rushes est jete.** On y parle technique entre artificiers ; ce
  n'est pas destine au public. La bande-son est le lit musical de `musique.py`,
  ecrit de toutes pieces donc libre de droits.
- **Pas de sous-titres.** Seuls un titre d'ouverture et une carte de fin.
- **Le logo de la marque** ferme le Reel, en PNG transparent.

Les points de coupe tombent sur la grille du lit musical (120 BPM, 0,5 s par
temps) : les plans changent sur les temps forts, et le montage tiendra aussi si
la musique est remplacee par une piste du meme tempo dans Instagram.
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

VERT, MAGENTA, BLANC = "#AEDA4A", "#F5399B", "#FFFFFF"
TEMPS = 0.5   # 120 BPM

# (fichier, point d'entree, duree, carte) — durees en multiples de 0,5 s
MONTAGE = [
    ("T3.MP4",         3.0, 2.0, "ouverture"),
    ("M12.MP4",        6.0, 2.0, None),
    ("M6.MP4",         4.0, 1.0, None),
    ("M7.MP4",         5.2, 1.0, None),
    ("M8A-Angle1.MP4", 4.0, 2.0, None),
    ("M8B-Angle2.MP4", 5.0, 1.0, None),
    ("T5.MP4",         3.5, 1.0, None),
    ("T5.MP4",         7.0, 2.0, None),
    ("T2.MP4",         1.5, 1.0, None),
    ("M11.MP4",        2.0, 1.0, None),
    ("M11.MP4",        9.5, 2.0, None),
    ("M12.MP4",        9.0, 1.0, None),
    ("M13.MP4",        1.0, 2.0, None),
    ("M13.MP4",        3.0, 4.0, "fin"),
]
DUREE = sum(m[2] for m in MONTAGE)


def logo_uri():
    return "data:image/png;base64," + base64.b64encode(LOGO.read_bytes()).decode()


def html_carte(genre):
    if genre == "ouverture":
        corps = ('<div class="haut"><div class="eyebrow">Coulisses</div>'
                 '<h1>De la caisse<br>au dispositif</h1>'
                 '<div class="rule"></div></div>')
    else:
        corps = ('<div class="voile"></div>'
                 '<div class="bas"><h1 class="fin">13 minutes<br>de show</h1>'
                 f'<img class="logo" src="{logo_uri()}" alt="Mon Artifice"></div>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:{L}px;height:{H}px;background:transparent;overflow:hidden}}
body{{display:flex;flex-direction:column;justify-content:center;padding:0 74px;
  box-sizing:border-box;position:relative}}
h1{{font-family:'Anton','Arial Narrow',Impact,sans-serif;font-weight:400;
  text-transform:uppercase;font-size:112px;line-height:.93;color:{BLANC};margin:0;
  letter-spacing:.012em;text-shadow:0 4px 44px rgba(0,0,0,.9),0 2px 8px rgba(0,0,0,.75)}}
h1.fin{{font-size:126px}}
.eyebrow{{font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;font-weight:700;
  font-size:31px;letter-spacing:.36em;text-transform:uppercase;color:{VERT};
  margin-bottom:24px;text-shadow:0 2px 16px rgba(0,0,0,.95)}}
.rule{{width:158px;height:8px;background:{MAGENTA};margin-top:32px;border-radius:2px}}
.voile{{position:absolute;inset:0;background:linear-gradient(180deg,
  rgba(8,8,15,0) 0%,rgba(8,8,15,.30) 34%,rgba(8,8,15,.80) 72%,rgba(8,8,15,.93) 100%)}}
.haut,.bas{{position:relative}}
.logo{{width:430px;margin-top:54px;display:block;
  filter:drop-shadow(0 3px 26px rgba(0,0,0,.9))}}
</style></head><body>{corps}</body></html>"""


def rendre_cartes():
    TRAVAIL.mkdir(parents=True, exist_ok=True)
    cartes = {}
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={"width": L, "height": H})
        for i, (_, _, _, genre) in enumerate(MONTAGE):
            if not genre:
                continue
            f = TRAVAIL / f"carte{i:02d}.png"
            pg.set_content(html_carte(genre))
            pg.wait_for_timeout(600)
            pg.screenshot(path=str(f), omit_background=True)
            cartes[i] = f
        b.close()
    return cartes


def couper(i, fichier, debut, duree, carte):
    """Un plan recadre en 9:16, sans son : la bande-son est ajoutee au montage."""
    sortie = TRAVAIL / f"plan{i:02d}.mp4"
    vf = (f"scale={L}:{H}:force_original_aspect_ratio=increase,"
          f"crop={L}:{H},fps=30,format=yuv420p")
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-ss", str(debut), "-t", str(duree),
           "-i", str(RUSHES / fichier)]
    if carte:
        # -loop : sans lui le PNG n'a qu'une image, le fondu la fige a alpha 0
        # et la carte reste invisible
        cmd += ["-loop", "1", "-framerate", "30", "-t", str(duree),
                "-i", str(carte), "-filter_complex",
                f"[0:v:0]{vf}[v];[1:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1[c];"
                f"[v][c]overlay=0:0[out]", "-map", "[out]"]
    else:
        cmd += ["-vf", vf, "-map", "0:v:0"]
    # -an : le son des rushes est ecarte, on y parle technique
    cmd += ["-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", str(sortie)]
    subprocess.run(cmd, check=True)
    return sortie


def main():
    TRAVAIL.mkdir(parents=True, exist_ok=True)
    cartes = rendre_cartes()
    plans = [couper(i, f, d, du, cartes.get(i))
             for i, (f, d, du, _) in enumerate(MONTAGE)]

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
    print(f"→ {sortie.relative_to(RAC)}  {DUREE:.0f} s  "
          f"({sortie.stat().st_size // 1024} Ko)  {len(MONTAGE)} plans")
    return sortie


if __name__ == "__main__":
    main()
