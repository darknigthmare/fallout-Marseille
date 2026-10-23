# Importer des sources géographiques mesurées

Le jeu conserve son pack de base. Un enrichissement local peut ajouter des
empreintes de bâtiments, des routes et une grille de relief plus précise pour
une région existante. L'import ne fabrique aucune mesure et n'établit pas à lui
seul une fidélité intégrale du territoire : celle-ci dépend de l'emprise, de la
date, de la résolution et des attributs réellement fournis par la source.

## Formats et coordonnées

- **GeoJSON FeatureCollection** : bâtiments `Polygon`/`MultiPolygon`, routes
  `LineString`/`MultiLineString`. Les anneaux intérieurs, les composantes et les
  sommets sont conservés, sans simplification ni fermeture implicite. Les
  coordonnées sont `[longitude, latitude]`, éventuellement suivies d'une altitude
  dont le référentiel vertical doit être déclaré. Les données `EPSG:2154`
  (Lambert-93) peuvent être converties en WGS84 pendant l'import avec `--crs`.
- **Relief JSON** : `width`, `height`, `bbox: [sud, ouest, nord, est]`,
  `rowOrder: "north-to-south"`, `values` à plat. L'emprise va du centre du premier
  échantillon au centre du dernier. Les mesures absentes sont `null` ; les valeurs
  ne sont ni arrondies, ni interpolées par l'importateur.
- **ESRI ASCII Grid** : en `EPSG:4326`, avec `ncols`, `nrows`, `cellsize`,
  `NODATA_value` et une origine `xllcorner`/`yllcorner` ou
  `xllcenter`/`yllcenter`. Pour une origine au coin, l'import ajoute exactement un
  demi-pixel afin de retrouver le centre des échantillons. L'ordre des lignes
  nord-sud et les valeurs NoData sont conservés. Un raster projeté doit être
  converti explicitement avant cet import ; déclarer son EPSG ne transforme pas
  une grille projetée en grille régulière WGS84.
- **GeoTIFF** : le convertisseur `tools/convert_ign_dem.py` produit le JSON de
  relief compatible à partir d'un fichier fourni. Il conserve son reçu de
  conversion (SHA-256 du TIFF, CRS, transformée et résolution d'origine,
  rééchantillonnage, résolution de sortie). Ce reçu reste distinct du SHA-256 du
  JSON importé. Consulter l'aide du convertisseur pour ses dépendances et options.

Les propriétés d'origine sont conservées, notamment `hauteur`, `z_min_sol`,
`z_max_toit`, `height`, `min_height`, `roof:height`, `largeur_de_chaussee`,
`largeur_chaussee`, `width` et les attributs de pont/tunnel. Une valeur absente
reste absente ; une hauteur calculée à partir d'un nombre d'étages n'est pas une
mesure du toit.

Le schéma WFS BD TOPO contrôlé le 23 octobre 2026 expose en réalité les noms
`altitude_minimale_sol`, `altitude_maximale_sol`, `altitude_minimale_toit` et
`altitude_maximale_toit`, ainsi que `hauteur`. Ils restent conservés sous ces noms.
Certains objets signalent `methode_d_acquisition_altimetrique: "Pas de Z"` et
portent le marqueur `-1000` dans leurs coordonnées. Pour la seule ressource
`ign-bdtopo`, cette combinaison explicite retire la troisième coordonnée absente,
conserve exactement XY et inscrit le nombre de marqueurs retirés dans
`provenance.sourceGeometryZNoData`. Une altitude inconnue ne devient jamais un
sol à −1 000 m, et la même valeur sans ces métadonnées est refusée.

Pour convertir un MNT GeoTIFF réellement disponible localement :

```bash
python3 -m pip install -r requirements-geo.txt
python3 tools/convert_ign_dem.py /chemin/mnt.tif \
  --bbox 43.290,5.565,43.294,5.571 \
  --spacing 1 \
  --vertical-datum NGF-IGN69 \
  --output /tmp/relief-mesure.json
```

L'exemple demande des nœuds espacés d'au plus environ un mètre ; il ne transforme
pas une donnée native grossière en mesure d'une précision métrique. Le
convertisseur utilise le plus proche échantillon valide selon le masque du
fichier, conserve les NoData et borne la fenêtre lue à 16 777 216 cellules et la
sortie à 1 048 576 nœuds. Importer ensuite le JSON obtenu avec les métadonnées du
TIFF réel et `--terrain /tmp/relief-mesure.json --vertical-datum NGF-IGN69`.

## Import local

Exemple pour des fichiers effectivement acquis et dont les droits, la date et
le référentiel sont connus. Adapter les métadonnées à la source réelle :

```bash
python3 tools/import_world_sources.py \
  --region geo_huveaune \
  --geojson /chemin/batiments.geojson \
  --terrain /chemin/relief.json \
  --source "IGN BD TOPO et RGE ALTI" \
  --resource ign-releve-local \
  --license "Licence Ouverte 2.0" \
  --attribution "IGN" \
  --acquired-at 2026-10-23 \
  --vertical-datum "NGF-IGN69" \
  --source-url https://data.geopf.fr/
```

Il est préférable d'importer séparément des sources de provenances différentes.
Pour ajouter ensuite un fichier de routes sans perdre les bâtiments ni le
relief déjà installés :

```bash
python3 tools/import_world_sources.py \
  --region geo_huveaune \
  --geojson /chemin/routes.geojson \
  --source "IGN BD TOPO" \
  --resource ign-bdtopo \
  --license "Licence Ouverte 2.0" \
  --attribution "IGN" \
  --acquired-at 2026-10-23 \
  --vertical-datum "NGF-IGN69" \
  --source-url https://data.geopf.fr/ \
  --merge
```

Le chemin par défaut est `data/map_pack/enrichment/`. `--output` permet de
préparer le même dossier ailleurs avant de l'installer à cet emplacement. Les
URL de citation ne sont jamais contactées par cet outil ; l'acquisition réseau
est une opération distincte. Ne pas mettre de jeton, identifiant ou paramètre
secret dans une URL de provenance.

Les identifiants de régions sont ceux de
`data/map_pack/terrain/manifest_v039.json`. Chaque objet doit intersecter la
région sélectionnée. L'outil refuse les géométries invalides au lieu de les
réparer silencieusement. Il accepte au plus 20 000 objets, 250 000 sommets,
2 048 sommets par anneau, 1 048 576 échantillons par grille et 64 Mio par fichier.
Ces bornes doivent conduire à découper les sources en extraits utiles ; elles ne
justifient pas de supprimer des bâtiments ou de simplifier leurs emprises en
prétendant conserver une fidélité totale.

L'acquéreur `tools/acquire_public_world.py` contrôle les capacités et le schéma
WFS vivants, conserve les réponses HTTP exactes avec leurs requêtes et SHA-256,
puis termine toutes les pages avant d'importer. Son `acquisitionCoverage`
contient l'emprise réellement interrogée, `crs: "EPSG:4326"`, `complete: true`,
le nom de couche et le nombre total `returned`. L'import vérifie ces champs et
leur cohérence avec la collection, puis les conserve dans
`properties.provenance.coverage`. Cette emprise est distincte de l'enveloppe des
objets reçus : les coins interrogés sans route restent couverts par le reçu de
la requête. Elle atteste une extraction complète de la couche pour cette
requête, pas un relevé exhaustif de tous les objets présents physiquement.

## Réimport, fusion et conservation

- Réimporter exactement le même lot produit les mêmes octets et la même empreinte.
- `--merge` vérifie d'abord le chemin, la taille, le SHA-256, les géométries et les
  provenances du lot actif. Il conserve les grilles de relief et les objets
  absents du nouvel import. Un objet de même type et même
  identifiant est mis à jour une fois pour la même ressource source. Une collision
  entre fournisseurs différents est refusée pour éviter de remplacer un bâtiment
  par un objet sans rapport. Les provenances restent attachées à chaque objet ;
  un lot mixte énumère ses sources.
- Un relief plus étendu ou plus grossier n'efface pas une dalle fine. Les grilles
  de fournisseurs, emprises, dimensions ou référentiels différents coexistent.
  Seul un réimport de la même ressource, de la même emprise, des mêmes dimensions
  et du même référentiel actualise sa propre grille. Le lot est borné à 16 grilles,
  4 194 304 échantillons au total et 64 Mio ; la limite de 1 048 576 échantillons
  s'applique toujours à chaque grille.
- `--replace` remplace volontairement tout le lot actif de la région. Cette option
  est distincte de `--merge`. Les anciens fichiers restent sur disque.
- Une erreur de validation ou d'intégrité ne remplace pas l'index actif. Les
  fichiers de données sont adressés par leur contenu ; l'index n'est basculé
  qu'après l'écriture du lot valide. Le pack de base n'est jamais réécrit.
- La publication utilise un verrou de fichier POSIX sur le dossier de sortie.
  Deux imports simultanés sérialisent leur lecture/fusion/écriture afin de ne pas
  perdre la région ou les données ajoutées par l'autre. Le noyau libère le verrou
  si un processus s'arrête ; le fichier `.import.lock` peut rester vide sur disque
  sans signaler un import actif. Après 30 secondes d'attente, un second import
  rend une erreur explicite et peut être relancé. Cette commande de publication
  vise l'environnement Linux ; le jeu lui-même conserve ses lanceurs habituels.

## Contrat lu par le moteur

`data/map_pack/enrichment/index.json` :

```json
{
  "schemaVersion": 1,
  "crs": "EPSG:4326",
  "regions": {
    "geo_huveaune": {
      "path": "data/map_pack/enrichment/geo_huveaune-<sha16>.json",
      "sha256": "<sha256 du fichier complet>",
      "bytes": 1234,
      "bbox": [43.29, 5.5, 43.291, 5.502],
      "kinds": ["building", "road", "terrain"],
      "source": {"name": "…", "resource": "…", "license": "…", "attribution": "…", "acquiredAt": "2026-10-23"}
    }
  }
}
```

Le lot contient `schemaVersion`, `region`, `source`, `sources`, `features` et
éventuellement `terrain` ou `terrainTiles`. Les objets GeoJSON portent
`properties.kind: "building" | "road"`, `properties.sourceId` et
`properties.provenance`. Cette provenance conserve le SHA-256 du fichier
d'origine et son CRS. Sans identifiant fourni, l'identité est dérivée de la
géométrie d'origine et le préfixe `geometry:` la distingue d'un identifiant du
fournisseur.

Un lot à grille unique conserve `terrain` avec
`macro: "enrichment:geo_huveaune"`. Un lot contenant plusieurs grilles écrit
uniquement `terrainTiles: [...]`, chaque grille portant
`macro: "enrichment:geo_huveaune:<sha16>"`. Cet identifiant dérive du SHA-256 du
JSON canonique des champs `sourceResource`, `verticalDatum`, `width`, `height`,
`bbox`, `rowOrder` et `values` ; les dates de téléchargement ne changent pas
l'identité d'une même mesure. Les grilles portent leur emprise WGS84,
`sourceResource`, `verticalDatum` et `provenance`. Une éventuelle conversion TIFF
est conservée dans `terrain.provenance.conversion`. Le moteur vérifie l'empreinte
du lot avant de le publier dans une scène ; un lot absent ne devient pas une
preuve de précision supplémentaire.

## Acquisition réellement intégrée à Aubagne

Le 23 octobre 2026, les capacités, les schémas et les pages WFS ont effectivement
été reçus en HTTPS depuis la Géoplateforme, avec vérification TLS. L'extrait
`[43.293, 5.565, 43.300, 5.576]` contient **1 404 bâtiments et 472 tronçons de
route**, soit 1 876 objets. Le nombre reçu correspond au total annoncé par le
service ; les trois pages d'objets sont conservées avec leurs requêtes et
empreintes. Le [reçu public BD TOPO](../implementation/real-sources/IGN_BDTOPO_AUBAGNE.json)
décrit les schémas vivants, les décomptes et les contrôles d'intégrité.

L'enrichissement livré conserve simultanément :

- une grille RGE ALTI de **174 777 nœuds**, sur l'emprise ci-dessus, espacés
  d'environ deux mètres ;
- une grille issue du MNT LiDAR HD de **145 396 nœuds**, espacés d'environ
  0,5 m autour de `[43.2956, 5.5698, 43.2976, 5.5718]`, avec l'empreinte et la
  résolution de son GeoTIFF d'origine ;
- toutes les emprises, les anneaux intérieurs, les sommets de routes, les
  attributs mesurés disponibles et leur provenance individuelle.

L'ajout de la grille plus étendue a conservé la dalle fine. Les reçus de
couverture ont ensuite été ajoutés en réimportant les données déjà téléchargées,
sans nouvelle collecte : chaque géométrie et chaque propriété ont été comparées
aux pages HTTP dont la taille et le SHA-256 ont été revérifiés.

Les sources déclarent des précisions planimétriques de 2,5 à 5 m pour les
bâtiments et de 2,5 à 20 m pour les routes de cet extrait. Onze bâtiments et
51 routes signalent une altitude géométrique absente. La conservation fidèle de
ces objets ne constitue donc pas une certification de précision métrique partout,
ni une reconstruction des façades, de chaque forme de toiture ou des intérieurs.

Pour une nouvelle acquisition volontaire du même secteur, le client valide à
nouveau le schéma et toutes les pages avant la fusion :

```bash
python3 tools/acquire_public_world.py buildings \
  --region geo_huveaune --bbox 43.293,5.565,43.300,5.576
python3 tools/acquire_public_world.py roads \
  --region geo_huveaune --bbox 43.293,5.565,43.300,5.576
```

Les enrichissements locaux sont des sorties de données ignorées par Git ; leur
restauration demande le paquet préparé ou une acquisition/import explicite. Les
archives de base ne sont pas modifiées par ces commandes.

## Contrôles

```bash
python3 tests/expansion/importer_sources.py
```

Les tests couvrent notamment la conservation d'une cour intérieure et des
MultiPolygon, les attributs mesurés de hauteur et largeur, un point de contrôle
Lambert-93, l'origine des pixels ASCII, les NoData, le reçu de conversion TIFF,
la fusion relief/bâtiments/routes, les empreintes, la conservation d'un index en
cas de corruption et les codes de sortie de l'outil en ligne de commande.
