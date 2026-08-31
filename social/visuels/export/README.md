# Visuels exportés

Images prêtes à publier, **1080 × 1350 px** (format 4:5, celui qui occupe le plus de
hauteur dans le fil Instagram). JPEG qualité 92, progressif.

Générés directement depuis les fichiers HTML par `social/visuels/build_visuels.py` puis
capture Chromium — **pas besoin de passer par Canva pour exporter.** Canva reste utile
pour retoucher à la main ; ces fichiers-là sont la sortie automatique.

## Régénérer

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
from PIL import Image
import pathlib
RAC = pathlib.Path("/home/user/monartifice_blog")
SRC, OUT = RAC / "social/visuels/2026/09", RAC / "social/visuels/export/2026-09"
OUT.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    pg = b.new_page(viewport={'width': 1080, 'height': 1350}, device_scale_factor=1)
    for f in sorted(SRC.glob("*.html")):
        pg.goto(f.resolve().as_uri()); pg.wait_for_timeout(600)
        els = pg.query_selector_all('[data-document-role="page"]')
        for i, e in enumerate(els, 1):
            nom = f"{f.stem}-{i:02d}.png" if len(els) > 1 else f"{f.stem}.png"
            e.screenshot(path=str(OUT / nom))
    b.close()
for f in sorted(OUT.glob('*.png')):
    Image.open(f).convert('RGB').save(f.with_suffix('.jpg'), 'JPEG',
                                      quality=92, optimize=True, progressive=True)
    f.unlink()
PY
```

Le nom de fichier porte la date et le rang de la slide : `2026-09-07-...-03.jpg` est la
troisième image du carrousel du 7 septembre. C'est aussi ce que la colonne `medias` du CSV
attend, dans l'ordre.
