# Objets et gestes emblématiques du Wasteland — 2 novembre 2026

Les systèmes S.P.E.C.I.A.L., V.A.T.S., avantages, radiations, Stimpaks/RadAway, crochetage, terminaux, compagnons, Pip-Boy et radio étaient déjà présents. La poursuite du 2 novembre ajoute trois holobandes originales, les nouvelles formes de deux créatures existantes, le programme domestique de nouvelles habitations et des retouches FPS/HUD. Collections, consommables, distributeurs, grenades, mines et dossiers conservent leurs mécanismes. Les formes, positions et récits inventés restent distincts des relevés géographiques.

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

## Distributeurs à réparer

Deux [distributeurs Nuka-Cola](DISTRIBUTEURS_NUKA_COLA.md) originaux sont placés dans les scènes d’Aubagne et de Marseille. **E** ouvre le panneau depuis leur face ; chaque machine demande **deux ferrailles et un circuit** pour sa réparation unique. Le Nuka-Cola classique coûte **30 capsules**, le Quantum **65 capsules**.

| Machine | Bouteilles classiques | Quantum |
| --- | ---: | ---: |
| Ateliers d’Aubagne | 3 | 1 |
| Comptoir de Marseille | 4 | 1 |

Les relais géographiques correspondants partagent la réparation et les mêmes réserves finies. Acheter retire une bouteille du stock et l’ajoute à **INV → AIDE** ; une réentrée ou Continuer ne renouvelle rien. Le paiement, le stock et l’inventaire sont sauvegardés ensemble, avec restauration entière si l’écriture échoue. L’implantation géographique exige un sol source utilisable, une marge libre et le respect du volume du joueur ; modèles et positions restent inventés.

## Holobandes des relais

Trois [holobandes originales](HOLOBANDES.md), soit **quinze segments de transcription**, rejoignent le lecteur **RADIO → HOLODISQUES** existant. « La relève ne tient pas dans une colonne », « Le formulaire à deux colonnes » et « Canal 13 · la veille du passage » se trouvent aux ateliers d’Aubagne, à Marseille et à Saint-Charles, avec leurs contreparties géographiques.

**E** collecte chaque copie à proximité, avec regard, support et accès vérifiés. Scène narrative et relais représentent le même exemplaire. Le lecteur conserve transcription complète, segments, pause, vitesse et marque-page après Continuer. Les anciens holodisques gardent leurs états ; aucune seconde collection n’est créée. Ces bandes ne se consomment pas, ne se revendent pas, ne distribuent pas de récompense de quête et n’ajoutent ni voix enregistrée ni flux audio. Une sauvegarde refusée annule leur collecte.

Les trois nouveaux identifiants sont inclus dans le compteur global de bandes. Leur collecte ne déclenche toutefois pas encore les badges hérités des seuils **10, 30, 60 et 81**, dont le déclenchement appartient à l’ancien collecteur. Ce raccordement cosmétique reste ouvert ; aucune capsule, expérience ou ressource n’est liée à ces badges.

Les récits sont des créations du jeu fondées sur son canon conservé. Ils ne tranchent aucun dossier ouvert et ne sont pas présentés comme des conversations privées retrouvées.

## Placement et persistance

Les présentoirs possèdent leurs modèles procéduraux et collisions propres. Leur support permet de monter puis de redescendre sans tomber à l’intérieur du solide. Les placements évitent les obstacles, les habitants, les dangers et les accès prioritaires ; la géographie réelle et ses colliders ne sont pas remplacés par des boîtes.

En extérieur géographique, le jeu exige un relais sûr actif, un terrain source utilisable et une marge libre. Une altitude absente ou un emplacement devenu impraticable refuse le placement ou la prise ; aucune hauteur de terrain n’est fabriquée. La couche géographique désactivée et le laboratoire synthétique ne donnent pas ces récompenses.

Collecte, lecture, consommation et troc contrôlent leur contexte actif. Une écriture de sauvegarde refusée ou une exception annule le changement de fiche, d’objet et de capsules. Pour un achat ou une vente, les deux bourses, le stock et le journal sont également restaurés ; une seule écriture conserve l’opération complète. Changer d’étage, de scène ou de session ne permet pas de doubler une figurine ou de renouveler une réserve vidée.

Les figurines, magazines et bouteilles fixes restent bornés à treize exemplaires, avec des modèles de cinq à douze primitives chacun ; seuls les exemplaires du lieu courant sont ajoutés. Les deux distributeurs ont leur propre registre borné. Les [consommables et dépendances](CONSOMMABLES_ET_DEPENDANCES.md) gardent leurs effets, tolérance, retrait et traitement sauvegardés. La collection, les animations et les assets finaux de toute la franchise restent un chantier ouvert.

## Grenades et créatures récurrentes

Les [grenades à main](GRENADES_A_MAIN.md) possèdent une trajectoire, une fusée sauvegardée, des rebonds et des dégâts occultés, avec achat fini et fabrication réelle. N ou le bouton Grenade effectue le lancer depuis la position du personnage. Les [Radscorpions, Fangeux, Goules sauvages et Griffes de la mort](BESTIAIRE_REGIONAL.md) disposent de formes originales sur leurs acteurs existants. La poursuite enrichit les deux dernières silhouettes, leur préparation visuelle et leurs postures blessées. Les identités, règles d’attaque, statistiques et butins hérités restent autoritaires ; les assemblages ne s’imposent pas dans les volumes où ils ne tiennent pas.


## Mines et préparation d’un passage

Les [mines à fragmentation](MINES_A_FRAGMENTATION.md) se posent par **P**, sur un sol libre, chargé et presque horizontal. Elles s’arment après 2,5 secondes actives ; un ennemi proche au même niveau et visible déclenche un avertissement de 0,65 seconde. **E** permet de désamorcer et reprendre l’exemplaire à portée. Le joueur et les civils ne les déclenchent pas, mais le souffle peut blesser le joueur.

Le stock est fini : deux mines chez Baptiste et deux à Noailles. Un établi permet d’en fabriquer avec quatre ferrailles, trois composants chimiques et un circuit. Le sac, le poids, la bourse et les recettes restent ceux du jeu. Les positions, scènes, étages, phases et délais sont sauvegardés, avec au plus 24 mines posées. Les menus, supports absents et scènes non chargées suspendent les délais ; voyager ne déplace pas une mine. La réaction en chaîne n’est pas implémentée.

## Mains, armures et mobilier

La [vue FPS](VUE_FPS.md) conserve ses mains articulées, treize profils dans neuf familles et huit alimentations de recharge. X, clic droit, Visée et LT maintiennent la présentation dans l’axe ; la transition et la rotation cyclique sont retravaillées sans annoncer de nouvelle règle de dégâts. Les notifications du [HUD](HUD_FPS.md) emploient 12 px, cherchent une bande libre et peuvent défiler. Les modèles restent stylisés ; les formats réellement exécutés relèvent du bilan de validation.

Les lits, cuisines et établis admissibles des [intérieurs](INTERIEURS_USAGES.md) conservent leurs services par E. Sept types de rangements déjà placés permettent aussi de déposer puis reprendre dix-neuf types de fournitures, avec capacités inventées de 10 à 45 kg et au plus 512 dépôts non vides. Chaque dépôt commence vide, garde son stock par bâtiment, étage, plan et meuble, et utilise la masse du sac ordinaire ; une transaction refusée est entièrement annulée. Les dispositions et signatures des layouts 1–5 sont conservées. Le layout 6 s’adresse uniquement aux nouvelles habitations inventées admissibles : salle d’eau privée, chambre et cuisine sont recherchées selon la place et la circulation. Douche et réfrigérateur sont hors service ; ils ne produisent aucune ressource. Les registres bornés gardent version et porte retenue sans éviction, avec retour au layout 5 pour les identités inconnues lorsque leurs limites sont atteintes.

Les huit [dossiers de continuité](LORE_CONTINUITE.md) et leurs liaisons restent intacts. Après les décisions des Communes du Mistral et des Gilets de Cendre, la copie du reçu se remet au second relais nommé ; revenir au donneur accorde un contre-don unique selon l’issue. Ces deux suites utilisent l’inventaire ordinaire, le journal, le suivi, la radio et Continuer, sans seconde récompense de dossier ni réapprovisionnement. Les programmes intérieurs non relevés et les nouveaux récits sont des créations du jeu ; aucune conversation privée supplémentaire n’a été récupérée.

Le [bilan du 2 novembre](../verification/expansion/city_continuation_20261102/CITY_INTEGRATION.json) rattache **3 318 contrôles descriptifs réussis, 13 méthodes et 100 événements de capture native**, sans échec, au HTML `4581c0c29ce5c74da3aba7430227fba844aed1eb40f1b1fc4d7965c7a6600d78`. Les modèles avec fixtures, comparaisons de sources, parcours assistés et entrées émulées gardent leurs périmètres ; leur somme ne représente pas autant de parties humaines. Les six contrôles supplémentaires de livraison du service worker restent hors de ces totaux.

Le [bilan intégré du 1er novembre](../verification/expansion/continuation_20261101_integrated/CONTINUATION_INTEGRATION.json) conserve ses **3 312 contrôles et 76 captures** sur `c0f13de3…` à titre historique. Le [bilan avant intégration](../verification/expansion/continuation_20261101/CONTINUATION_INTEGRATION.json) conserve ses 3 310 contrôles sur `98a78a1c…`. Les bilans [immersion](../verification/expansion/immersion/IMMERSION_INTEGRATION.json), [Wasteland](../verification/expansion/wasteland/WASTELAND_INTEGRATION.json) et [précision](../verification/expansion/precision/PRECISION_INTEGRATION.json) gardent leurs propres programmes. Les modèles, parcours assistés, comparaisons de sources et entrées émulées sont distingués ; ils ne certifient ni toute Marseille en 1:1, ni du matériel physique. La distribution Drive n’est pas annoncée comme actualisée.
