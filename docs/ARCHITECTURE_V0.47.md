# Architecture v0.47

`src/v047/00_stream_primitives.js` expose BudgetCache, SpatialGrid, validation des marqueurs vides et SHA-256 de repli. Les tests Node n’ont pas besoin du navigateur.

`01_staging.js` prépare une banque de terrain privée, des tuiles indexées, des maillages terrain globaux et une nature déterministe. Aucune de ces étapes ne publie d’état partiel.

`02_streaming.js` lie la Gate héritée à un chargement anticipé, à sa promotion bloquante, à l’annulation et au changement de scène. Les identifiants de tâche empêchent une réponse tardive de piloter l’interface d’une autre demande.

`03_interface.js` affiche uniquement l’état courant : ressources chargées, estimations de mémoire, origines, erreurs et inspection du disque. Les contrôles QA sont exposés dans la surface debug existante, pas dans le menu public.

`04_lab_safety.js` conserve séparément le monde de campagne, sa banque de terrain, ses tuiles et son état avant l’entrée dans le banc. Le menu historique ne doit ni sauvegarder le banc ni remplacer la scène conservée par son décor d’Aubagne après un retour.

## Publications
Une transaction suit : manifeste requis → lectures validées → banque terrain privée → réemploi/import géométrique → maillages et masques → vérification d’annulation → publication. Le décor courant reste utilisable pendant le préchargement. À la marge de sûreté, le mouvement attend.

Les rayons restent ceux de la branche : rayon source 940 m et portée visible 720 m, avec fenêtre d’avancement plus petite. Il ne s’agit pas d’une certification d’accessibilité de l’intégralité d’une commune.

## Serveur local
`tools/serve_game.py` écoute sur 127.0.0.1. `/__mistral/local-data` appelle l’audit existant en lecture seule, avec cache serveur de 30 secondes et réponse HTTP no-store. Aucun téléchargement ni écriture de données géographiques n’est déclenché par ce bouton.

## Compatibilité
Les sources `src/v046` ne sont pas modifiées : la v0.47 les étend par des modules chargés après elles. Les originales de l’outil de build et des fichiers remplacés sont archivées. Le projet complet peut être reconstruit par `python3 tools/build_single.py`.
