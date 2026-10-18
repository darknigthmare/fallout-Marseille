# Architecture v0.42

## Modules

- `src/v042/00_catalog.js` — catalogue embarqué des 248 sites.
- `src/v042/01_state.js` — état, migration, index et paramètres.
- `src/v042/02_layer.js` — streaming de proximité, extérieurs, PNJ, contrats, hostiles et récompenses.
- `src/v042/03_instance.js` — instances visitables et objectifs intérieurs.
- `src/v042/04_interface.js` — carte Pip-Boy, filtres, repères et progression régionale.
- `src/v042/05_boot.js` — intégration de version et surface de diagnostic.
- `tools/build_fallout_layer_v042.py` — génération déterministe du catalogue.
- `tools/audit_fallout_layer_v042.py` — validation statique du placement.

## Invariants

- 31 sites par macro-région ;
- coordonnées contenues dans leur emprise ;
- identifiants uniques ;
- catalogue reproductible à seed fixe ;
- aucune modification des données cartographiques officielles ;
- seuls les sites proches possèdent des objets de monde ;
- un site sécurisé ne duplique ni récompense ni boss ;
- les intérieurs conservent le retour WGS84 vers leur entrée ;
- les types ennemis doivent appartenir au catalogue du jeu.
