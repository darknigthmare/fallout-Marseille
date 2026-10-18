# Installation v0.49

Décompressez l’archive et utilisez `LANCER_APP_WINDOWS.bat`, `LANCER_APP_LINUX.sh` ou `LANCER_APP_MAC.command`. Python est nécessaire au serveur local. Le HTML peut aussi être ouvert directement ; une origine HTTP locale reste recommandée pour les fichiers et le stockage.

## Développement et tests
Python 3.11+, Node.js et Chromium via Playwright sont nécessaires aux tests, pas au jeu déjà compilé.

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m playwright install chromium
python3 tools/build_single.py
python3 tools/check_v049.py
python3 tests/v049/capture.py
python3 tools/package_v049.py
```

Les nouveaux tests utilisent `CHROMIUM_PATH` s’il est défini, puis Chromium système, puis le navigateur fourni par Playwright. Les scripts historiques restent archivés dans leur version d’origine. `--workers 3` permet de paralléliser la QA ; l’exécution séquentielle reste la valeur par défaut.

## Test du défaut antérieur
```bash
python3 tests/v049/baseline.py
```

Cette commande exécute le HTML v0.48 conservé dans l’historique pour reproduire le défaut de soin lors du déchargement. Ce contrôle n’est pas compté comme une réussite du programme v0.49.

## Données géographiques
Les outils d’installation sont conservés mais les anciens relais distants ne sont pas garantis disponibles. Exécutez l’audit pour connaître les fichiers réellement installés :

```bash
python3 tools/validate_real_map_v046.py --require-complete --report verification/v049/LOCAL_DATA_STATE.json
```

Une erreur de cet audit signifie que le pack est incomplet. Le banc synthétique Ctrl + Maj + F9 permet de vérifier le programme sans prétendre disposer du territoire réel.
