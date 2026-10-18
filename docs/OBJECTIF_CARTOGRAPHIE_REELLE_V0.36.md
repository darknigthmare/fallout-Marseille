# FALLOUT : MISTRAL — Objectif cartographie réelle v0.36+

## Priorité verrouillée

La reconstruction géographique réelle Marseille–Aubagne–La Ciotat et du périmètre associé devient le chantier prioritaire. Aucun nouveau mode, arc narratif ou système secondaire ne doit passer devant cette fondation tant que la carte n'est pas installée, jouable, mesurée et auditée.

## Emprise complète actuelle

Huit macro-régions sont déjà définies dans le projet : Marseille, Huveaune, Garlaban, Calanques, La Ciotat, Frioul, Étoile et Sainte-Baume.

Le plan calculé depuis la v0.35 représente :

- 367 tuiles vectorielles de base au zoom 14 ;
- 5 517 tuiles cadastrales au zoom 16 ;
- 5 884 tuiles vectorielles au total ;
- relief à construire séparément depuis une source altimétrique officielle.

## État réel du moteur

Déjà présent :

- projection géographique et repère métrique ;
- import MVT vérifié ;
- empreintes cadastrales avec cours intérieures ;
- routes et voies ferrées ;
- eau, landuse et landcover ;
- import de grilles de relief ;
- cache local et cycle de streaming ;
- propriété des entités par tuile ;
- suppression des doublons ;
- audits de tuiles et sources ;
- scripts de préchargement reprenables.

Encore manquant ou incomplet :

- acquisition effective du pack complet ;
- relief réel complet sur les huit macro-régions ;
- validation des raccords de routes entre tuiles ;
- fusion des bâtiments coupés par les limites de tuiles ;
- fondations adaptées aux pentes ;
- hauteurs de bâtiments enrichies et signalement des estimations ;
- littoral et surfaces marines validés ;
- couverture végétale, parcs et forêts auditée ;
- ponts, tunnels et étagements contrôlés ;
- LOD géométriques mesurés ;
- budget mémoire et temps de chargement par anneau ;
- raccord physique des intérieurs existants aux vraies portes ;
- suppression définitive des anciens extérieurs procéduraux de secours ;
- QA visuelle commune par commune.

## Sources prévues

- Cadastre Etalab pour les empreintes de bâtiments et limites utiles ;
- OpenStreetMap pour les routes, sentiers, voies ferrées, hydrographie et usages du sol ;
- IGN / Géoplateforme pour la topographie et l'altimétrie ;
- orthophotographie uniquement comme référence de contrôle et non comme texture distribuée par défaut.

Chaque source devra avoir une provenance, un millésime, une licence, une empreinte SHA-256 et une attribution visible dans le jeu.

## Pipeline cible

1. Télécharger et vérifier les données brutes.
2. Découper l'emprise exacte du jeu.
3. Reprojeter dans le repère métrique du moteur.
4. Construire le terrain et les tuiles de streaming.
5. Importer routes, eau, végétation et bâtiments.
6. Fusionner les raccords aux frontières des tuiles.
7. Construire trois niveaux de LOD au minimum.
8. Relier portes réelles et intérieurs instanciés.
9. Mesurer mémoire, temps de chargement et densité.
10. Comparer chaque secteur aux données sources.

## Critères d'acceptation

La carte ne sera pas considérée comme livrée tant que :

- les routes principales sont continues ;
- le littoral est correct ;
- les bâtiments sont aux bonnes positions ;
- le nombre de bâtiments est comparable aux données sources ;
- les grandes forêts, parcs, cours d'eau et voies ferrées sont présents ;
- le relief correspond aux altitudes sources ;
- aucun quartier procédural de secours n'est présenté comme réel ;
- les changements de tuile ne provoquent ni trou ni téléportation ;
- les intérieurs sont accessibles par des passages cohérents ;
- les attributions et licences sont incluses ;
- un rapport visuel et statistique couvre toute l'emprise.

## Première livraison cartographique attendue

La prochaine version dédiée doit fournir :

- le manifeste complet de la zone ;
- l'installateur ou importeur des données ;
- un pack réel vérifié ou une procédure reproductible pour le construire ;
- streaming et LOD fonctionnels ;
- une traversée réelle Aubagne → Marseille et Aubagne → La Ciotat ;
- un rapport de couverture montrant ce qui est présent, absent ou estimé.
