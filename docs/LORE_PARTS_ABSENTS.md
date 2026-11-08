# La part des absents — six caisses après la Cour du Lys

## Reprise et statut

Base : `da8e4f99b5d08480101910088c64a4012bbca301`, après la fusion de la première audience du Lys (PR 12). Cette suite est du **fan-lore original de Fallout: Mistral**, non du canon officiel de la franchise. Ses règles de partage sont fictionnelles, pas une description du droit français.

Le règlement de l’audience est déjà acquis. Cette quête ne couronne pas à nouveau LOUIS et ne demande pas une seconde abdication. Elle met ce règlement à l’épreuve d’une pénurie concrète : **six caisses, trois destinations, une seule répartition**.

Le nouveau lieu `v069-cale-des-parts` réemploie l’ancrage approximatif d’If déjà présent dans le catalogue. C’est un quai fictionnel séparé, construit avec les formes et matériaux du moteur existant ; ce n’est ni un quai relevé ni une restitution du monument. Aucun fichier géographique, trait de côte, bâtiment relevé ou altitude n’est changé.

## Le conflit : ne pas effacer les absents

Maëlle revient avec un lot limité. Les cuisines accueillent les habitants déjà présents, des naufragés dorment sous l’auvent, et l’équipage doit préparer son retour. Tous ont une raison de demander plus que leur minimum. Aucun intitulé de politique ne fait apparaître une septième caisse.

Les trois règlements précédents restent reconnus : sous serment, les titres ont déjà été retirés du rationnement ; dans la commune, LOUIS est déjà guide ; sous régence, l’administration reste provisoire. Le texte de la rencontre distingue ces situations, sans réécrire le registre d’origine. Les trois plans restent accessibles dans chacun de ces contextes : il n’existe pas de pénalité cachée obligeant le joueur à refaire son choix précédent.

## Trois personnes sur le quai

**Maëlle Sarti**, passeuse des Francs du Large, n’est plus seulement une voix proposée par les représentants maritimes : elle possède un acteur local dans cette nouvelle scène. Elle protège ses deux matelots, mais refuse de négocier le droit de manger des personnes qu’ils ont repêchées. Elle paie une manutention terminée, pas une signature. Son apparition sur le quai ne constitue pas un recrutement.

**Éloi Ferrand**, délégué des Sections libres, porte une opposition révolutionnaire locale. Son utilité est de refuser les privilèges de naissance ; son danger est de remplacer les titres par une obligation d’adhésion politique. Nora lui oppose la situation d’une mère naufragée tenant encore sa fille. Il conserve ses convictions, mais abandonne ici le formulaire d’adhésion des bénéficiaires. Cette scène ne prétend pas clore toute la campagne de la Convention.

**Nora Haddad**, habitante du refuge, ne parle pas au nom d’une catégorie abstraite. Sa cuisine compte déjà six personnes ; deux autres viennent d’arriver. Elle ne veut ni perdre sa place ni rendre les nouveaux venus invisibles. Elle demande de leur faire une place, sans faire passer sa propre inquiétude pour de l’égoïsme pur.

Le joueur écoute ces positions, mais n’impose aucun serment à ceux qui reçoivent le lot. L’absurde institutionnel demeure, sans transformer la mission en simple collecte de formulaires.

## Une boucle matérielle complète

Après la clôture effective de **« Le roi ne mange pas »**, les représentants du Vieux-Port et de Ratonneau proposent **« Ravitaillement du Lys · La part des absents »**. Les anciens sujets de conversation et la première traversée vers la Cour restent disponibles.

Le passage est narratif, par chargement. Aucun trajet de bateau, navigation libre ou itinéraire maritime IGN n’est ajouté. La cale reste une instance distincte de la Cour. La sortie conserve le mécanisme natif de retour au départ.

Sur place, le joueur rencontre Maëlle, lit la consigne du ponton et sécurise séparément les amarres **bâbord** et **tribord**. La manivelle ne baisse pas la barrière avec un seul verrou engagé. La barrière est réellement bloquante ; son ouverture modifie aussi la collision. Le trajet libre ne demande aucun saut.

Une alternative technique demande **Intelligence 5 et un circuit** : elle commande les deux verrous et abaisse la barrière. Le circuit est retiré une fois. La voie manuelle demeure entièrement gratuite, y compris avec Intelligence 1 et un sac vide. Une tentative prématurée ne consomme rien.

Après avoir entendu Nora et Éloi, le joueur examine les propositions auprès de Maëlle. La confirmation fixe un plan exclusif ; elle ne distribue encore aucune caisse.

## Trois répartitions, pas trois récompenses politiques

| Plan | Cuisines du refuge | Accueil des naufragés | Équipage | Compromis |
|---|---:|---:|---:|---|
| La part des naufragés | 3 | 2 | 1 | Une marge pour les arrivants, pas de provision supplémentaire pour les marins. |
| La prochaine traversée | 3 | 1 | 2 | Le minimum immédiat pour les arrivants, une réserve pour l’équipage. Cela ne déclenche pas une flotte simulée. |
| Les cuisines d’abord | 4 | 1 | 1 | Une marge pour les habitants, sans restaurer une priorité de titre ; les autres groupes n’ont que leur minimum. |

Les **six caisses A à F** ont chacune une identité persistante. Une caisse se trouve soit au râtelier, soit portée, soit à une seule destination. On ne peut en porter qu’une à la fois. Le modèle de la caisse portée apparaît devant le joueur ; son ancienne collision disparaît du râtelier. Un dépôt fait apparaître la caisse à destination, avec sa collision.

Un emplacement complet refuse la caisse sans la perdre. Le joueur peut la reposer à **son propre râtelier**. La sortie, y compris l’appel natif de sortie d’instance, refuse le départ avec une caisse portée ; une fois les mains libres, le joueur peut interrompre le déchargement puis revenir. Les caisses collectives ne deviennent jamais des vivres vendables dans l’inventaire normal.

Maëlle doit constater la remise des six caisses, pas simplement leur retrait du stock. Elle verse alors **40 capsules une seule fois**, quelle que soit la répartition. Une caisse encore portée empêche la clôture. Les destinations, le stock vide et la récompense restent enregistrés après sauvegarde et rechargement.

## Persistance, interface et limites de simulation

Le registre `v069Parts`, schéma 1, conserve la source politique, les deux voix, la consigne, les amarres, l’ouverture, le plan, la place de chaque caisse, la clôture et une révision. Il ne modifie ni `v068Lys` ni les autres arcs. Retirer plus tard le colis d’accueil du Lys ne réécrit pas sa source politique et ne bloque donc pas la cargaison.

Les confirmations contrôlent leur révision, le propriétaire de sauvegarde et la scène. Les actions vérifient à nouveau la proximité, la visibilité et la situation du joueur. Combat, chargement, laboratoire ou joueur en l’air interdisent une opération. Une sauvegarde refusée ou une exception annule la transaction de cargaison et son coût éventuel. Les versions futures ou les états impossibles du nouveau registre sont refusés plutôt que réinitialisés avec six caisses neuves ; ce contrôle n’est pas un système de sécurité multijoueur.

Le chapitre **DATA → LA PART DES ABSENTS**, le journal, les objectifs locaux, l’affichage de quête et la station textuelle **Les caisses du Lys** décrivent la progression réelle. Le suivi extérieur indique le départ du Vieux-Port ; Ratonneau reste l’autre possibilité.

Le lot change les caisses visibles, les verrous, la barrière, la couleur du repère de répartition, les textes et les capsules. Il ne simule pas la faim quotidienne de familles autonomes, une livraison par bateau animé, des déplacements d’équipage, un compagnon recruté, du doublage ou une campagne militaire. Le maintien d’une caisse portée dans cette scène n’ajoute pas un système universel de portage au combat.

## Fichiers et vérifications

L’implémentation est séparée en `src/v050/10l_parts_absents.js` (modèle) et `10m_parts_runtime.js` (liaison au jeu). Le module du Lys n’est pas modifié. Le constructeur canonique existant assemble automatiquement les modules dans cet ordre. La version extérieure 0.50 est conservée pour ne pas changer artificiellement les clés de sauvegarde.

`tests/expansion/lore_parts_absents.cjs` vérifie notamment les **18 combinaisons** des trois règlements précédents, deux accès et trois plans, les coûts, les quotas, les migrations et la préservation des autres registres. `parts_browser_smoke.py` joue le nouvel intérieur avec les vraies interfaces, interactions E et collisions du programme. Les huit parcours antérieurs sont aussi relancés.

Les positions sont scriptées, les prérequis préparés par le modèle réel du Lys, les ports synthétiques et le stockage isolé. Le retour exact sur la scène retenue est vérifié lors d’une visite interrompue ; après remplacement de l’état de jeu, les coordonnées de retour sauvegardées sont contrôlées sans réutiliser une scène appartenant à une ancienne sauvegarde. Ce n’est pas une validation du retour à froid sur toutes les données IGN ni une partie humaine complète. Les chiffres, empreintes et résultats de la reconstruction distante sont conservés dans `verification/parts/QA.json`.

## Chantiers toujours ouverts

La succession du Lys, une campagne de la Convention, les opérations des Francs et de l’Amirauté, les navires, les lieux maritimes relevés, la vie quotidienne des familles et les compagnons restent distincts de ce déchargement fini. Un lot de six caisses ne clôt ni la faction ni le jeu.
