# Identité de marque — Mon Artifice

## Le logo

Le logo officiel porte la signature **« Mon Artifice — by Ciels en Fête »**. La relation entre
les deux marques est donc déjà tranchée par le logo lui-même : Mon Artifice est la boutique,
Ciels en Fête est l'artificier. Les textes doivent s'aligner sur cette formulation.

| Fichier | Usage |
|---|---|
| `logo-mon-artifice.svg` | **Version de référence.** Fond transparent, contre-formes percées. Lettrage blanc → fonds sombres et photos. |
| `logo-mon-artifice-fond-clair.svg` | Lettrage nuit `#08080F` → fonds blancs ou clairs. |
| `logo-mon-artifice.png` | Version matricielle 620 px, transparente. C'est celle qui est embarquée dans les visuels. |
| `logo-source-original.svg` | Fichier d'origine, conservé pour référence. **Ne pas utiliser tel quel.** |

### Ce qui a été corrigé sur le fichier d'origine

Le fichier livré contenait un **carré noir plein de 1500 × 1500** en premier tracé (100 Ko à lui
seul), avec le logo détouré dedans. C'est ce qui donnait le fond noir.

Le supprimer ne suffisait pas : les 36 tracés noirs restants ne sont pas du fond, ce sont les
**contre-formes** — l'intérieur du « o » de Mon, celui du « A » d'Artifice, les points. Les
supprimer aussi bouchait les lettres ; les garder laissait des taches noires visibles sur tout
fond clair.

La version de référence les transforme en **masque SVG** : elles percent réellement le tracé.
Le logo est donc correct sur n'importe quel fond, y compris une photo.

## Couleurs

Relevées sur le fichier vectoriel, par surface de tracé.

| Rôle | Code | Note |
|---|---|---|
| Vert anis | `#8DBB20` | Gerbe de gauche |
| Magenta | `#D50174` | Gerbe de droite |
| Blanc | `#FFFFFF` | Lettrage |
| Nuit | `#08080F` | Fond des visuels |

> Le fichier d'origine contient une quarantaine de variantes de ces deux teintes
> (`#8EBB21`, `#D40175`…). Ce sont des artefacts de vectorisation automatique, pas des
> couleurs de marque. Les deux codes ci-dessus font foi.

## Règle de placement

Le logo se place **en bas à droite**, taille constante d'un visuel à l'autre. Il ne change
jamais de couleur, ne se déforme pas, et n'est jamais posé sur une zone claire d'une photo
sans voile assombrissant.
