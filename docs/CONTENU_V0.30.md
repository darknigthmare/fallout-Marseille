# v0.30 — Sous la cuirasse

## Base vérifiée
Continuation de l’archive complète v0.29, non d’une maquette ou d’une capture. Son empreinte et les 84 fichiers préservés sont décrits dans `data/BASE_V029.json`. Les scènes, quêtes et systèmes historiques restent présents dans le programme ; aucun nouveau secteur cartographique n’est ajouté.

## Armures assistées
Douze définitions sont reconnues, dont onze modèles déjà présents dans le catalogue et le nouveau châssis industriel **M-45 des amarres**. Cela ne signifie pas douze modèles 3D uniques.

Chaque tenue reconnue garde six intégrités : casque, plastron, bras gauche/droit, jambe gauche/droite. L’ancienne condition moyenne initialise les six valeurs sans les remettre à neuf. La fiche moyenne est pondérée : casque 14 %, plastron 30 %, bras 13 % chacun, jambes 15 % chacune.

Un impact significatif use la plaque de sa région ; une plaque à zéro ne fournit plus sa protection locale. Les morceaux de blindage correspondants ne sont plus dessinés, mais l’ossature reste visible. Le plastron abrite le circuit : lorsqu’il casse, les moteurs s’arrêtent. La protection passive des autres plaques demeure.

Les traumatismes corporels v0.28 restent distincts. Une réparation ne remonte ni les PV, ni les membres du porteur. Les petites corrections globales héritées, par exemple la maintenance d’un compagnon, ajoutent un delta borné sans niveler les six états.

## Cœurs et énergie
Un cœur neuf est retiré de la réserve de munitions pour produire une charge installée de 100 %. Il ne peut être installé dans un emplacement déjà occupé. Éjecter le cœur l’ajoute à une réserve de cellules entamées, avec sa charge exacte ; aucune cellule neuve n’est rendue. La réserve est bornée à quarante. Les valeurs importées sont validées.

L’assistance doit être arrêtée pour manipuler le cœur ou changer de tenue. La manipulation nécessite une situation sûre. La charge installée suit le porteur lorsqu’il change de modèle, plutôt que d’être un emplacement séparé pour chaque armure.

Consommation de simulation : 0,014 point par unité de déplacement réellement parcourue ; course ×1,55 ; servos ×1,25. Un saut réussi coûte 0,25 point et une action V.A.T.S. réellement émise 0,35 point. Une collision sans déplacement, un tir annulé ou une consultation d’interface ne consomme pas cette charge. Aucun débit au ralenti ni pour les tirs libres ordinaires. Un cœur épuisé est retiré et l’assistance se coupe ; il reste possible de marcher lourdement ou de ranger la tenue.

## Effets d’assistance
Capacité de portage +60 tant que le moteur fonctionne ; mêlée ×1,20. La marche motorisée va de 82 à 92 % de la référence selon l’état des jambes. Hors tension, elle vaut 58 %. Les effets de blessures et l’encombrement facultatif continuent ensuite de s’appliquer. L’armure n’est ni une invulnérabilité ni un bouclier énergétique.

## Atelier et trois configurations exclusives
Un seul réglage par modèle ; installer un autre réglage remplace le précédent sans remboursement. Les devis vérifient la pièce, la tenue, l’état, la scène, les ressources, la sécurité et la proximité. Ranger le Pip-Boy, importer une sauvegarde ou changer de scène annule le devis. Aucune expérience de réparation répétable.

- **Servos de portage** : +25 de capacité supplémentaire, vitesse +6 points, consommation de mouvement +25 %, uniquement sous tension. Coût : six ferrailles, trois circuits, trois pièces d’arme.
- **Joints de confinement** : résistance aux radiations +12 points, pondérée par casque/plastron, même hors tension. Coût : cinq tissus, quatre produits chimiques, trois ferrailles.
- **Écrans réfractaires** : résistance au feu +20 points pondérée par les plaques ; masse +4. Coût : six argiles réfractaires, quatre ferrailles, deux plaques navales.

Réparer une pièce consomme au minimum une ferraille et une pièce d’arme, avec un coût croissant selon les dégâts. Casque et plastron nécessitent aussi un circuit. Une pièce intacte n’a pas de devis payant. Les raccourcis historiques de réparation renvoient vers l’entretien local au lieu de niveler gratuitement les six plaques.

La revente puis le rachat conservent les six plaques et la configuration. Plusieurs exemplaires d’occasion présents chez un vendeur gardent leurs fiches séparées. Le budget fini du marchand reste requis. Les cœurs restent au porteur, sans recharge ni nouvelle cellule lors de l’échange.

## Baie et représentation
Dans la cour des amarres : portique, M-45 stationné, établi, sectionneur, casier du cœur, portillon d’épreuve et Alba Rousset. Une sous-zone s’ajoute aux dix déjà présentes, sans changement de scène. Un actionneur est placé dans la galerie haute du dépôt ; un cahier sur une table au Poste du palan 12.

Le M-45 est composé de volumes 3D originaux avec plaques, ossature, pistons, casque et logement dorsal. Cette base partagée est portée en troisième personne. La charge et l’intégrité moyenne apparaissent dans le HUD ; celui-ci est placé sous le suivi de quête pour ne pas le masquer. Un entourage léger apparaît en première personne avec un casque alimenté intact. Pas de nouvelle animation d’entrée, de sortie ni de ragdoll.

## Une force empruntée
L’intervention optionnelle commence auprès d’Alba. Il faut : accepter, récupérer l’actionneur, lire le cahier, consigner la baie, confirmer sa remise en état, puis éprouver le portillon. Réparation 45 réduit le coût des travaux de quatre ferrailles/deux circuits à deux ferrailles. Aucun G.O.A.T. n’est obligatoire.

Le M-45 est attribué avec ses six plaques à 85 %. Le cœur à 65 % se récupère séparément sur le casier, une fois. Le portillon peut être ouvert avec un essai assisté consommant exactement 2 % de charge, ou par une manivelle ne demandant pas de cellule. La collision se retire réellement et le passage est traversable.

Deux accords gardent le châssis au joueur :
- **Tournées de secours** : une réserve de soins visible dans la cour ; une trousse de traumatologie et deux attelles attribuées.
- **Autonomie** : un rayonnage de maintenance visible ; quatre pièces d’arme, deux circuits, trois ferrailles attribués.

Chaque accord donne une fois 70 capsules et 85 XP. Trois scènes textuelles propres à chaque accord, six au total. Les preuves et les décisions des quêtes antérieures ne sont pas remplacées. Les fournitures de conclusion sont une récompense attribuée à la validation ; leur décor n’est pas un distributeur infini.

**Pas une seconde peau**, holodisque d’Alba, comporte cinq segments originaux. Acquisition physique puis lecture/transcription dans le Pip-Boy, sans voix enregistrée.
