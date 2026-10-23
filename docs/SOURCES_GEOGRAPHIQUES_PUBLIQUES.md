# Sources publiques pour Marseille et ses environs

Recherche effectuée le 23 octobre 2026 dans les dépôts et services officiels de l’IGN. Après application de la configuration réseau, une **vraie dalle MNT LiDAR HD de 2 000 × 2 000 pixels au pas de 0,50 m** a été acquise autour d’Aubagne. Un extrait reprojeté de **145 396 points**, sans NoData, a été intégré au jeu tout en conservant les objets vectoriels acquis séparément. La disponibilité native des autres secteurs de Marseille et La Ciotat reste à vérifier dalle par dalle. [Preuve d’acquisition](../implementation/real-sources/IGN_LIDARHD_MNT_AUBAGNE.json).

## Données utilisables

| Besoin | Source publique identifiée | Ce qu’elle apporte | Ce qu’elle ne garantit pas |
|---|---|---|---|
| Relief précis | **MNT LiDAR HD IGN** | Modèle du sol annoncé au pas de **50 cm**, dérivé de points sol/eau/virtuels classés. | La résolution de grille ne signifie pas une exactitude de 50 cm en toute position. La couverture, la date et la précision du lot restent à examiner. |
| Relief de référence | **RGE ALTI IGN** | Altitudes mesurées accessibles par l’API altimétrique et produits téléchargeables. Le jeu utilise déjà une grille échantillonnée de cette source. | Densifier une grille par interpolation ne recrée pas la résolution native de la source. |
| Bâtiments | **BD TOPO IGN**, couche WFS `BDTOPO_V3:batiment` | Objets vectoriels de bâtiments et attributs exposés par le schéma du service. Les hauteurs peuvent être utilisées lorsqu’elles sont renseignées et interprétées avec leur définition. | Une emprise avec une hauteur n’est pas un relevé complet des façades, toitures ou intérieurs. Une hauteur absente reste inconnue. |
| Routes et ouvrages | **BD TOPO IGN**, couche WFS `BDTOPO_V3:troncon_de_route` | Tracé et attributs du réseau routier ; géométrie et attributs doivent être conservés lors de l’import. | Un axe routier ne décrit pas automatiquement les bordures, trottoirs, marquages ou profils de ponts. |
| Toitures, végétation et sursol | **Nuages de points LiDAR HD**, **MNS** et **MNH** | Relevés 3D classés et modèles du sursol/hauteur permettant une reconstruction plus détaillée que les extrusions simples. | Le nuage ne constitue pas à lui seul un modèle de jeu texturé, topologiquement réparé et doté d’intérieurs. |

La documentation IGN du LiDAR HD annonce au moins **10 impulsions/m²**, et 5 au-dessus de 3 200 m. Il s’agit d’une caractéristique d’acquisition, pas d’un nombre garanti de points conservés sur chaque surface. Les produits dérivés MNT/MNS/MNH sont explicitement annoncés en **licence ouverte** dans l’actualité officielle de mars 2025. Conserver pour chaque lot le texte de licence et l’attribution fournis lors de son acquisition.

## Références confirmées

Les liens de catalogue suivants sont publiés par l’IGN. Ils désignent des produits ou interfaces, pas des fichiers de dalles dont le téléchargement aurait été vérifié ici :

- [MNT LiDAR HD — catalogue](https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_MNT-LIDAR-HD) et [téléchargement](https://cartes.gouv.fr/telechargement/IGNF_MNT-LIDAR-HD).
- [MNS LiDAR HD — téléchargement](https://cartes.gouv.fr/telechargement/IGNF_MNS-LIDAR-HD).
- [MNH LiDAR HD — téléchargement](https://cartes.gouv.fr/telechargement/IGNF_MNH-LIDAR-HD).
- [Nuages de points LiDAR HD — catalogue](https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_NUAGES-DE-POINTS-LIDAR-HD).
- [BD TOPO — catalogue](https://cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_BD-TOPO).
- [État de diffusion LiDAR indiqué par l’IGN](https://macarte.ign.fr/carte/mThSup/diffusionMNxLiDARHD).

La configuration officielle consultée énumère bien `BDTOPO_V3:batiment` et `BDTOPO_V3:troncon_de_route` en WFS. Elle énumère aussi des index de nuages de points sous les noms **singuliers** `IGNF_NUAGES-DE-POINTS-LIDAR-HD:bloc` et `IGNF_NUAGES-DE-POINTS-LIDAR-HD:dalle`. Certaines actualités utilisent des noms différents ou anciens : le client doit donc vérifier les identifiants actuels avec `GetCapabilities`, plutôt que supposer qu’un nom historique fonctionne toujours.

## Acquisition par les services publics

### Bâtiments et voirie : WFS

La documentation confirme le protocole **WFS 2.0.0** à cette adresse :

```text
https://data.geopf.fr/wfs/ows
```

Ordre des opérations :

1. `SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities` : vérifier les couches et projections disponibles.
2. `REQUEST=DescribeFeatureType&TYPENAMES=BDTOPO_V3:batiment` et la même requête pour `BDTOPO_V3:troncon_de_route` : lire les noms, types et définitions des attributs.
3. `REQUEST=GetFeature&RESULTTYPE=hits` sur une petite emprise : connaître le nombre d’objets attendus.
4. Extraire les objets en pages bornées et contrôler le total, les identifiants et la projection avant de publier le résultat local.

La documentation indique **30 requêtes/s** pour le service et son tutoriel QGIS indique une limite de **5 000 objets par requête**. Un client doit rester en dessous de ces limites et prendre en compte les limites effectivement annoncées par le service. Le paramétrage de l’ordre des axes doit être explicite : un BBOX en latitude/longitude inversée pourrait sélectionner un autre endroit sans produire une erreur HTTP.

La métadonnée CSW officielle de la BD TOPO a fourni le [descriptif de contenu 3.5, juillet 2026](https://data.geopf.fr/annexes/ressources/documentation/DC_BDTOPO_3-5.pdf), qui a été consulté :

- `hauteur` décrit la distance entre le point bas du sol et le point haut de la gouttière ; **0 signifie inconnu ou non significatif**. Ce champ ne décrit pas nécessairement le faîte du toit.
- Les noms PostgreSQL sont `altitude_minimale_sol`, `altitude_minimale_toit`, `altitude_maximale_toit` et `altitude_maximale_sol` ; leurs noms Shapefile comprennent `Z_MIN_SOL`, `Z_MIN_TOIT`, `Z_MAX_TOIT` et `Z_MAX_SOL`. Les valeurs de toit peuvent provenir de traitements statistiques du MNS : la valeur maximale est notamment un 9e décile, moins fiable pour les petits bâtiments ou constructions légères.
- `position_par_rapport_au_sol` est un **niveau ordinal**, pas une hauteur en mètres : 0 au sol, positif en sursol/sur pont, négatif souterrain/en tunnel. Une route sous un bâtiment peut rester au niveau 0. Ne pas transformer ce code en une élévation arbitraire.
- `largeur_de_chaussee` désigne la chaussée d’accotement à accotement et, en ville, de trottoir à trottoir. Cette largeur est indicative : elle peut être mesurée, estimée ou dérivée du nombre de voies.

Le schéma vivant doit toujours être contrôlé avec `DescribeFeatureType` avant acquisition. Une altitude absolue de toit ne doit pas être assimilée à une hauteur relative ; une largeur renseignée n’est pas une certification de mesure sur chaque rue.

### Objets vectoriels effectivement intégrés

L’extrait BD TOPO autour d’Aubagne, emprise `[43.293, 5.565, 43.300, 5.576]`, contient actuellement **1 404 objets bâtiment** et **472 tronçons de route**, soit **1 876 objets** après import. Le nombre a été contrôlé dans le bundle actif. Les emprises, anneaux intérieurs, attributs et identifiants source sont conservés ; ces nombres ne représentent pas des façades ou intérieurs reconstruits individuellement. Le descriptif de contenu IGN précise que certains attributs de hauteur ou de largeur sont calculés ou estimés : « attribut fourni par la source » ne signifie pas « mesure indépendante vérifiée sur place ».

### Altitudes : API IGN

Documentation confirmée :

```text
https://data.geopf.fr/altimetrie/resources
https://data.geopf.fr/altimetrie/resources/ign_rge_alti_wld
https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json
```

La méthode `POST` accepte un objet JSON où `lon` et `lat` sont des listes de coordonnées sous forme de texte séparées par `|`, et `resource` identifie la source demandée. `measures=true` permet de demander des informations sur la source et la précision. Les limites documentées sont **5 000 points par requête** et **5 requêtes/s par adresse IP**. Les valeurs sont arrondies à deux décimales ; cette présentation décimale n’est pas une garantie de précision centimétrique. Une absence de couverture renvoie notamment `-99999` et doit devenir une valeur manquante, jamais une altitude inventée.

Pour obtenir un relief de quelques mètres autour d’un point de jeu, une acquisition bornée peut employer cette API. Pour remplacer de larges secteurs par une grille de 0,5 ou 1 m, utiliser les dalles natives est plus adapté que des millions de requêtes ponctuelles.

### Dalles natives : catalogue Atom

L’API de téléchargement permet de découvrir les fichiers sans fabriquer de noms de versions ou de dates :

```text
https://data.geopf.fr/telechargement/capabilities
https://data.geopf.fr/telechargement/resource/{resourceName}
https://data.geopf.fr/telechargement/resource/{resourceName}/{subResourceName}
```

Le service emploie Atom. Ses réponses sont **paginées**, avec `page` à partir de 1, `limit` de 50 au maximum et un total `gpf_dl:totalentries`. Les filtres documentés incluent `polygon` (couples longitude,latitude séparés par `;`, en EPSG:4326), `zone` (par exemple `D013` pour les Bouches-du-Rhône), `crs`, `format` et les dates d’édition. La limite annoncée est **10 requêtes/s par IP**. Les noms exacts des ressources et les liens de fichiers doivent provenir des réponses du catalogue, puis être conservés dans la provenance.

La configuration IGN expose également des couches MNT/MNS LiDAR en WMS à `https://data.geopf.fr/wms-r/wms`, dont `IGNF_LIDAR-HD_MNT_ELEVATION.ELEVATIONGRIDCOVERAGE.LAMB93` et `.WGS84G`, avec les formats `image/geotiff` et `image/x-bil;bits=32`. Leur présence dans une configuration n’atteste pas une couverture locale actuelle. Une image d’ombrage `SHADOW` ne doit jamais être traitée comme une grille d’altitudes numériques.

## Acquisition native effectivement réalisée

Le catalogue Atom interrogé contient 116 ressources réparties sur trois pages ; le nom de produit `IGNF_MNT-LIDAR-HD` n’est pas directement une ressource de téléchargement Atom dans cette réponse. Le service WFS annonce cependant `IGNF_LIDAR-HD_METADONNEE:metadata`. Son objet réel `metadata.62849`, dont le polygone couvre le point d’Aubagne, fournit un lien `url_mnt` complet vers un export GeoTIFF numérique officiel. Ce lien a été utilisé tel que publié, sans fabriquer un chemin de dalle.

- Dalle : `LHD_FXX_0908_6248_MNT_O_0M50_LAMB93_IGN69.tif`.
- Mission : `21LHD7PQ` ; acquisition source du 26 juin 2021 ; édition du 14 mars 2025.
- Export téléchargé : 16 000 513 octets, une bande Float32, pixels de 0,50 × 0,50 m, NoData `-9999`.
- Référentiels déclarés par la métadonnée : Lambert-93 / IGN69.
- SHA-256 reçu : `51f2638620a03f04891910f5e07e3e897e37c97e158d7320d631f97d0323435c`. Aucun checksum fournisseur distinct n’était fourni ; cette empreinte identifie les octets reçus sous TLS.
- Extrait de jeu : emprise `[43.2956, 5.5698, 43.2976, 5.5718]`, grille WGS84 de 326 × 446 points, échantillonnage au plus proche, 145 396 altitudes et zéro absence. Le rééchantillonnage est explicitement enregistré dans la provenance ; ce n’est pas une revendication de précision absolue à 50 cm.

L’en-tête WKT de cet export WMS n’est pas reconnu automatiquement comme EPSG:2154 par GDAL : il décrit la projection Lambert-93 avec un datum générique. L’option explicite `--source-crs EPSG:2154` utilise le CRS publié dans la requête et la métadonnée IGN ; le WKT original et ce choix sont conservés dans le reçu. Aucun CRS n’est deviné à partir des coordonnées.

L’outil reproductible réalise la découverte, vérifie la couverture, télécharge le GeoTIFF sous un nom contenant son empreinte et produit la grille :

```bash
python -m pip install -r requirements-geo.txt
python tools/acquire_ign_dem.py \
  --bbox 43.2956,5.5698,43.2976,5.5718 --spacing 0.5 \
  --output /workspace/.cloud-setup/fallout-marseille/results/native-dem
```

Le répertoire de sortie contient `ACQUISITION.json` avec les URL publiques intégrales, métadonnées de mission, emprises, en-tête natif, empreinte et chemin de la grille. L’import final emploie `tools/import_world_sources.py --terrain <grille> --merge` et les déclarations de source correspondantes. Une nouvelle acquisition peut recevoir une édition ultérieure du service ; il faut alors comparer les preuves et revalider le résultat.

## Intégration dans le jeu

Le pack actuel reste la base de repli. L’[import des sources locales](IMPORT_SOURCES_REELLES.md) prépare des enrichissements explicites et vérifiés sans remplacer les archives d’origine. Un lot précis doit conserver :

- son emprise et sa projection d’origine ;
- sa résolution ou son espacement réel, son ordre de lignes et ses valeurs NoData ;
- le référentiel vertical des altitudes ;
- ses identifiants d’objets et les anneaux intérieurs des emprises ;
- sa source, sa date d’acquisition, sa licence, son attribution et son empreinte SHA-256.

Importer d’abord une emprise bornée autour d’Aubagne permet de contrôler l’alignement au sol, les cours intérieures, les pentes, les niveaux routiers et les passages sous ouvrages avant d’étendre aux huit secteurs. Une grille densifiée par calcul ou un toit estimé doit rester indiqué comme tel dans le bilan de fidélité. Ces sources rapprochent la géométrie du terrain réel ; elles ne suffisent pas à certifier une reproduction exhaustive « 1:1 » de toutes les rues, façades et pièces.

## État réseau de cette recherche

Les dépôts officiels GitHub ont été accessibles avec vérification TLS. Les premiers appels directs ont été refusés par le proxy. Après application de la spécification réseau 3, les services Atom, WFS et WMS de `data.geopf.fr` ont répondu et l’acquisition native ci-dessus a réussi sans relâcher TLS ni contourner le proxy. `geoservices.ign.fr/bdtopo` redirige vers `cartes.gouv.fr`, ce qui demande une destination supplémentaire pour consulter cette interface. La dalle et les métadonnées utilisées ici proviennent directement de `data.geopf.fr` et n’ont pas nécessité ce détour.

## Sources consultées et versions

- [Configuration officielle des couches IGN](https://github.com/IGNF/geoportal-configuration/blob/f7818bf37f125b8cb955abc20fa238f5fad6a62e/entreeCarto.json), commit `f7818bf37f125b8cb955abc20fa238f5fad6a62e`.
- [Documentation IGN : MNT LiDAR HD au pas de 50 cm](https://github.com/IGNF/cartes.gouv.fr-documentation/blob/4f70f5e70e4d7eca8f902aaa8010d43683db1346/content/fr/partenaires/ign/observations-regulieres-territoire/relief/mnt-lidar-hd.md).
- [Documentation IGN : calcul altimétrique et limites](https://github.com/IGNF/cartes.gouv.fr-documentation/blob/4f70f5e70e4d7eca8f902aaa8010d43683db1346/content/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/calcul-altimetrique.md).
- [Documentation IGN : WFS](https://github.com/IGNF/cartes.gouv.fr-documentation/blob/4f70f5e70e4d7eca8f902aaa8010d43683db1346/content/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/wfs.md) et [tutoriel QGIS](https://github.com/IGNF/cartes.gouv.fr-documentation/blob/4f70f5e70e4d7eca8f902aaa8010d43683db1346/content/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/tutoriels-api/qgis.md).
- [Documentation IGN : API de téléchargement Atom](https://github.com/IGNF/cartes.gouv.fr-documentation/blob/4f70f5e70e4d7eca8f902aaa8010d43683db1346/content/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/telechargement.md).
- [Annonce officielle des produits LiDAR et de leur licence ouverte](https://github.com/IGNF/cartes.gouv.fr-documentation/blob/4f70f5e70e4d7eca8f902aaa8010d43683db1346/content/fr/partenaires/ign/generalites-ign/actualites/2025-03-lidarhd-et-produits-derives.md).
- [Documentation IGN : bâtiments BD TOPO et mise à jour des emprises](https://github.com/IGNF/cartes.gouv.fr-documentation/blob/4f70f5e70e4d7eca8f902aaa8010d43683db1346/content/fr/partenaires/ign/generalites-ign/actualites/2026-09-bd-topo-rnb.md).

Les références épinglées prouvent ce qui a été lu ; elles ne remplacent pas un contrôle de disponibilité et de contenu des services à la date d’un téléchargement.
