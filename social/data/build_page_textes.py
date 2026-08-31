#!/usr/bin/env python3
"""Genere la page HTML des textes de publication, a copier-coller.

Le CSV sert a l'import automatique ; cette page sert quand on programme a la main.
Elle reprend exactement les memes donnees, lues aux memes endroits.
"""
import html
import json
import pathlib

RAC = pathlib.Path(__file__).resolve().parents[2]
DATA = json.loads((RAC / "social/data/publications.json").read_text(encoding="utf-8"))
SORTIE = pathlib.Path("/tmp/claude-0/-home-user-monartifice-blog/"
                      "57e78697-be58-5808-bc0a-6310eaa79157/scratchpad/textes-septembre.html")

CSS = """
:root{
  --ground:#F2F3F7; --surface:#FFFFFF; --raised:#E8EAF1;
  --ink:#12121F; --ink-2:#4A4E60; --ink-3:#767B8C;
  --line:#D8DBE5; --line-fort:#B9BDCC;
  --vert:#6F9612; --vert-fond:#EDF4DC;
  --magenta:#B00160; --magenta-fond:#FBE6F0;
  --alerte:#9A5B00; --alerte-fond:#FBEFDC;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#08080F; --surface:#111120; --raised:#1B1B31;
    --ink:#F3F4F8; --ink-2:#C8CBD4; --ink-3:#8B90A2;
    --line:#26263F; --line-fort:#3A3A5A;
    --vert:#AEDA4A; --vert-fond:#1B2410;
    --magenta:#F5399B; --magenta-fond:#2A0A1B;
    --alerte:#E9B45C; --alerte-fond:#2A1F0C;
  }
}
:root[data-theme="dark"]{
  --ground:#08080F; --surface:#111120; --raised:#1B1B31;
  --ink:#F3F4F8; --ink-2:#C8CBD4; --ink-3:#8B90A2;
  --line:#26263F; --line-fort:#3A3A5A;
  --vert:#AEDA4A; --vert-fond:#1B2410;
  --magenta:#F5399B; --magenta-fond:#2A0A1B;
  --alerte:#E9B45C; --alerte-fond:#2A1F0C;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font-family:'IBM Plex Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
  font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased}
.enveloppe{max-width:1180px;margin:0 auto;padding:0 20px 96px}

header.tete{padding:56px 0 30px;border-bottom:2px solid var(--line-fort)}
h1{font-family:'Anton',Impact,'Arial Narrow',sans-serif;font-weight:400;
  font-size:clamp(40px,7vw,74px);line-height:.94;margin:0 0 14px;letter-spacing:.01em;
  text-transform:uppercase;text-wrap:balance}
.chapo{max-width:62ch;color:var(--ink-2);font-size:17px;margin:0}
.chapo b{color:var(--ink)}

.compteurs{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}
.compteur{background:var(--surface);border:1px solid var(--line);border-radius:3px;
  padding:9px 14px;display:flex;align-items:baseline;gap:8px}
.compteur strong{font-family:'Anton',Impact,sans-serif;font-size:22px;font-weight:400;
  font-variant-numeric:tabular-nums;line-height:1}
.compteur span{font-size:12.5px;color:var(--ink-3);text-transform:uppercase;letter-spacing:.07em}
.compteur.ok strong{color:var(--vert)}
.compteur.bloque strong{color:var(--alerte)}

h2.section{font-family:'Anton',Impact,sans-serif;font-weight:400;text-transform:uppercase;
  font-size:26px;letter-spacing:.02em;margin:64px 0 6px;display:flex;align-items:center;gap:12px}
h2.section::after{content:"";flex:1;height:2px;background:var(--line-fort)}
.section-note{color:var(--ink-2);margin:0 0 26px;max-width:64ch;font-size:15.5px}

.pub{background:var(--surface);border:1px solid var(--line);border-radius:4px;
  margin-bottom:20px;overflow:hidden}
.pub-tete{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 16px;
  padding:20px 22px;border-bottom:1px solid var(--line);background:var(--raised)}
.quand{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:13px;font-weight:600;
  color:var(--ink-2);font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.titre{font-family:'Anton',Impact,sans-serif;font-weight:400;font-size:24px;
  text-transform:uppercase;letter-spacing:.015em;flex:1 1 260px;line-height:1.12}
.etiq{font-size:11.5px;text-transform:uppercase;letter-spacing:.08em;padding:4px 9px;
  border-radius:2px;border:1px solid var(--line-fort);color:var(--ink-2);white-space:nowrap}
.etiq.epingle{background:var(--vert-fond);border-color:var(--vert);color:var(--vert);font-weight:600}
.etiq.manque{background:var(--alerte-fond);border-color:var(--alerte);color:var(--alerte);font-weight:600}

.fichiers{padding:14px 22px;border-bottom:1px solid var(--line);
  font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:12.5px;color:var(--ink-3);
  display:flex;flex-wrap:wrap;gap:6px 14px;align-items:baseline}
.fichiers b{color:var(--ink-2);font-family:'IBM Plex Sans',sans-serif;font-weight:600;
  font-size:12px;text-transform:uppercase;letter-spacing:.07em}
.fichiers ol{margin:0;padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:6px 14px;
  counter-reset:f}
.fichiers li{counter-increment:f}
.fichiers li::before{content:counter(f) ". ";color:var(--vert)}

.duo{display:grid;grid-template-columns:1fr 1fr}
@media (max-width:820px){.duo{grid-template-columns:1fr}}
.canal{padding:20px 22px 22px;min-width:0}
.canal+.canal{border-left:1px solid var(--line)}
@media (max-width:820px){.canal+.canal{border-left:0;border-top:1px solid var(--line)}}
.canal-tete{display:flex;align-items:center;gap:9px;margin-bottom:14px}
.pastille{width:9px;height:9px;border-radius:50%;flex:none}
.ig .pastille{background:var(--magenta)}
.fb .pastille{background:var(--vert)}
.canal-nom{font-size:12px;text-transform:uppercase;letter-spacing:.1em;font-weight:600}
.ig .canal-nom{color:var(--magenta)}
.fb .canal-nom{color:var(--vert)}
.canal-compte{font-size:12px;color:var(--ink-3);margin-left:auto;
  font-family:'IBM Plex Mono',monospace}

.champ{margin-bottom:16px}
.champ:last-child{margin-bottom:0}
.champ-tete{display:flex;align-items:center;gap:10px;margin-bottom:7px}
.champ-nom{font-size:11.5px;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-3);
  font-weight:600}
.copier{margin-left:auto;font:inherit;font-size:12px;font-weight:600;cursor:pointer;
  background:transparent;color:var(--ink-2);border:1px solid var(--line-fort);
  border-radius:2px;padding:3px 11px;transition:background .12s,color .12s,border-color .12s}
.copier:hover{background:var(--raised);color:var(--ink)}
.copier:focus-visible{outline:2px solid var(--vert);outline-offset:2px}
.copier.fait{background:var(--vert-fond);border-color:var(--vert);color:var(--vert)}
.bloc{background:var(--ground);border:1px solid var(--line);border-left:3px solid var(--line-fort);
  border-radius:2px;padding:13px 15px;font-size:14.5px;line-height:1.62;color:var(--ink-2);
  white-space:pre-wrap;overflow-wrap:anywhere;max-height:290px;overflow-y:auto}
.ig .bloc{border-left-color:var(--magenta)}
.fb .bloc{border-left-color:var(--vert)}
.bloc.tags{font-family:'IBM Plex Mono',monospace;font-size:12.5px;line-height:1.75;
  color:var(--ink-3);max-height:none}

.bloque .pub-tete{background:var(--alerte-fond)}
.manque-quoi{padding:16px 22px;font-size:14.5px;color:var(--ink-2)}
.manque-quoi code{font-family:'IBM Plex Mono',monospace;font-size:13px;background:var(--raised);
  padding:1px 6px;border-radius:2px;color:var(--ink)}

.avert{background:var(--alerte-fond);border:1px solid var(--alerte);border-radius:3px;
  padding:15px 18px;margin:26px 0;color:var(--ink);font-size:15px}
.avert b{color:var(--alerte)}
footer{margin-top:64px;padding-top:24px;border-top:1px solid var(--line);
  color:var(--ink-3);font-size:13.5px}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

JS = """
document.addEventListener('click', function(e){
  const b = e.target.closest('.copier');
  if(!b) return;
  const bloc = document.getElementById(b.dataset.cible);
  const txt = bloc.textContent;
  const fini = () => {
    const av = b.textContent;
    b.textContent = 'Copié'; b.classList.add('fait');
    setTimeout(() => { b.textContent = av; b.classList.remove('fait'); }, 1600);
  };
  const secours = () => {
    // presse-papiers refusé : on sélectionne, l'utilisateur fait Cmd+C
    const s = window.getSelection(); const r = document.createRange();
    r.selectNodeContents(bloc); s.removeAllRanges(); s.addRange(r);
    b.textContent = 'Sélectionné — Ctrl+C';
    setTimeout(() => { b.textContent = 'Copier'; }, 2600);
  };
  if(navigator.clipboard && window.isSecureContext){
    navigator.clipboard.writeText(txt).then(fini).catch(secours);
  } else { secours(); }
});
"""


def bloc(cid, nom, contenu, tags=False):
    if not contenu:
        return ""
    return (f'<div class="champ"><div class="champ-tete">'
            f'<span class="champ-nom">{nom}</span>'
            f'<button class="copier" data-cible="{cid}">Copier</button></div>'
            f'<div class="bloc{" tags" if tags else ""}" id="{cid}">'
            f'{html.escape(contenu)}</div></div>')


def carte(d, pret):
    e = []
    e.append(f'<article class="pub{"" if pret else " bloque"}">')
    e.append('<div class="pub-tete">')
    e.append(f'<span class="quand">{d["date"]} · {d["jour"]} · {d["heure"]}</span>')
    e.append(f'<span class="titre">{html.escape(d["titre"])}</span>')
    if d["epingle"]:
        e.append('<span class="etiq epingle">À épingler</span>')
    e.append(f'<span class="etiq">{html.escape(d["fmt"])}</span>')
    if not pret:
        quoi = "vidéo à tourner" if d["reel"] and not d["manque"] else ", ".join(d["manque"])
        e.append(f'<span class="etiq manque">manque {html.escape(quoi)}</span>')
    e.append('</div>')

    if pret:
        e.append('<div class="fichiers"><b>Images</b><ol>'
                 + "".join(f"<li>{html.escape(f)}</li>" for f in d["images"])
                 + '</ol></div>')
    else:
        if d["reel"]:
            m = ("La vidéo reste à tourner puis à monter. "
                 f"Plans à faire : <code>{'</code>, <code>'.join(d['manque'])}</code>."
                 if d["manque"] else "La vidéo reste à tourner puis à monter.")
        else:
            m = ("Visuel incomplet, photos manquantes : "
                 f"<code>{'</code>, <code>'.join(d['manque'])}</code>.")
        e.append(f'<div class="manque-quoi">{m} Le texte, lui, est écrit et définitif.</div>')

    i = d["date"].replace("/", "")
    e.append('<div class="duo">')
    e.append('<div class="canal ig"><div class="canal-tete"><span class="pastille"></span>'
             '<span class="canal-nom">Instagram</span>'
             '<span class="canal-compte">Mon Artifice (instagram)</span></div>')
    e.append(bloc(f"ig{i}", "Légende", d["ig"]))
    e.append(bloc(f"cig{i}", "Premier commentaire — hashtags", d["cig"], tags=True))
    e.append('</div>')
    e.append('<div class="canal fb"><div class="canal-tete"><span class="pastille"></span>'
             '<span class="canal-nom">Facebook</span>'
             '<span class="canal-compte">Mon Artifice (facebook)</span></div>')
    e.append(bloc(f"fb{i}", "Légende", d["fb"]))
    e.append(bloc(f"cfb{i}", "Premier commentaire — relance", d["cfb"]))
    e.append('</div></div></article>')
    return "".join(e)


def main():
    prets = [d for d in DATA if not d["manque"] and not d["reel"]]
    bloques = [d for d in DATA if d["manque"] or d["reel"]]
    img = sum(len(d["images"]) for d in prets)

    p = []
    p.append("<title>Textes de septembre</title>")
    p.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    p.append('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
             'family=Anton&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400;600'
             '&display=swap">')
    p.append(f"<style>{CSS}</style>")
    p.append('<div class="enveloppe">')
    p.append('<header class="tete"><h1>Textes de septembre</h1>'
             '<p class="chapo">Les légendes et les premiers commentaires des 18 publications, '
             'prêts à copier. <b>Instagram et Facebook portent des textes différents</b> — '
             'ne copiez pas l\'un dans l\'autre, vous perdriez la moitié du travail '
             'd\'écriture.</p>')
    p.append('<div class="compteurs">'
             f'<div class="compteur ok"><strong>{len(prets)}</strong>'
             '<span>programmables</span></div>'
             f'<div class="compteur"><strong>{img}</strong><span>images prêtes</span></div>'
             f'<div class="compteur bloque"><strong>{len(bloques)}</strong>'
             '<span>en attente d\'images</span></div>'
             f'<div class="compteur"><strong>{len(DATA)}</strong>'
             '<span>textes écrits</span></div>'
             '</div></header>')

    p.append('<div class="avert"><b>Ne jamais sponsoriser.</b> Meta interdit la publicité '
             'payante sur les feux d\'artifice : un post boosté peut valoir une restriction '
             'du compte. Tout reste organique.</div>')

    p.append('<h2 class="section">Programmables</h2>')
    p.append('<p class="section-note">Visuels faits, textes définitifs. Les noms de fichiers '
             'sont ceux du dossier <code>visuels/export/2026-09/</code>, dans l\'ordre du '
             'carrousel.</p>')
    p += [carte(d, True) for d in prets]

    p.append('<h2 class="section">En attente d\'images</h2>')
    p.append('<p class="section-note">Le texte de ces publications est écrit et définitif — '
             'vous pouvez déjà le mettre en brouillon. C\'est le visuel qui manque : une photo '
             'd\'archive qui ne m\'est pas parvenue, une photo à prendre le 5, ou une vidéo à '
             'monter.</p>')
    p += [carte(d, False) for d in bloques]

    p.append('<footer>Mon Artifice — septembre 2026. Généré depuis les fichiers de publication : '
             'si un texte change à la source, cette page se régénère avec '
             '<code>build_page_textes.py</code>.</footer>')
    p.append("</div>")
    p.append(f"<script>{JS}</script>")

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text("\n".join(p), encoding="utf-8")
    print(f"{SORTIE}  ({SORTIE.stat().st_size // 1024} Ko)")
    print(f"  {len(prets)} programmables · {len(bloques)} en attente · {img} images")


if __name__ == "__main__":
    main()
