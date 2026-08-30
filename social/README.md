# Mon Artifice — Contenus réseaux sociaux

Instagram + Facebook · Septembre 2026 → Août 2027 · **208 publications**

## Comment c'est organisé

| Fichier | Contenu |
|---|---|
| `STRATEGIE.md` | Piliers, cadence, direction artistique, règles de rédaction, banques de hashtags. **À lire en premier.** |
| `PRODUITS.md` | **Généré** depuis la base SQL par `data/build_produits.py`. Specs réelles (catégorie, calibre, durée, coups, hauteur, distance de sécurité, vidéo), sans prix. Contient le rapport de qualité des données. |
| `COULISSES-PLAN-PHOTO.md` | Plan de prise de vue des photos métier : 6 séquences, cadrages, consignes. |
| `calendrier/CALENDRIER-ANNUEL.md` | Vue macro des 12 mois, temps forts et campagnes. |
| `calendrier/2026-09.md` | Calendrier détaillé du mois : date, heure, pilier, format, sujet, produit. |
| `posts/2026/09/*.md` | Un fichier par publication : brief visuel, texte Instagram, texte Facebook, hashtags, story associée. |
| `visuels/2026/09/*.html` | **Un fichier par publication.** Chaque carrousel est un design Canva autonome, directement publiable. Voir `visuels/2026/09/README.md`. |
| `VALIDATION-SEPTEMBRE.md` | Ce qui reste pour publier : photos manquantes, relectures, décisions. |
| `visuels/build_visuels.py` | Générateur des visuels. Les textes sont lus depuis `posts/` — **source unique de vérité**. |

## Phase actuelle : pré-lancement

**La boutique n'est pas en ligne.** Septembre ne contient donc **aucun post produit** et
**aucun CTA vers le site** — le CTA du mois est le message privé. Le pilier Produit démarre
en octobre. Voir la section « Phase de pré-lancement » de `STRATEGIE.md`.

## Régénérer le catalogue

```bash
python3 social/data/build_produits.py
```

Relit `data/produits.json` (export SQL) et réécrit `PRODUITS.md`. **Ne pas éditer `PRODUITS.md`
à la main** : il est écrasé à chaque exécution.

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

## Canva — état de l'import

Le dépôt étant passé en public, l'import fonctionne directement depuis l'URL brute GitHub.

| | |
|---|---|
| **Dossier** | [Mon artifice / 2026 / 09 - Septembre](https://www.canva.com/folder/FAHTx4uZdp4) |
| **Designs** | Un par publication, nommé `JJ/MM — Titre` |
| **Source** | `social/visuels/2026/09/<date>-<slug>.html` |

Chaque design contient exactement les slides de sa publication. La slide 1 porte la légende
Instagram en notes de page ; les suivantes rappellent leur rang.

### Réimporter après modification

```bash
python3 social/visuels/build_visuels.py      # régénère les 17 fichiers
git add -A && git commit && git push          # publie la nouvelle version
```

Puis relancer l'import de la publication concernée. **L'import crée un nouveau design** : il ne
met pas à jour l'existant. Avantage du découpage en un fichier par publication : on ne réimporte
que celle qui a changé, sans toucher aux autres déjà retouchées dans Canva.

> ⚠️ **Le dépôt est public.** N'y placez ni prix, ni données clients, ni identifiants tant qu'il
> l'est. Une fois tous les mois importés dans Canva, il peut être repassé en privé : les designs
> Canva n'ont plus besoin de lui.

## Rappels non négociables

- **Aucun prix** dans les visuels ni les textes.
- **Ne jamais booster une publication** : Meta refuse la publicité payante sur les feux d'artifice.
- **Vérifier le stock la veille** de chaque publication produit.
- Les posts marqués ⚠️ dans `posts/` contiennent des affirmations réglementaires **à faire relire**
  avant publication.
