# Installer la carte réelle v0.38

## Pack complet
```bash
python3 tools/install_real_map_v038.py --endpoint cloud
```

## Sélections
```bash
python3 tools/install_real_map_v038.py --source base
python3 tools/install_real_map_v038.py --source cadastre
python3 tools/install_real_map_v038.py --macro geo_huveaune
python3 tools/install_real_map_v038.py --verify-only
```

## Fichiers vides officiels
Une coordonnée cadastrale sans contenu produit :
- un fichier `.pbf` de zéro octet ;
- un fichier voisin `.pbf.empty.json` attestant la réponse officielle vide.

La suppression du marqueur rend le fichier invalide à l'audit.

## Volumétrie
Le cache cloud contient environ 86,97 Mo de données PBF. La taille finale sur disque est supérieure à cause des répertoires, rapports et marqueurs de tuiles vides.
