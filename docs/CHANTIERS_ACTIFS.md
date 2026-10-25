# Chantiers du 25 octobre 2026

Cette livraison prolonge `833d687`. Les sources géographiques acquises restent distinguées des aménagements, objets et règles inventés. Le HTML courant est `120e04972fb08a6f59b929d8a0952010712cf3849b8e512c383ff3a8ae87d636` ; **la validation intégrée finale est réussie sur le périmètre livré**. Le [nouveau bilan](../verification/expansion/precision/PRECISION_INTEGRATION.json) conserve les résultats de ce programme, distincts des preuves historiques.

| Chantier | Périmètre de la nouvelle livraison | État de vérification |
| --- | --- | --- |
| Relief précis | 12 km² centraux, douze dalles LiDAR HD officielles, 48 morceaux natifs de 0,50 m Lambert-93/NGF-IGN69 ; anciennes données conservées ailleurs. | Sources et régressions validées ; parcours natif 78/78. Les 288 comparaisons ponctuelles Float32 sont des mesures source séparées. |
| Façades | Portes à panneaux, vitrage, vantaux, menuiseries et persiennes inventés, avec réservations et omissions de budget ; passage et segments source conservés. | Régressions et parcours architectural/menuiseries 135/135 validés, dans les budgets déclarés. |
| Intérieurs | Layout 4 par usages explicites, six équipements nouveaux, priorité aux fonctions principales, circulation et quantités déclarées ; dispositions sauvegardées 1/2/3 conservées. | Régressions et sauvegardes validées ; commerce et atelier IGN visités par E, collisions, Continuer et sorties vérifiés : 56/56. |
| Bestiaire régional | Cinq silhouettes du canon conservé ; vol borné et projectile réel du Gabian, Rat-couronné et Cigale sur des slots existants admissibles. | Cinq variantes éprouvées sur modèle ; parcours natif borné du bestiaire 40/40. Toutes les espèces ne sont pas annoncées comme capturées. |
| Consommables et soins | Jet, Buffout, Mentats et Psycho, effets temporaires, tolérance, retrait, stocks finis et soin local de Sofia avec transaction atomique. | Contrats des quatre familles validés ; boucle native Mentats/Sofia et reprise 74/74. |
| Manette | Favoris, lampe et plan, gaucher, neutralisation des commandes maintenues et pause à la déconnexion de la manette utilisée. | Modèle et pilote DOM/HTTP 54/54 validés avec API Gamepad simulée ; aucun matériel physique certifié. |
| Monde et chargement | Relief natif local prioritaire, banques publiées séparées des préparations, caches bornés, sources anciennes et contrôles terrain/eau/solides conservés. | Régressions et parcours finaux validés sur le HTML courant, avec préparations et aides déclarées. |
| Lore des factions | Quatre dossiers complémentaires de la livraison précédente conservés, avec preuves, décisions persistantes, réactions et radio textuelle. | Parcours intégré de continuité validé ; aucune conversation privée récupérée. |
| Armures assistées | Plaques, cœurs, configurations, quête et entretien des systèmes existants préservés. | Contrats de conservation et parcours intégré validés sur le programme courant. |
| Collections | Figurines SPECIAL, magazines et Nuka-Cola conservés, effets et acquisitions finies composés avec les nouveaux consommables. | Régressions de composition et parcours intégré validés, acquisitions finies conservées. |
| Diagnostics et installation | Restauration locale des six ZIP supplémentaires, vérification de taille/SHA, audit HTTP, reprise et conservation des imports valides. | Installations, serveurs réels, trois contrôles HTTP isolés et trois sorties identiques de reconstruction validés. |

## Périmètre de données

Le nouveau lot de relief ajoute **157 896 379 octets d’archives**, environ **150,58 Mio**, dans six ZIP. Les binaires extraits représentent **192 328 140 octets**, environ **183,42 Mio**. Il ne remplace pas les anciennes grilles hors de son support. Les 12 km² centraux ne constituent pas un LiDAR de 0,50 m sur toute la commune. [Relief précis](RELIEF_PRECIS.md).

Les détails de [façade](FACADES_MENUISERIES.md) et les [programmes intérieurs](INTERIEURS_USAGES.md) sont des créations métriques. Aucun relevé mesuré supplémentaire de baie, façade ou pièce n’a été acquis. Les documents déjà liés gardent leur géométrie et leur attribution ; un nom d’établissement ne devient pas une catégorie d’usage IGN.

## Validation livrée et preuves historiques

Le [bilan courant](../verification/expansion/precision/PRECISION_INTEGRATION.json) distingue les méthodes suivantes.

| Méthode sur le HTML courant | Contrôles réussis |
| --- | ---: |
| Unités et outils : 30 suites, aucun test ignoré | 1 241 |
| Contrats hérités : quinze processus de code 0 | 434 |
| Sorties identiques de reconstruction | 3 |
| Contrôles HTTP isolés du runtime | 3 |
| Parcours natif du relief précis | 78 |
| Parcours natif architectural et menuiseries | 135 |
| Parcours natif des usages intérieurs | 56 |
| Parcours natif du bestiaire régional | 40 |
| Parcours natif des consommables et du soin | 74 |
| Pilote DOM/HTTP de manette, API Gamepad simulée | 54 |
| Parcours natif de continuité : lore, armure, collections et Continuer | 206 |
| **Somme des contrôles par ces méthodes** | **2 324** |

Les méthodes peuvent couvrir les mêmes mécanismes : ces 2 324 contrôles ne sont pas 2 324 parcours équivalents. Les mesures sur fichiers source, les modèles et fixtures, les trajets assistés dans le vrai navigateur et le matériel simulé restent distingués. Les **288 comparaisons ponctuelles Float32 avec les GeoTIFF sources sont hors de cette somme**. Les **42 captures réelles** et **403 empreintes de production vérifiées** sont conservées avec leurs limites et leurs aides de placement ou de simulation. L’API Gamepad est simulée dans le pilote DOM ; aucun modèle de manette physique n’est certifié. Les tentatives interrompues, échouées ou visant un autre HTML restent séparées.

La livraison `833d687` conserve son [bilan historique](../verification/expansion/continuation/CONTINUATION_INTEGRATION.json), avec **1 847 contrôles et 23 captures natives** sur le HTML `ea8ba2e3d9ba9ed1925628672f4c596475ff2437de06bfa7979ee03f6f59f0bf`. Son pilote de bestiaire capturait une espèce, tandis que trois variantes étaient contrôlées sur banc. Ses comparaisons de façades — 191/191 portes ciblées, 187/191 cas avec fenêtres, 72/72 approches et jusqu’à 12 624 ouvertures paginées — étaient hors de ce total et ne dénombraient pas les portes de toute Marseille. Les [1 492 contrôles du 24 octobre](../verification/expansion/architecture/ARCHITECTURE_INTEGRATION.json) restent également historiques.

## Origine du lore

Les neuf factions, huit dossiers et vingt-cinq noms conservés dans la v0.46 constituent le canon disponible. Le projet ChatGPT correspondant a été retrouvé, mais la lecture de son historique reste limitée par le service. Aucun contenu de conversation non lu n’est présenté comme récupéré. Les dossiers complémentaires, formes de créatures et règles de jeu sont des prolongements écrits dans le dépôt ; les anciens fichiers v0.44 non accessibles ne sont pas déclarés restaurés.

## Travaux de plus longue durée

La couverture des requêtes IGN sur la commune et l’échelle métrique ne certifient pas chaque construction ni une fidélité documentaire et visuelle intégrale 1:1. Les relevés absents, limites de circulation, programmes partiels et budgets de rendu restent déclarés. Art final, voix enregistrées, équilibrage complet, performances sur matériels variés et visite humaine exhaustive restent des chantiers distincts.
