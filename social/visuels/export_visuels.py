#!/usr/bin/env python3
"""Exporte en JPEG 1080x1350 les visuels des publications **completes**.

Une publication est complete quand chacune de ses slides est soit dessinee, soit
appuyee sur une photo deja presente dans social/photos/2026-09/. Les autres ne sont
pas exportees : leurs maquettes portent encore un cadre reserve avec un code de plan,
et un fichier exporte finirait tot ou tard programme par erreur.
"""
import importlib.util
import pathlib
from PIL import Image
from playwright.sync_api import sync_playwright

RAC = pathlib.Path(__file__).resolve().parents[2]
SRC = RAC / "social/visuels/2026/09"
OUT = RAC / "social/visuels/export/2026-09"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

spec = importlib.util.spec_from_file_location("bv", RAC / "social/visuels/build_visuels.py")
bv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bv)

photos = {f.name.split("-")[0] for f in (RAC / "social/photos/2026-09").glob("*.jpg")}


def manquantes(post):
    codes = []
    for s in post["slides"]:
        c = s.get("shot") or (s["img"].split("-")[0] if s.get("img") else None)
        if c and c not in photos:
            codes.append(c)
    return codes


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.glob("*.jpg"):
        f.unlink()

    fichiers = sorted(SRC.glob("*.html"))
    assert len(fichiers) == len(bv.POSTS), "visuels et publications desynchronises"

    exportes, bloques = 0, []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for post, f in zip(bv.POSTS, fichiers):
            trous = manquantes(post)
            if trous:
                bloques.append(f'{post["date"]} — {post["titre"]} ({", ".join(trous)})')
                continue
            pg.goto(f.resolve().as_uri())
            pg.wait_for_timeout(600)
            els = pg.query_selector_all('[data-document-role="page"]')
            for i, e in enumerate(els, 1):
                nom = f"{f.stem}-{i:02d}" if len(els) > 1 else f.stem
                png = OUT / f"{nom}.png"
                e.screenshot(path=str(png))
                Image.open(png).convert("RGB").save(
                    OUT / f"{nom}.jpg", "JPEG", quality=92, optimize=True, progressive=True)
                png.unlink()
                exportes += 1
            print(f"  {post['date']}  {len(els)} image(s)  {post['titre']}")
        b.close()

    print(f"\n{exportes} images exportees")
    if bloques:
        print(f"{len(bloques)} publications non exportees, photos manquantes :")
        for x in bloques:
            print(f"  - {x}")


if __name__ == "__main__":
    main()
