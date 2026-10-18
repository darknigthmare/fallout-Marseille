# Architecture v0.40

## Modules
- `src/v040/00_state.js` — définitions, preuves embarquées et persistance ;
- `src/v040/01_corridors.js` — roadbook, préchargement et suivi de continuité ;
- `src/v040/02_stitching.js` — frontières exactes de tuiles, fusion de bâti et raccords terrain ;
- `src/v040/03_interface.js` — Pip-Boy, statut et HUD ;
- `src/v040/04_boot.js` — initialisation et surface QA ;
- `supabase/functions/fallout-mistral-corridors-v040` — relais de preuve en lecture seule.

## Invariants
- une preuve non certifiée ne peut pas lancer un roadbook ;
- les preuves hors ligne sont les mêmes géométries que les preuves cloud arrondies au microdegré ;
- un déplacement anormal est compté comme rupture ;
- un bâtiment n’est fusionné qu’avec une union convexe sûre ;
- une cellule terrain NoData n’est jamais remplacée par une altitude officielle inventée ;
- la route de construction cloud répond 410 après gel des preuves.
