# Territoire et exploration : état de l’implémentation

**Bilan historique de la livraison `bb122d0`.** L’extension communale suivante, ses façades et ses intérieurs sont décrits dans [Marseille entière](MARSEILLE_ENTIERE.md), avec un [bilan de validation distinct](../verification/expansion/city/CITY_INTEGRATION.json). Les chiffres et tests ci-dessous concernent l’acquisition précédente d’Aubagne.

Les changements prolongent le jeu existant et ses sauvegardes. Le pack géographique livré reste la base, enrichie par des **sources IGN réellement acquises autour d’Aubagne** : 1 404 objets bâtiment, 472 tronçons de route et deux grilles de relief détaillées. Cette acquisition locale ne certifie pas une reproduction exhaustive de Marseille « 1:1 », ni l’achèvement de tout le contenu d’un jeu Fallout.

## Géométrie et relief

| Élément | Comportement implémenté | Limite explicite |
|---|---|---|
| Emprises | Import GeoJSON en WGS84 ou Lambert-93, identifiants stables, polygones multiples et cours intérieures préservés. Les sources supplémentaires sont vérifiées avant publication. | La qualité et la date du relevé restent celles de sa source. Un contour ne contient pas les détails des façades. |
| Bâtiments | Lecture des hauteurs et unités renseignées, socles décalés, altitudes absolues de sol/toit et métadonnées de provenance. Un bâtiment sans altitude utilisable est omis et comptabilisé. | Les hauteurs absentes restent estimées selon les règles du moteur et sont identifiées comme telles. Aucun intérieur réel n’est déduit d’une emprise cadastrale. |
| Toitures | Pour les formes prises en charge, à deux pans ou à un pan, explicitement cotées et orientées, rayons, projectiles et lignes de vue utilisent les triangles du toit et des murs. Les corps n’entrent plus en collision avec l’air au-dessus d’un pan incliné. Les surfaces accessibles permettent marche, accroupissement et atterrissage, avec les limites de pas et de pente. | La BD TOPO acquise ne fournit pas la forme de chaque toit. Une forme inconnue, non prise en charge ou dépourvue des dimensions nécessaires conserve une enveloppe estimée. Aucun intérieur réel ni détail de façade n’est déduit de cette collision extérieure. |
| Sol | NoData conservées, interpolation refusée lorsque ses points nécessaires manquent, choix documenté du relevé disponible le plus fin, altitudes négatives préservées. Le secteur acquis dispose de points RGE ALTI au pas demandé de 2 m et d’un extrait MNT LiDAR HD issu de pixels natifs de 50 cm. | Hors de ces emprises, les grilles de base ont toujours leur espacement d’origine, d’environ 48 à 162 m. Le pas d’une grille ne garantit pas son exactitude XY ou Z. |
| Relief importé | Maillage des nœuds de la grille importée près du joueur, découpe du maillage lointain et raccord des frontières. | Un voisinage fin est borné à 262 144 sommets. Le relief plus lointain conserve un LOD de 32 m. Les conversions GeoTIFF signalent explicitement leur rééchantillonnage. |
| Surfaces du sol | Les anciens aplats de landcover, landuse et park sont découpés sur le périmètre du relief fin et de son raccord ; leurs couleurs sont reportées sur les triangles du MNT. | Les couleurs sont échantillonnées au centre des triangles. Les anneaux source restent intacts ; ce traitement ne constitue pas une orthophoto ni une mesure supplémentaire. |
| Routes | Largeurs renseignées et coordonnées XYZ source conservées ; pour les routes IGN explicitement au sol sans cote verticale de structure, le ruban affiché est dérivé au contact du MNT utilisé par la physique, avec provenance distincte. Les largeurs et surfaces déduites restent déclarées. | Le maillage au sol ne reproduit pas les Z bruts de l’axe. Un axe routier ne fournit pas les trottoirs, marquages, glissières ou détails de chaussée absents de la source. |
| Ponts | Surface de marche issue des triangles d’un tablier explicitement coté ; limite de marche, passage inférieur, sauts, atterrissages et chute après déchargement traités. | La source définit une surface sans épaisseur. Aucune dalle, rambarde ou structure porteuse absente du relevé n’est inventée. |
| Rendu | Regroupement des géométries opaques compatibles avec couleurs par sommet, invalidation du cache et libération des buffers lors du streaming. | Les objets transparents et les pièces éclairées de près restent séparés. Les performances matérielles restent à mesurer sur la machine du joueur. |

Le maillage du sol conserve le décalage visuel hérité de −0,06 m pour séparer les couches rendues. Les hauteurs utilisées par la banque de terrain et la physique restent celles des mesures. Ce décalage de rendu ne constitue pas un nouveau relevé.

Les XYZ d’un bâtiment restent conservés dans les données de source. Leur seule présence ne permet pas de décider qu’ils représentent le sol ou le toit : les altitudes du volume utilisent des attributs dont la sémantique est explicite.

## Fonctionnalités jouables ajoutées

**STAT → BIVOUAC** permet de fabriquer un kit avec trois ferrailles et un tissu, de le déployer près du personnage sur un emplacement stable et libre, puis de le replier et réutiliser. Le camp possède ses objets et une interaction dans le monde. Le repos et les préparations consomment leurs fournitures ; les blessures et radiations restent traitées par les systèmes de soins existants.

**DATA → ENTRAIDE** relie l’exploration aux relais habités découverts. Les livraisons exigent un habitant accessible à proximité, consomment les fournitures et améliorent la réputation associée. Chaque besoin n’est récompensé qu’une fois par relais. Le kit, le camp et les reçus sont migrés avec les sauvegardes. Si l’écriture échoue, temps, objets et récompenses sont restaurés.

Les manettes à disposition standard disposent du déplacement, du regard, du tir, des interactions, du V.A.T.S., du Pip-Boy et de la navigation des menus. Les zones mortes, la sensibilité et l’aide sont accessibles dans les options. Les contrôles automatisés simulent l’API Gamepad ; ils ne remplacent pas une vérification avec un périphérique physique.

Les systèmes existants de combat, compagnons, équipement, fabrication, survie, factions, campagne et sauvegarde sont conservés. Des modèles et animations finaux, du doublage, une validation humaine de toutes les branches et un équilibrage complet restent des travaux de contenu distincts ; ils ne sont pas présentés comme terminés.

## Acquisition et intégration des sources publiques

Les services IGN ont répondu aux requêtes HTTPS réelles et les acquisitions suivantes ont été importées. La [documentation des sources](SOURCES_GEOGRAPHIQUES_PUBLIQUES.md) conserve les services, la définition des attributs et la provenance ; la [preuve LiDAR](../implementation/real-sources/IGN_LIDARHD_MNT_AUBAGNE.json) identifie les octets et la conversion reçus.

| Source effectivement acquise | Contenu intégré | Emprise et portée |
|---|---|---|
| BD TOPO IGN, bâtiments | **1 404 objets bâtiment** avec identifiants, anneaux intérieurs et attributs de sol, toit et précision disponibles | Acquisition demandée sur `[43.293, 5.565, 43.300, 5.576]`, dans l’ordre sud, ouest, nord, est. Les objets intersectants sont conservés entiers et peuvent dépasser ce rectangle. |
| BD TOPO IGN, routes | **472 tronçons de route** avec géométrie et attributs source | Même emprise demandée ; un axe ne décrit pas tous les trottoirs, bordures ou équipements de la voie. |
| RGE ALTI IGN | **174 777 altitudes**, grille de **447 × 391 nœuds**, au pas demandé d’environ **2 m**, sans NoData dans cet extrait | `[43.293, 5.565, 43.300, 5.576]`. Il s’agit de points interrogés auprès de la ressource altimétrique, pas d’une certification de résolution native ou de précision absolue à 2 m. |
| MNT LiDAR HD IGN | **145 396 altitudes**, grille de **326 × 446 nœuds**, sans NoData dans cet extrait | `[43.2956, 5.5698, 43.2976, 5.5718]`. L’export GeoTIFF source possède des pixels natifs de **0,50 × 0,50 m** ; la grille du jeu est reprojetée vers des nœuds WGS84 par échantillonnage **au plus proche (`nearest`)**, explicitement déclaré. |

Les services ont été consultés le 23 octobre 2026. La dalle LiDAR porte sa propre chronologie : mission `21LHD7PQ`, acquisition du 26 juin 2021 et édition du 14 mars 2025. Le référentiel vertical est conservé dans chaque grille, notamment NGF-IGN69. Un nombre de décimales ou un pas de 50 cm ne vaut pas une garantie de précision absolue à 50 cm.

Les précisions planimétriques et altimétriques BD TOPO varient selon les objets et restent attachées à leurs attributs. Certaines hauteurs ou largeurs sont calculées ou estimées par le fournisseur. Une altitude de toit, une hauteur à la gouttière et un niveau routier ordinal ne sont pas interchangeables. Ces données améliorent ce secteur précis ; elles ne représentent pas toute Marseille, ses façades, ses toitures détaillées ou ses intérieurs.

Le conditionnement reproductible emploie `tools/world_source_bundle.py` et un reçu sous `data/map_pack/enrichment_archives/manifest.json`. Il vérifie le ZIP, chaque fichier et le schéma des sources avant restauration. Au lancement normal, le serveur appelle cette restauration **hors réseau** lorsqu’une archive est fournie ; un import utilisateur déjà valide est conservé et un import invalide n’est pas remplacé silencieusement. L’archive fournie et sa restauration sur une destination vierge ont été vérifiées : tous les octets correspondent au lot actif, le second lancement conserve les imports valides et un fichier corrompu est refusé.

```bash
# Vérifier les couches actuellement annoncées.
python3 tools/acquire_public_world.py layers

# Plan sans réseau du secteur RGE ALTI acquis autour d’Aubagne.
python3 tools/acquire_public_world.py terrain --region geo_huveaune \
  --bbox 43.293,5.565,43.300,5.576 --spacing 2 --dry-run
```

Les acquisitions effectives emploient des requêtes bornées, des contrôles de coordonnées, des pages complètes et une publication validée. Les sources successives se fusionnent sans effacer les autres couches. L’[import local](IMPORT_SOURCES_REELLES.md) décrit GeoJSON, ASCII et GeoTIFF, ainsi que les projections, licences, empreintes et remplacements explicites.

## Validation de la livraison

Le [bilan actuel](../verification/expansion/real_sources/REAL_SOURCE_INTEGRATION.json) est construit seulement après vérification des rapports, des octets installés, du reçu ZIP et du SHA du programme. Le HTML servi et le HTML autonome ont le même SHA-256 : `8fa283b9d27e58299ab3c291a180084d8d5760716b6afc84c498f03831d19a16`. La reconstruction dans un répertoire neuf reproduit exactement les trois sorties, avec syntaxe JavaScript validée.

| Groupe exécuté | Résultat | Périmètre |
|---|---:|---|
| Logique et outils | 397 réussis | Géométrie, cache, rendu, physique, transactions, acquisition, conversion et installation ; fixtures isolées |
| Contrats hérités | 434 réussis | 15 suites sur leurs bancs contrôlés, mêmes assertions ; exécution séquentielle |
| Parcours natif | 84 réussis | HTTP et stockage natifs, campagne, atelier, rues, cour, voyages et Continuer ; aides de progression et de positionnement déclarées |
| Sources IGN réelles | 26 réussis | Octets installés et SHA, hauteurs/largeurs/XYZ, deux grilles, absence des anciens aplats, cache entre deux ancres |
| Sources synthétiques | 16 réussis | Sources temporaires explicitement synthétiques, moteur et HTTP réels |
| Bivouac et entraide | 19 réussis | Cartes et stockage réels ; personnage financé et réceptionnaire préparés par un adaptateur déclaré |
| Manette | 33 réussis | UI, clavier et stockage réels ; API Gamepad explicitement simulée |
| Panneau des sources | 22 réussis | Premier inventaire HTTP réel, puis scénarios de présentation/erreur contrôlés ; service worker désactivé pour ces interceptions |
| Rendu WebGL | 18 réussis | Composant natif isolé : positions, matériaux, pixels et trous NoData |
| Surfaces de pont | 8 réussis | Physique de production avec géométrie contrôlée dans Chromium |
| Toitures cotées | 14 réussis | Construction, rayons et physique de production avec fixtures dans Chromium |
| Restauration hors réseau | 11 réussis | Archive réelle fournie, répertoire vide, comparaison de tous les octets et HTTP ; corruption refusée |

Les essais sur le programme complet sont associés au SHA ci-dessus. Les composants isolés et la restauration de fichiers portent leur propre périmètre ; ils ne certifient pas à eux seuls tout le HTML. Les rapports minimaux sont conservés à côté du bilan JSON, et les preuves complètes avec captures sous `/workspace/.cloud-setup/fallout-marseille/implementation/current/`.

L’inspection visuelle et l’audit de triangles confirment que les anciens aplats ne masquent plus le MNT ni son raccord. Les couleurs sont prélevées au centre des triangles, à partir des anneaux des polygones existants et de leurs trous ; ce traitement de couleur ne modifie pas les altitudes. Les absences de mesure restent sans triangle et ne sont plus recouvertes par un ancien aplat. Le cache fin contient au plus deux patches, sur un budget estimé de 64 Mio, distinct du cache de relief de base. Les petits extraits qui tiennent dans le budget de sommets et une emprise de 512 m restent identiques entre les ancres proches.

Le préflight de réutilisation du LiDAR a observé deux hits, aucune éviction et 145 396 nœuds conservés. Les durées d’environ 1,58 s et 1,44 s ont été mesurées avec le rendu continu mis en pause pour isoler la préparation ; elles ne sont pas une promesse de temps de chargement ou de fréquence d’images sur la machine du joueur.

La cadence native mesurée sur cette machine avec SwiftShader est de 700 ms à la médiane et 1116.6 ms au p95, sur 5 intervalles. C’est du rendu logiciel en Chromium headless, pas une mesure sur carte graphique physique. Les performances du jeu restent à vérifier sur le matériel cible.

Le parcours natif emploie les actions de diagnostic existantes pour progresser dans l’histoire et placer la caméra. Les données géographiques HTTP, collisions et sauvegardes restent réelles ; il ne s’agit pas d’une campagne humaine intégralement jouée sans assistance. Les fixtures temporaires ne sont jamais publiées comme des relevés réels. Les tests de manette ne remplacent pas une vérification de périphérique physique.

Le [bilan historique](../verification/expansion/IMPLEMENTATION_SUMMARY.json), associé au HTML `8f4619bc…22d5aaa`, reste conservé. Il précède cette acquisition IGN et ne certifie pas le nouvel exécutable. Les autres essais intermédiaires restent identifiés par leur propre SHA. La pause de la fixture héritée d’annulation est de 1,5 s pour rendre le bouton actionnable sous rendu logiciel ; les assertions de phase, annulation et restauration restent exécutées.
