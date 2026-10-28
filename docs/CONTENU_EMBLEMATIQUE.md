# Objets et gestes emblématiques du Wasteland — 28 octobre 2026

Les systèmes S.P.E.C.I.A.L., V.A.T.S., avantages, radiations, Stimpaks/RadAway, crochetage, terminaux, compagnons, Pip-Boy, radio et plusieurs créatures de Fallout étaient déjà présents. Les collections de figurines, lectures temporaires et bouteilles de Nuka-Cola sont conservées. La livraison actuelle ajoute la pose de mines et une présentation FPS enrichie des armes et armures, avec usages physiques du mobilier et nouveaux engagements de factions. Les modèles et placements sont des créations du jeu ; ce ne sont ni des relevés IGN ni des assets récupérés d’un jeu commercial.

## Figurines S.P.E.C.I.A.L.

Sept figurines physiques correspondent à Force, Perception, Endurance, Charisme, Intelligence, Agilité et Chance. Une interaction à proximité récupère l’exemplaire et ajoute **un point permanent**, une seule fois, à l’attribut correspondant, dans la limite de **10**. Une fiche déjà au maximum conserve la figurine sans dépasser cette limite. Endurance et Agilité recalculent aussi les maxima de PV et de PA selon les règles existantes.

Les scènes narratives d’Aubagne, Marseille, Font de Mai, Saint-Charles, des Céramistes, du Panier et du Vieux-Port de La Ciotat proposent ces exemplaires. Leurs relais géographiques utilisent **les mêmes identifiants de collection** : passer d’une scène à l’autre ne donne pas un deuxième bonus. La sauvegarde conserve la fiche modifiée et le registre de collecte ; la migration ne réapplique pas la récompense.

Dans le Pip-Boy, **DATA → COLLECTION** affiche les figurines récupérées et les règles de progression. Le panneau ne permet pas de prendre un objet à distance.

## Magazines d’aptitudes

Quatre lectures rejoignent la rubrique **INV → AIDE** :

| Magazine | Effet de lecture |
|---|---|
| Le Mécano du désert | Réparation +10 |
| Médecine de terrain | Médecine +10 |
| Science ! · édition Mistral | Science +10 |
| Armes et munitions · fiche de tir | Balistique +10 |

La lecture consomme un exemplaire et applique le bonus pendant **120 secondes de simulation active**, avec un plafond d’aptitude de **100**. Les menus et chargements ne réduisent pas la durée. Une même aptitude déjà renforcée ne consomme pas un autre exemplaire et ne cumule pas les points. Les effets et lectures restent enregistrés après **Continuer**.

Les exemplaires fixes apparaissent dans les scènes déjà jouables de l’Atelier des souffles, de l’Annexe des Veilleurs, de la Traverse des Archives et de la station de mouillage, ainsi que dans leurs relais géographiques. La lecture intervient dans les calculs d’aptitude utilisés par les tests existants ; elle n’accomplit pas une quête à la place du joueur.

## Nuka-Cola et Quantum

Les bouteilles sont visibles dans le monde et se prennent par l’interaction habituelle. Leur consommation s’effectue depuis **INV → AIDE** ou le sac.

| Boisson | PV | PA | Radiations | Capsule récupérée |
|---|---:|---:|---:|---:|
| Nuka-Cola | +12 | +20 | +2 | 1 |
| Nuka-Cola Quantum | +20 | +60 | +5 | 1 |

Les PV et PA respectent les maxima actuels, et les radiations restent dans la plage du jeu. Une dose retire une bouteille et applique ses effets dans la même opération sauvegardée. Les prix de référence dépassent la capsule récupérée ; consommer ne crée pas une boucle d’achat rentable.

Les bouteilles et magazines possédés peuvent être revendus au comptoir par les contrôles habituels. Le prix de reprise reste inférieur au prix d’achat du même objet dans le contexte courant, y compris avec les remises de réputation : un aller-retour immédiat ne crée pas de capsules. Leur revente alimente le stock fini du marchand, sans ajouter un nouvel approvisionnement automatique.

À la première création de certaines réserves inventées d’intérieurs municipaux, un tirage déterministe ajoute aussi une bouteille ou un magazine. Ce contenu est fini. Les réserves déjà existantes, les coffres appartenant à des habitants et les caches de quête ne sont pas réapprovisionnés par cette extension.

## Placement et persistance

Les présentoirs possèdent leurs modèles procéduraux et collisions propres. Leur support permet de monter puis de redescendre sans tomber à l’intérieur du solide. Les placements évitent les obstacles, les habitants, les dangers et les accès prioritaires ; la géographie réelle et ses colliders ne sont pas remplacés par des boîtes.

En extérieur géographique, le jeu exige un relais sûr actif, un terrain source utilisable et une marge libre. Une altitude absente ou un emplacement devenu impraticable refuse le placement ou la prise ; aucune hauteur de terrain n’est fabriquée. La couche géographique désactivée et le laboratoire synthétique ne donnent pas ces récompenses.

Collecte, lecture, consommation et troc contrôlent leur contexte actif. Une écriture de sauvegarde refusée ou une exception annule le changement de fiche, d’objet et de capsules. Pour un achat ou une vente, les deux bourses, le stock et le journal sont également restaurés ; une seule écriture conserve l’opération complète. Changer d’étage, de scène ou de session ne permet pas de doubler une figurine ou de renouveler une réserve vidée.

Le budget global reste borné à treize exemplaires fixes, avec des modèles de cinq à douze primitives chacun ; seuls les exemplaires du lieu courant sont ajoutés. Les [consommables et dépendances](CONSOMMABLES_ET_DEPENDANCES.md) gardent leurs effets, tolérance, retrait et traitement sauvegardés. La collection, les animations et les assets finaux de toute la franchise restent un chantier ouvert.

## Grenades et créatures récurrentes

Les [grenades à main](GRENADES_A_MAIN.md) possèdent une trajectoire, une fusée sauvegardée, des rebonds et des dégâts occultés, avec achat fini et fabrication réelle. N ou le bouton Grenade effectue le lancer depuis la position du personnage. Les [Radscorpions et Fangeux](BESTIAIRE_REGIONAL.md) reçoivent des modèles originaux, des membres VATS et des préparations d’attaque sur les créatures déjà présentes ; leurs identités, PV et butins restent ceux de la sauvegarde.


## Mines et préparation d’un passage

Les [mines à fragmentation](MINES_A_FRAGMENTATION.md) se posent par **P**, sur un sol libre, chargé et presque horizontal. Elles s’arment après 2,5 secondes actives ; un ennemi proche au même niveau et visible déclenche un avertissement de 0,65 seconde. **E** permet de désamorcer et reprendre l’exemplaire à portée. Le joueur et les civils ne les déclenchent pas, mais le souffle peut blesser le joueur.

Le stock est fini : deux mines chez Baptiste et deux à Noailles. Un établi permet d’en fabriquer avec quatre ferrailles, trois composants chimiques et un circuit. Le sac, le poids, la bourse et les recettes restent ceux du jeu. Les positions, scènes, étages, phases et délais sont sauvegardés, avec au plus 24 mines posées. Les menus, supports absents et scènes non chargées suspendent les délais ; voyager ne déplace pas une mine. La réaction en chaîne n’est pas implémentée.

## Mains, armures et mobilier

La [vue FPS](VUE_FPS.md) présente mains articulées, manches, avant-bras, terminal de poignet et gantelets des armures reconnues. Neuf familles d’armes ont des formes stylisées distinctes, avec pose de soutien, rechargement, recul, sprint et abaissement près des murs. Chaque arme du catalogue n’a pas un modèle unique. X, le clic droit capturé et Visée maintiennent la présentation dans l’axe ; les règles de direction et de dégâts du monde restent conservées. Le [HUD](HUD_FPS.md) réunit jauges, munitions, boussole et suivi, avec préférences et réduction des mouvements.

Les lits, cuisines et établis admissibles des [intérieurs](INTERIEURS_USAGES.md) proposent leurs usages par E, avec coûts ordinaires et réserve finie. Les huit [dossiers de continuité](LORE_CONTINUITE.md), dont les Communes du Mistral et les Gilets de Cendre, relient rencontres, décisions, fournitures, réputations et radios textuelles. Les programmes intérieurs non relevés et les nouveaux récits sont des créations du jeu.

Le [bilan courant](../verification/expansion/immersion/IMMERSION_INTEGRATION.json) identifie le HTML `844376c014575111f268f292c8307bb3f47ac33629604406f5e0da00104c5a34`. Les méthodes de modèle et les parcours natifs assistés sont distincts ; les 2 892 contrôles descriptifs et 55 captures gardent leur méthode et leurs limites. Les anciens résultats de [Wasteland](../verification/expansion/wasteland/WASTELAND_INTEGRATION.json), 2 887 contrôles et 62 captures sur `ed6e4103…`, et de [précision](../verification/expansion/precision/PRECISION_INTEGRATION.json), 2 324 contrôles, restent historiques. Les créations stylisées, les contextes émulés et les mesures géographiques partielles ne certifient ni Marseille intégralement en 1:1 ni du matériel physique.
