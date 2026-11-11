# La consigne des gabians — Les objets trouvés

> **Actualisation :** le présent chapitre décrit le lot initial. La publication des oiseaux est dans la PR 18 ; [De main en main](LORE_GABIANS_RESTITUTIONS.md) ajoute désormais les trois propriétaires présents, leurs remises personnelles et le schéma 2. Les limites historiques ci-dessous ne doivent pas être lues comme le statut de cette extension.

## Place dans Fallout: Mistral

Ce lot prolonge les rats-câbles fusionnés dans `8924be65a69f7335364b09934bc908bf17d0973e`. Il est livré localement avec son programme et son correctif source : il n'est pas présenté comme déjà publié sur GitHub.

Le représentant de la **Halte caravanière du Vieux-Port**, identité existante `v042-marseille-caravan-01`, connaît Nora Ferrand. Son sujet « Consigne · Les objets trouvés » permet de rejoindre la cour. Le déplacement est une transition narrative ; la cour `v073-consigne-gabians` est une création fictionnelle, distincte des relevés IGN. Aucun bâtiment, quai ou tracé côtier réel n'est déplacé ou inventé dans les données géographiques.

Cette histoire relève du fan-lore original du projet, pas du canon officiel de Fallout. Elle n'exige ni les rats, ni le conseil régional, ni la succession du Lys. Les anciennes décisions restent intactes.

## Nora Ferrand, gardienne des affaires des autres

La consigne n'est pas une banque. On y laisse ce que l'on ne peut pas emporter sur une barque trop chargée, sur un chantier, ou pendant une traversée incertaine. Nora attache aux objets un ticket portant un nom et une description, souvent corrigée plusieurs fois.

Elle ne réclame pas une identité administrative parfaite. Un signe reconnu, un voisin qui se souvient, une poignée réparée ensemble valent mieux pour elle qu'un tampon impeccable. Ce principe explique son métier ; le lot n'ajoute pas un système général de propriété ou de justice à la région.

Nora a laissé les plateaux ouverts pendant qu'elle aidait à décharger une caisse. Deux gabians ont emporté de petits objets dans les paniers de récupération suspendus où ils se sont installés. Ils ne poursuivent pas un projet politique et n'ont pas choisi leurs victimes selon leur dossier.

> « Objets trouvés, objets perdus… Il manque une colonne : objets qui s'envolent. »

Nora ne demande pas « deux oiseaux morts ». Elle veut pouvoir rendre les affaires que leurs propriétaires lui ont confiées. Elle a déjà mis de côté deux petits lots de restes de poisson. Ils ne sortent pas du sac du joueur et ne deviennent pas une réserve de nourriture revendable.

## Trois objets, trois absences ordinaires

**La clé de cabine d'Éloi.** Éloi a changé plusieurs fois de bateau. La serrure n'existe peut-être plus. La clé lui rappelle la première cabine où il pouvait dormir avec une porte fermée. Rendre cet objet ne déverrouille pas artificiellement un navire absent du jeu.

**La bague de quart de Mina.** Elle l'enlève pour travailler près des cordages et l'avait attachée à son ticket de consigne. Le joueur ne décide ni de son mariage ni de son héritage : il retrouve un bien personnel confié à Nora.

**Le sifflet de Rachid.** Le passeur l'utilisait pour annoncer le dernier passage. Sans lui, il crie. Nora remarque qu'il se fatigue et que sa voix porte moins loin. Restituer le sifflet ne crée pas automatiquement une flotte ou une ligne régulière.

Le registre raconte ces histoires. Sa lecture est facultative : elle enrichit la récupération sans obliger à lire une note pour reconnaître une clé déjà ramassée. À la restitution, chaque objet reçoit sa propre réplique et apparaît sur le comptoir.

Les trois propriétaires sont évoqués dans les dialogues ; ils ne sont pas trois nouveaux PNJ incarnés dans cette cour. **Nora est le seul nouvel habitant présent dans cette scène.** Elle n'est pas recrutable comme compagne.

## Les deux gabians

Le **Gabian des filets** et le **Gabian de la tôle** sont deux individus du modèle régional existant `gabianBombardier`. Leurs noms identifient leurs territoires, pas deux espèces supplémentaires. Le Biset de plomb, le Pigeon-paratonnerre et le Général Biset ne sont pas ajoutés par ce lot.

Les oiseaux suivent des couloirs de vol locaux. Ils gardent la zone des paniers, puis peuvent rejoindre deux points de nourrissage distincts. Les volumes des ailes, du corps et de la tête restent ceux du rig régional utilisé pour le ciblage natif. Les blessures des ailes ralentissent le déplacement ; brûlure et ralentissement sont conservés dans la sauvegarde.

Le gabian annonce son lâcher corrosif pendant **1,1 seconde**. Le point visé est fixé au début : reculer ou se décaler permet de quitter la zone. Le projectile devient ensuite un objet visible en chute, vérifie les obstacles et n'applique son impact qu'une fois. Un couvert interposé peut l'arrêter.

Attirer le tireur ou le tuer ne supprime pas un projectile déjà lâché. Celui-ci possède son propre état sauvegardé. Un cadavre descend progressivement jusqu'au sol ; recharger en cours de descente ne recrée pas un oiseau vivant.

Ce sont des comportements scénarisés dans une scène bornée, pas une simulation libre de toute l'avifaune marseillaise. Le vol des objets a eu lieu avant l'arrivée du joueur : **aucune munition, clé ou ressource de son inventaire ordinaire n'est prélevée au hasard**.

## Récupérer sans détruire

Les chemins latéraux donnent accès aux restes de poisson sans obliger à traverser le centre du territoire des gabians. Après la pose, les oiseaux doivent réellement parcourir leur trajet. Une blessure ou un obstacle peut retarder l'arrivée. Les compagnons cessent de prendre automatiquement pour cible un gabian ainsi détourné ; une brûlure déjà appliquée continue pourtant d'agir.

La cour utilise deux palans qui appartenaient à la consigne avant l'installation des nids. Le joueur peut abaisser les paniers sans les détruire, une fois l'oiseau concerné à l'écart et les dangers dissipés.

Deux méthodes sont disponibles pour chaque panier :

| Méthode | Coût | Mouvement |
|---|---|---|
| Manivelle | Aucun objet, aucun seuil d'Intelligence | Descente à 0,7 m/s |
| Réglage du réducteur | Intelligence 5 et une ferraille, consommée une seule fois | Descente à 1,4 m/s |

Le déplacement est de **3,5 mètres**, du plateau à 4,2 m jusqu'au niveau de récupération à 0,7 m. Le panier, son nid, ses objets, les cordages et son volume de collision suivent le même état. Ils ne se téléportent pas au clic du dialogue.

Si le joueur ou Nora occupe le volume balayé sous la charge, le palan s'arrête. Il reprend quand le volume est libre. Le jeu ne transforme pas cette manœuvre en piège qui traverse le joueur ou l'écrase. Ces mécanismes sont des abstractions de jeu et non des instructions de manutention réelle.

La collecte n'est autorisée qu'à la fin de la descente, depuis le bon panier. Les objets ont des silhouettes distinctes — clé à dents, anneau et sifflet — et disparaissent physiquement du nid au moment de leur prise.

## Une chaîne de possession finie

Chaque objet conserve exactement un état : **dans le nid → transporté dans le sac de mission → rendu à Nora**. Aucun de ces états ne sert de monnaie ou de matériau ordinaire. Sortir de la scène n'efface pas le transport. Recharger ne remplit pas à nouveau le panier.

Le joueur rend les objets un par un. À la fin, Nora verse **45 capsules une seule fois**. Le paiement exige les trois restitutions et la fin des dangers ; il n'est pas accordé pour la seule ouverture des palans ou la mort des gabians.

Trois constats sont calculés à partir des oiseaux :

- **Deux survivants :** les deux ont rejoint les points de nourrissage ; cela ne certifie pas que le joueur n'a jamais tiré.
- **Une perte :** un oiseau est mort, l'autre est à l'écart. La mort ne disparaît pas du carnet.
- **Deux pertes :** les deux sont morts. Le joueur doit encore descendre les paniers, récupérer et rendre les objets.

La récompense reste identique : Nora rémunère la restitution, pas une prime au cadavre. Il n'y a pas de butin ni d'expérience renouvelable par gabian.

## Interface et persistance

Le registre `v073Gabians`, schéma 1, conserve les objets, les positions des oiseaux en millimètres, leurs phases et blessures, les effets, l'annonce et la chute d'un projectile, les appâts, les méthodes et positions des paniers, puis le constat final. Les objets graphiques et les collisions sont reconstruits à partir de ces données.

Le Pip-Boy propose **DATA → GABIANS · OBJETS TROUVÉS**. Le journal, le repère vers le Vieux-Port, l'objectif local et le bulletin textuel reflètent les étapes réelles. Les anciens sujets du représentant restent accessibles.

Les échanges refusés par la sauvegarde sont annulés. Un point de passage automatique non enregistré met la simulation locale en pause et invite à retenter l'écriture auprès de Nora. Une confirmation périmée ne permet pas de répéter une transaction. Comme pour les rats, l'annulation d'une blessure en cas d'écriture refusée ne recrée pas une balle déjà tirée par le système d'arme.

## Portée vérifiée et chantiers encore ouverts

Les tests du modèle et les parcours navigateur portent sur cette cour, son vrai code d'interaction, le tir natif, les collisions, les trois issues et la sauvegarde/reconstruction. Les déplacements et visées de test sont scriptés ; le représentant extérieur est une scène synthétique utilisant la véritable identité de catalogue. Le rendu de test est logiciel.

Le lot ne certifie pas une traversée complète sur les données IGN, la reprise à froid de cette nouvelle mission après fermeture du navigateur, les performances d'un appareil donné ou une campagne humaine prolongée. Le test de reprise à froid des rats est une preuve du lot précédent, pas une certification implicite de celui-ci.

Restent distincts : pigeons et boss documentaires, caches régionales dynamiques, vols d'inventaire avec protections anti-blocage, autres métiers de la consigne, restitution directe aux trois propriétaires, doublage, nouvelles animations détaillées, navigation libre et vérification des accès géographiques réels.
