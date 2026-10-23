# Architecture de Marseille : sources et créations

Ce catalogue distingue les données géographiques réellement obtenues des détails d’architecture à créer. La recherche du 23 octobre 2026 a vérifié le catalogue data.gouv.fr et la documentation IGN. Elle n’est pas une recherche exhaustive de toutes les archives d’architectes, et ne prouve pas qu’aucun plan public n’existe.

Le [reçu de recherche](../implementation/city-sources/ARCHITECTURE_CATALOGUE.json) conserve les requêtes, réponses et empreintes, ainsi que les limites d’accès. **Aucun plan coté de façade ou d’intérieur n’a été acquis par cette recherche.** Aucun modèle architectural mesuré n’est donc déclaré installé sur cette seule base.

## Géométrie et attributs documentés

La couche [BD TOPO `BDTOPO_V3:batiment`](https://data.geopf.fr/wfs/ows?service=WFS&version=2.0.0&request=DescribeFeatureType&typenames=BDTOPO_V3%3Abatiment), en Licence Ouverte 2.0, fournit les emprises et des attributs de volume, d’usage, de niveaux et de matériaux. Les valeurs absentes restent inconnues. Les précisions XY/Z et les méthodes d’acquisition appartiennent à chaque objet ; ces données ne constituent pas des façades complètes ou des relevés de pièces.

Le [descriptif IGN 3.5, juillet 2026](https://data.geopf.fr/annexes/ressources/documentation/DC_BDTOPO_3-5.pdf), pages 69, 75 et 76, précise notamment :

- `nombre_d_etages` est le nombre total de niveaux **rez-de-chaussée compris**. Les sous-sols ne sont pas comptés. Il ne faut pas ajouter un niveau à cette valeur.
- `nombre_de_logements` peut être reporté uniquement sur le plus grand bâtiment lors d’un appariement de plusieurs bâtiments et locaux. Il ne fournit pas le nombre exact de portes ou de pièces de chaque emprise.
- `materiaux_des_murs` et `materiaux_de_la_toiture` sont des codes à deux caractères issus des fichiers fonciers. Sans table de correspondance vérifiée, un code numérique ne doit pas être transformé en un matériau prétendument documenté.
- `date_creation` et `date_modification` concernent l’objet de la base, pas sa construction. Une année de création de fiche n’établit pas un style architectural historique. `date_d_apparition` peut provenir de la date des locaux appariés lorsque ces dates sont homogènes.
- Une hauteur, même renseignée, ne donne ni la disposition des baies ni l’orientation des pièces. Les altitudes de toit peuvent être calculées à partir du modèle de surface ; elles ne constituent pas un relevé de chaque pente.

Les [tables MAJIC des murs](https://piece-jointe-carto.developpement-durable.gouv.fr/NAT004/DTerNP/html3/annexes/desc_pb40_pevprincipale_dmatgm.html) et [des toits](https://piece-jointe-carto.developpement-durable.gouv.fr/NAT004/DTerNP/html3/annexes/desc_pb40_pevprincipale_dmatto.html) sont liées par le PDF IGN. Leur lecture a été refusée par le proxy courant, avec une erreur de tunnel HTTP 403. Aucun contournement n’a été utilisé ; ce refus ne prouve pas que les tables sont indisponibles publiquement.

## Références municipales identifiées

Les métadonnées ci-dessous ont été lues dans l’API officielle data.gouv.fr. Elles annoncent la Licence Ouverte 2.0. Les fichiers sont hébergés sur `www.datasud.fr`, dont l’accès a été refusé par le proxy courant. Leur contenu détaillé n’a donc pas été audité ou importé ici.

| Référence vérifiée dans le catalogue | Contenu annoncé | Usage possible et limite |
|---|---|---|
| [Marseille — Bâtiments institutionnels](https://www.data.gouv.fr/datasets/marseille-batiments-institutionnels-1) · [CSV annoncé](https://www.datasud.fr/fr/dataset/datasets/1822/resource/2282/download/) | Coordonnées, informations et points de géolocalisation des bâtiments institutionnels | Identification et usage ; aucun plan coté annoncé. |
| [Marseille — Monuments historiques](https://www.data.gouv.fr/datasets/marseille-monuments-historiques-1) · [CSV annoncé](https://www.datasud.fr/fr/dataset/datasets/1867/resource/2327/download/) · [PDF annoncé](https://www.datasud.fr/fr/dataset/datasets/1867/resource/2328/download/) | Adresses, références Mérimée et points de géolocalisation | Le « plan des monuments » désigne une carte de localisation ; il ne doit pas être présenté comme un plan des pièces. |
| [Parcours 7 — des Danaïdes au Palais Longchamp](https://www.data.gouv.fr/datasets/marseille-parcours-culturels-7-des-danaides-au-palais-longchamp) · [GeoJSON annoncé](https://www.datasud.fr/fr/dataset/datasets/1993/resource/2474/download/) | Tracé culturel, informations sur les bâtiments et monuments, géolocalisation | Peut documenter un nom, une fonction ou une histoire ; ne démontre pas les dimensions des colonnades ou des salles. |
| [Parcours 8 — de Longchamp à l’Évêché](https://www.data.gouv.fr/datasets/marseille-parcours-culturels-8-de-longchamp-a-leveche) · [GeoJSON annoncé](https://www.datasud.fr/fr/dataset/datasets/2050/resource/2529/download/) | Tracé culturel et informations patrimoniales | Même distinction entre description et relevé métrique. |
| [Parcours 6 — de l’Hôtel Dieu à la Vieille Charité](https://www.data.gouv.fr/datasets/marseille-parcours-culturels-6-de-lhotel-dieu-a-la-vieille-charite) · [GeoJSON annoncé](https://www.datasud.fr/fr/dataset/datasets/1992/resource/2473/download/) | Tracé culturel et informations patrimoniales | Aucun plan coté de la cour, des galeries ou de la chapelle acquis. |

Les requêtes du reçu incluent notamment « Marseille plans architecture », « Marseille façades », « Mucem plan », « Bati3D » et « maquette numérique Marseille ». Aucun de leurs résultats n’a fourni ici un plan coté exploitable. Les recherches « Longchamp Marseille » et « Vieille Charité » ont identifié les parcours ci-dessus. Le catalogue peut évoluer ; les résultats ne constituent pas une affirmation sur toutes les ressources publiques hors de ce catalogue.

## Règles de reconstruction

L’échelle du jeu est métrique. Les emprises, cours, positions et hauteurs disponibles peuvent être conservées à cette échelle sans que chaque détail soit connu. Les différences de précision du relevé restent explicites.

Pour un élément documenté, les annotations doivent préciser le bâtiment concerné, les unités, le repère, les dimensions, la source, la date et le droit de réutilisation. Une photographie peut servir de référence visuelle si sa licence le permet ; sans cotation ni calibration, elle ne certifie pas une largeur ou une hauteur. Une annotation valide peut remplacer uniquement les éléments qu’elle décrit : un plan de rez-de-chaussée ne documente pas automatiquement tous les étages.

Les ouvertures, volets, balcons, cloisons, escaliers, mobilier et décors sans relevé approprié sont des **créations procédurales cohérentes**. Leur génération doit rester stable pour un même identifiant source, tenir dans le volume et les anneaux du bâtiment, préserver les cours, et assurer des circulations et sorties utilisables. Les types résidentiel, industriel, commercial, sportif ou religieux peuvent orienter le plan lorsque l’usage est renseigné ; ils ne donnent pas l’identité réelle d’une pièce.

Une façade ou un intérieur inventé peut respecter les mètres, les niveaux documentés et l’emprise réelle. Il ne constitue pas une reproduction vérifiée de la façade ou du plan réel. Cette distinction permet d’étendre le monde jouable sans présenter les créations comme de nouveaux relevés.
