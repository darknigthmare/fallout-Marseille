# Marseille : prolongement parallèle

HTML gelé : `ea8ba2e3d9ba9ed1925628672f4c596475ff2437de06bfa7979ee03f6f59f0bf` ; **315 hashes** revérifiés.

**1 847 contrôles** : 1 080 unités, 434 contrats hérités, 3 sorties de reconstruction identiques, 206 contrôles natifs de lore/armure/collectes, 101 contrôles architecturaux et 23 contrôles du bestiaire. Les méthodes et aides sont séparées dans `CONTINUATION_INTEGRATION.json`. Les 23 captures sont de vrais rendus WebGL, identifiés par SHA et signature PNG.

Les rapports originaux restent intacts. `architecture/ACTUAL_LAYOUT_AUDIT.svg` est un plan dérivé du vrai layout, lié par SHA au JSON et au rapport natif. `facades/` et `world/` conservent leurs preuves ciblées, sans les compter une deuxième fois ; les rejouements en échec sont clairement rangés comme baseline. Les 1 492 contrôles précédents restent historiques dans le dossier voisin `architecture`.

`PREFLIGHT_SUMMARY.json` explique les erreurs de préparation/pilote : helper privé, attente layout2, interpréteur sans dépendance raster, diagnostic annulé et cleanup Playwright. Aucun préflight ni image ratée ne compte comme validation finale ou bug de production établi. Aucun contenu de conversation ChatGPT privé n’est copié.

L’architecture sans relevé reste inventée. Les parcours natifs sont assistés ; ils ne certifient pas toutes les branches, créatures, rues ou pièces de Marseille. Les observations de réseau sont conservées. L’architecture dispose d’une attestation de processus exit0 ; son stdout avait été diffusé par l’outil et les checks/stages restent dans le rapport.

Le collecteur ne lance ni build, navigateur ni test : `python scripts/collect_continuation.py --repo CHEMIN --evidence DOSSIER_QA --check-only`. `--publish` écrit uniquement `verification/expansion/continuation/` après validation. Les hashes de tous les fichiers publiés figurent dans `MANIFEST.json`, hors lui-même.
