# Surfaces observées : contextes Bourse et Opéra

Cette tranche ajoute quatre emprises IGN au MNS supérieur : un volume dans le
contexte du Palais de la Bourse et trois dans celui de l’Opéra Municipal de
Marseille. Elle conserve exactement les dix-neuf surfaces précédentes et les
douze liens de l’atlas documentaire. **Aucun relevé de façade, ouverture ou plan
de pièce n’a été acquis ou ajouté.**

Le payload contient désormais 23 records, 5 reçus de dalles et 142 427 triangles.
Son empreinte est
`c89a3a22e3b2d55c08d30361ba5c65cae88392b74635a6d5cc2bc7599d99ae7c`.
Le [reçu d’extension](MNS_EXTENSION_20261102.json) conserve les empreintes des
anciens records, les identifiants nouveaux et les limites. Le
[reçu de préparation](BOURSE_OPERA_BUILD_RECEIPT.json) détaille les surfaces et les
sources utilisées.

## Acquisition et coordonnées

La dalle MNS `0892-6247` a été téléchargée le 2 novembre 2026 à l’URL IGN publiée
dans les métadonnées déjà acquises. Le
[reçu HTTP et raster](0892-6247-MNS_RECEIPT.json) fixe ses 16 000 513 octets et son
SHA-256 `4354e54417d2c2d00392f90820c69c3195145dd0bae244f36fe58aa8b7126b62`.
Le produit est attribué à IGN — Géoplateforme, LiDAR HD et BD TOPO, en Licence
Ouverte 2.0 ; l’acquisition LiDAR est datée de 2021 dans les métadonnées. La date
du téléchargement ne devient pas la date du relevé.

Le service déclare LAMB93/EPSG:2154 et IGN69 ; le raster Float32 possède un pas
natif de 0,50 m et une sentinelle NoData de `-9999`. Le WKT reçu est conservé
exactement : l’identification automatique d’un code EPSG par la bibliothèque est
absente pour ce TIFF WMS. Les paramètres, coordonnées et unités restent ceux de
la requête et des métadonnées officielles. Le pas natif ne certifie pas une
précision absolue de 50 cm.

L’emprise Bourse traverse le raccord entre `0892-6248` et `0892-6247`. La première
préparation, limitée à la dalle ancienne, a été refusée. Les deux tableaux source
ont ensuite été concaténés verticalement, sans rééchantillonnage ni création de
cellules. Les sommets aux centres natifs gardent leurs valeurs ; seules les
intersections avec le contour BD TOPO utilisent le plan du triangle raster
original. Les cours et contours sont conservés et une mesure NoData intersectant
une emprise provoque un refus.

Le [rejeu indépendant des cellules](NATIVE_CELL_REPLAY.json) a comparé les
**19 529 centres natifs exactement** et les **2 154 intersections** des quatre
surfaces aux deux TIFF originaux. Aucune cellule NoData n’a été utilisée. Les
tolérances numériques de ce contrôle sont des tolérances de calcul, pas une
précision supplémentaire du relevé.

## Noms, usages et limites

La [recherche officielle bornée](OFFICIAL_CATALOGUE_CHECKS.json) a obtenu 58 zones
IGN et six réponses de recherche data.gouv sans résultat pour leurs termes
exacts. Cela ne démontre pas l’absence de plans dans toutes les archives.

La zone nommée Bourse, non fictive et déclarée à 3 m, ne recouvre qu’environ 28,7 %
du bâtiment candidat ; elle ne passe donc pas le filtre strict d’association
documentaire à toute une emprise. La zone Opéra déclare 5 m et ne passe pas non
plus ce filtre. Ces noms restent des **contextes**, avec leurs sources et
limitations dans les nouveaux records ; aucun treizième lien documentaire n’est
forcé. Saint-Victor et Saint-Jean ne sont pas ajoutés à cette tranche.

Le MNS décrit la surface supérieure observée, qui peut inclure des équipements
ou des éléments de sursol. Il ne donne pas les détails de façade, les plans des
salles, les pentes sémantiques d’un toit ou une identification architecturale de
chaque composante. Les générateurs existants gardent la responsabilité des
parties non documentées.

## Préparation reproductible et contrôles

La préparation est hors réseau, à partir des deux TIFF acquis et des reçus
versionnés :

```bash
python tools/extend_bourse_opera_surfaces.py \
  --mns-cache DOSSIER_DALLES_ANTERIEURES \
  --new-mns-cache DOSSIER_DALLE_0892_6247 \
  --include-opera --output DOSSIER_DE_PREPARATION
node tests/expansion/landmark_surfaces.cjs
```

Le changement du validateur porte seulement sur la borne des reçus : huit au
maximum, cinq utilisés. Les budgets de records, triangles, sommets, octets et les
autres refus restent inchangés. Les 41 contrôles purs distinguent les données
réelles et les fixtures synthétiques ; ils ne constituent pas une visite de jeu.
Le pilote natif conserve les quatre contextes précédents, ajoute Bourse/Opéra et
attend le gel coordonné du HTML avant exécution.
