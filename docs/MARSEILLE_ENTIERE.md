# Marseille : couverture communale et architecture jouable

Le territoire supplémentaire couvre la commune officielle **13055, Marseille, îles comprises**. Les bâtiments, routes, relief et littoral proviennent de données IGN réellement téléchargées. Les façades et intérieurs ajoutent une interprétation jouable stable, à l’échelle métrique, dans les emprises disponibles. Les détails inventés sont distingués des annotations documentées.

Le [prolongement du 25 octobre](CHANTIERS_ACTIFS.md) améliore les portes sur de courts pans, les programmes compacts d’intérieur et la conservation du monde pendant les chargements. Il ajoute aussi les [dossiers des factions](LORE_CONTINUITE.md), l’entretien des [armures assistées existantes](ARMURES_ASSISTEES.md), les [collections](CONTENU_EMBLEMATIQUE.md) et trois variantes du [bestiaire régional](BESTIAIRE_REGIONAL.md). Sa [validation finale](../verification/expansion/continuation/CONTINUATION_INTEGRATION.json) est réussie sur le programme du 25 octobre ; les rapports du 24 octobre ci-dessous restent historiques. Aucun nouveau relevé architectural mesuré n’est acquis pour ces ajouts.

## Données livrées

| Ensemble | Contenu et portée |
|---|---|
| Limite communale | Objet administratif IGN de 38 320 sommets ; enveloppe `[43.1696313, 5.22875102, 43.39105653, 5.53254336]`, dans l’ordre sud, ouest, nord, est. |
| Bâtiments et routes | **291 001 identifiants d’objets bâtiment** et **55 449 identifiants de tronçons routiers** distincts, issus de 77 rectangles de requête couvrant le polygone communal, subdivisés en **290 partitions** pour le chargement. |
| Relief communal | Grille de fond au pas demandé de **25 m**, complétée par **25 partitions au pas demandé de 10 m** couvrant toute l’enveloppe. Les points communs aux frontières sont conservés et comparés. |
| Littoral | Mer obtenue à partir de BD CARTO « Eau libre » et de **148 lignes BD TOPO « Plus hautes eaux »**, découpée en **118 tuiles**, avec **97 trous d’îles** préservés. Les découpes techniques ne simplifient pas le trait de côte. |
| Secteur détaillé historique d’Aubagne | Les 1 404 objets bâtiment, 472 routes et deux relevés locaux plus fins déjà acquis restent disponibles, avec leur provenance distincte. |

Les objets WFS sont conservés entiers. Ces totaux incluent les objets de bordure et quelques retours conservateurs de l’index spatial du fournisseur ; ils ne dénombrent ni des adresses, ni des immeubles physiques tous strictement situés dans Marseille. La couverture signifie que toutes les partitions de requête prévues sur le territoire officiel ont été terminées et vérifiées. Elle ne certifie pas que la base IGN recense chaque construction existante.

Les coordonnées et attributs de chaque partition ont été comparés aux réponses HTTPS originales, empreintes comprises. Le [rejeu géométrique exact](../implementation/city-sources/EXACT_SOURCE_GEOMETRY_REPLAY.json) précise les rares omissions d’altitude explicitement documentées. Les [requêtes et leur provenance](../implementation/city-sources/IGN_MARSEILLE_ACQUISITION.json) et les [qualités des attributs](../implementation/city-sources/IGN_MARSEILLE_SOURCE_QUALITY.json) sont conservées séparément.

## Relief, rues et mer

Les grilles proviennent d’interrogations réelles de la ressource `ign_rge_alti_wld`, en altitude NGF-IGN69. Le pas de 10 m décrit l’espacement demandé entre échantillons, pas une précision absolue de 10 m ni la résolution native du relevé. Le jeu utilise le relevé valable le plus fin disponible ; les relevés d’Aubagne de 2 m et l’extrait LiDAR HD issu de pixels natifs de 50 cm gardent donc leur intérêt local.

Les NoData exacts du fournisseur et les observations hors de la plage prise en charge par le moteur sont comptés séparément. Les observations brutes, leur position et leurs empreintes restent traçables ; aucune altitude fictive ne comble les absences. Une grille de requête complète peut ainsi comporter des points sans hauteur utilisable. L’audit des frontières compare les valeurs **et leur validité**.

| Grilles interrogées | Observations de nœuds | Hauteurs utilisables | NoData fournisseur | Hors plage du moteur |
|---|---:|---:|---:|---:|
| Fond 25 m | 973 180 | 740 688 | 221 059 | 11 433 |
| Ensemble des 25 partitions 10 m | 6 091 015 | 4 637 224 | 1 374 634 | 79 157 |
| Nœuds fins dans le vrai polygone communal | 2 388 076 | 2 387 237 | 5 | 834 |

Ces comptages comprennent les doublons des bords partagés. Une partition fine, surtout maritime, ne possède aucune hauteur utilisable ; elle reste explicitement décrite. Les [preuves d’acquisition du relief](../implementation/city-sources/TERRAIN_ACQUISITION.json) et des [40 frontières](../implementation/city-sources/TERRAIN_SHARED_EDGES.json) retracent les 7 064 195 observations et les 19 744 nœuds partagés, sans différence de hauteur ou de validité. Les observations hors plage ne sont pas toutes assimilées à des erreurs fournisseur ou à une bathymétrie mesurée.

Les largeurs routières renseignées ont priorité. Sinon, la largeur est une estimation déclarée selon la nature de voie : un sentier n’hérite plus de la largeur d’une chaussée automobile. Les itinéraires de bac et liaisons maritimes restent des objets source sans recevoir un faux revêtement routier.

Les XYZ fournis restent intacts dans les géométries source et les tracés routiers conservés. Pour les routes IGN explicitement au niveau ordinal zéro, sans pont, tunnel, altitude ou dégagement vertical explicite, **le maillage affiché est dérivé au contact du MNT disponible**, le même sol que celui utilisé par la physique. Cette représentation empêche un ancien axe altimétrique peu détaillé de former un ruban flottant au-dessus de la rue ; elle ne se présente pas comme une mesure exacte des Z de chaussée. Son profil distingue `sourceHeightBasis`, `surfaceDerived`, les sources du terrain et le décalage visuel de 8,5 cm. Les absences de terrain restent sans face. Les structures et cotes verticales explicites gardent leur géométrie altimétrique source.

La mer est déterminée par les polygones et le littoral source. Une altitude zéro ou la seule position hors commune ne suffisent pas à classer un point comme de l’eau. La marche est bloquée sur la mer, avec les exceptions des supports effectivement mesurés, des scènes historiques et des mécanismes de bateau existants. Les réponses maritimes d’un chargement remplacé ou annulé ne sont pas republiées dans le monde courant. La baignade n’est pas implémentée. Le niveau de rendu nominal de l’eau à zéro ne représente pas la marée instantanée.

## Façades et intérieurs

Les volumes conservent les contours, cours intérieures, hauteurs et altitudes exploitables. Le nombre IGN `nombre_d_etages` comprend le rez-de-chaussée. Les valeurs nulles ou invalides ne deviennent pas des niveaux documentés. Sans nombre de niveaux valable, les nefs, tribunes, silos, serres et halles restent des volumes fonctionnels cohérents avec leur usage ; une hauteur de clocher ne devient pas une série d’appartements. Les identifiants stables maintiennent la même architecture lors d’un nouveau chargement ; les différentes composantes d’un même objet restent distinctes.

Les façades ajoutent des ouvertures, portes, volets et encadrements selon l’usage disponible. Les usages explicites priment sur la nature générique « Industriel, agricole ou commercial ». Les contours courbes sont développés sur leurs segments originaux : les ouvertures suivent ces segments, sans redresser l’emprise. L’inventaire des baies se parcourt par pages sans plafond de 160 colonnes. Le rendu conserve ses budgets ; il réserve chaque ouverture entière avant ses ornements et signale les reports. Les candidats sur courts pans et contours quantifiés conservent leurs segments source ; la largeur utile du passage est contrôlée avant l’accès. Les ouvertures documentées gardent leurs cotes et leur arête d’origine. La porte dessinée correspond à l’entrée retenue par le contrôle d’accès. Sur un terrain en pente, une entrée peut desservir un niveau supérieur ; elle ne force pas tous les bâtiments au même rez-de-chaussée. Les espaces trop petits ou trop bas et les bâtiments sans altitude exploitable sont signalés dans les diagnostics plutôt que déclarés accessibles.

Une pression sur **Interagir** près d’une porte accessible ouvre l’intérieur du même bâtiment. Les pièces suivent son contour, ses concavités et ses cours. Les niveaux sont chargés à la demande et reliés par les choix du palier. Il s’agit de transitions entre niveaux, pas d’une simulation de montée à pied dans tous les escaliers. La sortie restitue le point extérieur enregistré.

Les nouvelles entrées utilisent le programme intérieur **version 3**. Les intérieurs inventés peuvent comporter des pièces réellement closes, avec des cloisons, une ouverture de porte de 1,20 m et une circulation conservée. Sanitaires, chambres, cuisines, bureaux, réserves, salles de soin ou vestiaires dépendent de l’usage et de la place disponible. Le reste de l’emprise demeure un volume ouvert explicitement décrit. Les pièces et les meubles suivent l’orientation du bâtiment, avec des collisions correspondantes. Dix-huit types de mobilier fournissent lits, cuisines, sanitaires, rangements, sièges et équipements de travail. Les contenus restent fictifs. Dans les résidentiels inventés de moins de 55 m² par niveau, le programme peut employer un lit simple de 0,95 × 2,05 m et un WC séparé de 0,60 × 0,85 m. Ce sont des choix métriques de création ; les modèles visibles et leurs collisions utilisent ces mêmes dimensions. Un niveau documenté ne reçoit pas ces substitutions de programme.

Le calcul est borné à 10 pièces, 32 meubles, 4 096 cellules d’échantillonnage et 180 essais de circulation par niveau. Le programme compact ajoute jusqu’à 256 points de contrôle près des bords source. Quand ce contrôle détecte qu’une cloison isolerait un recoin praticable, la pièce proposée est écartée et le volume reste ouvert. Les volumes très grands, complexes, trop petits ou dont la circulation initiale n’est pas prouvée par cette grille peuvent conserver des espaces ouverts et des fonctions non placées. L’inspection expose les omissions, les surfaces closes et ouvertes et le budget utilisé. Ce contrôle borné ne certifie pas l’accessibilité de chaque point arbitraire ni un plan réel complet. Les visites sauvegardées des programmes versions 1 et 2 sont reprises avec leur disposition antérieure ; elles ne reçoivent pas des cloisons nouvelles autour du personnage. Le programme version 3 s’applique aux nouvelles entrées. Les contenants ont un inventaire fini, conservé dans les sauvegardes et après **Continuer**.

Les annotations documentaires peuvent fournir des ouvertures, dimensions ou plans précis, avec source et attribution. Le moteur conserve les parties ainsi renseignées et complète les autres de façon cohérente. La liaison exige la géométrie source exacte, le volume métrique et l’ordre des arêtes ; une annotation ne se déplace pas silencieusement après réordonnancement d’un contour. Le nouvel atlas facultatif et son outil de validation sont décrits dans [l’installation des annotations](ARCHITECTURE_DOCUMENTEE.md). Les plans enregistrés dans une sauvegarde persistent après reprise, sortie et réentrée, avec quotas et retour à l’état précédent si l’écriture échoue. **Aucun plan coté de façade ou d’intérieur n’a été acquis dans la recherche publique effectuée ici.** Le [catalogue d’architecture](CATALOGUE_ARCHITECTURE_MARSEILLE.md) expose les références trouvées et les limites d’accès. Les données géographiques ne documentent pas automatiquement la disposition réelle des fenêtres et des pièces. Douze associations de bâtiments à deux sites IGN sont installées : onze volumes religieux du site Notre-Dame de la Garde et un bâtiment du Centre de Conservation et de Ressources du Mucem. Elles décrivent une appartenance de site et ne constituent pas douze relevés architecturaux.

## Chargement et installation

Le serveur normal restaure l’archive communale livrée, sans acquisition réseau, dans `data/map_pack/city/`. Chaque fichier possède une taille et une empreinte vérifiées ; les imports utilisateur déjà valides sont conservés. Les fichiers corrompus provoquent un diagnostic explicite. La validation initiale de l’atlas représente plusieurs centaines de mégaoctets à lire et peut prendre plus d’une minute avant l’ouverture du serveur.

```bash
python3 tools/serve_game.py
python3 tools/city_sources.py audit
```

Les positions fictives sauvegardées des sites sont revérifiées sur les sources chargées avant une réapparition : altitude utilisable, eau et solides. Les coordonnées sûres sont conservées avec la hauteur courante ; aucune hauteur n’est fabriquée. Cette revalidation ne déplace pas les acteurs déjà actifs et ne renouvelle pas leur butin.

Le panneau des cartes affiche les totaux municipaux issus de l’audit du serveur. Il distingue l’ensemble installé du voisinage actuellement rendu. Le chargement de la ville conserve des caches bornés : sources vectorielles 64 Mio/24 entrées, relief 48 Mio/8 entrées, eau 8 Mio/16 entrées et planification de façades 8 Mio/64 entrées et plans intérieurs inventés 1 Mio/4 entrées. Les nouvelles fenêtres de terrain remplacent les précédentes ; les reliefs fins ne s’accumulent pas dans la banque active pendant la marche. Ces budgets ne représentent pas la mémoire totale du navigateur.

Les détails de façade ont une portée et un budget variables selon la qualité graphique. Toute la ville est disponible par déplacement et chargement du voisinage ; ses centaines de milliers d’objets ne sont pas dessinés simultanément. La campagne, ses scènes historiques, le Pip-Boy, les combats, le bivouac, l’entraide et les sauvegardes précédentes sont conservés.

## Validation et fidélité

Le [bilan du 25 octobre](../verification/expansion/continuation/CONTINUATION_INTEGRATION.json) valide le programme HTML `ea8ba2e3d9ba9ed1925628672f4c596475ff2437de06bfa7979ee03f6f59f0bf`. Le [suivi des chantiers](CHANTIERS_ACTIFS.md) détaille les huit axes livrés et leur périmètre.

| Méthode sur le programme du 25 octobre | Contrôles réussis |
|---|---:|
| Modèles de production et outils : 27 suites, sans test ignoré | 1 080 |
| Contrats hérités : quinze processus sans échec, bancs contrôlés | 434 |
| Parcours natif architectural | 101 |
| Parcours natif intégré : lore, armure, collections et Continuer | 206 |
| Pilote natif de bestiaire : une espèce capturée | 23 |
| Sorties identiques d’une reconstruction indépendante | 3 |

Ces **1 847 contrôles** peuvent couvrir les mêmes mécanismes par des méthodes différentes. Leur somme ne représente pas autant de parcours équivalents. Les **23 captures natives** restent distinguées des fixtures, des aides de placement et des plans d’audit. Les trois variantes du bestiaire sont testées sur banc contrôlé ; le pilote natif n’en montre qu’une. Aucun de ces essais ne constitue une visite humaine exhaustive de la commune et de la campagne.

La [comparaison ciblée de façades](../verification/expansion/continuation/facades/FACADES_CONTINUATION.json), **hors du total de 1 847**, retrouve une porte conforme aux contrôles du modèle sur **191 des 191 contours courts retenus**, contre 188 dans la livraison précédente ; 187 reçoivent des fenêtres. Les 72 approches complexes sont retrouvées, sans ouverture dépassant les segments source contrôlés. L’inventaire paginé atteint 12 624 ouvertures inventées sur un objet ciblé. Ces chiffres décrivent les cas comparés ; ils ne dénombrent pas toutes les portes physiques de Marseille et ne certifient pas l’accès de chaque bâtiment sur le terrain.

Les résultats historiques ci-dessous concernent leurs programmes identifiés et restent conservés séparément.

### Livraison architecturale du 24 octobre : `48418cc`

Le prolongement architectural du 24 octobre est vérifié séparément dans [ARCHITECTURE_INTEGRATION.json](../verification/expansion/architecture/ARCHITECTURE_INTEGRATION.json), sur le programme de cette livraison, avec comparaison de cas IGN réels, régressions documentaires déclarées synthétiques et parcours dans le navigateur. La couverture vectorielle, le relief et le littoral acquis précédemment restent inchangés.

| Méthode sur le programme du 24 octobre | Contrôles réussis |
|---|---:|
| Modèles de production, outils et fixtures documentaires explicitement synthétiques | 877 |
| Quinze suites de contrats hérités, adaptées et exécutées dans une copie isolée | 434 |
| Parcours communal natif : mer, secteurs, étages, reprise, réserve finie et retour | 77 |
| Nouveau parcours natif : douze associations réelles, façade courbe, pièces closes, déplacement, reprise | 101 |
| Sorties identiques d’une reconstruction indépendante | 3 |

Ces **1 492 contrôles** portent sur le HTML `72a6230345abd1bfb889896f5923f3c66962148fb70f5d941fd2e58b59a8e817`. Les méthodes restent distinctes et leurs assertions peuvent couvrir les mêmes mécanismes. Les placements de caméra, chargements de secteurs et pauses de simulation sont déclarés ; ces essais ne représentent pas une visite humaine exhaustive de Marseille.

La [comparaison des données réelles](../verification/expansion/architecture/coverage-final/SUMMARY.md) retrouve une porte compatible et rendue sur **188 des 191 contours courts ciblés**, avec trois résidus conservateurs expliqués ; 183 reçoivent des fenêtres. Elle vérifie aussi les 27 faux rejets d’arrondi et la pagination complète de quatre grandes emprises, jusqu’à 12 588 ouvertures inventées sur un objet. Ces résultats ciblés ne dénombrent pas toutes les portes physiques de la commune. Le [plan de contrôle](../verification/expansion/architecture/native/ACTUAL_LAYOUT_AUDIT.svg) montre les coordonnées réellement exportées d’un intérieur natif, en distinguant son contour source de ses pièces inventées.

Aucune exception JavaScript ni requête de partition locale échouée n’est relevée dans les parcours finaux. Les sondages externes Supabase refusés par le réseau cloud et les tentatives de test antérieures restent consignés séparément. Les rapports ne transforment pas ces observations en relevés architecturaux. Les plafonds de rendu et les omissions d’aménagement restent ceux décrits ci-dessus.

### Première livraison communale : `cac50f3`

Les preuves de la première livraison communale sont regroupées dans [le bilan de validation communal](../verification/expansion/city/CITY_INTEGRATION.json). Il distingue les tests de logique, les bancs synthétiques hérités, les parcours Chromium utilisant les vrais fichiers HTTP et la restauration dans une destination vierge. Les aides de diagnostic pour placer le personnage, figer la simulation ou choisir un secteur sont déclarées ; elles ne remplacent pas une exploration humaine exhaustive de la commune. Les captures du jeu y sont distinctes des cartes d’audit de données.

| Méthode sur le programme livré | Contrôles réussis |
|---|---:|
| Modèles de production, physique, outils et fixtures déclarées | 744 |
| Contrats hérités, bancs contrôlés ; scripts reproduits depuis l’adaptateur du dépôt | 434 |
| Parcours communal natif : mer, Vieux-Port, Estaque, façades, étages, reprise et butin | 76 |
| Parcours natif de campagne, continuité, voyages et sauvegarde | 84 |
| Intégration native des sources détaillées conservées d’Aubagne | 26 |
| Restauration réelle dans un dossier vierge et serveur Python standard indépendant | 28 |
| Régression routière native ciblée, avec ses contrôles de modèle distinctement déclarés | 22 |
| Reconstruction indépendante : trois sorties identiques octet pour octet | 3 |

Ces rapports historiques visent le HTML `36205a8fbb8045445e666f6c2435e9ef25880a3d2088b1a8febf72f65e4132aa`. Les différentes catégories ne sont pas des parcours équivalents et leurs contrôles peuvent couvrir les mêmes mécanismes. Les observations de réseau optionnel refusé et d’audits annulés restent conservées dans les rapports ; aucune exception JavaScript ni requête géographique installée échouée n’a été relevée dans les parcours natifs concernés. La cadence Chromium en rendu logiciel sur le cloud ne constitue pas un engagement de performances sur ordinateur.

Les relevés BD TOPO indiquent couramment une précision XY de 2,5 à 5 m. Les dates et qualités varient selon l’objet. Les formes de toit, détails de rue et ornements absents ne deviennent pas connus par génération procédurale. Le résultat étend l’ensemble du territoire demandé et son architecture jouable à l’échelle métrique ; il ne certifie pas une reproduction visuelle et documentaire intégrale de chaque bâtiment réel.

Les rapports antérieurs d’Aubagne et de v0.50 restent historiques, avec leurs propres empreintes de programme. Ils ne valident pas automatiquement cette extension.

Sources : **IGN, Géoplateforme — Licence Ouverte 2.0**, avec les attributions du pack historique conservées.
