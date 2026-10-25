# Bestiaire régional : cinq rencontres matérialisées

Les noms **Gabian bombardier**, **Rat-câble**, **Rat-couronné**, **Cigale du Mistral** et **CERFA-77** sont déjà présents dans `V046_LORE.bestiary` (`src/v046/04_lore.js`). Le module `src/v050/13_regional_bestiary.js` leur fournit des assemblages procéduraux originaux, des animations et les volumes réellement ciblés. Rat-couronné et Cigale remplacent ainsi, sur leurs nouvelles rencontres admissibles, les silhouettes de robot utilisées jusqu'ici par le fallback des types `giantRat` et `mistralCicada`.

La provenance des cinq noms est le canon Git v0.46. La lecture des conversations privées du projet ChatGPT « Falllout:Marseille » reste limitée par le service : aucun contenu non lu n'est présenté comme récupéré. Les formes, mouvements et attaques ci-dessous sont des extensions écrites pour cette livraison. Les vingt autres noms du bestiaire ne sont pas annoncés comme vingt nouveaux personnages finis.

| Espèce | Silhouette et animation | Type, statistiques et butin conservés | Attaque |
| --- | --- | --- | --- |
| Rat-câble | Quadrupède bas, oreilles, museau, quatre pattes alternées, carapace métallique et câble caudal segmenté ; 25 éléments | `molerat` | Morsure préparée, 0,68 s |
| Rat-couronné | Flanc brun, museau et incisives, oreilles, couronne de cuivre à cinq pointes, quatre pattes alternées et queue souple ; 30 éléments | `giantRat`, avec ses données v0.12 existantes | Ruée préparée, 0,82 s |
| Cigale du Mistral | Abdomen segmenté, yeux composés, antennes, six pattes alternées, deux ailes nervurées et tymbales vibrants ; 31 éléments | `mistralCicada`, avec ses données v0.12 existantes | Projection toxique du tymbal, 1,20 s ; IA terrestre héritée |
| Gabian bombardier | Bec, tête, ailes plumeuses, pattes, queue, sac ventral ; battement, oscillation et contraction ; 23 éléments et une goutte pendant la préparation | `bloatfly`, identité, PV, vitesse, dégâts, type toxique et butin d'origine | Vol mesuré, cible verrouillée pendant 1,35 s, puis projectile balistique réel |
| CERFA-77 | Bureau blindé roulant, lecteur mobile, formulaire, bac, tampon et pince ; 24 éléments | `protectron` ou `concordeDrone` | Injonction armée, 1,65 s |

CERFA-77 reste distinct du nom canonique « Percepteur 3000 ». Les données de `giantRat` et de `mistralCicada` viennent de `V012_ENEMIES`, déjà appliqué aux types de rencontre. Aucune nouvelle table de PV ou de récompenses n'est ajoutée.

## Apparition et conservation des campagnes

Le planning conserve exactement les **21 emplacements historiques** de la première livraison du module 13. Rat-couronné et Cigale peuvent occuper au plus **un autre emplacement régulier existant** par site, pour un total de **41 emplacements potentiels** dans le catalogue territorial de 248 sites. Aucun site, emplacement ou identifiant d'ennemi n'est créé. Les emplacements d'élite et de boss gardent leur identité.

Une nouvelle variante exige un monde géographique actif, des sources installées, un sol mesuré cohérent et une empreinte libre d'eau et d'obstacles. Pour le Gabian, cette admission emploie son volume aérien complet, même si la hauteur héritée du centre du nid diffère de celle de son XY sur une pente. Aucun recalage de position n'est nécessaire. Un refus garde l'acteur de base. Ces 41 possibilités ne constituent donc pas 41 apparitions garanties.

Les prévisualisations restent dans une `WeakMap` transitoire liée à leur objet monde et à leur objet campagne. Seul le monde effectivement publié peut enregistrer leurs variantes, après la fin de la transition et du chargement. Un checkpoint v049 intermédiaire ne les fait pas passer pour d'anciennes rencontres. Une prévisualisation annulée ou une autre campagne ne peut écrire ce registre.

Les acteurs déjà actifs, enregistrés dans v049, blessés dans v022, morts ou pourvus d'un cadavre ne reçoivent pas une nouvelle variante. Les vieux `bloatfly` non assignés gardent leur comportement antérieur. Le contrôle précède les wrappers de création : `v049Own` n'est pas pris pour la visite antérieure d'un slot. L'installation ne déplace aucun acteur actif.

Le même identifiant, type de base, PV, blessures, statistiques et butin restent autoritaires. `state.v053Bestiary.assignments` conserve seulement `{species, baseType}` par identifiant résolu, avec au plus 256 entrées et 96 Kio. La sauvegarde ordinaire écrit ensemble ce registre et les rencontres v049. La migration rejette les identités inconnues ou les associations espèce/type incompatibles. Les 21 anciennes associations se rechargent sans modification.

## Vol du Gabian et lâcher corrosif

Le Gabian assigné se déplace réellement en X/Y/Z : décollage, patrouille, approche, orbite et préparation du lâcher. Son type de base reste `bloatfly` ; la nouvelle mise à jour aérienne remplace sa marche héritée. La vitesse horizontale et ses pénalités de blessures sont conservées. La hauteur de croisière visée est de 2,20 m au-dessus du sol source et le plafond du comportement est de 8 m au-dessus de cette mesure. La poursuite cesse si le joueur sort du rayon de 80 m autour du nid, pour libérer l'état de combat. Les choix de direction restent locaux et bornés : ce n'est pas une recherche globale de chemins aériens.

Chaque colonne de vol exige les tuiles base et cadastre, une hauteur finie issue du banc actif et l'absence d'eau source. Le contrôle n'utilise jamais le zéro de secours de `groundHeightAt`. Les mesures du centre et de quatre marges empêchent le relief de couper la silhouette. L'ensemble des ailes animées tient dans un rayon de 0,96 m et une tranche verticale conservatrice de +0,10 à +1,35 m par rapport à la position de l'acteur.

Les mouvements balaient cette enveloppe tous les 18 cm au plus, contre les collisions source et les objets de jeu à leur véritable hauteur. Le Gabian peut rester sous un plafond assez haut ou passer au-dessus d'un toit bas ; il ne traverse ni façade, plafond ni relief. Quand la direction est bloquée, il essaie une composante horizontale à hauteur constante, deux tangentes puis une montée locale validée. Sans passage valide, il attend. Aucune colonne absente ou aquatique ne devient un plancher inventé ; sa préparation d'attaque est alors annulée.

Après le délai visible, le sac libère une goutte réelle : position, vitesse horizontale vers la cible verrouillée, gravité de 9,8 m/s², limite de vie de 3 s. Le projectile est rendu pendant sa chute et balaie le trajet tous les 5 cm au plus. Son rayon de 7 cm s'applique dans les trois dimensions pour rencontrer aussi les dalles très minces, le terrain et les façades/toits. Un impact n'applique les dégâts hérités que dans son rayon de 0,85 m, à hauteur compatible et avec une ligne de vue libre ; s'écarter de la cible verrouillée permet de l'éviter. Les obstacles ou une couverture manquante empêchent un dégât à travers le décor. Le registre volatil est borné à 32 projectiles, 16 effets d'impact et 8 constats d'impact ; un changement de monde ou de campagne les retire.

Le temps de vol, la préparation et la chute s'arrêtent dans les menus. Le danger aérien participe à l'état de combat et à l'affichage furtif existants. Le sol et les collisions restent obtenus par les fonctions de production, sans dépendance à un nouveau format de fichier terrain.

La position aérienne et les blessures sont sauvegardées par v049. À la restauration, un Gabian déjà assigné peut reprendre son altitude si son volume est toujours admissible. Les phases visuelles et les projectiles transitoires ne sont pas des récompenses persistantes ; ils ne sont pas recréés par le chargement.

## Ciblage et restes

Le rig v025 fournit simultanément les éléments visibles, les parties VATS et leurs volumes orientés. Les huit coins de chaque élément avec sa rotation propre entrent dans le volume de sa partie. Ailes, tymbales, couronne, câble, lecteur, tampon et roues utilisent les groupes de dégâts reconnus par v025/v049. VATS fige le temps de pose ; la réduction des mouvements fige les oscillations automatiques.

Les empreintes sont contrôlées : 0,90 m pour Rat-câble/CERFA, 0,96 m pour Gabian, 0,98 m pour Rat-couronné et 1 m pour Cigale. Les espèces terrestres gardent leur IA de base, avec la validation de cette empreinte ; une dérive d'attente hors du sol admissible est annulée.

La mort utilise les fonctions existantes et le même conteneur `territory|remains:<identifiant>`. Aucun deuxième butin n'est créé. Le Gabian mort rejoint directement le support mesuré ou le dessus de toit admissible sous lui ; il n'y a pas encore d'animation de chute du cadavre. Sans source valide, aucun support n'est inventé. Ses quantités initiales et restantes, le type d'acteur, les prélèvements déjà faits et les retours après déchargement gardent leurs propriétaires v026/v049. Le cadavre de chaque espèce reprend sa silhouette couchée et les marqueurs v026.

## Vérification

```sh
node --check src/v050/13_regional_bestiary.js
node tests/expansion/regional_bestiary.cjs
python -m py_compile tests/expansion/regional_bestiary_native.py
```

Les 67 cas du harnais exécutent le vrai catalogue v042, la publication v047, `addEnemy`, `damageEnemy`, `killEnemy`, les rigs v025, l'IA de base et les télégraphes v021, la récupération physique v026 et les wrappers v049. Ils couvrent les cinq créations, les 21 associations historiques, les anciennes campagnes, la publication avec checkpoint intermédiaire, les sauvegardes de blessures/altitude, le butin fini, les plafonds/toits/parois minces/relief, les sources manquantes, le projectile réel, l'impact et l'esquive. Terrain, scène, stockage et interface restent des fournisseurs contrôlés : ces tests ne sont pas des mesures géographiques supplémentaires.

Le pilote HTTP `regional_bestiary_native.py` est préparé pour un Gabian réellement admis, son altitude et son volume libres au-dessus du pack installé, un projectile esquivé par marche réelle sous pas de simulation, et au moins un Rat-couronné ou une Cigale visible à un slot existant. Il exige des SHA coordonnés et `--run`. Il n'injecte ni acteur, source, HTML ni sauvegarde historique et n'utilise que les diagnostics publics. Une exécution doit conserver ses captures et son rapport séparément de la preuve historique du Rat-câble de la livraison précédente.

Après `v053BestiaryAfterInit`, les diagnostics en lecture seule sont :

- `v053BestiaryInfo()` : acteurs présents, slots admissibles, refus, volumes/hauteurs de vol, projectiles et huit derniers impacts avec leur résultat ;
- `v053BestiaryCatalog()` : définition des cinq espèces ;
- `v053BestiaryActor(id)` : état et géométrie clonée d'un acteur présent.

Ces diagnostics ne créent ni rencontre ni récompense. Exemples de slots existants : `v042:v042-huveaune-nest-01:outside:0` (Rat-câble), `v042:v042-huveaune-nest-01:outside:1` (Rat-couronné), `v042:v042-garlaban-nest-01:outside:1` (Cigale) et `v042:v042-marseille-nest-05:outside:0` (Gabian).
