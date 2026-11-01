# Statut de production — 1er novembre 2026

La poursuite de `29df190` améliore la vue FPS et avance six chantiers en parallèle. Le programme vérifié est le HTML `98a78a1cd1ca8748d12f206ec5f5fe3562706b00057b84628343f22d36560241`. Le [bilan courant](../verification/expansion/continuation_20261101/CONTINUATION_INTEGRATION.json) rattache chaque méthode, script, sortie réelle et capture à ces octets.

| Chantier | Comportement livré | Portée et limite |
| --- | --- | --- |
| FPS et HUD | Treize profils dans neuf familles, huit alimentations distinctes, prises relevées, visée LT/X/souris, retours des tirs et PV réellement appliqués, délai de rechargement et sous-titres repositionnés. | Modèles originaux stylisés ; poignets partiellement sous le HUD en portrait. Les dégâts, directions et FOV du monde gardent leurs règles. |
| Lieux connus | MNS IGN natif de 0,50 m de la Major/Garde conservé ; chapelle de la Vieille Charité et Pharo ajoutés : dix-huit composantes admissibles sur dix-neuf. | Surfaces supérieures mesurées, sans relevé de façade ou de pièces. Pharo contextuel, Charité au sol masquée dans la capture ; vues élevées assistées. |
| Zones du nord | Estaque et Saint-Antoine : 206 240 nœuds rééchantillonnés au plus proche, au pas demandé de 1 m ; imports communaux chargés et anciens lots revisités. | Deux rectangles locaux ; les 12 km² centraux natifs de 0,50 m et les 384 832 nœuds sud restent distincts. Aucun port ou gare intégralement reconstruit par ces rasters. |
| Intérieurs | E ouvre les dépôts des rangements existants : dix-neuf fournitures ordinaires, sept familles de meubles, capacités de 10 à 45 kg, 512 dépôts non vides au maximum. | Dispositions et signatures 1–5 conservées ; dépôts initialement vides, locaux au bâtiment/étage/meuble. Les aménagements non relevés restent inventés. |
| Lore | Reçus des Communes/Gilets remis au second relais, retour au donneur et contre-don fini selon le choix, journal/radio/suivi/Continuer. | Les huit dossiers et leurs choix sont conservés. Récit original fondé sur le canon sauvegardé, sans nouvelle conversation privée récupérée. |
| Contenu emblématique | Deux distributeurs Nuka-Cola, réparation réelle, achats classiques/Quantum, consommation et stock partagé avec leurs relais géographiques, sans apparition dans le volume du joueur. | Mobilier inventé. Stocks finis, paiement de 30/65 capsules ; réparation de deux ferrailles et un circuit. Les anciens systèmes emblématiques restent présents. |

## Vérification du programme courant

**3 310 contrôles descriptifs**, **76 événements de capture**, **13 méthodes** et **361 empreintes**. Les méthodes se chevauchent ; les modèles, comparaisons d’octets et parcours assistés ne sont pas autant de parties humaines.

| Méthode | Contrôles confirmés |
| --- | ---: |
| Modèles et outils, fixtures contrôlées | 1 763 |
| Reconstruction indépendante, comparaisons d’octets | 3 |
| HTTP isolé, dépendances Python standard | 3 |
| Contrats hérités, géométries et réseau contrôlés | 434 |
| Vue FPS native | 142 |
| Retours de combat FPS natifs | 44 |
| HUD natif, formats et commandes | 90 |
| DOM avec API Gamepad simulée | 63 |
| Surfaces MNS natives, quatre sites | 64 |
| Intérieurs, portes, services et dépôts natifs | 122 |
| Dossiers et contre-dons natifs des factions | 472 |
| Distributeurs Nuka-Cola natifs | 64 |
| Relief nord natif et anciens lots revisités | 46 |
| **Somme descriptive** | **3 310** |

Les quarante et une suites de modèles regroupent vingt-six suites terminées avant l’interruption de l’environnement et quinze reprises avec les mêmes empreintes. Chaque sortie enfant et journal est vérifié, sans suite comptée deux fois ; la sortie globale de l’ancien processus interrompu reste non observée. Les quinze processus des contrats hérités ont tous terminé réellement avec le code zéro.

Après les parcours natifs, le seul adaptateur de test `tools/check_v050.py` a aligné son cache attendu sur la version PWA13. Le code du jeu et le HTML restent identiques ; l’ancien attendu12, ses deux échecs, le diff d’une ligne et les empreintes avant/après sont archivés. Les scripts exécutés des modèles et des parcours natifs restent vérifiés strictement. Les captures transitoires finales conservent état DOM avant/après et durée de capture, sans remplacer l’horloge du jeu.

## Portée et chantiers ouverts

La commune conserve ses 290 partitions, 291 001 identifiants d’objets bâtiment, 55 449 tronçons routiers et 118 partitions d’eau. La campagne, les armures assistées, collections, dépendances, soins, bestiaire, bivouac, entraide, portes, grenades et mines restent disponibles.

**La reproduction intégrale 1:1 de toutes les façades et de tous les intérieurs de Marseille reste non certifiée.** Les maillages FPS sont stylisés et les programmes non documentés sont inventés. L’art final, les voix, l’équilibrage, les performances sur appareils physiques et la visite humaine exhaustive restent ouverts. Le tactile et l’API Gamepad sont émulés dans leurs méthodes respectives.

En petit paysage tactile, une notification d’armure peut passer sous assistance/suivi ; les jauges et commandes principales vérifiées restent séparées. Certaines vues de mobilier sont rapprochées, les surfaces MNS sont rugueuses et les vues élevées montrent des artefacts d’eau hérités. Ces limites sont gardées dans les fiches visuelles, sans retouche d’image.

Les éléments du projet ChatGPT accessibles auparavant n’apportaient pas de récit supplémentaire exploitable. Les neuf factions, huit dossiers historiques et vingt-cinq noms conservés demeurent la source du canon. Aucune nouvelle récupération de conversation n’est revendiquée.

## Bilans historiques

Les [2 892 contrôles et 55 captures de `29df190`](../verification/expansion/immersion/IMMERSION_INTEGRATION.json), sur `844376c0…`, les [2 887 contrôles et 62 captures de Wasteland](../verification/expansion/wasteland/WASTELAND_INTEGRATION.json), sur `ed6e4103…`, et les [2 324 contrôles et 42 captures de précision](../verification/expansion/precision/PRECISION_INTEGRATION.json) restent immuables. Le dossier de preuve `continuation` antérieur est également conservé ; la livraison courante utilise `continuation_20261101`. Ces anciens résultats ne sont pas réattribués au programme courant.

[Chantiers](CHANTIERS_ACTIFS.md) · [Vue FPS](VUE_FPS.md) · [HUD](HUD_FPS.md) · [MNS](SILHOUETTES_MNS.md) · [Relief nord](RELIEF_NORD_MARSEILLE.md) · [Intérieurs](INTERIEURS_USAGES.md) · [Lore](LORE_CONTINUITE.md) · [Distributeurs](DISTRIBUTEURS_NUKA_COLA.md).
