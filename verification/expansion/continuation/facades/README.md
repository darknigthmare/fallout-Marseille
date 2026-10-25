# Façades : prolongement du 25 octobre 2026

Ces preuves utilisent les modules gelés :

- `07_facades.js` : `855db991e5053752a7d1a366cac3610f6ea7b304461e448d99e45362a49eb432` ;
- `08_city_interiors.js` : `1f5c099bc4082baa6c64660fe6aacb22a52b839b2cbdaf0ce29cb55a4fbc83bf`.

## Résultats et portée

Le modèle trouve et rend maintenant une porte sur les **191 contours compatibles ciblés**, contre **188** au commit `48418cc` et **0** au commit `cac50f3`. Les 72 approches de grandes emprises sont retrouvées et rendues. Aucun segment d’ouverture vérifié ne quitte ses arêtes source ; les contours et trois index communaux restent inchangés. Quatre inventaires paginés produisent une séquence identique avec des pages de 31, 128 et 4 096 éléments ; le plus grand contient **12 624 ouvertures inventées**.

187 contours reçoivent des fenêtres. Les quatre autres cas restent explicitement motivés : trois tours techniques sans registre de fenêtre et un conflit de dimension/porte. Aucun compteur ne prétend dénombrer toutes les portes réelles de Marseille.

Les deux anneaux cadastraux de 88/89 microsegments sont développés sans supprimer de coordonnées : les supports détectent les petits décrochements quantifiés mais gardent les vrais angles droits séparés. La largeur projetée, le dégagement intérieur et extérieur sont vérifiés. Les portes inventées étroites gardent 0,78 m de largeur et deux jambages de 0,15 m. Les fenêtres sont inventées ; aucune cote documentaire n’est déplacée.

`ACTUAL_SOURCE_CASES.json` conserve les trois objets acquis, leurs propriétés/provenances/attributions originales, les empreintes des chunks et leurs anneaux métriques dérivés avec la projection de production. Chaque objet a été comparé à son chunk installé. `RESIDUAL_ENTRANCE_METRICS.json` conserve les largeurs projetées et dégagements intérieurs/extérieurs réellement exportés des candidats, avec contrôle du rayon d’acteur de 0,38 m. Attribution : **IGN — Géoplateforme, BD TOPO ; Licence Ouverte 2.0**. Ces objets géographiques ne mesurent pas les portes et fenêtres générées.

Les tests isolés réussissent : **89 contrôles existants + 19 nouveaux = 108**. Les plans documentaires de régression, angles/encoches synthétiques et stress numérique sont explicitement des fixtures ; ils ne sont pas installés dans l’atlas du jeu. Les comparaisons géométriques ne sont pas comptées comme assertions supplémentaires ou parcours natifs. Aucun navigateur n’a été lancé ici. Relief de seuil, collisions avec les voisins, droit d’accès et habitabilité réels restent hors de cette preuve.

## Reproduction portable

Le clone doit contenir les données communales extraites des archives vérifiées ; si nécessaire, exécuter `python3 tools/city_sources.py install` depuis ce clone. Définir `MISTRAL_REPO_ROOT` vers ce clone, puis, depuis le dossier de cette preuve :

```bash
MISTRAL_REPO_ROOT=/chemin/du/clone node run_facades_tests.cjs
MISTRAL_REPO_ROOT=/chemin/du/clone node residual_metrics.cjs
MISTRAL_REPO_ROOT=/chemin/du/clone MISTRAL_BASELINE_DIR="$PWD/baseline-48418cc" MISTRAL_AUDIT_OUTPUT_DIR=/tmp/facades-48418cc node curves_compare.cjs --final
MISTRAL_REPO_ROOT=/chemin/du/clone MISTRAL_BASELINE_DIR="$PWD/baseline-cac50f3" MISTRAL_AUDIT_OUTPUT_DIR=/tmp/facades-cac50f3 node curves_compare.cjs --final
```

Le runner utilise les octets exacts des tests archivés, avec leur résolution de chemins d’origine vers les modules du clone ; aucun état de jeu ni résultat de moteur n’est substitué. Les SHA du runner, des tests et des modules sont conservés. Le comparateur est dérivé du comparateur précédent ; `ORIGINAL_COMPARATOR_IDENTITY.json` décrit les seules adaptations de portabilité et d’identité de baseline. Les instantanés de baseline proviennent des blobs Git exacts, identifiés dans chaque `BASELINE_IDENTITY.json`.

Par défaut les scripts exigent les SHA gelés ci-dessus et les trois index communaux d’origine. `MISTRAL_EXPECT_FACADE_SHA` / `MISTRAL_EXPECT_INTERIOR_SHA` permettent uniquement une nouvelle comparaison explicite sur d’autres modules ; elle produit de nouveaux résultats et ne revalide pas cette campagne historique. Les journaux conservent les chemins absolus réellement utilisés, tandis que les commandes ci-dessus sont portables.

`FACADES_CONTINUATION.json` résume les résultats ; `MANIFEST.json` donne les empreintes de tous les fichiers de cette preuve, hors lui-même.
