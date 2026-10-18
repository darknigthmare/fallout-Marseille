# Architecture cartographique v0.38

## Sources
- `src/v038/00_state.js` : compteurs vérifiés et migration.
- `src/v038/01_streaming.js` : relais v0.38 et gestion des tuiles vides.
- `src/v038/02_interface.js` : Pip-Boy et statut cartographique.
- `src/v038/03_boot.js` : initialisation et crédits.

## Backend
- Storage privé `fallout-mistral-map-v037`.
- Table RLS `mistral_map_tile_cache`, sans accès client direct.
- Vue agrégée `mistral_map_cache_stats` en `security_invoker`.
- Fonction Edge `fallout-mistral-map-v038` avec JWT obligatoire.

## Contrat d'une tuile vide
Une réponse source HTTP 204 est mémorisée avec `is_empty=true`, `bytes=0`, SHA-256 du corps vide et aucune création de fichier PBF dans Storage. Le relais répond 200 avec un corps vide et `X-Map-Empty: 1`, afin que le moteur distingue « rien à afficher » de « erreur réseau ».
