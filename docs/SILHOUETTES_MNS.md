# Surfaces mesurées de la Major et de Notre-Dame de la Garde

Les volumes connus de ces deux sites disposent désormais d’une surface supérieure issue du **MNS LiDAR HD de l’IGN au pas natif de 0,50 m**, à la place de leur seul plafond horizontal. Les emprises, cours, identifiants, altitudes de base et descripteurs historiques des bâtiments sont conservés. La géométrie visible et la collision supérieure utilisent le même maillage découpé.

Le MNS décrit la surface supérieure observée lors de l’acquisition. Il ne fournit ni la structure des combles, ni les baies, ni les pièces, ni une identification sémantique de chaque statue ou toiture. Il peut contenir bruit de mesure, végétation ou objets présents à cette date. Les finitions de couleur et les murs verticaux prolongés jusqu’à la surface sont des représentations du jeu. Cette amélioration ne certifie pas les deux monuments intégralement en 1:1.

## Sources et périmètre

Les URL `url_mns` proviennent des métadonnées officielles IGN déjà acquises. Trois GeoTIFFs Float32 ont été obtenus par HTTPS avec vérification TLS, en Lambert-93 et NGF-IGN69 : `0891-6248`, `0892-6248` et `0892-6246`. Les métadonnées annoncent des acquisitions du 26 juin au 17 octobre 2021 selon la dalle, et une édition du 14 mars 2025. Leurs reçus et SHA-256 figurent dans [MNS_ACQUISITION.json](../implementation/landmark-surfaces/MNS_ACQUISITION.json).

Ces fichiers totalisent 48 001 539 octets et restent dans le cache externe d’acquisition. Le jeu distribue un [index](../data/map_pack/landmark_surfaces/index.json) et un maillage attribué de 3 468 895 octets ; aucun GeoTIFF supplémentaire n’est dupliqué dans le dépôt. La Licence Ouverte 2.0 et l’attribution IGN accompagnent les données.

Les emprises proviennent de deux partitions BD TOPO existantes, inchangées : cinq composantes recouvrant la zone de la Major et douze recouvrant celle de Notre-Dame de la Garde. Ces recouvrements établissent le contexte géographique utilisé pour ce travail ; ils ne rebaptisent pas chaque composante comme bâtiment central du monument. L’atlas architectural historique de douze associations reste séparé et inchangé.

Le lot contient **17 composantes, 46 052 sommets et 82 363 triangles de surface**. Une composante, `BATIMENT0000000273400986`, comporte un bord MNS à 155,187 m alors que sa base IGN historique est à 155,5 m. Le moteur refuse ce remplacement et conserve son volume précédent. Les seize composantes admissibles représentent 81 022 triangles supérieurs. Aucun échantillon n’est relevé artificiellement pour faire passer ce contrôle.

Deux exemples montrent la différence avec l’ancien volume uniforme :

| Composante source | Ancien plafond uniforme NGF | Sommet MNS obtenu NGF |
| --- | ---: | ---: |
| `BATIMENT0000000258938065`, zone de la Major | 49,6 m | 79,852554 m |
| `BATIMENT0000000273400985`, zone de Notre-Dame de la Garde | 171,4 m | 210,167938 m |

La différence signale une nouvelle observation de surface, pas une correction rétroactive des attributs BD TOPO. Les deux valeurs source restent inspectables.

## Découpage et comportement

Le [constructeur hors ligne](../tools/build_landmark_surfaces.py) conserve les valeurs Float32 aux centres natifs de pixels. Chaque cellule est divisée suivant une diagonale constante, puis ses triangles sont découpés dans les emprises IGN originales, avec leurs trous. Seuls les nouveaux sommets de découpage utilisent l’interpolation sur le triangle source. Les deux dalles adjacentes de la Major sont concaténées sans rééchantillonnage avant le découpage pour conserver la bande entre leurs centres de pixels.

La couverture projetée doit égaler l’aire source et les seuls bords libres doivent retrouver son périmètre. Les NoData intersectant une emprise provoquent un refus. Le constructeur n’ajoute ni dôme analytique, ni pente supposée, ni point de hauteur inventé.

Le moteur exige les coordonnées géographiques originales et les mêmes attributs d’altitude pour appliquer une surface. Les limites restent bornées : 24 composantes, 40 000 sommets et 60 000 triangles par composante, 220 000 triangles au total, fichier limité à 16 Mio. Le rendu conserve les tampons de géométrie bornés du moteur existant. Un index métrique réduit les recherches locales dans les triangles ; il ne constitue pas une mesure de fluidité sur un GPU matériel.

Les rayons, le support, les collisions de corps et les grenades retrouvent la surface réellement publiée par la même classe de solides de toiture. Les façades procédurales sont filtrées à l’affichage : un triangle inventé dépassant le MNS local est omis, ce qui évite les fenêtres flottantes au-dessus d’une pente plus basse. Cette omission ne transforme pas les autres ouvertures inventées en relevé documentaire. Les plans des instances restent les plans historiques du jeu ; le MNS extérieur ne renseigne pas leurs pièces.

Les diagnostics `v056LandmarkInfo` et `v056LandmarkSurface` exposent la couverture, les refus, les bornes, les nombres de triangles et les identités source. Ils renvoient des copies des informations de mesure consultables. Le champ `applied` est un historique borné des surfaces construites, pas le nombre de caps simultanément publiés ; le pilote vérifie donc aussi les identifiants et tailles des caps effectivement présents dans la scène. Le filtre de façade se rattache par WeakMap au cap réellement collecté, afin qu’une préparation hors écran annulée ne remplace pas celui de la scène courante.

## Vérification

Les [31 contrôles de modèles](../tests/expansion/landmark_surfaces.cjs) couvrent le lot réellement expédié, ses SHA-256 et partitions d’origine, les refus de source/NoData/liaison et de triangles hors cellule native, l’interpolation, la conservation des coordonnées et volumes historiques, le toit incliné et son fond dans la vraie classe de collision, le chargement optionnel, une scène déjà ouverte, l’invalidation du cache de support, le changement de scène, la préparation annulée d’une copie non publiée et le repère commun réellement employé par les fonctions de projection v046. Les fixtures synthétiques de ces tests restent explicitement séparées des données de Marseille et ne sont pas installées dans l’atlas.

Deux reconstructions hors ligne depuis les trois GeoTIFFs acquis ont produit le même JSON, SHA-256 `e50ea945c27e47a3f706c8ea381975032cd6b37857baa913f4f9430fcab3c6f6`. Une comparaison indépendante avec les trois Float32 originaux retrouve les 36 341 centres natifs exactement et les 9 711 sommets de découpage avec un écart numérique maximal de 1,63 × 10⁻⁸ m sur leurs plans de triangle. Ces 46 052 observations de source restent hors de la somme des contrôles de jeu ; cet écart de calcul ne mesure pas la précision physique du relevé.

Le [pilote navigateur](../tests/expansion/landmark_surfaces_native.py) prépare des visites HTTP réelles des deux sites, des comparaisons avec les sommets acquis, la collision/visibilité et un rechargement suivi du bouton Continuer. Il ne démarre qu’avec `--run` et le SHA du HTML attendu. Ses vues élevées sont des inspections assistées ; elles ne certifient pas une visite humaine ni chaque façade. Le résultat de la campagne intégrée doit être consulté pour connaître l’exécution effectivement retenue.

La campagne native retenue sur le HTML `844376c014575111f268f292c8307bb3f47ac33629604406f5e0da00104c5a34` a effectivement réussi **44 contrôles**, avec **cinq captures originales examinées**. Elle vérifie les cinq caps réellement publiés de la Major et les onze de Notre-Dame de la Garde par leurs identifiants et tailles, les sommets/visibilités physiques, le refus de la composante sous sa base, puis le rechargement et Continuer. Le cartouche technique central reste masqué ; l’attribution compacte est entièrement visible sous les raccourcis, ouvre le vrai panneau des sources puis revient au jeu, et le repère de proximité ne recouvre ni le critique ni le niveau. Le serveur du pilote est arrêté et son port refuse une connexion après la sortie réussie. Les deux annulations réseau observées concernent uniquement la métadonnée `/__mistral/local-data` (phase non enregistrée) ; dix-huit sondes Supabase externes ont échoué dans cet environnement. Les événements bruts sont conservés, sans exception JavaScript ni erreur HTTP locale.
