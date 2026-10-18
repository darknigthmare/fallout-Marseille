# Installer le territoire local v0.41

## Prérequis
Python 3.11 ou plus récent et accès Internet à Supabase.

## Installation complète
```bash
python3 tools/install_local_pack_v041.py --workers 3
```

L’installateur récupère les 24 archives JWT, les contrôle, installe les PBF puis lance l’installation des huit terrains.

## Couche générale uniquement
```bash
python3 tools/install_local_pack_v041.py --source base --skip-terrain
```

## Cadastre uniquement
```bash
python3 tools/install_local_pack_v041.py --source cadastre --skip-terrain
```

## Vérification hors téléchargement
```bash
python3 tools/install_local_pack_v041.py --verify-only
```

## Benchmark
```bash
python3 tools/benchmark_map_v041.py
```

## Reprise
Les archives sont conservées temporairement dans `data/map_pack/.chunks_v041` pendant le traitement. Utilisez `--keep-chunks` pour les garder. Les écritures finales passent par des fichiers `.part` puis un remplacement atomique.

## Fichiers produits
- `data/map_pack/local_pack_v041_status.json`
- `data/map_pack/benchmark_v041.json`
- `data/map_pack/france-vector/...`
- `data/map_pack/cadastre/...`
- `data/map_pack/terrain/...`
