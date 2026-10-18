# Installation de la v0.47

Décompressez le ZIP complet ou le ZIP jeu dans un dossier. Lancez le script d’application de votre système : Windows `LANCER_APP_WINDOWS.bat`, Linux `LANCER_APP_LINUX.sh`, macOS `LANCER_APP_MAC.command`. Le serveur Python reste lié à 127.0.0.1.

Le HTML autonome fonctionne également pour ouvrir le programme, mais l’accès aux fichiers et au stockage peut différer selon le navigateur. Le serveur local est préférable.

## Mesurer les fichiers présents
```bash
python3 tools/validate_real_map_v046.py --report verification/v047/LOCAL_DATA_STATE.json --require-complete
```

La commande retourne un échec lorsque le pack manque. Le bouton d’audit dans CONTINUITÉ effectue la même lecture par le serveur local et ne lance pas de téléchargement.

Les installateurs historiques sont conservés, mais la disponibilité actuelle de leurs relais distants n’a pas été établie ici. Une erreur d’accès n’est pas remplacée par de fausses données.

## Reconstruire et tester
```bash
python3 tools/build_single.py
python3 tools/check_v047.py
python3 tests/v047/capture.py
```

Les tests Python nécessitent Playwright et Chromium ; le chemin utilisé sur cette machine est `/usr/bin/chromium`. Les tests Node purs et le serveur n’ont pas cette dépendance. Aucun navigateur ni fonte n’est livré dans l’archive.
