# Marseille : couverture communale et architecture jouable

Le territoire supplémentaire couvre la commune officielle **13055, Marseille, îles comprises**. Les bâtiments, routes, relief et littoral proviennent de données IGN réellement téléchargées. Les façades et intérieurs ajoutent une interprétation jouable stable, à l’échelle métrique, dans les emprises disponibles. Les détails inventés sont distingués des annotations documentées.

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

La mer est déterminée par les polygones et le littoral source. Une altitude zéro ou la seule position hors commune ne suffisent pas à classer un point comme de l’eau. La marche est bloquée sur la mer, avec les exceptions des supports effectivement mesurés, des scènes historiques et des mécanismes de bateau existants. La baignade n’est pas implémentée. Le niveau de rendu nominal de l’eau à zéro ne représente pas la marée instantanée.

## Façades et intérieurs

Les volumes conservent les contours, cours intérieures, hauteurs et altitudes exploitables. Le nombre IGN `nombre_d_etages` comprend le rez-de-chaussée. Les identifiants stables maintiennent la même architecture lors d’un nouveau chargement ; les différentes composantes d’un même objet restent distinctes.

Les façades ajoutent des ouvertures, portes, volets et encadrements selon l’usage disponible. La porte dessinée correspond à l’entrée retenue par le contrôle d’accès. Sur un terrain en pente, une entrée peut desservir un niveau supérieur ; elle ne force pas tous les bâtiments au même rez-de-chaussée. Les espaces trop petits ou trop bas et les bâtiments sans altitude exploitable sont signalés dans les diagnostics plutôt que déclarés accessibles.

Une pression sur **Interagir** près d’une porte accessible ouvre l’intérieur du même bâtiment. Les pièces suivent son contour, ses concavités et ses cours. Les niveaux sont chargés à la demande et reliés par les choix du palier. Il s’agit de transitions entre niveaux, pas d’une simulation de montée à pied dans tous les escaliers. La sortie restitue le point extérieur enregistré.

Le mobilier dépend de l’usage : lit, cuisine, coin repas, salon, sanitaires et rangement lorsque l’espace le permet ; comptoirs et rayonnages pour le commerce ; postes de travail et stockage pour l’industrie ; équipements adaptés aux usages de bureau ou de soin. Dix-huit modèles simples possèdent leurs propres volumes de collision. Le budget est borné à 32 meubles par niveau ; les zones fonctionnelles sont des aménagements **partiels inventés**, pas des plans complets certifiés. Les passages sont contrôlés sur les géométries concaves et meublées. Les contenants ont un inventaire fini, conservé dans les sauvegardes et après **Continuer**.

Les annotations documentaires peuvent fournir des ouvertures, dimensions ou plans précis, avec source et attribution. Le moteur conserve les parties ainsi renseignées et complète les autres de façon cohérente. **Aucun plan coté de façade ou d’intérieur n’a été acquis dans la recherche publique effectuée ici.** Le [catalogue d’architecture](CATALOGUE_ARCHITECTURE_MARSEILLE.md) expose les références trouvées et les limites d’accès. Les données géographiques ne documentent pas automatiquement la disposition réelle des fenêtres et des pièces.

## Chargement et installation

Le serveur normal restaure l’archive communale livrée, sans acquisition réseau, dans `data/map_pack/city/`. Chaque fichier possède une taille et une empreinte vérifiées ; les imports utilisateur déjà valides sont conservés. Les fichiers corrompus provoquent un diagnostic explicite. La validation initiale de l’atlas représente plusieurs centaines de mégaoctets à lire et peut prendre plus d’une minute avant l’ouverture du serveur.

```bash
python3 tools/serve_game.py
python3 tools/city_sources.py audit
```

Le panneau des cartes affiche les totaux municipaux issus de l’audit du serveur. Il distingue l’ensemble installé du voisinage actuellement rendu. Le chargement de la ville conserve des caches bornés : sources vectorielles 64 Mio/24 entrées, relief 48 Mio/8 entrées, eau 8 Mio/16 entrées et planification de façades 8 Mio/64 entrées. Les nouvelles fenêtres de terrain remplacent les précédentes ; les reliefs fins ne s’accumulent pas dans la banque active pendant la marche. Ces budgets ne représentent pas la mémoire totale du navigateur.

Les détails de façade ont une portée et un budget variables selon la qualité graphique. Toute la ville est disponible par déplacement et chargement du voisinage ; ses centaines de milliers d’objets ne sont pas dessinés simultanément. La campagne, ses scènes historiques, le Pip-Boy, les combats, le bivouac, l’entraide et les sauvegardes précédentes sont conservés.

## Validation et fidélité

Les preuves de cette extension sont regroupées dans [le bilan de validation communal](../verification/expansion/city/CITY_INTEGRATION.json). Il distingue les tests de logique, les bancs synthétiques hérités, les parcours Chromium utilisant les vrais fichiers HTTP et la restauration dans une destination vierge. Les aides de diagnostic pour placer le personnage, figer la simulation ou choisir un secteur sont déclarées ; elles ne remplacent pas une exploration humaine exhaustive de la commune. Les captures du jeu y sont distinctes des cartes d’audit de données.

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

Les rapports visent le HTML `36205a8fbb8045445e666f6c2435e9ef25880a3d2088b1a8febf72f65e4132aa`. Les différentes catégories ne sont pas des parcours équivalents et leurs contrôles peuvent couvrir les mêmes mécanismes. Les observations de réseau optionnel refusé et d’audits annulés restent conservées dans les rapports ; aucune exception JavaScript ni requête géographique installée échouée n’a été relevée dans les parcours natifs concernés. La cadence Chromium en rendu logiciel sur le cloud ne constitue pas un engagement de performances sur ordinateur.

Les relevés BD TOPO indiquent couramment une précision XY de 2,5 à 5 m. Les dates et qualités varient selon l’objet. Les formes de toit, détails de rue et ornements absents ne deviennent pas connus par génération procédurale. Le résultat étend l’ensemble du territoire demandé et son architecture jouable à l’échelle métrique ; il ne certifie pas une reproduction visuelle et documentaire intégrale de chaque bâtiment réel.

Les rapports antérieurs d’Aubagne et de v0.50 restent historiques, avec leurs propres empreintes de programme. Ils ne valident pas automatiquement cette extension.

Sources : **IGN, Géoplateforme — Licence Ouverte 2.0**, avec les attributions du pack historique conservées.
