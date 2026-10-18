# Démarrage et installation

## Programme

Extraire tout le ZIP. Lancer `LANCER_APP_WINDOWS.bat` ou le script Linux/macOS correspondant. Python 3.11+ convient au serveur local ; Node est utile pour reconstruire et lancer les tests, pas pour jouer à l’HTML déjà compilé.

## Carte réelle

Conserver les données vectorielles dans `data/map_pack/france-vector/` et `data/map_pack/cadastre/`. Les huit grilles attendues vont dans `data/map_pack/terrain/geo_*.json`.

Les outils hérités `install_local_pack_v041.py` et `install_terrain_v039.py` sont inclus, sans garantie de disponibilité de leurs endpoints historiques dans cette session. Leur présence n’est pas la preuve d’une installation réussie.

Validation sans faux succès :

```sh
python3 tools/validate_real_map_v046.py --require-complete
```

Un résultat incomplet retourne un code de sortie non nul. Le rapport JSON distingue fichiers absents, invalides et coordonnées officiellement vides.

## Banc sans pack

Ctrl + Maj + F9 ouvre le banc synthétique. Il ne sauvegarde pas la campagne. Le bandeau reste visible. Fermer/recharger le jeu termine le banc.

## Reconstruction

```sh
python3 tools/build_single.py
node --check src/game.js
python3 tools/check_v046.py
```

Les tests navigateur exigent Playwright et Chromium, déjà utilisés pour cette livraison. Les tests Node ne nécessitent pas de paquet npm tiers.
