# Contenu v0.40 — Corridors continus

## Traversées certifiées

| Corridor | Distance graphe | Distance directe | Ratio | Tuiles | Objets routiers | Nœuds | Segments | Points simplifiés |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Aubagne → Marseille Vieux-Port | 23,701 km | 21,898 km | 1,082 | 78 | 50 778 | 211 820 | 285 518 | 72 |
| Aubagne → La Ciotat | 22,740 km | 19,083 km | 1,192 | 43 | 14 365 | 84 367 | 100 476 | 109 |

Les deux extrémités sont accrochées à moins de 30 mètres du graphe. Aucun PBF nécessaire au calcul n’était absent.

## Roadbook
Le joueur active un corridor depuis le Pip-Boy. Le système place un objectif devant lui, précharge les tuiles, mémorise la progression et signale tout déplacement supérieur à 650 mètres qui ne correspond pas à une transition normale.

## Raccords cadastraux
Les empreintes touchant deux tuiles voisines sont fusionnées seulement si :
- elles partagent une frontière réelle de tuile ;
- leur hauteur est compatible ;
- leurs intervalles se recouvrent ;
- leur identifiant concorde ou l’enveloppe convexe n’ajoute pas une surface excessive.

Les fragments incertains restent séparés : aucune emprise n’est inventée pour obtenir un meilleur compteur.

## Relief
Les chevauchements des grilles RGE ALTI voisines sont comparés sur 17 × 17 échantillons. Les passages entre macro-régions utilisent un fondu vertical de 1,15 seconde pour éviter un saut instantané du joueur.
