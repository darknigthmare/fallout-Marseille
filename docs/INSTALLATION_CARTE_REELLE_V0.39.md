# Installation de la carte réelle v0.39

## Prérequis
Python 3.10 ou plus récent. Le ZIP compact ne contient pas les données territoriales lourdes.

## Tout installer

```bash
python3 tools/install_real_map_v039.py --endpoint cloud
```

## Vectoriel uniquement

```bash
python3 tools/install_real_map_v039.py --source vector --endpoint cloud
```

## Relief uniquement

```bash
python3 tools/install_real_map_v039.py --source terrain
```

## Limiter à une macro-région

```bash
python3 tools/install_real_map_v039.py --macro geo_huveaune
```

## Vérifier sans télécharger

```bash
python3 tools/install_real_map_v039.py --verify-only
```

## Résultats
Les PBF sont rangés sous `data/map_pack/base` et `data/map_pack/cadastre`. Les huit grilles sont rangées sous `data/map_pack/terrain`.

Chaque fichier est écrit via un fichier temporaire puis renommé atomiquement. Les PBF sont décodés avant conservation. Les grilles terrain sont vérifiées pour leur macro, emprise, dimensions, nombre de cellules, ressource, NoData et SHA-256.
