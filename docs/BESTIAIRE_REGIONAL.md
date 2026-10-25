# Bestiaire régional : trois rencontres matérialisées

Les noms **Gabian bombardier**, **Rat-câble** et **CERFA-77** sont déjà présents dans `V046_LORE.bestiary` (`src/v046/04_lore.js`). Le module `src/v050/13_regional_bestiary.js` ajoute leurs assemblages procéduraux originaux, leur animation et leurs volumes ciblables. Les autres entrées du bestiaire restent à leur niveau antérieur : cette livraison ne représente pas vingt-cinq nouveaux personnages finis.

La provenance de ces trois noms est le dépôt Git v0.46. Les conversations privées du projet ChatGPT « Falllout:Marseille » n'ont pas pu être relues : leur accès renvoie une limitation de débit. Aucun détail de ces conversations n'est présenté comme récupéré. Les formes, poses et variantes d'attaque décrites ici sont des extensions écrites pour cette livraison.

| Espèce | Assemblage et animation | IA conservée | Préparation d'attaque |
| --- | --- | --- | --- |
| Rat-câble | Quadrupède bas, oreilles, museau, quatre pattes alternées, carapace métallique et câble caudal segmenté animé ; 25 éléments | `molerat` : poursuite et morsure, PV/dégâts/butin d'origine | Morsure, 0,68 s |
| Gabian bombardier | Bec, tête, ailes avec plumes, pattes, queue, sac ventral ; battement, oscillation et contraction du sac ; 23 éléments, plus une goutte pendant la préparation | `bloatfly` : déplacement au sol et tir toxique hérités | Lâcher corrosif, 1,35 s |
| CERFA-77 | Petit bureau blindé roulant, lecteur optique mobile, formulaire, bac, tampon et pince ; 24 éléments | `protectron` ou `concordeDrone` : déplacement, couverture et tir hérités | Injonction armée, 1,65 s |

Le Gabian a une silhouette de vol rasant. Il ne dispose pas d'une navigation aérienne complète ni d'un solveur de bombardement. Les télégraphes utilisent le mécanisme existant : cible verrouillée, délai, possibilité de s'écarter ou de rompre la ligne de vue. Les dégâts, les statistiques de l'archétype, le type d'attaque et les statuts restent ceux de la rencontre d'origine. La portée effective du télégraphe est bornée à 1,85 m pour la morsure, 14 m pour le Gabian et 22 m pour CERFA-77, sans dépasser la portée héritée (avec le minimum de mêlée existant). CERFA-77 reste distinct de l'autre nom canonique « Percepteur 3000 ».

## Apparition et compatibilité des campagnes

Le planning choisit au plus un emplacement régulier par site hostile existant. Il comprend **21 emplacements potentiels** dans le catalogue territorial de 248 sites ; il ne crée aucun site, emplacement ou identifiant d'ennemi. Les emplacements d'élite et de boss gardent leur identité.

Une variante n'est admise que pour un **nouvel acteur** du monde géographique actif : territoire mesuré chargé, sol couvert par les sources, hauteur cohérente, empreinte et marge de marche sans eau ni obstacle. La validation utilise `v050TravelGround`, le banc altimétrique du monde et les collisions installées. Un emplacement refusé garde son acteur de base, sans variante. Le module n'affirme donc pas que les 21 variantes apparaissent systématiquement.

Les prévisualisations de chargement ne modifient pas le registre des variantes. Leurs candidats demeurent dans une `WeakMap` transitoire liée à l'objet monde et à l'objet campagne : seule la première mise à jour du monde effectivement publié, après la fin du chargement, peut les admettre. Un checkpoint v049 intermédiaire ne transforme pas à tort ces acteurs fraîchement créés en anciennes rencontres. Une prévisualisation remplacée, ou issue d'une autre campagne, ne peut écrire le registre. Le laboratoire, les transitions, les chargements en attente, les intérieurs et les mondes sans sources sont exclus. Aucun déplacement d'acteur actif n'est effectué à l'installation.

Les campagnes existantes sont prioritaires. Un acteur déjà actif, enregistré dans v049, blessé dans l'ancien registre v022, déclaré mort ou possédant déjà un cadavre ne reçoit pas une nouvelle variante. Le contrôle du registre a lieu **avant** les wrappers de création v049 ; une simple attribution de propriétaire au monde n'est pas prise pour une ancienne rencontre.

Les variantes retenues ajoutent seulement une métadonnée visuelle et un nom. Le même identifiant, type d'IA, PV, blessures, position, statistiques et inventaire de butin restent gérés par leurs modules existants. `state.v053Bestiary.assignments` conserve seulement `{species, baseType}` par identifiant résolu : maximum 256 entrées et budget de 96 Kio. La sauvegarde ordinaire écrit ce registre avec l'état des rencontres. Le chargement rejette les identités inconnues, les espèces incompatibles et les changements d'archétype.

## Ciblage, collisions et restes

Le rig v025 fournit simultanément les éléments visibles, les parties VATS et leurs volumes orientés. Les huit coins de chaque élément, avec sa rotation propre, entrent dans le volume de sa partie. Ailes, câble, lecteur, tampon et roues sont ciblables ; leurs groupes de dégâts utilisent les groupes déjà reconnus par v025/v049. Le temps de pose reste figé pendant VATS. L'option de réduction des mouvements fige les oscillations automatiques.

Chaque silhouette tient dans une empreinte horizontale contrôlée (0,90 m pour Rat-câble/CERFA, 0,96 m pour Gabian). Les nouveaux déplacements vérifient cette empreinte avant l'IA existante. Un déplacement d'attente hérité qui aboutirait hors du sol admissible est annulé. Le banc du contrôle se renouvelle avec le banc altimétrique ou les collisions du monde.

La mort passe par les véritables fonctions existantes. Le conteneur demeure `territory|remains:<identifiant>` ; aucune deuxième récompense n'est créée. Le cadavre utilise une pose couchée de la même silhouette et conserve les marqueurs de rendu v026. Ses quantités initiales et restantes, son type d'acteur, les prélèvements déjà faits et le retour après déchargement gardent leur propriétaire v026/v049.

## Vérification

```sh
node --check src/v050/13_regional_bestiary.js
node tests/expansion/regional_bestiary.cjs
```

Le harnais fait exécuter le vrai catalogue v042, la publication v047, `addEnemy`, `damageEnemy`, `killEnemy`, les rigs v025, l'IA de base et les télégraphes v021, la récupération physique v026 et les wrappers de persistance v049. Ses 35 cas couvrent les trois créations, les anciennes rencontres actives/blessées/mortes, les cadavres, les prévisualisations annulées, la publication normale avec checkpoint intermédiaire, l'esquive des attaques réelles, les poses/empreintes/volumes, la migration, le retour avec blessures et le prélèvement fini après mort. Ses fournisseurs de terrain, scène, stockage et interface sont contrôlés : ces tests ne constituent pas une nouvelle mesure géographique ni une capture native.

Après `v053BestiaryAfterInit`, les diagnostics en lecture seule sont :

- `v053BestiaryInfo()` : acteurs réellement présents, emplacements encore éligibles et refus de validation ;
- `v053BestiaryCatalog()` : définition des trois espèces ;
- `v053BestiaryActor(id)` : état et géométrie clonée d'un acteur présent.

Ils ne créent ni rencontre ni récompense. Des exemples de slots candidats existants sont `v042:v042-huveaune-nest-01:outside:0`, `v042:v042-marseille-nest-05:outside:0` et `v042:v042-marseille-nest-02:outside:2`. Une vérification native doit employer un acteur réellement admis par le chargement courant.
