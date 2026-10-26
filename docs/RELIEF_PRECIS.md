# MNT LiDAR HD natif du centre de Marseille

Cette extension ajoute **12 km²**, depuis douze exports numériques officiels IGN, au pas natif de **0,50 m**. Elle couvre un rectangle Lambert-93 autour du Vieux-Port, du Panier, de Saint-Charles, de Notre-Dame-de-la-Garde et de Longchamp. Elle ne couvre pas toute la commune et ne certifie pas une précision absolue de 50 cm.

Les anciens index, grilles et archives restent inchangés. Le nouveau lot est dans `data/map_pack/precision_archives/`. Les fichiers de travail `data/map_pack/precise/` sont extraits et vérifiés au démarrage du serveur ; ils sont exclus de Git.

## Source et quantité

| Élément | Valeur déclarée et contrôlée |
|---|---|
| Produit | IGN, MNT LiDAR HD, mission `21LHD7PQ`, classement `IGN_AUTO_V5` |
| Acquisition des points | 26 juin au 17 octobre 2021 selon les métadonnées de mission |
| Édition du produit | 14 mars 2025 |
| Référentiels | Lambert-93, EPSG:2154 déclaré dans l’export ; altitudes NGF-IGN69 |
| Emprise native | Est 892 000 à 895 000 m ; Nord 6 245 000 à 6 249 000 m |
| Originaux reçus | Douze GeoTIFF, chacun 2 000 × 2 000 Float32, 16 000 513 octets |
| Pas et ordre | 0,50 m ; lignes du nord vers le sud ; origine aux centres des pixels |
| Cellules source | 48 000 000, sans rééchantillonnage des altitudes |
| Morceaux de jeu | 48 fenêtres Float32 little-endian, au plus 1 001 × 1 001 cellules |
| Comptage avec halos | 48 082 035 échantillons ; 82 035 répétitions de cellules partagées |
| NoData du lot reçu | **0** ; le marqueur publié est `-9999` et son traitement reste testé |
| Binaires extraits | 192 328 140 octets |
| Transport Git | Six ZIP, 157 896 379 octets au total ; le plus grand fait 26 781 912 octets |
| Licence et attribution | Licence Ouverte 2.0 ; IGN — LiDAR HD |

La découverte interroge réellement `IGNF_LIDAR-HD_METADONNEE:metadata` sur le WFS de `data.geopf.fr`. Chaque URL `url_mnt` est utilisée telle que publiée ; aucun chemin de dalle ou de date n’est fabriqué. Les reçus conservent les objets de métadonnées, URL publiques, WKT reçu, transformée, date de réception et SHA-256. Le SHA décrit les octets reçus sous HTTPS vérifié ; aucun checksum indépendant du fournisseur n’était fourni.

Le WKT du service n’est pas automatiquement reconnu comme EPSG:2154 par GDAL. Le CRS effectif provient du paramètre explicite `CRS=EPSG:2154` et de `systeme_planimetrique=LAMB93`. Ce choix et le WKT brut restent dans le reçu. Aucune conversion verticale n’est appliquée.

## Découpe et lecture

L’outil copie les cellules Float32 sur leur treillis Lambert-93 original. Une ligne et une colonne communes permettent l’interpolation entre morceaux, y compris entre deux GeoTIFF voisins. Seules les boîtes de recherche sont transformées en WGS84 ; les altitudes et les coordonnées de leurs centres restent natives.

La lecture du terrain emploie les quatre voisins natifs valides et indique cette interpolation dans son résultat. Un centre exact ne dépend pas de voisins de poids nul. Une absence fine à l’intérieur du support reste une absence ; elle n’est pas remplacée par une altitude grossière présentée comme fine. En dehors du véritable support natif, les anciennes sources continuent à fonctionner.

Le lot réellement reçu ne contient pas de cellule NoData. Les tests du marqueur et des triangles manquants utilisent des fixtures explicitement synthétiques ; aucun trou synthétique n’est injecté dans le parcours natif ni présenté comme une observation IGN.

## Rendu et budgets

Le jeu affiche les **vrais centres natifs**, à 0,50 m, dans un carré local de 255 m, avec au plus **261 121 sommets** et **520 200 triangles** avant répartition des couleurs. Les triangles touchant une absence ne sont pas émis. Un raccord rejoint le niveau de détail périphérique. Le décalage visuel historique de −0,06 m est conservé ; les hauteurs physiques restent les altitudes absolues de la source.

Au bord de l’atlas, le carré de rendu est recadré dans les bornes des centres réellement fournis. Le joueur et les échantillons ne sont pas déplacés. Le terrain grossier extérieur au support est conservé ; une fenêtre désirée ne peut pas supprimer une zone sans lui fournir de triangles. Les quatre bords et les coins sont couverts par les régressions.

Un plan ne demande que les morceaux intersectant une marge de 384 m autour de son ancrage : au plus neuf morceaux, soit environ 34,4 Mio de données natives actives. Le cache natif est limité à 48 Mio et douze entrées ; le cache du maillage à 48 Mio et une entrée. Ces limites estiment les ressources conservées. Elles ne mesurent pas tout le tas JavaScript, les tableaux temporaires, les banques transitoires, les autres sources ou la mémoire GPU. Les préparations restent séparées de la banque publiée et le laboratoire ne reçoit pas ces sources.

## Rubans routiers au contact du LiDAR

Les chaussées au sol BD TOPO étaient déjà distinctes de leur axe XYZ conservé : leur représentation visible suit le MNT utilisé par la physique, avec un décalage visuel de +0,085 m. Une triangulation longitudinale espacée d'environ douze mètres pouvait toutefois couper une bosse entre ses sommets. La nouvelle adaptation subdivise les triangles de ce seul ruban lorsqu'un sondage aux milieux des arêtes ou au centre s'écarte de la source native. L'empreinte XY, les largeurs, les coordonnées XYZ source, les reçus et les hauteurs physiques restent conservés. Les ponts, tunnels et chaussées à cote explicite ne passent pas par cette adaptation.

Le raffinement vise des sondages à 0,04 m d'écart et des arêtes au plus longues de 8 m, jusqu'à une limite de subdivision de 1 m et 2 048 divisions adaptatives par ruban. Les partitions d'arêtes sont ensuite propagées aux triangles voisins pour éviter les fissures. La limite de résolution et le budget sont signalés dans le reçu ; **0,04 m n'est pas une borne continue de précision**, ni une nouvelle mesure du terrain. Un sondage NoData fait subdiviser puis omettre le triangle concerné, sans altitude nulle inventée. Le lot réel reçu n'a aucune cellule NoData ; les cas manquants de cette règle restent des fixtures synthétiques déclarées.

La régression de l'objet réel `troncon_de_route.6003809`, au Vieux-Port, utilise les binaires LiDAR installés et la géométrie source attribuée déjà conservée. Le modèle en coordonnées Lambert-93 absolues passe de 14 à 126 triangles ; l'écart maximum sondé aux centres des triangles passe d'environ 0,2191 m à 0,04650 m. Le navigateur publie 134 triangles dans son repère local et sa chaîne de conversion inverse/projection : les subdivisions proches du seuil d'arête peuvent varier avec les arrondis. Il retrouve ces mêmes écarts et les quatre feuilles adaptatives limitées par le seuil de 1 m. Ces mesures portent sur cette route, pas toutes les voies de Marseille. Les routes extérieures au véritable support natif gardent leur représentation antérieure. Les indices et archives géographiques ne sont pas modifiés.

`node --test tests/expansion/native_road_surfaces.cjs` vérifie quinze contrats : conservation de l'emprise et du sens des faces, altitudes, bosses, distinction du grossier, partitions partagées, NoData, budgets, exclusion des supports documentés et véritable objet source. Le véritable empaqueteur GPU conserve tous les indices des rubans raffinés en morceaux d'au plus 54 000 sommets, sous la limite WebGL Uint16. Le diagnostic de scène `v055NativeRoadInfo` expose les comptes et les comparaisons sondées ; le pilote natif existant conserve ses contrôles de terrain et ajoute cette vérification routière.

## Reproduction hors ligne

Les GeoTIFF originaux et leurs reçus complets sont conservés dans le cache d’acquisition externe, hors Git. Les archives du projet contiennent les binaires nécessaires au jeu, leurs reçus et les échantillons de preuve attribués ; elles n’ajoutent pas un deuxième exemplaire des GeoTIFF complets.

```bash
python -m pip install -r requirements-geo.txt
python tools/acquire_precise_terrain.py --cache /chemin/cache-ign
python tools/acquire_precise_terrain.py --cache /chemin/cache-ign \
  --offline --root /chemin/reconstruction-independante
python tools/precise_terrain_sources.py --prepare
```

Le mode `--offline` ne consulte pas le réseau. Il refuse un original absent ou différent de son reçu. La reconstruction réalisée dans cette itération produit les six ZIP et le manifeste **strictement identiques**, depuis le cache reçu. Chaque ZIP reste inférieur à 64 Mio ; chaque membre décompressé est borné à 8 Mio et le total à 256 Mio. L’installation refuse les empreintes incorrectes, les chemins sortant du répertoire choisi et les fichiers existants altérés.

## Vérifications

- `node --test tests/expansion/precise_terrain.cjs` : 22 contrôles sur centres, demi-pixels, ordre nord/sud, NoData, priorité des sources, budgets, chargements annulés, renouvellement d’index, laboratoire et maillage réellement produit, dont le maintien du grossier à la bordure.
- `python tests/expansion/test_precise_terrain.py` : 11 contrôles sur binaires, reçus, halos, ZIP, installation hors ligne, corruption et véritables réponses HTTP.
- Revue indépendante : 288 comparaisons sur les 48 morceaux contre les douze GeoTIFF, sans déplacement de centre ni inversion des lignes.
- Preuve historique de `3d94e4c` : `tests/expansion/precise_terrain_native.py`, **78/78 contrôles natifs réussis**, dans un seul contexte Chromium sur le HTML `120e04972fb08a6f59b929d8a0952010712cf3849b8e512c383ff3a8ae87d636`. Neuf hauteurs sont comparées aux GeoTIFF originaux, dont un point entre quatre centres ; vingt-quatre sommets du maillage actif sont comparés à leurs cellules source. Une annulation de chargement laisse la banque publiée inchangée. À la bordure ouest, le pilote vérifie simultanément la présence de triangles grossiers à l'extérieur et de triangles fins à l'intérieur. Quatre captures et les mesures de mémoire sont conservées.

Ce rapport historique `PRECISE_TERRAIN_NATIVE.json` conserve le SHA du script exécuté (`50ce1fb5edd79ce4a0c2582177c92e3f0b21945fd867dc90b4ae1ab01f15001f`), les reçus et les aides de placement déclarées. Il n'enregistre aucune erreur JavaScript ou HTTP ; une requête PBF annulée pendant la séquence d'annulation volontaire et neuf observations réseau Supabase externes restent distinguées et visibles. La première tentative, limitée par une recherche de caméra trop petite dans ce quartier dense, est conservée séparément ; sa correction porte uniquement sur le pilote.

La nouvelle exécution conserve ces 78 contrôles et ajoute treize contrôles de route : **91/91**, quatre captures, un seul contexte Chromium, processus réellement terminé avec le code 0 sur le HTML `ed6e4103b23a45c413fef182862a93accb72ec25c6e1d8b101251822bfd5c670`. Le script exécuté a le SHA `39b1f25d8963d3ab5bf16a746a3e4e4e26f542149950d9ce426adf5e27f209b8`. Les huit sommets routiers contrôlés sont comparés aux GeoTIFF originaux et à l'offset annoncé. Le quartier Vieux-Port publié contient 998 rubans raffinés, passant de 10 534 à 111 001 faces ; aucun budget de division n'est atteint, et 10 459 feuilles restent explicitement limitées par l'arête de 1 m. Aucun seuil de précision continue n'en est déduit. Les captures montrent les scènes réelles de relief ; elles ne constituent pas un gros plan photographique des chaussées. Le nouveau rapport conserve les mêmes distinctions entre absence réelle de NoData, cas synthétiques, annulation volontaire et observations réseau externes. Le port HTTP a également été vérifié fermé après la fin du processus.

Les preuves historiques des itérations précédentes restent inchangées. Ces vérifications portent sur ce lot et ces parcours bornés ; elles ne constituent pas une visite humaine exhaustive de Marseille.
