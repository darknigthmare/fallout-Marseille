# Architecture cartographique v0.37

## Modules du moteur

- `src/v037/00_state.js` — contrat de couverture, plages exactes, état persistant.
- `src/v037/01_cache_streaming.js` — IndexedDB, éviction, sources et préchargement.
- `src/v037/02_topology.js` — graphe routier, raccords et déduplication du bâti.
- `src/v037/03_interface.js` — Pip-Boy, statut, métriques et commandes.
- `src/v037/04_boot.js` — initialisation, crédits, HUD et surface QA.

## Outils

- `install_real_map_v037.py` — acquisition/validation locale.
- `audit_real_map_v037.py` — couverture et topologie globale.
- `build_map_manifest_v036.py` — générateur historique du plan, dont le résultat v0.37 est conservé.
- `mvt_audit_v036.py` — décodeur MVT autonome réutilisé.

## Cache cloud

- Edge Function : `fallout-mistral-map-v037`.
- Storage privé : `fallout-mistral-map-v037`.
- Table technique : `mistral_map_tile_cache`.
- RLS active ; aucun privilège SELECT pour `anon` et `authenticated` ; aucune politique publique.
- La clé privilégiée n’est jamais envoyée au client.

## Invariants

- une coordonnée hors manifeste est refusée côté jeu et côté relais ;
- une réponse non MVT n’est pas conservée ;
- le cache ne change pas le contenu officiel ;
- le compteur acquis n’utilise jamais le nombre théorique du manifeste ;
- une tuile absente n’est pas un défaut topologique confirmé ;
- le relief absent n’est jamais synthétisé comme donnée officielle.
