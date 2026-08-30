# Mon Artifice — Contenus réseaux sociaux

Instagram + Facebook · Septembre 2026 → Août 2027 · **208 publications**

## Comment c'est organisé

| Fichier | Contenu |
|---|---|
| `STRATEGIE.md` | Piliers, cadence, direction artistique, règles de rédaction, banques de hashtags. **À lire en premier.** |
| `PRODUITS.md` | Catalogue de référence, sans prix, avec l'angle éditorial de chaque produit et son statut de stock. |
| `calendrier/CALENDRIER-ANNUEL.md` | Vue macro des 12 mois, temps forts et campagnes. |
| `calendrier/2026-09.md` | Calendrier détaillé du mois : date, heure, pilier, format, sujet, produit. |
| `posts/2026/09/*.md` | Un fichier par publication : brief visuel, texte Instagram, texte Facebook, hashtags, story associée. |
| `visuels/2026/09/septembre-2026.html` | Les 17 visuels, en pages séparées, prêts à importer dans Canva. |
| `visuels/build_visuels.py` | Générateur des visuels. Les textes sont lus depuis `posts/` — **source unique de vérité**. |

## Régénérer les visuels

```bash
python3 social/visuels/build_visuels.py
```

Le script relit les légendes Instagram depuis `posts/2026/09/*.md` et les injecte en notes de page.
Modifier un texte dans un fichier post, relancer le script : le visuel et sa note sont à jour.

## Chaîne de production vers Canva

1. Les visuels sont générés en un seul fichier HTML multi-pages.
   Chaque page porte `data-document-role="page"`, un `data-label` daté, et la légende Instagram en
   notes de page.
2. Le fichier est poussé sur un dépôt **public** (l'import Canva n'accepte que des URL HTTPS
   publiques — voir « Étape manuelle » ci-dessous).
3. L'import Canva crée **un design de 17 pages**, rangé dans `Mon artifice / 2026 / 09 - Septembre`.
4. Chaque page est ensuite retouchable individuellement dans Canva.

## Étape manuelle en attente

Le connecteur GitHub de la session ne peut pas créer de dépôt (droits limités à `monartifice_blog`).
Pour débloquer l'import Canva, créer un dépôt **public** nommé `monartifice-visuels` :

👉 https://github.com/new — nom `monartifice-visuels`, visibilité **Public**, cocher « Add a README ».

Ce dépôt ne contiendra **que** les fichiers HTML des visuels — c'est-à-dire des maquettes destinées à
être publiées sur Instagram de toute façon. Aucune donnée commerciale, aucun prix, aucun fichier privé.
`monartifice_blog` reste privé.

## Rappels non négociables

- **Aucun prix** dans les visuels ni les textes.
- **Ne jamais booster une publication** : Meta refuse la publicité payante sur les feux d'artifice.
- **Vérifier le stock la veille** de chaque publication produit.
- Les posts marqués ⚠️ dans `posts/` contiennent des affirmations réglementaires **à faire relire**
  avant publication.
