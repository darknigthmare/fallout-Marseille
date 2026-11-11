# Une place dans la cour

**Extension du 11 novembre 2026 — suite de Les gestes retrouvés.**
Base de travail : `a589d8de0da349a0bcdfc6d1636eb41a1595a02e`, PR 18.
Création originale de fan-lore pour Mistral ; aucune revendication de canon officiel.

## Intention

Une restitution ne doit pas laisser trois personnes figées pour toujours dans une file. Leur objet a une place dans leur vie, pas seulement dans un registre de quête. Cette extension leur donne une courte marche, une destination visible et un échange facultatif après la remise. Elle ne transforme pas ces personnes en compagnons ni leur cour en réseau de transport.

L'accès est celui de la consigne des gabians, depuis le Vieux-Port. Une remise personnelle réussie, directe ou depuis le dépôt de Nora, ouvre une nouvelle proposition dans le dialogue de son propriétaire. Le joueur choisit de la faire : aucune ancienne partie ne reçoit rétroactivement une promenade ou un souvenir qu'elle n'a pas joué. La clôture historique de Nora reste indépendante.

## Éloi : dessiner une porte qui ferme

Proposition : **« Vous vouliez me montrer le Demain ? »**

Éloi rejoint une table, à l'écart du comptoir. Sur le carton posé là apparaît un croquis sommaire de sa cabine : une couchette, le moteur tout près, une porte. Ce dessin est un souvenir ; ce n'est ni une carte nautique exploitable ni une localisation géographique inventée. Il n'ouvre aucune épave et ne remet aucun bateau en état.

À l'arrivée, le joueur peut lui demander où se trouvait la cabine. Éloi explique pourquoi il gardait sa clef même en dormant : posséder une porte qui ferme comptait davantage que la taille de la pièce. Il termine en remarquant que, sur le dessin, il a laissé la porte ouverte. La clef rendue reste à sa ceinture.

Le croquis devient visible à l'arrivée réelle. Il n'y a pas d'animation détaillée du crayon ou des doigts.

## Mina : le droit de finir son quart

Proposition : **« Vous avez enfin fini votre quart ? »**

Mina va près du banc de fin de quart. Remettre sa bague signifie qu'elle a fini de travailler les cordages : elle ne la porte pas pour reprendre un geste dangereux. Elle plaisante sur une bâche qui claquait et qu'on lui avait présentée comme une urgence ; à force de faire des heures, la bâche pouvait elle aussi réclamer un contrat.

Cette scène montre une minute où Mina n'a rien à tenir. Le joueur peut rester parler sans recevoir une tâche supplémentaire. La bague suit désormais la main du modèle natif, y compris pendant la marche et les changements d'orientation.

Mina reste **debout près du banc** : la pose assise, sa transition et une animation de repos spécifique ne sont pas livrées.

## Rachid : ne pas vendre une traversée imaginaire

Proposition : **« Qu'allez-vous annoncer au panneau ? »**

Rachid rejoint le panneau des passages. L'ardoise est lisible physiquement et par interaction : **PAS D'HORAIRE CONFIRMÉ**. Le sifflet lui est revenu ; cela ne crée pas le bateau manquant. Il raconte avoir effacé un départ à l'aube écrit par quelqu'un qui avait un beau crayon, mais ni embarcation ni rame.

La nouvelle conversation conserve le rôle de Rachid : annoncer ce qui est vrai plutôt que remplir une file d'attente avec une rumeur. Aucun ferry, embarquement, horaire simulé ou réseau maritime n'est ajouté. Le panneau est fixe ; son installation manuelle n'est pas animée.

## Gameplay incarné

Les trois personnages conservent leur identité et leur modèle existants. Chacun suit un trajet authored distinct dans la cour, à vitesse régulière, avec le cycle de marche existant. Les pas sont échantillonnés pour vérifier les collisions. Un obstacle, le joueur ou une autre personne les fait attendre, sans téléportation pour forcer la réussite.

Le joueur peut leur parler avec l'interaction native en chemin, demander **« Attendez-moi ici un instant »**, puis **« Vous pouvez reprendre votre chemin »**. Le dialogue reste disponible à leur position réelle, pas au comptoir abandonné. Une invitation donnée juste après la remise attend la fin du geste de reconnaissance avant de lancer la marche.

Les menus, dialogues, chargements, combats et la mort du joueur suspendent le déplacement. Le saut du joueur ne bloque pas une promenade sûre. Réduire les mouvements retire l'oscillation des membres, mais conserve le déplacement continu. Le journal indique l'emplacement ou l'attente et le souvenir déjà écouté.

Il s'agit de trois trajets locaux scénarisés, pas d'une navigation libre, d'un emploi du temps jour/nuit ou de départs hors champ. Les personnes restent dans la cour et abordables à l'arrivée.

## Persistance et transactions

`v076Consigne`, schéma 1, stocke une révision et, pour chaque propriétaire, le départ choisi, la distance en millimètres, l'attente explicite et le souvenir écouté. Les positions et orientations sont reconstruites depuis les trajets. Aucun modèle, nœud de rendu ou objet de navigateur n'est sérialisé.

Une sauvegarde ancienne sans ce registre reçoit des promenades non commencées. Le registre `v073Gabians` reste au schéma 2. Une invitation exige une remise personnelle réelle ; une distance incohérente, une version inconnue ou une conversation périmée est refusée. Les autres dossiers ne sont pas réinitialisés.

Les choix sont transactionnels. La marche enregistre des points de contrôle tous les deux mètres, aux angles et à l'arrivée. Un échec de sauvegarde restaure l'état juste avant le point de contrôle, arrête le trajet et propose de réessayer en parlant au personnage. Une sortie ne continue pas après un échec de sauvegarde. Les appels manuels de sauvegarde prennent la distance actuelle, même entre deux points de contrôle.

La prime historique reste **45 capsules, une fois**. Les promenades et souvenirs ne donnent ni seconde prime, ni objets supplémentaires, ni nouveau palier de faction.

## Historique de la vérification locale

Sources : `10y_consigne_vie.js` (données et règles), `10z_consigne_vie_runtime.js` (intégration native), corrections ciblées de `10u_gabians_runtime.js` et `10x_consigne_gestes.js`. La compilation locale remplace des modules identifiés une seule fois dans le programme antérieur dont l'empreinte est vérifiée, puis insère les deux nouveaux modules dans l'ordre de la compilation normale.

**727 tests de logique réussis, dont 76 nouveaux ; 927 contrôles sur 17 parcours navigateur réussis, dont 54 sur cette extension.** Les images fournies proviennent du programme de cette édition. Les parcours utilisent un extérieur synthétique, des positions pilotées, un stockage mémoire isolé et un rendu logiciel. Ils ne sont pas une campagne humaine ou une traversée IGN.

Les trois nouveaux scénarios de reprise après fermeture du navigateur sont écrits, mais leur exécution est bloquée avant le premier scénario par `ERR_BLOCKED_BY_ADMINISTRATOR`. Les anciennes suites à froid des oiseaux et rats sont également bloquées ici. **Aucune reprise à froid n'est donc certifiée pour cette édition.** Les résultats à froid des versions précédentes ne sont pas reportés comme réussites actuelles.

L'archive de départ ne contient pas toutes les sources du dépôt. La reconstruction canonique `tools/build_single.py` et les quatre suites territoriales ne sont pas exécutées localement sur cette édition. Le programme et son assemblage incrémental déterministe sont vérifiés ; la compilation complète et la CI restent à lancer dans le dépôt complet. Le workflow fourni est préparé, pas publié ni exécuté.

## Reste ouvert

Transfert continu entre les mains du joueur et du destinataire ; animation des doigts et du dessin ; doublage ; assise de Mina ; vrais emplois du temps et destinations extérieures ; navigation libre ; effets régionaux ; ferry et traversée pilotable. La PR 17 COCHONNET reste séparée. Les missions et factions précédentes ne sont pas déclarées terminées par cet épilogue local.


## Publication depuis le dépôt complet

La consolidation du 11 novembre reprend ces sources sur `cfa5edd4439e214331323c3a3f1b9833ff464942`, après fusion de la PR 18. Le programme est reconstruit par `tools/build_single.py` dans le dépôt complet ; son résultat ne doit être déclaré validé qu’après l’exécution effective du workflow. `verification/bible-sync/QA.json` conserve l’empreinte, les résultats et les scénarios exécutés. Le précédent rapport local ci-dessus reste historique et n’est pas supprimé.

Le registre documentaire n’ajoute ni nouveau personnage, ni récompense, ni règle de faction. Les vingt ensembles narratifs et leurs limites sont indexés dans la bible centrale et contrôlés automatiquement lors des validations suivantes.
