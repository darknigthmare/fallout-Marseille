# Chantiers du 28 octobre 2026

La vue FPS et le HUD sont la priorité de cette livraison. Les lieux connus, les zones du sud, les services intérieurs, les factions et les mines avancent en parallèle sur le même programme `844376c014575111f268f292c8307bb3f47ac33629604406f5e0da00104c5a34`. Le [bilan d’intégration](../verification/expansion/immersion/IMMERSION_INTEGRATION.json) rattache chaque preuve au HTML effectivement exécuté.

| Chantier | Comportement livré | Portée et limite |
| --- | --- | --- |
| Vue FPS et HUD | Mains articulées, avant-bras et neuf familles d’armes ; prise, visée maintenue, rechargement, recul et abaissement près d’un mur. Jauges, boussole, objectifs et commandes réorganisés, HUD compact et préférences conservées. | Modèles stylisés par famille ; pas un modèle unique pour chaque arme. Les contrôles et la direction de tir du monde gardent leurs règles. Les formats émulés ne certifient pas un appareil physique. |
| Lieux connus | Surfaces supérieures MNS IGN de 0,50 m à la Major et Notre-Dame de la Garde, avec rendu et collision concordants : seize composantes admissibles sur dix-sept. | Une composante est refusée sous sa base historique. Le MNS décrit le sursol acquis, sans relevé de façade ni plan de pièces. |
| Zones du sud | Deux fenêtres autour du Vélodrome et de Borély : 384 832 nœuds MNT importés au pas demandé de 1 m, au plus proche de GeoTIFFs natifs de 0,50 m. | Deux rectangles locaux ; le treillis central natif de 12 km² et les anciennes grilles restent distincts. Les rasters de sol ne reproduisent pas le stade ou le château. |
| Intérieurs | E utilise les lits, cuisines et établis admissibles déjà placés, avec approches physiques, fournitures ordinaires, effets et compteurs sauvegardés. | Les dispositions et signatures des layouts 1–5 sont conservées. Le mobilier et les usages sans relevé sont inventés ; le parcours natif vérifie l’établi et sa réserve, les autres services ont des contrats contrôlés. |
| Lore | Huit dossiers de continuité, dont les nouveaux engagements des Communes et des Gilets : deux relais nommés, décisions exclusives, coûts finis, réputations, radio, dialogues et Continuer. | Les six dossiers précédents et le canon du dépôt restent conservés. Les nouvelles histoires sont des prolongements originaux, sans nouvelle conversation privée récupérée. |
| Contenu emblématique | Mines à fragmentation posées avec P, récupérables par E, stock et recette finis, armement, avertissement, souffle occulté et persistance par scène/étage. | Vingt-quatre mines posées au maximum ; pas de réaction en chaîne. Les protections historiques des PNJ et la dernière sauvegarde vivante restent les règles du jeu. |

## Ce qui reste ouvert

- **Fidélité de Marseille.** Étendre les relevés au-delà des fenêtres acquises, documenter les façades et les pièces, traiter les absences et visiter les accès. Les contours IGN, le MNT et le MNS ne constituent pas un modèle architectural complet.
- **Art et mise en scène.** Donner à chaque arme et personnage ses finitions, développer les animations, les voix et les effets. Les neuf familles FPS sont des formes stylisées originales.
- **Intérieurs et circulation.** Documenter les plans disponibles, approfondir les usages inventés et vérifier les grands volumes. Les services s’appuient sur les meubles admissibles, avec des omissions exposées.
- **Campagne et équilibrage.** Développer les conséquences du canon existant, les branches et la progression avec les réserves finies, sans promettre de systèmes physiques absents.
- **Matériel et parcours complets.** Tester les performances, le tactile et les manettes sur appareils physiques, puis les parties humaines continues. Les aides et API émulées de la QA actuelle restent identifiées.

La campagne, les armures assistées, figurines, magazines, Nuka-Cola, consommables et dépendances, bestiaire, grenades, bivouac, entraide et navigation existants restent disponibles. Le canon vient des dossiers conservés dans le dépôt ; la consultation du projet ChatGPT n’a pas fourni de récit supplémentaire exploitable.

## Preuves courantes

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

Le bilan retient **2 892 contrôles descriptifs et 55 événements de capture native**, issus de treize méthodes distinctes. Les 350 entrées du gel de production, les scripts exécutés, aides, erreurs réseau brutes et limites sont identifiés dans le bilan. Les modèles, parcours assistés, octets comparés et entrées simulées ne sont pas autant de parties équivalentes.

La commune conserve ses 290 partitions, 291 001 identifiants d’objets bâtiment, 55 449 tronçons routiers et 118 partitions d’eau. Le relief central de 0,50 m couvre 12 km² ; les deux fenêtres méridionales de 1 m et les autres grilles ont leur propre provenance. Les associations documentaires, le MNS supérieur et les programmes inventés restent distingués.

La reproduction intégrale 1:1 de toutes les façades et de tous les intérieurs de Marseille reste non certifiée. L’art final, les voix, l’équilibrage complet, les performances sur matériels variés et la visite humaine exhaustive restent ouverts. Les modèles d’armes sont stylisés par famille et les aménagements non relevés sont des créations du jeu. Les API Gamepad et contextes tactiles émulés ne certifient pas de périphérique physique.

Les [2 887 contrôles et 62 captures de `f4a7337`](../verification/expansion/wasteland/WASTELAND_INTEGRATION.json), sur le HTML `ed6e4103b23a45c413fef182862a93accb72ec25c6e1d8b101251822bfd5c670`, restent historiques. Le [bilan de précision antérieur](../verification/expansion/precision/PRECISION_INTEGRATION.json) conserve ses 2 324 contrôles, 42 captures et ses propres sources ; ses 288 comparaisons de cellules ne sont pas recomptées. Aucun de ces bilans ne valide automatiquement le programme courant.

[État de production](STATUT_PRODUCTION.md) · [Marseille entière](MARSEILLE_ENTIERE.md) · [Commandes](CONTROLES.md).
