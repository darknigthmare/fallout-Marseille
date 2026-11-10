# COCHONNET — La mène des Cent Trêves

## Continuité et provenance

Ce chapitre poursuit `8924be65a69f7335364b09934bc908bf17d0973e` (rats-câbles, PR #16). Il donne un terrain au COCHONNET déjà présent dans les dossiers « On joue encore » et « Tu tires ou tu pointes ? ». Il ne remplace ni leurs sites, ni leurs conditions de remise, ni leurs récompenses.

La cour `v073-cour-cent-treves` est un lieu **fictionnel** relié au représentant existant du Vieux-Port (`v042-marseille-caravan-01`). Le passage est un chargement narratif : aucun boulodrome réel, relevé IGN, nouveau chemin géographique ou bâtiment cadastral n’est inventé. Ce contenu relève du fan-lore de Mistral, pas du canon officiel de Fallout.

## Nelly, la machine et le mètre

Nelly Ferrand arbitre les désaccords de la cour. Elle conserve un mètre, une feuille de résultats et un lanceur mécanique COCHONNET-3. Une machine peut tricher dans ses discours ; ses boules, elles, doivent rester là où elles se sont arrêtées.

> « Le lanceur a survécu à trois guerres de voisinage. Le mètre aussi. Les deux sont sous ma garde. »

La Ligue offre un terrain neutre, pas une solution magique aux conflits de Provence. Nelly interdit les armes pendant la mène. Ce règlement protège le jeu sans transformer ses voisins en citoyens exemplaires. Le représentant du port plaisante sur le lanceur : il confond une poignée de mains et une remise à zéro.

Nelly n’est pas une nouvelle compagne recrutée. Le lanceur est un assemblage original de primitives du moteur, pas un modèle d’archive, une IA générale ou un adversaire humain animé.

## Une exposition, pas un championnat officiel

Une mène oppose le joueur au lanceur, avec **trois boules chacun et aucune mise**. Nelly place le but à une position déterministe variant entre les mènes. Le camp qui n’a pas le point rejoue ; quand il n’a plus de boules, l’autre termine ses lancers. Une égalité au millimètre fait alterner les camps. Si le but sort entièrement, la mène est annulée, sans victoire.

Les points sont calculés après stabilisation : chaque boule du camp le plus proche située devant la meilleure adverse compte. Les mesures affichées sont des distances **entre centres**, et sont marquées provisoires pendant le mouvement. Le but peut être déplacé par un choc ; une boule sortie ne compte plus. Les règles d’égalité, les dimensions agrandies et les gestes appartiennent à cette exposition fictive, pas à une simulation certifiée de compétition.

## Jouer dans le monde

Depuis le cercle, la commande de tir habituelle lance une boule. Recharger alterne **pointer**, en cloche, et **tirer**, rasant. Interagir ouvre des réglages de force par pas de 1 ou de 5, avec boutons explicites et confirmation de lancer. L’orientation horizontale de la caméra donne la direction ; une visée trop éloignée du terrain est refusée sans consommer de boule. Il n’y a pas de jauge réflexe à arrêter au bon instant.

La ligne au sol indique l’axe, pas un point d’arrivée garanti. Le lanceur emploie la même simulation que le joueur, avec une imprécision déterministe. Il examine les positions arrêtées, pas la prochaine commande du joueur.

Les sphères décrivent un arc, rebondissent, roulent, se heurtent et s’arrêtent. La simulation est simplifiée : pas fixe de 5 ms, gravité, restitution et frottement de roulement ; pas de rotation physique détaillée, déformation du sol, effets de vent ou simulation libre de tous les objets de la cour. Les limites blanches définissent les sorties. Les rails visibles se trouvent en dehors de ces limites et ne renvoient pas les boules sur le terrain.

## Une trêve réellement appliquée

Dans cette instance, tirer n’utilise pas l’arme équipée. Les tirs maintenus ne jouent pas automatiquement la boule suivante. La visée VATS, le lancer de grenade et la pose de mine sont refusés. Le chargeur, les réserves et l’état de l’arme ne sont pas débités. Un départ avec une grenade déjà armée est refusé.

La mène ne verse **aucune capsule, expérience ou objet**. La découverte d’un nouveau lieu reste une fonction du moteur géographique existant ; elle n’est pas une récompense de victoire. Les autres lieux gardent leurs armes et leurs contrôles habituels.

## Sauvegarde et anciens résultats

Le registre `v073Boules`, schéma 1, conserve les positions et vitesses des sept sphères au maximum, les boules utilisées, les tours, la force, le geste et le résultat mesuré. Il contient uniquement des données, pas des objets WebGL. Une sauvegarde en plein vol est donc distincte d’une remise à zéro du terrain.

Chaque résultat terminé incrémente une fois les compteurs historiques COCHONNET. Les anciennes victoires restent intactes ; elles ne créent pas de faux terrains ou de boules rétroactives. Les anciens boutons probabilistes du panneau France sont remplacés par l’accès au terrain, sans recréer les autres boutons de quêtes. Une victoire physique satisfait le préalable de victoire des anciens dossiers ; leurs preuves et remises sur place restent nécessaires.

Les sauvegardes incohérentes sont refusées, notamment les identités dupliquées, les tours impossibles, les scores inventés et les mouvements non finis. Une écriture refusée annule l’action et ses compteurs. Si la mesure ne peut pas être sauvegardée, la simulation s’arrête avant validation : Nelly permet de réessayer.

Le Pip-Boy, le journal, le repère local et la radio textuelle présentent le même état. Les menus et chargements suspendent la simulation. Une nouvelle campagne ne reprend pas la mène précédente.

## Portée des vérifications

Les tests du modèle et les parcours navigateur sont livrés avec les sources. Les parcours instrumentés utilisent des positions et visées scriptées, un relais extérieur synthétique, un stockage isolé et un rendu logiciel. Le test séparé de reprise à froid prépare le point par des helpers, puis ferme Chromium et reprend avec son vrai profil disque sur le HTML de production inchangé. Son résultat doit être lu dans l’artefact CI ; la seule présence du script n’est pas une réussite.

Le retour ordinaire au point extérieur retenu est testé. Après remplacement de la sauvegarde ou redémarrage, le moteur doit reconstruire l’extérieur à partir des données géographiques : ce lot ne certifie pas ce trajet IGN, tous les navigateurs ou les performances matérielles. Le test à froid couvre une URL de fichier hors ligne, pas une coupure électrique.

Restent ouverts : championnat en plusieurs mènes jusqu’à 13, équipes et adversaires humains animés, lancer manuel du but, variantes de terrains, boules équipables, paris éventuels et conséquences diplomatiques prolongées. Aucun de ces éléments n’est présenté comme livré ici.
