# Relief mesuré de l’Estaque et de Saint-Antoine

Deux fenêtres du nord de Marseille reçoivent le MNT LiDAR HD de l’IGN au lieu de la grille communale de 10 m. Elles sont hors de l’ancienne emprise `geo_marseille`, dont la limite nord est 43,34° ; elles utilisent donc la véritable région `geo_marseille_commune` enregistrée par l’atlas communal.

| Quartier | Nœuds WGS84 : sud, ouest, nord, est | Grille | Nœuds valides |
| --- | --- | --- | ---: |
| Estaque | `[43.3624, 5.3130, 43.3652, 5.3168]` | 310 × 313 | 97 030 |
| Saint-Antoine | `[43.3690, 5.3570, 43.3720, 5.3610]` | 326 × 335 | 109 210 |

Ces **206 240 nœuds** proviennent de deux GeoTIFF officiels de 2 000 × 2 000 pixels Float32, au pas natif de 0,50 m, en Lambert-93 / NGF-IGN69. Les URL complètes sont celles du champ `url_mnt` des métadonnées WFS effectivement reçues, après consultation du catalogue Atom. Le relevé date de 2021, mission `21LHD7PQ`, édition du 14 mars 2025 ; le téléchargement du jeu date du 1er novembre 2026. Le proxy et la vérification HTTPS sont conservés.

Les données de jeu sont **reprojetées et rééchantillonnées au plus proche**, sur des nœuds WGS84 au pas demandé de **1 m**. L’espacement effectif figure dans les reçus. Aucune altitude n’est lissée ou ajustée ; aucun trou n’est comblé. Les deux extraits reçus ne contiennent aucun NoData. Les 12 km² de treillis central natif de 0,50 m conservent leur archive et leur propre contrat ; ils ne sont pas agrandis par ces fenêtres.

Le MNT décrit le sol. Il ne décrit ni les façades, ni les installations du port, ni les bâtiments des gares, ni les intérieurs. Ces deux rectangles ne reproduisent donc pas intégralement les quartiers. Les bâtiments et les routes proviennent des couches déjà présentes ; la résolution des nœuds ne certifie pas leur exactitude absolue ni une fidélité architecturale 1:1.

## Chargement et installation

Le chargeur communal prend désormais en compte ses imports locaux vérifiés avant d’ajouter la grille de base à une banque de terrain en préparation. Le rendu et la physique utilisent alors les nœuds les plus fins qui couvrent la position. La banque publiée n’est pas modifiée pendant la préparation ; une annulation et une empreinte incorrecte empêchent la publication. L’importeur hors ligne accepte les limites de l’atlas communal complet installé, sans élargir les anciennes régions.

```bash
python3 tools/world_source_bundle.py install
```

L’archive active `world-sources-3df84df4ae353420.zip` fait **5 410 454 octets**. Elle ajoute uniquement `geo_marseille_commune` aux lots Aubagne et sud de Marseille déjà distribués. Les fichiers et les descripteurs historiques des deux régions restent identiques. L’ancien ZIP reste conservé.

Dans une installation existante validée, une région absente est ajoutée. Une autre version de `geo_marseille_commune` importée par le joueur garde la priorité : elle n’est pas remplacée par les fenêtres fournies. Une corruption est refusée ; elle n’entraîne pas une réparation silencieuse. L’index est publié atomiquement après les fichiers immuables.

Les [reçus d’acquisition](../implementation/north-terrain/ACQUISITION.json) et le [reçu de mise à jour locale](../implementation/north-terrain/PACKAGE_AND_LOCAL_UPGRADE.json) identifient les sources et la distribution. Les TIFF originaux demeurent dans le cache externe. Le [contrôle hors ligne](../implementation/north-terrain/OFFLINE_DISTRIBUTION.json) vérifie le vrai nouveau ZIP, la mise à jour depuis le vrai ancien ZIP, l’identité des installations, la relance et la conservation d’un import utilisateur explicitement synthétique.

## Vérifications

Le [rejeu indépendant](../implementation/north-terrain/EXACT_SOURCE_REPLAY.json), utilisant `rasterio.sample` plutôt que la lecture par fenêtres du convertisseur, retrouve les **206 240 valeurs sélectionnées identiques** aux TIFF originaux, sans divergence. Ce contrôle atteste la conservation des cellules après le rééchantillonnage déclaré, sans constituer une mesure indépendante de leur précision dans le monde réel.

Le [pilote natif](../tests/expansion/north_terrain_native.py) charge le véritable HTML par HTTP, demande les deux secteurs, compare les nœuds physiques et les sommets des triangles rendus, puis revisite les anciens lots sud et Aubagne. Ses choix de secteurs et placements de caméra à partir des collisions et du sol réels sont des aides déclarées. Il ne remplace ni une visite humaine exhaustive ni un relevé d’architecture.

```bash
node tests/expansion/city_streaming.cjs
python3 -m unittest discover -s tests/expansion -p test_import_regions.py
python3 -m unittest discover -s tests/expansion -p test_world_source_bundle.py
```

Les contrats contrôlés comprennent le chargement des imports par la seule ressource de sol communal, le refus des octets altérés, l’annulation en cours de chargement, les limites nord effectivement installées et le refus de nœuds extérieurs. Leurs grilles et déclarations communales synthétiques sont distinctes des observations IGN ci-dessus.

Le [parcours natif courant](../verification/expansion/continuation_20261101/north/NORTH_TERRAIN_NATIVE.json), sur le HTML `98a78a1c…`, réussit **46 contrôles et deux captures**. Dix nœuds physiques, six sommets de triangles et les anciens lots sud/Aubagne sont contrôlés. Les images montrent un relief facetté et les volumes stylisés existants ; elles ne certifient pas la reproduction des gares, du port ou des façades.
