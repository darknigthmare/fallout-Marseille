# Relief mesuré autour du Vélodrome et de Borély

Deux fenêtres du sud de Marseille reçoivent un relief IGN plus fin que la grille communale de 10 m. Elles couvrent les abords du Vélodrome et du château Borély, hors des 12 km² du lot natif central. Elles totalisent **384 832 nœuds**, dans deux rectangles d'environ 450 m de largeur. La couverture centrale native, ses archives et les deux grilles historiques d'Aubagne restent identiques.

| Secteur | Boîte de nœuds WGS84 : sud, ouest, nord, est | Grille | Nœuds valides |
| --- | --- | --- | ---: |
| Vélodrome | `[43.2688, 5.393, 43.2725, 5.3985]` | 448 × 413 | 185 024 |
| Château Borély | `[43.2553, 5.378, 43.2593, 5.3835]` | 448 × 446 | 199 808 |

Le produit est le **MNT LiDAR HD IGN**, mission `21LHD7PQ`, édition du 14 mars 2025, acquis en 2021. Le MNT décrit le sol ; il ne fournit pas les tribunes, le toit du stade, les façades ou les pièces du château. Aucun de ces éléments n'est présenté comme ajouté par ces rasters.

Les deux GeoTIFF originaux comportent chacun 2 000 × 2 000 pixels Float32 au pas natif de 0,50 m, en Lambert-93 / NGF-IGN69. L'URL complète de chaque export provient du champ `url_mnt` des véritables métadonnées WFS. Elle n'est pas reconstituée à partir d'un nom supposé. Le téléchargement conserve la vérification HTTPS et le proxy de l'environnement.

Les données de jeu sont **reprojetées et rééchantillonnées au plus proche** sur des nœuds WGS84 au pas demandé de **1 m**. Les espacements effectifs sont enregistrés dans chaque reçu. Il ne s'agit donc pas d'une extension du treillis natif central de 0,50 m. Aucun lissage, comblement de trou ni changement de référentiel vertical n'est appliqué. Les deux extraits reçus ne contiennent aucun NoData ; les tests de trous emploient des fixtures synthétiques distinctes.

Le moteur de terrain existant sélectionne cette grille plus fine pour la physique. Son rendu local reprend les nœuds importés et un raccord vers le niveau de détail périphérique. Le pas des nœuds ne certifie ni la précision absolue du relevé ni la fidélité intégrale des deux lieux. Les traces et bâtiments restent ceux des sources déjà installées.

Les [reçus d'acquisition](../implementation/south-terrain/ACQUISITION.json) identifient les deux TIFF originaux par SHA-256, avec leurs métadonnées, dates, URL, CRS et conversions. Les TIFF restent dans le cache externe ; le jeu n'en distribue pas une seconde copie. L'archive active `data/map_pack/enrichment_archives/world-sources-8398e107b6d86bb3.zip` fait 4 081 015 octets et contient l'ancien lot Aubagne inchangé plus le nouveau lot `geo_marseille`. L'ancien ZIP demeure conservé.

## Installation et conservation des imports

```bash
python3 tools/world_source_bundle.py install
```

Le serveur réalise aussi cette restauration au démarrage. Dans une installation existante validée, une mise à jour ajoute uniquement les régions fournies absentes de l'index. Elle conserve les descripteurs et tous les octets des régions déjà présentes, y compris une autre version importée par le joueur. Si `geo_marseille` est déjà associé à un import utilisateur, celui-ci garde donc la priorité et ces fenêtres ne l'écrasent pas.

Le résultat combiné est validé avant écriture ; tous les conflits de fichiers sont contrôlés avant la première copie. L'index actif est publié atomiquement après les membres. Une interruption avant cette publication laisse l'ancien index utilisable ; une relance peut terminer. Une source existante corrompue, un lien symbolique ou un dépassement de budget provoque un refus.

Le [contrôle hors ligne du véritable ZIP](../implementation/south-terrain/OFFLINE_DISTRIBUTION.json) vérifie une installation vide, une mise à jour depuis le précédent ZIP effectivement distribué et une relance. Les fichiers actifs de l'installation neuve et de l'installation mise à jour sont identiques ; le lot Aubagne et son descripteur restent conservés. Cette vérification de distribution est distincte d'un parcours de jeu.

## Vérification indépendante

`tools/audit_resampled_dem.py` compare chaque nœud du lot importé avec le TIFF original fourni par l'opérateur. Ce rejeu utilise l'API `rasterio.sample`, distincte de la lecture par fenêtres du convertisseur. L'original doit correspondre au SHA du reçu de conversion.

Le [rejeu effectué](../implementation/south-terrain/EXACT_SOURCE_REPLAY.json) retrouve **384 832 valeurs identiques**, zéro divergence et une erreur absolue maximale de zéro entre les cellules sélectionnées et les valeurs importées. Cela atteste la conservation de ces cellules après l'échantillonnage déclaré, pas une mesure indépendante de leur exactitude dans le monde réel. Les [sources actives](../implementation/south-terrain/SOURCE_AUDIT.json) restent inspectables.

```bash
python3 -m unittest discover -s tests/expansion -p test_world_source_bundle.py
python3 -m unittest discover -s tests/expansion -p test_resampled_dem_audit.py
python3 tools/audit_resampled_dem.py \
  --directory data/map_pack/enrichment --region geo_marseille \
  --original /cache/velodrome/original.tif \
  --original /cache/borely/original.tif \
  --report /tmp/rejeu-relief-sud.json
```

Les tests de distribution couvrent notamment l'ajout d'une région absente, la conservation d'un import utilisateur différent, les conflits avant écriture, l'interruption de publication et le budget combiné. Les quatre tests du rejeu utilisent des TIFF synthétiques annoncés ; ils détectent une altitude modifiée, un trou comblé et un original différent. Ils ne sont pas comptés comme des observations géographiques.
