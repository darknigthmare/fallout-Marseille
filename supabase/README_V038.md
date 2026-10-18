# Relais cartographique v0.38

Le relais `fallout-mistral-map-v038` sert exclusivement les coordonnées inscrites dans `mistral_map_tile_cache`. Le stockage est privé, la table utilise RLS et les rôles clients n'ont aucun droit direct. Les réponses cadastrales 204 sont représentées par une métadonnée `is_empty=true` et un corps de taille zéro avec `X-Map-Empty: 1`.

La fonction de préchauffage cadastrale a été neutralisée après l'acquisition complète des 5 517 coordonnées.
