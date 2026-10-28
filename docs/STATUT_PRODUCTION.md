# Statut de production — 28 octobre 2026

La livraison poursuit `f4a7337` avec une vue FPS enrichie et des progrès parallèles sur les lieux, le relief, les intérieurs, le lore et les mines. Le programme courant est le HTML `844376c014575111f268f292c8307bb3f47ac33629604406f5e0da00104c5a34`. Le [bilan d’intégration](../verification/expansion/immersion/IMMERSION_INTEGRATION.json) distingue les preuves de chaque chantier.

| Chantier | Comportement livré | Portée et limite |
| --- | --- | --- |
| Vue FPS et HUD | Mains articulées, avant-bras et neuf familles d’armes ; prise, visée maintenue, rechargement, recul et abaissement près d’un mur. Jauges, boussole, objectifs et commandes réorganisés, HUD compact et préférences conservées. | Modèles stylisés par famille ; pas un modèle unique pour chaque arme. Les contrôles et la direction de tir du monde gardent leurs règles. Les formats émulés ne certifient pas un appareil physique. |
| Lieux connus | Surfaces supérieures MNS IGN de 0,50 m à la Major et Notre-Dame de la Garde, avec rendu et collision concordants : seize composantes admissibles sur dix-sept. | Une composante est refusée sous sa base historique. Le MNS décrit le sursol acquis, sans relevé de façade ni plan de pièces. |
| Zones du sud | Deux fenêtres autour du Vélodrome et de Borély : 384 832 nœuds MNT importés au pas demandé de 1 m, au plus proche de GeoTIFFs natifs de 0,50 m. | Deux rectangles locaux ; le treillis central natif de 12 km² et les anciennes grilles restent distincts. Les rasters de sol ne reproduisent pas le stade ou le château. |
| Intérieurs | E utilise les lits, cuisines et établis admissibles déjà placés, avec approches physiques, fournitures ordinaires, effets et compteurs sauvegardés. | Les dispositions et signatures des layouts 1–5 sont conservées. Le mobilier et les usages sans relevé sont inventés ; le parcours natif vérifie l’établi et sa réserve, les autres services ont des contrats contrôlés. |
| Lore | Huit dossiers de continuité, dont les nouveaux engagements des Communes et des Gilets : deux relais nommés, décisions exclusives, coûts finis, réputations, radio, dialogues et Continuer. | Les six dossiers précédents et le canon du dépôt restent conservés. Les nouvelles histoires sont des prolongements originaux, sans nouvelle conversation privée récupérée. |
| Contenu emblématique | Mines à fragmentation posées avec P, récupérables par E, stock et recette finis, armement, avertissement, souffle occulté et persistance par scène/étage. | Vingt-quatre mines posées au maximum ; pas de réaction en chaîne. Les protections historiques des PNJ et la dernière sauvegarde vivante restent les règles du jeu. |

## Vérification du programme courant

Le bilan retient **2 892 contrôles descriptifs sur treize méthodes et 55 événements de capture native**, avec 350 empreintes de sources et de construction. Les méthodes se chevauchent et ne représentent pas autant de parties.

| Méthode sur le programme courant | Résultat confirmé |
| --- | ---: |
| Modèles et outils, 39 suites | 1 605 |
| Reconstruction indépendante, sorties identiques | 3 |
| Distribution HTTP isolée | 3 |
| Vue FPS native | 67 |
| HUD natif, interfaces et formats | 90 |
| Surfaces MNS natives, Major et Garde | 44 |
| Intérieurs, portes et services natifs | 94 |
| Dossiers natifs des Communes et des Gilets | 327 |
| Mines natives | 70 |
| Relief sud natif | 39 |
| Contrats hérités contrôlés | 434 |
| DOM avec API Gamepad simulée | 54 |
| Grenades natives | 62 |
| **Somme descriptive** | **2 892** |

Le gel de production identifie 350 entrées. Les preuves contrôlées, comparaisons d’octets/HTTP et parcours Chromium assistés sont des méthodes différentes, avec des périmètres qui se chevauchent. Les aides de positionnement, de préparation et les entrées simulées sont déclarées. Les essais échoués, interrompus ou visant un autre HTML restent séparés du résultat courant.

## Portée conservée

La campagne, les armures assistées, collections, dépendances et soins, bestiaire, bivouac, entraide, mer, portes et grenades des livraisons précédentes restent présents. Les ajouts de données géographiques de cette livraison sont les surfaces MNS des deux sites et les deux fenêtres MNT du sud.

La commune conserve ses 290 partitions, 291 001 identifiants d’objets bâtiment, 55 449 tronçons routiers et 118 partitions d’eau. Le relief central de 0,50 m couvre 12 km² ; les deux fenêtres méridionales de 1 m et les autres grilles ont leur propre provenance. Les associations documentaires, le MNS supérieur et les programmes inventés restent distingués.

La reproduction intégrale 1:1 de toutes les façades et de tous les intérieurs de Marseille reste non certifiée. L’art final, les voix, l’équilibrage complet, les performances sur matériels variés et la visite humaine exhaustive restent ouverts. Les modèles d’armes sont stylisés par famille et les aménagements non relevés sont des créations du jeu. Les API Gamepad et contextes tactiles émulés ne certifient pas de périphérique physique.

Le projet ChatGPT correspondant a été consulté ; les éléments accessibles n’ajoutent pas de lore exploitable et ses archives ne sont pas accessibles depuis cet environnement. Les neuf factions, huit dossiers historiques et vingt-cinq noms déjà conservés dans le dépôt demeurent le canon.

Les [2 887 contrôles et 62 captures de `f4a7337`](../verification/expansion/wasteland/WASTELAND_INTEGRATION.json), sur le HTML `ed6e4103b23a45c413fef182862a93accb72ec25c6e1d8b101251822bfd5c670`, restent historiques. Le [bilan de précision antérieur](../verification/expansion/precision/PRECISION_INTEGRATION.json) conserve ses 2 324 contrôles, 42 captures et ses propres sources ; ses 288 comparaisons de cellules ne sont pas recomptées. Aucun de ces bilans ne valide automatiquement le programme courant.

[Vue FPS](VUE_FPS.md) · [HUD](HUD_FPS.md) · [MNS des monuments](SILHOUETTES_MNS.md) · [Relief sud](RELIEF_SUD_MARSEILLE.md) · [Intérieurs](INTERIEURS_USAGES.md) · [Lore](LORE_CONTINUITE.md) · [Mines](MINES_A_FRAGMENTATION.md) · [Installation](INSTALLATION_V050.md).
