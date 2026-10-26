# Bestiaire : cinq créations régionales et deux figures récurrentes

Les noms **Gabian bombardier**, **Rat-câble**, **Rat-couronné**, **Cigale du Mistral** et **CERFA-77** sont déjà présents dans `V046_LORE.bestiary` (`src/v046/04_lore.js`). Le module `src/v050/13_regional_bestiary.js` leur fournit des assemblages procéduraux originaux, des animations et les volumes réellement ciblés. Rat-couronné et Cigale remplacent ainsi, sur leurs nouvelles rencontres admissibles, les silhouettes de robot utilisées jusqu'ici par le fallback des types `giantRat` et `mistralCicada`.

La provenance des cinq noms est le canon Git v0.46. Le projet ChatGPT a été consulté sans apporter de lore supplémentaire exploitable ; aucun contenu non lu n’est présenté comme récupéré. Les formes, mouvements et attaques ci-dessous sont des extensions écrites pour cette livraison. Les vingt autres noms du bestiaire ne sont pas annoncés comme vingt nouveaux personnages finis. Le **Radscorpion** et le **Fangeux**, déjà présents comme types `radscorpion` et `mirelurk` dans le cœur du jeu, reçoivent également deux assemblages originaux. Ils relèvent du bestiaire récurrent de Fallout et ne remplacent aucun des vingt-cinq noms locaux.

| Espèce | Silhouette et animation | Type, statistiques et butin conservés | Attaque |
| --- | --- | --- | --- |
| Rat-câble | Quadrupède bas, oreilles, museau, quatre pattes alternées, carapace métallique et câble caudal segmenté ; 25 éléments | `molerat` | Morsure préparée, 0,68 s |
| Rat-couronné | Flanc brun, museau et incisives, oreilles, couronne de cuivre à cinq pointes, quatre pattes alternées et queue souple ; 30 éléments | `giantRat`, avec ses données v0.12 existantes | Ruée préparée, 0,82 s |
| Cigale du Mistral | Abdomen segmenté, yeux composés, antennes, six pattes alternées, deux ailes nervurées et tymbales vibrants ; 31 éléments | `mistralCicada`, avec ses données v0.12 existantes | Projection toxique du tymbal, 1,20 s ; IA terrestre héritée |
| Gabian bombardier | Bec, tête, ailes plumeuses, pattes, queue, sac ventral ; battement, oscillation et contraction ; 23 éléments et une goutte pendant la préparation | `bloatfly`, identité, PV, vitesse, dégâts, type toxique et butin d'origine | Vol mesuré, cible verrouillée pendant 1,35 s, puis projectile balistique réel |
| CERFA-77 | Bureau blindé roulant, lecteur mobile, formulaire, bac, tampon et pince ; 24 éléments | `protectron` ou `concordeDrone` | Injonction armée, 1,65 s |

| Radscorpion | Céphalothorax segmenté, yeux et mandibules, huit pattes, deux pinces et queue articulée à huit segments ; 53 éléments | `radscorpion`, ses PV, blessures, vitesse, armure et butin existants | Dard préparé, 1,08 s ; queue qui se redresse et se replie vers la frappe |
| Fangeux | Carapace dorsale à cinq nervures, abdomen exposé, yeux pédonculés, deux pinces et pattes articulées ; 43 éléments | `mirelurk`, ses PV, blessures, vitesse, armure et butin existants | Cisaillement des pinces, 0,96 s ; avancée et fermeture pendant la préparation |

Ces deux modèles sont procéduraux et originaux ; aucun modèle, texture ou son extrait d'un jeu commercial n'est livré. Leur IA terrestre reste celle du type existant, avec la préparation v021 : l'attaque verrouille une cible, exige portée et ligne de vue lors de la frappe et peut être évitée ou interrompue. Les nouvelles formes utilisent réellement le rig de rendu et les volumes VATS ; pinces gauche/droite restent les membres `claw_l` et `claw_r` du groupe de dégâts `arms` déjà sauvegardé. Il n'y a pas de nouvel état de dégâts ou d'armure directionnelle.

CERFA-77 reste distinct du nom canonique « Percepteur 3000 ». Les données de `giantRat` et de `mistralCicada` viennent de `V012_ENEMIES`, déjà appliqué aux types de rencontre. Aucune nouvelle table de PV ou de récompenses n'est ajoutée.

## Apparition et conservation des campagnes

Le planning conserve exactement les **21 emplacements historiques** de la première livraison du module 13. Rat-couronné et Cigale peuvent occuper au plus **un autre emplacement régulier existant** par site, pour un total historique de **41 emplacements potentiels** dans le catalogue territorial de 248 sites. Les deux figures récurrentes utilisent au plus un autre emplacement régulier libre par site, après les deux groupes précédents : **31 possibilités supplémentaires**, soit **72 emplacements potentiels** au total. Une fixture issue du module de `3d94e4c` conserve les quarante et une associations précédentes et leur migration exacte. Aucun site, emplacement ou identifiant d'ennemi n'est créé. Les emplacements d'élite et de boss gardent leur identité.

Une nouvelle variante exige un monde géographique actif, des sources installées, un sol mesuré cohérent et une empreinte libre d'eau et d'obstacles. Pour le Gabian, cette admission emploie son volume aérien complet, même si la hauteur héritée du centre du nid diffère de celle de son XY sur une pente. Aucun recalage de position n'est nécessaire. Un refus garde l'acteur de base. Ces 72 possibilités ne constituent donc pas 41 apparitions garanties.

Les prévisualisations restent dans une `WeakMap` transitoire liée à leur objet monde et à leur objet campagne. Seul le monde effectivement publié peut enregistrer leurs variantes, après la fin de la transition et du chargement. Un checkpoint v049 intermédiaire ne les fait pas passer pour d'anciennes rencontres. Une prévisualisation annulée ou une autre campagne ne peut écrire ce registre.

Les acteurs déjà actifs, enregistrés dans v049, blessés dans v022, morts ou pourvus d'un cadavre ne reçoivent pas une nouvelle variante. Les vieux `bloatfly` non assignés gardent leur comportement antérieur. Le contrôle précède les wrappers de création : `v049Own` n'est pas pris pour la visite antérieure d'un slot. L'installation ne déplace aucun acteur actif.

Le même identifiant, type de base, PV, blessures, statistiques et butin restent autoritaires. `state.v053Bestiary.assignments` conserve seulement `{species, baseType}` par identifiant résolu, avec au plus 256 entrées et 96 Kio. La sauvegarde ordinaire écrit ensemble ce registre et les rencontres v049. La migration rejette les identités inconnues ou les associations espèce/type incompatibles. Les 21 anciennes associations se rechargent sans modification.

## Marge de création et conservation d'un corps existant

Une première création terrestre garde sa marge supplémentaire : le rayon complet du corps, puis quatre sondes à sa périphérie avec un rayon de 25 % du corps. Pour un Fangeux de rayon 1,28 m, cette admission peut réserver jusqu'à 1,60 m dans les directions sondées.

La marche, sa validation après l'IA et la restauration d'un acteur déjà assigné utilisent le même invariant physique : rayon complet du corps contre les solides, quatre points périphériques avec une sonde de rayon nul pour vérifier le MNT, l'eau et des différences de hauteur au plus égales à 0,50 m ; l'écart vertical central reste limité à 0,35 m. La marge supplémentaire extérieure au corps est réservée à la première création. Aucun acteur n'est déplacé au chargement et aucune affectation n'est effacée.

Un cas contrôlé utilisant le vrai `v050TravelGround`, le collisionneur, la locomotion et la sauvegarde v042/v049 démontrait l'incohérence antérieure : à 1,40 m d'un mur, un corps de rayon 1,28 m pouvait marcher mais perdait son rig au rechargement, car la sonde extérieure de 0,32 m touchait le mur. Le test échouait avant correction et passe après. Quatre autres régressions conservent le refus d'une nouvelle création dans cette marge, le refus de NoData au bord d'un corps sauvegardé et les mêmes vérifications pendant la marche et après l'IA. Il s'agit d'une fixture contrôlée existante, pas d'un relevé géographique inventé ni d'une attribution de la cause du refus natif antérieur.

## Vol du Gabian et lâcher corrosif

Le Gabian assigné se déplace réellement en X/Y/Z : décollage, patrouille, approche, orbite et préparation du lâcher. Son type de base reste `bloatfly` ; la nouvelle mise à jour aérienne remplace sa marche héritée. La vitesse horizontale et ses pénalités de blessures sont conservées. La hauteur de croisière visée est de 2,20 m au-dessus du sol source et le plafond du comportement est de 8 m au-dessus de cette mesure. La poursuite cesse si le joueur sort du rayon de 80 m autour du nid, pour libérer l'état de combat. Les choix de direction restent locaux et bornés : ce n'est pas une recherche globale de chemins aériens.

Chaque colonne de vol exige les tuiles base et cadastre, une hauteur finie issue du banc actif et l'absence d'eau source. Le contrôle n'utilise jamais le zéro de secours de `groundHeightAt`. Les mesures du centre et de quatre marges empêchent le relief de couper la silhouette. L'ensemble des ailes animées tient dans un rayon de 0,96 m et une tranche verticale conservatrice de +0,10 à +1,35 m par rapport à la position de l'acteur.

Les mouvements balaient cette enveloppe tous les 18 cm au plus, contre les collisions source et les objets de jeu à leur véritable hauteur. Le Gabian peut rester sous un plafond assez haut ou passer au-dessus d'un toit bas ; il ne traverse ni façade, plafond ni relief. Quand la direction est bloquée, il essaie une composante horizontale à hauteur constante, deux tangentes puis une montée locale validée. Sans passage valide, il attend. Aucune colonne absente ou aquatique ne devient un plancher inventé ; sa préparation d'attaque est alors annulée.

Après le délai visible, le sac libère une goutte réelle : position, vitesse horizontale vers la cible verrouillée, gravité de 9,8 m/s², limite de vie de 3 s. Le projectile est rendu pendant sa chute et balaie le trajet tous les 5 cm au plus. Son rayon de 7 cm s'applique dans les trois dimensions pour rencontrer aussi les dalles très minces, le terrain et les façades/toits. Un impact n'applique les dégâts hérités que dans son rayon de 0,85 m, à hauteur compatible et avec une ligne de vue libre ; s'écarter de la cible verrouillée permet de l'éviter. Les obstacles ou une couverture manquante empêchent un dégât à travers le décor. Le registre volatil est borné à 32 projectiles, 16 effets d'impact et 8 constats d'impact ; un changement de monde ou de campagne les retire.

Le temps de vol, la préparation et la chute s'arrêtent dans les menus. Le danger aérien participe à l'état de combat et à l'affichage furtif existants. Le sol et les collisions restent obtenus par les fonctions de production, sans dépendance à un nouveau format de fichier terrain.

La position aérienne et les blessures sont sauvegardées par v049. À la restauration, un Gabian déjà assigné peut reprendre son altitude si son volume est toujours admissible. Les phases visuelles et les projectiles transitoires ne sont pas des récompenses persistantes ; ils ne sont pas recréés par le chargement.

## Ciblage et restes

Le rig v025 fournit simultanément les éléments visibles, les parties VATS et leurs volumes orientés. Les huit coins de chaque élément avec sa rotation propre entrent dans le volume de sa partie. Ailes, tymbales, couronne, câble, lecteur, tampon et roues utilisent les groupes de dégâts reconnus par v025/v049. VATS fige le temps de pose ; la réduction des mouvements fige les oscillations automatiques.

Les empreintes sont contrôlées : 0,90 m pour Rat-câble/CERFA, 0,96 m pour Gabian, 0,98 m pour Rat-couronné, 1 m pour Cigale, 1,48 m pour Radscorpion et 1,28 m pour Fangeux. Les espèces terrestres gardent leur IA de base, avec la validation de cette empreinte ; une dérive d'attente hors du sol admissible est annulée.

La mort utilise les fonctions existantes et le même conteneur `territory|remains:<identifiant>`. Aucun deuxième butin n'est créé. Le Gabian mort rejoint directement le support mesuré ou le dessus de toit admissible sous lui ; il n'y a pas encore d'animation de chute du cadavre. Sans source valide, aucun support n'est inventé. Ses quantités initiales et restantes, le type d'acteur, les prélèvements déjà faits et les retours après déchargement gardent leurs propriétaires v026/v049. Le cadavre de chaque espèce reprend sa silhouette couchée et les marqueurs v026.

## Vérification

```sh
node --check src/v050/13_regional_bestiary.js
node tests/expansion/regional_bestiary.cjs
python -m py_compile tests/expansion/regional_bestiary_native.py
```

Les 87 cas du harnais exécutent le vrai catalogue v042, la publication v047, `addEnemy`, `damageEnemy`, `killEnemy`, les rigs v025, l'IA de base et les télégraphes v021, la récupération physique v026 et les wrappers v049. Ils couvrent les sept créations, les 41 associations précédentes et les 21 premières associations historiques, les anciennes campagnes, la publication avec checkpoint intermédiaire, les sauvegardes de blessures/altitude, le butin fini, les plafonds/toits/parois minces/relief, les sources manquantes, le projectile réel, l'impact et l'esquive. Terrain, scène, stockage et interface restent des fournisseurs contrôlés : ces tests ne sont pas des mesures géographiques supplémentaires.

Le pilote HTTP `regional_bestiary_native.py`, avec `--require-iconic`, exige en plus un Radscorpion et un Fangeux réellement admis, leurs assemblages et préparations d'attaque produites par la véritable IA, le ciblage VATS de leurs pinces, des captures sans retouche et la sauvegarde de leurs identités. La restauration exacte de la position est lue avant tout nouveau pas de l'IA ; le pas actif suivant et son recalage au sol mesuré sont contrôlés séparément. Il est préparé pour un Gabian réellement admis, son altitude et son volume libres au-dessus du pack installé, un projectile esquivé par marche réelle sous pas de simulation, et au moins un Rat-couronné ou une Cigale visible à un slot existant. Il exige des SHA coordonnés et `--run`. Il n'injecte ni acteur, source, HTML ni sauvegarde historique et n'utilise que les diagnostics publics. Une exécution doit conserver ses captures et son rapport séparément de la preuve historique du Rat-câble de la livraison précédente.

Sur le HTML final `ed6e4103b23a45c413fef182862a93accb72ec25c6e1d8b101251822bfd5c670`, avec le module 13 `aaf56e869b694105a3b89e594e32742b6c03e3f2000e935393df6f4dfde7c79b`, le parcours étendu a réussi **125 contrôles**, avec **neuf captures réelles** et un processus de code **0**. Il conserve l'ancien trajet Rat-couronné/Gabian et ajoute le Radscorpion `v042:v042-calanques-elite-03:outside:1` et le Fangeux `v042:v042-laciotat-elite-03:outside:1` : géométrie native, VATS au clavier sans dépense, préparation réelle, sauvegarde/Continuer et deux retours géographiques. Les cinq points de terrain et les collisions proches sont consignés avant la sauvegarde et au retour. Le contexte et le navigateur sont fermés avant la fin du pilote et le port HTTP est vérifié fermé. Les matériaux restent procéduraux ; il ne s'agit pas d'art final.

Le parcours réussi de 125 contrôles sur l'ancien HTML `c947e444` reste historique et distinct, sans changement d'empreinte. Les tentatives antérieures sont conservées séparément : une recherche de Fangeux limitée aux Calanques n'avait pas trouvé d'admission ; un contrôle de position était placé après le recalage physique hérité, même avec un `dt` nul. Une autre tentative a conservé le registre, le type et les PV du Fangeux mais a refusé son rig régional à la réadmission. La cause exacte de ce dernier refus n'a pas été capturée au moment de l'admission : elle n'est ni attribuée sans preuve au terrain ni déclarée corrigée. Le dernier parcours valide les deux restaurations à ses positions enregistrées, différentes de 0,366 m horizontalement entre la tentative refusée et le parcours historique réussi `c947e444` pour le Fangeux ; il ne certifie pas toutes les positions possibles. Le correctif démontré séparément sur fixture ne lui attribue pas cette cause ; il conserve le corps entier et les quatre contrôles de MNT/eau/hauteur, avec la marge supplémentaire réservée à la première création.

Après `v053BestiaryAfterInit`, les diagnostics en lecture seule sont :

- `v053BestiaryInfo()` : acteurs présents, slots admissibles, refus, volumes/hauteurs de vol, projectiles et huit derniers impacts avec leur résultat ;
- `v053BestiaryCatalog()` : définition des sept espèces ;
- `v053BestiaryActor(id)` : état et géométrie clonée d'un acteur présent.

Ces diagnostics ne créent ni rencontre ni récompense. Exemples de slots existants, sans garantie d'admission sur un sol donné : `v042:v042-huveaune-nest-01:outside:0` (Rat-câble), `v042:v042-huveaune-nest-01:outside:1` (Rat-couronné), `v042:v042-garlaban-nest-01:outside:1` (Cigale) et `v042:v042-marseille-nest-05:outside:0` (Gabian), `v042:v042-calanques-nest-03:outside:1` (Radscorpion) et `v042:v042-calanques-nest-01:outside:1` (Fangeux).
