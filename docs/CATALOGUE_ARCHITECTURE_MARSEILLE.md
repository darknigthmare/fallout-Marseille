# Architecture de Marseille : sources et créations

Ce catalogue distingue les données géographiques réellement obtenues des détails d’architecture à créer. La recherche du 23 octobre 2026 a vérifié le catalogue data.gouv.fr et la documentation IGN ; son prolongement du 24 octobre est décrit ci-dessous. Ces recherches ne sont pas un inventaire exhaustif des archives d’architectes et ne prouvent pas qu’aucun plan public n’existe.

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

## Recherche complémentaire du 24 octobre 2026

Le [nouveau reçu](../implementation/architecture-continuation/ARCHITECTURE_RESEARCH_2026-10-24.json) conserve les URL, résultats, empreintes et limites de cette recherche distincte. Sur 14 requêtes ciblées supplémentaires à data.gouv.fr, quatre ont répondu sans résultat pour leurs termes exacts, sept ont échoué avec HTTP 503 et trois ont expiré. Une erreur ou une expiration ne constitue pas une preuve d’absence de données. Les recherches comprenaient notamment « Marseille modèle bâtiment », « Marseille relevé architecture », « Marseille plan intérieur », « Vieille Charité plan » et « Marseille construction BIM ».

L’ancienne adresse officielle `geoservices.ign.fr/bati3d` a redirigé vers une page générique d’exploration de cartes ; aucun modèle BATI3D n’a été acquis. Une recherche complémentaire « merimee » a renvoyé un jeu toulousain hors périmètre et les métadonnées photographiques nationales « Mémoire — illustration Mérimée et Palissy ». La licence ODbL annoncée pour ces métadonnées ne certifie pas le droit de réutiliser les photographies correspondantes. Aucun plan coté ou relevé de façade ou d’intérieur supplémentaire n’a été obtenu.

Cinq schémas WFS IGN ont été acquis et conservés : zones d’activité ou d’intérêt, constructions surfaciques, linéaires, ponctuelles et toponymie. Ils décrivent des objets géographiques et leurs attributs, sans fournir ici une disposition des ouvertures ou des pièces. Les trois requêtes de constructions filtrées sur les fragments de noms choisis ont répondu sans objet ; ce constat porte sur ces filtres, pas sur toutes les constructions de Marseille.

## Noms et usages de sites réellement acquis

Une requête de la couche IGN `BDTOPO_V3:zone_d_activite_ou_d_interet` a fourni **28 zones nommées**, avec catégorie, nature, commune, précision planimétrique et indicateur `fictif`. La [réponse GeoJSON originale](../implementation/architecture-continuation/IGN_SITES_3a46168b2b65e4f4.geojson), acquise le 24 octobre 2026, contient 28 objets annoncés et 28 retournés, sous Licence Ouverte 2.0, attribution IGN — Géoplateforme, BD TOPO. Son SHA-256 est `3a46168b2b65e4f4646959dc5049c327d16fc613a2153a1ba3cf0df3f9121734`.

Le [catalogue des associations géométriques](../implementation/architecture-continuation/IGN_SITE_CONTEXT_CATALOGUE.json) conserve les identifiants des 28 zones et de leurs 106 candidats bâtiments, les attributs source, les recouvrements et chaque motif de rejet. La requête porte sur les fragments « charit », « longchamp », « garde », « mucem », « radieuse », « hôtel de ville », « pharo » et « major » dans l’enveloppe de Marseille ; elle ne couvre pas tous les sites de la commune. L’enveloppe inclut aussi des communes voisines : la « Cour d’Honneur de l’Hôtel de Ville » retournée appartient à La Penne-sur-Huveaune et ne doit pas être assimilée à l’hôtel de ville de Marseille.

Dans cette couche, `fictif` qualifie **la géométrie de la zone source**, pas l’existence du lieu. Huit des 28 géométries portent ce drapeau. La précision de 2,5 à 20 m est celle déclarée pour la zone IGN ; elle ne devient pas la précision d’une façade, d’un intérieur ou du bâtiment associé.

| Nom de la zone source | Précision de la zone (m) | Géométrie fictive | Candidats par recouvrement | Liens contextuels stricts proposés |
|---|---:|:---:|---:|---:|
| Cathédrale de la Major | 20 | non | 5 | 0 |
| Chapelle et Hospice de la Vieille Charité | 20 | non | 1 | 0 |
| Ancienne Église de la Major | 20 | non | 1 | 0 |
| Notre-Dame de la Garde | 3 | non | 12 | 11 |
| Collège Longchamp | 2,5 | non | 9 | 0 |
| École Maternelle Longchamp | 3 | non | 7 | 0 |
| École Primaire Major Cathédrale | 2,5 | non | 10 | 0 |
| Collège Notre-Dame de la Major | 3 | non | 6 | 0 |
| Parc Longchamp | 5 | non | 17 | 0 |
| Cour d’Honneur de l’Hôtel de Ville — La Penne-sur-Huveaune | 20 | oui | 0 | 0 |
| Place de la Major | 20 | oui | 0 | 0 |
| État-Major du Bataillon de Marins-Pompiers de Marseille | 5 | non | 4 | 0 |
| École Primaire Pharo Catalans | 3 | non | 7 | 0 |
| École Maternelle le Pharo | 3 | non | 4 | 0 |
| École Maternelle Rose la Garde | 20 | oui | 1 | 0 |
| École Primaire Rose la Garde | 2,5 | non | 8 | 0 |
| École Primaire Notre-Dame de la Major | 3 | non | 5 | 0 |
| Hôtel de Ville Pavillon Daviel | 20 | non | 1 | 0 |
| Jardin du Pharo | 20 | oui | 0 | 0 |
| Mucem-Musée des Civilisations de l’Europe et de la Méditerranée | 5 | non | 1 | 0 |
| Palais du Pharo | 5 | non | 1 | 0 |
| Esplanade de la Major | 20 | oui | 0 | 0 |
| Palais de Longchamp | 20 | oui | 1 | 0 |
| EHPAD Résidence Longchamp | 5 | oui | 1 | 0 |
| Poste de Marseille-Longchamp | 5 | non | 1 | 0 |
| Pôle Emploi de Marseille le Pharo | 20 | non | 1 | 0 |
| Centre de Conservation et de Ressources du Mucem | 3 | non | 1 | 1 |
| Musée de Notre-Dame de la Garde | 20 | oui | 1 | 0 |

Les calculs utilisent des copies XY des géométries existantes, projetées de WGS84 vers Lambert-93 pour mesurer les surfaces et les distances. Les trous et composantes multiples des polygones sont conservés. Les copies d’un même bâtiment dans plusieurs tuiles sont dédupliquées par identifiant source. Un candidat exige une intersection d’au moins 0,01 m² ; ce seuil de calcul ne donne aucune précision de relevé supplémentaire. Les coordonnées originales de l’atlas ne sont pas modifiées.

Les **12 propositions strictes** exigent une zone non fictive d’une précision déclarée d’au plus 3 m, au moins 99 % de l’emprise du bâtiment dans cette zone, et un centroïde intérieur situé à une distance du bord supérieure à la précision déclarée. Il faut en plus soit un candidat unique couvrant au moins 90 % de la zone, soit un bâtiment que l’IGN qualifie déjà d’église à usage religieux dans une zone religieuse. Les autres candidats restent des recouvrements à examiner, même lorsque leurs emprises semblent coïncider.

Onze volumes IGN satisfont ces règles sur le site Notre-Dame de la Garde ; leur libellé proposé est « Bâtiment religieux du site Notre-Dame de la Garde ». Ils ne sont pas tous identifiés comme la basilique centrale. Un douzième lien concerne le « Bâtiment du Centre de Conservation et de Ressources du Mucem ». Le dernier volume candidat de Notre-Dame de la Garde a un centroïde à environ 1,28 m du bord de la zone, donc sous la marge exigée de 3 m : il est rejeté. Le bâtiment principal du Mucem, le Palais du Pharo et la Poste de Marseille-Longchamp ne passent pas ce filtre, leur zone annonçant une précision de 5 m. Les établissements scolaires comportent plusieurs candidats sans identité individuelle suffisamment établie par ce seul recouvrement.

Les douze liens stricts sont installés dans [l’atlas architectural local](../data/map_pack/architecture/index.json), avec la géométrie originale de chaque bâtiment et les éléments de calcul conservés.

Ces propositions associent un **contexte de site** à des identifiants de bâtiments existants. Elles n’ajoutent aucun `facadeDocument` ou `interiorDocument`, aucune mesure de baie et aucun plan de pièce. Les façades et intérieurs sans référence appropriée continuent donc à relever des créations décrites ci-dessous.

## Règles de reconstruction

L’échelle du jeu est métrique. Les emprises, cours, positions et hauteurs disponibles peuvent être conservées à cette échelle sans que chaque détail soit connu. Les différences de précision du relevé restent explicites.

Pour un élément documenté, les annotations doivent préciser le bâtiment concerné, les unités, le repère, les dimensions, la source, la date et le droit de réutilisation. Une photographie peut servir de référence visuelle si sa licence le permet ; sans cotation ni calibration, elle ne certifie pas une largeur ou une hauteur. Une annotation valide peut remplacer uniquement les éléments qu’elle décrit : un plan de rez-de-chaussée ne documente pas automatiquement tous les étages.

Les ouvertures, volets, balcons, cloisons, escaliers, mobilier et décors sans relevé approprié sont des **créations procédurales cohérentes**. Leur génération doit rester stable pour un même identifiant source, tenir dans le volume et les anneaux du bâtiment, préserver les cours, et assurer des circulations et sorties utilisables. Les types résidentiel, industriel, commercial, sportif ou religieux peuvent orienter le plan lorsque l’usage est renseigné ; ils ne donnent pas l’identité réelle d’une pièce.

Une façade ou un intérieur inventé peut respecter les mètres, les niveaux documentés et l’emprise réelle. Il ne constitue pas une reproduction vérifiée de la façade ou du plan réel. Cette distinction permet d’étendre le monde jouable sans présenter les créations comme de nouveaux relevés.

## Surfaces supérieures LiDAR acquises le 28 octobre 2026

Trois MNS LiDAR HD officiels au pas natif de 0,50 m ont été acquis depuis les URL `url_mns` des métadonnées IGN. Leurs surfaces ont été découpées dans les emprises existantes de cinq composantes de la zone de la Major et douze de Notre-Dame de la Garde. Le jeu peut appliquer seize de ces dix-sept surfaces ; une composante reste refusée parce que son bord MNS descend sous sa base IGN historique.

Les 82 363 triangles candidats décrivent les sommets observés de ces emprises en 2021, sans nouvelle baie ou pièce documentée. La découpe conserve les centres natifs et interpole uniquement les nouveaux sommets de bord sur leurs triangles source. Les coordonnées XY, identifiants et anciens attributs restent inchangés. Les détails de provenance, volumes, collision, omissions et limites sont décrits dans [Surfaces mesurées de la Major et de Notre-Dame de la Garde](SILHOUETTES_MNS.md), avec le [reçu d’acquisition](../implementation/landmark-surfaces/MNS_ACQUISITION.json). Ces MNS ne constituent ni un relevé complet de façade ni un plan d’intérieur.
