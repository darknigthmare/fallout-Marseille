# Architecture cartographique v0.39

## Vectoriel
Le pipeline v0.38 reste la base : PBF OpenStreetMap/data.gouv.fr pour les routes, rails, eau et occupation du sol ; PBF Cadastre Etalab/DGFiP pour le bâti. Le cache privé contient 5 884 coordonnées traitées.

## Terrain
### Service final
`fallout-mistral-terrain-v039` est un relais en lecture seule avec JWT obligatoire. Il sert huit JSON privés et ferme la route de génération avec HTTP 410.

### Stockage
- bucket privé `fallout-mistral-terrain-v039` ;
- table `public.mistral_terrain_cache` sous RLS ;
- aucun droit de lecture direct pour `anon` ou `authenticated` ;
- un objet JSON par macro-région.

### Client
`src/v039/01_terrain.js` vérifie, assainit et applique le terrain. Les valeurs absolues utilisent un `Float32Array` accompagné d’un masque de validité. Les grilles peuvent être mises en cache dans IndexedDB sous les clés `terrain:v039:<macro>`.

### Rendu
La projection WGS84 utilise `v015GeoUnproject`, donc l’orientation des lignes nord-vers-sud reste cohérente avec le repère local dont l’axe Z augmente vers le sud. Les altitudes négatives proches du littoral sont conservées comme preuve mais sont limitées au plan marin dans le rendu actuel.

## Séparation des responsabilités
- le manifeste décrit ce qui doit exister ;
- le cache cloud prouve ce qui a été acquis ;
- le pack disque prouve ce qui est disponible hors ligne ;
- IndexedDB prouve ce que ce navigateur a déjà conservé ;
- l’audit topologique ne s’exécute pleinement qu’avec les PBF locaux.
