# Installation de la carte réelle v0.36

## Streaming immédiat

Le HTML peut charger les tuiles en ligne via le relais v0.36. Une connexion Internet est nécessaire. Les fichiers valides sont mis en cache par le navigateur.

## Pack local complet

Exécuter depuis le dossier du projet :

```sh
python3 tools/install_real_map_v036.py --workers 6
```

Options utiles :

```sh
# Reprendre uniquement le cadastre de Marseille
python3 tools/install_real_map_v036.py --source cadastre --macro geo_marseille

# Utiliser le relais CORS authentifié
python3 tools/install_real_map_v036.py --relay

# Vérifier les fichiers sans télécharger
python3 tools/install_real_map_v036.py --verify-only
```

Lancer ensuite le jeu avec le serveur local (`LANCER_APP_*`). Un navigateur ne peut généralement pas lire un dossier de PBF adjacent depuis une page `file://`.

## Audit

```sh
python3 tools/audit_real_map_v036.py
```

Le code retour est non nul tant que le pack est incomplet. Le JSON et le HTML d’audit sont écrits dans `verification/`.

## Relief

Acquérir des GeoTIFF RGE ALTI officiels couvrant l’emprise, puis :

```sh
python3 tools/terrain_real_v036.py /chemin/vers/*.tif
```

Le script refuse une cellule NoData ou une couverture inférieure à 99,9 %. Les huit JSON générés sont placés dans `data/map_pack/terrain/`.
