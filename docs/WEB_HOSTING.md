# Livraison web du vrai jeu

La base inspectée est `580f432e32369a950bb7761f9441da9f063f521e`, version 0.50.0. Le moteur WebGL, la campagne, les sauvegardes et les quatre familles de données géographiques restent ceux de cette source.

`python3 tools/build_web.py` restaure les archives déjà fournies, sans acquisition réseau, puis appelle les validateurs existants : pack de base, enrichissements, atlas communal et relief LiDAR natif. Toute absence ou corruption bloque la construction. La sortie `.vercel-static` contient tous les fichiers runtime de `data`, le vrai HTML et ses ressources PWA. Seuls les archives d’installation et leurs caches intermédiaires sont exclus de la sortie : leurs données extraites sont présentes.

Les données dépassent 1,1 Go une fois décompressées. Chaque réponse `data/*` utilise donc HTTP gzip ; le navigateur retrouve exactement les octets d’origine. `release-manifest.json` conserve pour chaque fichier les tailles et SHA-256 avant et après transport. Les objets, coordonnées, NoData, preuves, attributions et limites des sources ne sont pas réécrits.

Les quatre routes `/__mistral/local-data`, `/__mistral/world-sources`, `/__mistral/city-sources` et `/__mistral/precise-terrain` exposent les résultats réels de cette inspection à la construction. Ces fichiers sont immuables avec le déploiement. `auditMode`, `inspectedAt`, `sourceCommit` et `inspectionScope` indiquent cette portée ; le panneau ne prétend pas inspecter le disque du joueur en direct. L’export adapte seulement cette présentation du diagnostic. Il ne modifie pas les mécaniques, règles de déplacement, quêtes ou fichiers géographiques décodés. L’empreinte du HTML source et celle du HTML exporté restent distinctes.

## Vérifier

```bash
python3 tools/build_web.py
python3 tools/serve_web.py --port 9402
python3 tools/check_web.py --base-url http://127.0.0.1:9402
python3 -m unittest discover -s tests/expansion -p test_server_diagnostics.py -v
```

Le contrôle de sortie compare tous les fichiers runtime à la source, décode gzip et vérifie les empreintes ; le contrôle HTTP couvre chaque famille de cartes, le vrai HTML, le manifeste et les quatre routes. Reprendre ensuite le parcours dans un vrai navigateur : entrée en jeu, déplacement, Pip-Boy et chargement des données géographiques. Les commandes de contrôle ne constituent pas une campagne humaine complète ni une certification architecturale 1:1.

Sur Vercel, `vercel.json` sélectionne cette construction et définit les en-têtes gzip ainsi que les quatre réécritures exactes. Aucun serveur Python permanent, fonction volumineuse, base payante ou compte de jeu n’est requis. Les fichiers géographiques absents ne reçoivent jamais le HTML par une règle de repli SPA. Une nouvelle origine HTTPS possède ses propres sauvegardes navigateur ; les exports existants permettent de les transférer.

## Contrôle du 13 novembre 2026

La sortie locale a passé la comparaison de ses **7 761 fichiers runtime** : **1 130 533 682 octets décodés**, **276 960 249 octets gzip**. Le contrôle HTTP couvre la plus grosse ressource de chaque famille, y compris une dalle LiDAR native de 4 008 004 octets, et les quatre routes de diagnostic. Les huit tests existants du cache de diagnostic passent. Les preuves, requêtes réelles et deux captures du vrai navigateur sont dans [`verification/web-hosting-2026-11-13`](../verification/web-hosting-2026-11-13).

Le bouton natif Exploration libre, le déplacement physique et la carte du Pip-Boy fonctionnent dans Chromium. Ce mode préremplit le niveau 26 et le chapitre VI : ce contrôle ne représente pas une campagne terminée. La scène narrative montrée n’est pas la reconstruction géographique de la rue.

Un second parcours appelle explicitement le chargeur géographique existant pour contrôler la livraison, sans données synthétiques. Le navigateur reçoit les véritables partitions de bâtiments, routes et relief. La scène n’a toutefois pas atteint son état jouable dans les 240 secondes accordées au rendu logiciel SwiftShader ; aucun parcours géographique complet n’est annoncé. Les cartes n’ont pas été retirées et le moteur n’a pas été modifié pour masquer cette limite. Le relief LiDAR natif conserve sa couverture limitée à douze km² centraux.

Le projet Vercel `fallout-marseille-mistral` est créé et relié au dépôt. Au moment de ce contrôle, aucun déploiement Fallout n’a été accepté : le quota quotidien gratuit de l’équipe a été atteint avant sa soumission. `https://fallout-marseille-mistral.vercel.app` est donc une adresse prévue, pas une publication vérifiée. Après rétablissement de la capacité, contrôler aussi les en-têtes gzip et les empreintes décodées sur l’URL HTTPS réelle, puis répéter le parcours navigateur avant d’activer le lien du launcher.
