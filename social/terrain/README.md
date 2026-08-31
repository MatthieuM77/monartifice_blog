# Documents de terrain

Feuilles à imprimer, pensées pour être utilisées sur site — noir sur blanc, cases à cocher,
lisibles à la frontale.

| Fichier | Usage |
|---|---|
| `liste-tournage-05-09.pdf` | **Liste de tournage du feu du 5 septembre 2026.** 36 plans, 2 pages A4, classés dans l'ordre de la journée : au montage, avant le tir, pendant, après. |
| `liste-tournage-05-09.html` | Source. Modifier puis régénérer le PDF. |

## Régénérer le PDF

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
import pathlib
src = pathlib.Path('social/terrain/liste-tournage-05-09.html').resolve()
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(); pg.goto(src.as_uri())
    pg.pdf(path='social/terrain/liste-tournage-05-09.pdf', format='A4', print_background=True,
           margin={'top':'11mm','bottom':'9mm','left':'10mm','right':'10mm'})
    b.close()
PY
```

Le contenu vient de `COULISSES-PLAN-PHOTO.md` et `REELS.md` : si l'un des deux change,
reporter la modification ici aussi.
