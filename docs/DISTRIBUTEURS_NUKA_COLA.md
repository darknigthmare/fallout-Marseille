# Distributeurs Nuka-Cola

Deux machines originales rejoignent les scènes narratives d’Aubagne et de Marseille. Leur caisse rouge, leur enseigne géométrique, les bouteilles visibles, le monnayeur et le volet de récupération forment un modèle propre au jeu. Leurs positions sont inventées ; elles ne proviennent pas d’un relevé de mobilier urbain.

Approchez la face du distributeur et utilisez **E**. Le panneau présente l’alimentation, les capsules possédées et la réserve restante. Une réparation consomme **deux ferrailles et un circuit**, une seule fois par machine. Les achats utilisent ensuite le sac et la bourse ordinaires :

| Machine | Nuka-Cola à 30 capsules | Quantum à 65 capsules |
| --- | ---: | ---: |
| Ateliers d’Aubagne | 3 | 1 |
| Comptoir de Marseille | 4 | 1 |

Chaque paiement retire une seule bouteille de la réserve et la place dans **INV → AIDE**. Sa consommation suit les effets existants : PV et PA bornés, radiations et capsule conservée. La remise en service ne donne pas de bouteille ni de récompense répétable. Les stocks épuisés restent vides après une réentrée ou **Continuer**.

Les relais géographiques correspondants utilisent les mêmes identifiants, réparations et réserves que leurs machines narratives. Leur implantation exige un relais sûr effectivement chargé, un terrain source utilisable sur toute l’emprise, une pente limitée et une marge libre pour le joueur, les autres solides, habitants, dangers et accès prioritaires. Le macro municipal de Marseille partage le lien du macro marseillais historique. Une implantation impossible est omise jusqu’à une nouvelle validation des sources.

La caisse possède une collision de corps et un dessus porteur. Ouvrir et acheter recontrôlent portée, hauteur, ligne de vue, support, propriétaire de session, scène active et danger proche. Les touches de terrain restent suspendues dans le panneau ; **Tab** parcourt ses contrôles et **Échap** ou **Quitter** revient au jeu avec le focus sur la vue. La navigation manette existante reconnaît le panneau.

Réparation et achat sauvegardent leurs matériaux, capsules, bouteilles et stock dans la même opération. Une écriture refusée ou levée restaure toute la fiche, y compris les effets de bord de sauvegarde. Après une écriture réussie, une défaillance de présentation ne peut pas remettre la mémoire dans un état antérieur au JSON enregistré. Les anciens boutons, scènes et propriétaires de session sont invalidés avant une nouvelle action.

Les [contrats de production](../tests/expansion/iconic_vending.cjs) composent les machines avec les objets emblématiques et la consommation existants, sous des conditions contrôlées de géométrie, d’acteurs, d’interface et de stockage. Le [pilote natif](../tests/expansion/vending_native.py) utilise le HTML produit par HTTP, le vrai E, les boutons affichés, l’inventaire et Continuer. Il prépare explicitement les moyens de paiement et les caméras ; il ne prouve pas leur acquisition pendant une campagne humaine continue. Son format portrait est émulé. Le modèle demeure stylisé et les implantations demeurent des créations du jeu.

Le [parcours courant](../verification/expansion/continuation_20261101/vending/VENDING_NATIVE.json) réussit **64 contrôles natifs et six captures** : vraies commandes E, réparation, achats, épuisement, consommation dans AIDE, reprise et identité du stock au relais géographique. Les fonds et matériaux préparés sont une aide de contrôle, pas une preuve d’acquisition en campagne. Le format portrait est émulé ; son panneau se parcourt verticalement.
