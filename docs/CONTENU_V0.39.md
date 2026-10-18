# Contenu v0.39 — Relief officiel

## Axe exclusif de la version
La v0.39 ne rajoute aucun mode de jeu secondaire. Elle fait progresser la cartographie réelle par l’acquisition, la conservation et l’intégration de huit grilles altimétriques issues de la ressource officielle `ign_rge_alti_wld`.

## Huit macro-régions
- Marseille
- Huveaune
- Garlaban
- Calanques
- La Ciotat
- Frioul
- Étoile
- Sainte-Baume

Chaque région possède une grille de 161 × 161 cellules en ordre nord-vers-sud. Les altitudes absolues restent conservées dans la preuve JSON. Le moteur applique l’échelle locale de la macro-région uniquement au moment du rendu.

## NoData
Les valeurs `null`, non finies, inférieures ou égales à −100 m et supérieures ou égales à 9 000 m sont considérées comme NoData. Elles ne sont pas transformées en altitude nulle officielle. Le terrain de jeu conserve son plan de référence à cet endroit.

## Moteur
Le moteur charge le relief selon l’ordre suivant : pack local, IndexedDB, cache cloud privé. Il vérifie les dimensions, l’emprise, le nombre de valeurs, le nom de la ressource et les bornes d’altitude avant application.

Le maillage saute les triangles ne possédant pas assez de sommets valides. L’interpolation bilinéaire renormalise les poids autour des cellules NoData au lieu d’utiliser les sentinelles négatives.

## Outils
- `install_terrain_v039.py` : téléchargement et vérification des huit grilles.
- `audit_terrain_v039.py` : statistiques, NoData, SHA-256 et recouvrements inter-régions.
- `install_real_map_v039.py` : installation unifiée vectoriel + terrain.
- `audit_real_map_v039.py` : audit unifié cloud/local.

## Interface
Le Pip-Boy présente le nombre de grilles, les mesures valides, les cellules NoData, les extrema régionaux, la source et la provenance du terrain actif. L’écran de statut sépare le vectoriel complet du relief.
