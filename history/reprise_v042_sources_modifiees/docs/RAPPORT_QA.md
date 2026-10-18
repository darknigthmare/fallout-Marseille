# Rapport QA — Fallout : Mistral v0.42

## Résultat global

**204 contrôles réussis sur 204** sur le même HTML final.

- échec : **0** ;
- exception JavaScript remontée : **0** ;
- rapports dont l’empreinte diffère du HTML livré : **0** ;
- audit statique du catalogue : **248 sites valides, 0 erreur, 0 avertissement**.

Empreinte HTML testée :

`94835b6b97ba9d48131053e9d7f53edf6551a69280113e6c38ca1b510813e2db`

## Suites

| Suite | Résultat | Portée |
|---|---:|---|
| Couche Fallout v0.42 | **41/41** | catalogue, colonie, PNJ, contrat, élite, boss, abri, persistance et mobile |
| Couverture des huit régions | **25/25** | 248 projections, streaming et boss de chaque macro-région |
| Régression pack local v0.41 | **11/11** | distribution et interface du pack territorial |
| Régression corridors v0.40 | **16/16** | Aubagne–Marseille, Aubagne–La Ciotat, relief et stitching |
| Régression relief v0.39 | **16/16** | RGE ALTI, NoData, maillage et cache |
| Régression vectoriel v0.38 | **16/16** | cache, PBF et coordonnées vides |
| Régression produit v0.35 | **41/41** | sauvegardes, hub, opérations, carrière et session |
| Régression interface produit | **10/10** | reprise, mode sûr, diagnostic et crédits |
| Régression prologue | **22/22** | A-03 jusqu’à Aubagne |
| PWA | **6/6** | manifeste, icônes, cache et lanceurs |

## Points spécifiquement prouvés

- 31 sites sont projetés à l’intérieur de chacune des huit emprises ;
- une colonie et un boss régional sont réellement instanciés dans chaque macro-région ;
- les 41 familles ennemies référencées existent dans le bestiaire ;
- un contrat territorial sélectionne une menace non sécurisée ;
- une élite et un boss possèdent leurs rangs distincts ;
- un abri charge une instance visitable avec six sous-zones ;
- la sécurisation et le repère résistent à un aller-retour de sauvegarde ;
- le budget de streaming limite les sites actifs ;
- la carte reste utilisable sur une fenêtre 390 × 844.

## Portée et limites

Les essais sont automatisés dans Chromium avec rendu logiciel. Ils ne remplacent pas une visite humaine des 248 implantations, une certification sur téléphone matériel ou une campagne complète de plusieurs dizaines d’heures. Les données réseau distantes sont bloquées dans les tests de couche afin de vérifier que le catalogue et ses systèmes de jeu ne dépendent pas d’une réponse cloud instantanée.
