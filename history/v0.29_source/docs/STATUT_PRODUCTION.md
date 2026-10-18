# Statut réel — v0.29

Fan project Fallout non officiel. Livraison locale, sans publication GitHub/Vercel.

## Réalisé
HTML autonome construit depuis les sources. Trois contrôleurs nouveaux, deux anciens hacks raccordés, trois petits locaux de service, déduction persistante, habilitations, veille locale, carillon, perception progressive et enquête à deux conclusions. Le contenu narratif, les circuits sur holodisque, blessures, lampe, Pip-Boy et V.A.T.S. précédents restent présents. Les trois scènes concernées et les 86 configurations historiques sont couvertes par les contrôles indiqués dans le rapport QA.

## Non réalisé / limites
Aucune donnée cartographique officielle ou altimétrique ajoutée. Les cours et alcôves sont fictives et schématiques, pas des reproductions d'Aubagne/Marseille/La Ciotat. Les extérieurs géographiques stricts peuvent encore manquer de données ; utiliser la campagne en lieux scénarisés pour le contenu embarqué.
Modèles et animations procéduraux ; Adrien réutilise le modèle humain de métier. Le volet bascule entre ouvert et fermé, sans animation de moteur complexe. Les automates en veille restent debout, sans nouvelle animation mécanique unique. Aucun doublage ou flux radio Internet ajouté.
La perception utilise le point de vue et les collisions existants. La recherche sonore ne planifie pas une propagation acoustique réaliste à travers toutes les salles ; une atténuation de portée remplace cela. L'alerte de groupe et les tirs gardent leur logique historique. Les règles sont partagées entre familles : aucune refonte individuelle des 130 variantes n'est revendiquée.
Le temps de verrouillage progresse dans le jeu actif, pas en attendant dans l'appareil ou par un changement artificiel de l'horloge régionale. Pas de simulation hors écran des populations ou des nouvelles machines.
Tests dans Chromium avec rendu logiciel ; ni GPU matériel ni iPhone physique certifiés. L'origine file:// est refusée par la politique de l'environnement de test ; le HTML exact est donc exécuté via set_content. Le refus natif de stockage opaque est vérifié, puis les scénarios réussis utilisent un adaptateur mémoire déclaré. Aucun résultat de test ne certifie à lui seul un RPG commercial terminé ou un parcours humain de toutes les missions.
