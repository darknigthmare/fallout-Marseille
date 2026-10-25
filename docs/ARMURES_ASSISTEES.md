# Armures assistées : énergie, plaques et entretien

Le jeu possède déjà le système d’armure assistée de la v0.30 : six plaques indépendantes, cœurs neufs et entamés, modifications, protection passive, modèles portés visibles et quête d’acquisition du M-45. Le prolongement du 25 octobre conserve cette simulation et corrige ses opérations de sauvegarde. Il ajoute l’entretien auprès des mécaniciennes déjà présentes dans les relais géographiques.

## Utiliser un châssis

Appuyer sur **U**, ou ouvrir **Pip-Boy → STAT → ARMURE**. Le châssis doit d’abord être possédé et équipé. Insérer un cœur neuf ou sélectionner un cœur entamé, puis activer l’assistance. Couper les moteurs avant de changer de tenue ou de manipuler le cœur.

La charge diminue selon le déplacement réellement effectué, le saut et les actions V.A.T.S. émises. Un déplacement bloqué ne consomme rien. Le repos et les menus ne déchargent pas le cœur. À épuisement, les moteurs s’arrêtent : la marche ralentit et le portage assisté disparaît. Les plaques intactes continuent de protéger ; une plaque à zéro ne protège plus sa région. Le personnage peut ranger sa tenue pour repartir à pied.

Un cœur éjecté conserve sa charge exacte et rejoint la réserve des cœurs entamés. Le remettre en place ne le recharge pas. La réserve garde sa limite existante de quarante cœurs entamés. Les blessures du porteur, les plaques de l’armure et la charge sont trois états distincts.

## Trouver du matériel

La page ARMURE indique les stocks existants des comptoirs proposant des châssis ou des cœurs. L’achat se fait auprès du marchand, avec ses stocks et les capsules du personnage. Cette consultation ne crée ni achat ni équipement.

Dans la scène historique fictive de la cale sèche, Bastien et son point de commerce se trouvaient à l’intérieur d’un bâtiment entièrement solide. Le marchand et son comptoir sont désormais placés ensemble devant la façade sud, à un emplacement dont les collisions, l’approche à pied et les lignes de vue sont contrôlées. Les stocks, les prix et les autres habitants conservent leur état. Cette correction ne modifie aucun bâtiment géographique de Marseille.

**Une force empruntée**, à la baie des amarres, permet toujours d’obtenir le M-45 avec Alba Rousset. Il faut rapporter l’actionneur et le cahier, consigner la baie, puis restaurer le châssis avec les matériaux demandés. Son cœur d’essai est un exemplaire fini à **65 %**. L’essai du portillon peut se terminer à la manivelle, même sans batterie. La nouvelle page permet de suivre ce dossier ; les conditions et récompenses de l’histoire sont conservées.

## Entretenir sur la carte

Les établis historiques restent utilisables. Sur le territoire géographique, une **mécanicienne d’un relais sûr et découvert** peut aussi assurer l’entretien. Approcher à moins de **4 m**, sur le même niveau, avec une ligne de vue dégagée et hors danger, puis ouvrir ARMURE. La page nomme l’interlocutrice accessible et propose de suivre les relais techniques déjà découverts.

Choisir une plaque ou une modification, examiner le devis puis confirmer. Les matériaux proviennent du sac. Les réparations suivent les coûts existants de ferraille, pièces et circuits ; les trois configurations existantes gardent leurs coûts et effets. La même interlocutrice ou le même établi doit rester accessible au paiement. Un déplacement, une mort, une cloison, un changement de scène ou le chargement du secteur invalident le devis. Il faut alors en demander un nouveau.

Les habitants et leurs services sont du contenu fictif du jeu. Ils ne décrivent pas des ateliers ou des habitants réels de Marseille.

## Conservation et sauvegardes

Insertion, éjection, activation, changement de tenue, entretien, échanges de châssis ou de cœurs et opérations matérielles de la quête sont sauvegardés après leur résultat complet. La vente puis le rachat conservent les six plaques et la configuration dans le stock du marchand. Une erreur de stockage annule les mutations de charge, de pièces, de matériaux, de stock et de récompense ; les éléments physiques de la baie retrouvent leur état cohérent.

Les opérations refusent les transitions, les chargements, un personnage mort et le laboratoire synthétique. L’ancien schéma `v030` reste le propriétaire des armures et de la charge : aucune conversion vers un second inventaire n’est nécessaire.

## Vérification

```bash
node tests/expansion/power_armor.cjs
```

Ces régressions exécutent les fonctions de production v0.30 de charge, plaques, commerce, atelier et quête, puis l’extension de conservation. Les acteurs, la scène, l’interface et les erreurs de stockage sont des cas contrôlés explicitement déclarés. Elles ne constituent pas un parcours natif de tous les relais.

Les cas du comptoir utilisent l’empreinte exacte de l’ancien magasin dans une scène contrôlée. Ils vérifient le dégagement du porteur de rayon 0,38 m, les rayons de vue, le support physique du comptoir, la conservation des identités et le refus d’un placement obstrué. Le diagnostic en lecture seule `v053PowerArmorInfo().drydockService` indique le point d’approche et les positions retenues dans la scène chargée.
