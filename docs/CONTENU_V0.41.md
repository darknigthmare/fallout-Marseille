# Contenu v0.41 — Territoire local

## Distribution accélérée
Le manifeste vectoriel complet est regroupé dans 24 archives versionnées : cinq pour la couche générale et dix-neuf pour le cadastre. Les archives contiennent leur propre `chunk_manifest.json`, les PBF réels, et un marqueur `.pbf.empty.json` pour chaque coordonnée cadastrale officiellement vide.

## Installateur
`install_local_pack_v041.py` télécharge les archives avec une concurrence limitée, vérifie leur CRC, bloque les chemins absolus et `..`, limite la taille des membres, contrôle SHA-256, décode les MVT et extrait atomiquement. Une archive déjà téléchargée peut être reprise.

## Audit local
L’état final sépare PBF présents, coordonnées vides, fichiers manquants, fichiers invalides, octets et terrains. La commande `--verify-only` ne télécharge rien.

## Benchmark
`benchmark_map_v041.py` mesure le nombre de PBF décodés, les octets, le débit, les tuiles/s, les temps moyen/médian/p95/max et le pic RSS. Il inspecte aussi les huit terrains et les preuves de corridor.

## Interface
Une nouvelle rubrique `MAP > PACK LOCAL` et le statut de production affichent le manifeste distant, la couverture installée, les huit terrains et le benchmark local.

## Continuité
Les corridors Aubagne–Marseille et Aubagne–La Ciotat, le relief RGE ALTI, le recollage cadastral et les systèmes de jeu antérieurs restent présents.
