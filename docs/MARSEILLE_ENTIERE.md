# Marseille : couverture communale et architecture jouable

Le territoire supplémentaire couvre la commune officielle **13055, Marseille, îles comprises**. Les bâtiments, routes, relief et littoral proviennent de données IGN réellement téléchargées. Les façades et intérieurs ajoutent une interprétation jouable stable, à l’échelle métrique, dans les emprises disponibles. Les détails inventés sont distingués des annotations documentées.

Cette poursuite ajoute des routes adaptées au relief natif, des profils de menuiseries et des portes intérieures physiques ; les jeux de données acquis restent identiques. Le [bilan courant](../verification/expansion/wasteland/WASTELAND_INTEGRATION.json) identifie le HTML `ed6e4103b23a45c413fef182862a93accb72ec25c6e1d8b101251822bfd5c670`, **2 887 contrôles**, **62 captures réelles** et **405 empreintes de production**. Les modèles, contrats contrôlés, comparaisons d’octets/HTTP, parcours assistés et entrées simulées restent distingués. Cette somme ne dénombre pas des parties équivalentes. Les tentatives interrompues, échouées et visant un ancien programme sont conservées séparément, sans être comptées comme réussites du programme courant.

## Données livrées

| Ensemble | Contenu et portée |
|---|---|
| Limite communale | Objet administratif IGN de 38 320 sommets ; enveloppe `[43.1696313, 5.22875102, 43.39105653, 5.53254336]`, dans l’ordre sud, ouest, nord, est. |
| Bâtiments et routes | **291 001 identifiants d’objets bâtiment** et **55 449 identifiants de tronçons routiers** distincts, issus de 77 rectangles de requête couvrant le polygone communal, subdivisés en **290 partitions** pour le chargement. |
| Relief central natif ajouté | **12 km²**, douze dalles officielles et **48 morceaux Float32 de 0,50 m**, en Lambert-93/NGF-IGN69, sur un rectangle central. Les centres et altitudes restent sur le treillis natif. |
| Relief communal conservé | Grille de fond au pas demandé de **25 m**, complétée par **25 partitions au pas demandé de 10 m** couvrant toute l’enveloppe. Les points communs aux frontières sont conservés et comparés. |
| Littoral | Mer obtenue à partir de BD CARTO « Eau libre » et de **148 lignes BD TOPO « Plus hautes eaux »**, découpée en **118 tuiles**, avec **97 trous d’îles** préservés. Les découpes techniques ne simplifient pas le trait de côte. |
| Secteur détaillé historique d’Aubagne | Les 1 404 objets bâtiment, 472 routes et deux relevés locaux plus fins déjà acquis restent disponibles, avec leur provenance distincte. |

Les objets WFS sont conservés entiers. Ces totaux incluent les objets de bordure et quelques retours conservateurs de l’index spatial du fournisseur ; ils ne dénombrent ni des adresses, ni des immeubles physiques tous strictement situés dans Marseille. La couverture signifie que toutes les partitions de requête prévues sur le territoire officiel ont été terminées et vérifiées. Elle ne certifie pas que la base IGN recense chaque construction existante.

Les coordonnées et attributs de chaque partition ont été comparés aux réponses HTTPS originales, empreintes comprises. Le [rejeu géométrique exact](../implementation/city-sources/EXACT_SOURCE_GEOMETRY_REPLAY.json) précise les rares omissions d’altitude explicitement documentées. Les [requêtes et leur provenance](../implementation/city-sources/IGN_MARSEILLE_ACQUISITION.json) et les [qualités des attributs](../implementation/city-sources/IGN_MARSEILLE_SOURCE_QUALITY.json) sont conservées séparément.

## Relief, rues et mer

Le nouveau [lot LiDAR HD central](RELIEF_PRECIS.md) couvre les bornes Lambert-93 Est 892 000–895 000 m et Nord 6 245 000–6 249 000 m, autour du Vieux-Port, du Panier, de Saint-Charles, de Notre-Dame-de-la-Garde et de Longchamp. Douze GeoTIFF officiels fournissent 48 millions de cellules natives ; la découpe en 48 morceaux conserve les centres et altitudes Float32, avec des halos partagés. Les six ZIP ajoutent **157 896 379 octets (environ 150,58 Mio)** et l’extraction **192 328 140 octets (environ 183,42 Mio)**. Le lot reçu ne contient aucune cellule NoData ; les tests de trous utilisent des fixtures identifiées. Cette emprise de 12 km² ne constitue pas une couverture de toute Marseille au pas de 0,50 m.

Les anciennes grilles communales, conservées hors de ce support, proviennent d’interrogations réelles de la ressource `ign_rge_alti_wld`, en altitude NGF-IGN69. Le pas de 10 m décrit l’espacement demandé entre échantillons, pas une précision absolue de 10 m ni la résolution native du relevé. Le jeu utilise le relevé valable le plus fin disponible ; les relevés d’Aubagne de 2 m et l’extrait LiDAR HD issu de pixels natifs de 50 cm gardent donc leur intérêt local.

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

Les façades ajoutent des ouvertures, portes, volets et encadrements selon l’usage disponible. Les nouvelles [menuiseries et persiennes](FACADES_MENUISERIES.md) comportent panneaux, vitrages, vantaux de service, montants et lames inventés ; ils suivent les segments source, conservent le passage et n’ajoutent pas de collision. Les ensembles décoratifs sont alloués entiers dans leur budget ou explicitement différés. Les baies documentées ne reçoivent pas de menuiserie inventée à l’intérieur de leur enveloppe. Les usages explicites priment sur la nature générique « Industriel, agricole ou commercial ». Les contours courbes sont développés sur leurs segments originaux : les ouvertures suivent ces segments, sans redresser l’emprise. L’inventaire des baies se parcourt par pages sans plafond de 160 colonnes. Le rendu conserve ses budgets ; il réserve chaque ouverture entière avant ses ornements et signale les reports. Les candidats sur courts pans et contours quantifiés conservent leurs segments source ; la largeur utile du passage est contrôlée avant l’accès. Les ouvertures documentées gardent leurs cotes et leur arête d’origine. La porte dessinée correspond à l’entrée retenue par le contrôle d’accès. Sur un terrain en pente, une entrée peut desservir un niveau supérieur ; elle ne force pas tous les bâtiments au même rez-de-chaussée. Les espaces trop petits ou trop bas et les bâtiments sans altitude exploitable sont signalés dans les diagnostics plutôt que déclarés accessibles.

Une pression sur **Interagir** près d’une porte accessible ouvre l’intérieur du même bâtiment. Les pièces suivent son contour, ses concavités et ses cours. Les niveaux sont chargés à la demande et reliés par les choix du palier. Il s’agit de transitions entre niveaux, pas d’une simulation de montée à pied dans tous les escaliers. La sortie restitue le point extérieur enregistré. La mention sous la boussole indique la destination de l’objectif actif, et non la région de l’intérieur courant : « Pays d’Aubagne » peut donc rester affiché quand l’objectif est l’abri A-03, même pendant une visite à Marseille. Le nom du lieu courant reste affiché séparément.

Les nouvelles entrées utilisent le programme intérieur **layout 5**. Les [programmes par usage](INTERIEURS_USAGES.md) distinguent commerces, ateliers, bureaux, enseignement et santé à partir de valeurs explicites ou d’annotations clairement attribuées. Le nom d’un bâtiment ne suffit pas à lui attribuer une école ou un hôpital. Les principaux équipements sont prioritaires sur les réserves et archives ; un rayonnage de réserve ne remplace plus le rayonnage de vente public. Les intérieurs inventés peuvent comporter des pièces réellement closes, avec des cloisons, une ouverture de porte de 1,20 m et une circulation conservée. Sanitaires, chambres, cuisines, bureaux, réserves, salles de soin ou vestiaires dépendent de l’usage et de la place disponible. Le reste de l’emprise demeure un volume ouvert explicitement décrit. Les pièces et les meubles suivent l’orientation du bâtiment, avec des collisions correspondantes. Aux dix-huit types existants s’ajoutent **six équipements** : caisse, table scolaire double, tableau, photocopieur, armoire à outils et paravent de soins. Lits, cuisines, sanitaires, rangements, sièges et équipements de travail restent disponibles selon le programme. Les contenus restent fictifs. Dans les résidentiels inventés de moins de 55 m² par niveau, le programme peut employer un lit simple de 0,95 × 2,05 m et un WC séparé de 0,60 × 0,85 m. Ce sont des choix métriques de création ; les modèles visibles et leurs collisions utilisent ces mêmes dimensions. Un niveau documenté ne reçoit pas ces substitutions de programme.

Le calcul est borné à 10 pièces, 32 meubles, 4 096 cellules d’échantillonnage et 180 essais de circulation par niveau. Le programme introduit par le layout 4 étend aux nouveaux programmes les sondes auparavant réservées aux petites habitations : jusqu’à 256 points de contrôle près des bords source. Quand ce contrôle détecte qu’une cloison isolerait un recoin praticable, la pièce proposée est écartée et le volume reste ouvert. Les volumes très grands, complexes, trop petits ou dont la circulation initiale n’est pas prouvée par cette grille peuvent conserver des espaces ouverts et des fonctions non placées. L’inspection expose les omissions, les surfaces closes et ouvertes et le budget utilisé. Ce contrôle borné ne certifie pas l’accessibilité de chaque point arbitraire ni un plan réel complet. Les visites sauvegardées des programmes **1, 2, 3 et 4** sont reprises avec leurs cloisons, meubles, accès et signatures antérieurs, y compris pour les plans documentés. Le layout 5 s’applique aux nouvelles entrées et ajoute des portes coulissantes aux pièces compatibles, sans modifier les anciens plans. Les champs d’origine de l’usage, d’omissions et de quantités d’équipement restent inspectables ; un programme amputé ne peut pas annoncer tous ses équipements placés. Les contenants ont un inventaire fini, conservé dans les sauvegardes et après **Continuer**.

Les annotations documentaires peuvent fournir des ouvertures, dimensions ou plans précis, avec source et attribution. Le moteur conserve les parties ainsi renseignées et complète les autres de façon cohérente. La liaison exige la géométrie source exacte, le volume métrique et l’ordre des arêtes ; une annotation ne se déplace pas silencieusement après réordonnancement d’un contour. Le nouvel atlas facultatif et son outil de validation sont décrits dans [l’installation des annotations](ARCHITECTURE_DOCUMENTEE.md). Les plans enregistrés dans une sauvegarde persistent après reprise, sortie et réentrée, avec quotas et retour à l’état précédent si l’écriture échoue. **Aucun plan coté de façade ou d’intérieur n’a été acquis dans la recherche publique effectuée ici.** Le [catalogue d’architecture](CATALOGUE_ARCHITECTURE_MARSEILLE.md) expose les références trouvées et les limites d’accès. Les données géographiques ne documentent pas automatiquement la disposition réelle des fenêtres et des pièces. Douze associations de bâtiments à deux sites IGN sont installées : onze volumes religieux du site Notre-Dame de la Garde et un bâtiment du Centre de Conservation et de Ressources du Mucem. Elles décrivent une appartenance de site et ne constituent pas douze relevés architecturaux.

## Chargement et installation

Le serveur normal restaure l’archive communale livrée, sans acquisition réseau, dans `data/map_pack/city/`. Il prépare aussi les six ZIP natifs de `data/map_pack/precision_archives/` vers `data/map_pack/precise/`, avec contrôle des tailles et empreintes. Les anciens index, grilles et archives restent disponibles ; les fichiers natifs extraits sont exclus de Git. Chaque fichier possède une taille et une empreinte vérifiées ; les imports utilisateur déjà valides sont conservés. Les fichiers corrompus provoquent un diagnostic explicite. La validation initiale de l’atlas représente plusieurs centaines de mégaoctets à lire et peut prendre plus d’une minute avant l’ouverture du serveur.

```bash
python3 tools/serve_game.py
python3 tools/city_sources.py audit
```

Les positions fictives sauvegardées des sites sont revérifiées sur les sources chargées avant une réapparition : altitude utilisable, eau et solides. Les coordonnées sûres sont conservées avec la hauteur courante ; aucune hauteur n’est fabriquée. Cette revalidation ne déplace pas les acteurs déjà actifs et ne renouvelle pas leur butin.

Le panneau des cartes affiche les totaux municipaux issus de l’audit du serveur. Il distingue l’ensemble installé du voisinage actuellement rendu. Le chargement de la ville conserve des caches bornés : sources vectorielles 64 Mio/24 entrées, relief 48 Mio/8 entrées, eau 8 Mio/16 entrées et planification de façades 8 Mio/64 entrées et plans intérieurs inventés 1 Mio/4 entrées. Les nouvelles fenêtres de terrain remplacent les précédentes ; les reliefs fins ne s’accumulent pas dans la banque active pendant la marche. Le terrain natif ajoute un cache de 48 Mio/douze entrées et un cache de maillage de 48 Mio/une entrée, avec un voisinage préparé borné. Ces budgets estiment les ressources conservées et ne représentent pas la mémoire totale du navigateur ni la mémoire GPU.

Les détails de façade ont une portée et un budget variables selon la qualité graphique. Toute la ville est disponible par déplacement et chargement du voisinage ; ses centaines de milliers d’objets ne sont pas dessinés simultanément. La campagne, ses scènes historiques, le Pip-Boy, les combats, le bivouac, l’entraide et les sauvegardes précédentes sont conservés.

## Validation et fidélité

Le [bilan courant](../verification/expansion/wasteland/WASTELAND_INTEGRATION.json) identifie le HTML `ed6e4103b23a45c413fef182862a93accb72ec25c6e1d8b101251822bfd5c670`, **2 887 contrôles**, **62 captures réelles** et **405 empreintes de production**. Les modèles, contrats contrôlés, comparaisons d’octets/HTTP, parcours assistés et entrées simulées restent distingués. Cette somme ne dénombre pas des parties équivalentes. Les tentatives interrompues, échouées et visant un ancien programme sont conservées séparément, sans être comptées comme réussites du programme courant.

| Méthode | Contrôles réussis |
| --- | ---: |
| Modèles et outils | 1 401 |
| Sorties identiques de reconstruction | 3 |
| HTTP isolé de distribution | 3 |
| Contrats hérités contrôlés | 434 |
| Terrain et routes natifs | 91 |
| Architecture et menuiseries natives | 151 |
| Intérieurs et portes natifs | 70 |
| Bestiaire natif | 125 |
| Dossiers natifs des factions | 213 |
| Grenades natives | 62 |
| Continuité lore, armure et collections | 206 |
| Consommables et soin natifs | 74 |
| DOM avec API Gamepad simulée | 54 |
| **Somme descriptive** | **2 887** |

La commune conserve ses 290 partitions, 291 001 identifiants d’objets bâtiment, 55 449 tronçons routiers et 118 partitions d’eau. Le relief natif de 0,50 m reste limité aux 12 km² centraux ; les autres grilles et les relevés précédents restent disponibles ailleurs. Les douze associations documentaires à deux sites ne constituent pas des relevés de façades ou de pièces.

La reproduction intégrale 1:1 de chaque façade et intérieur de Marseille, l’art final, les voix, l’équilibrage complet, les performances sur matériels variés et une visite humaine exhaustive restent ouverts. Le matériel de manette physique n’est pas certifié par une API simulée. Les programmes inventés et leurs omissions restent inspectables.
