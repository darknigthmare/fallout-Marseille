# Le faux midi — cigales, balise et terrain

## Reprise et périmètre

Base : `9757fad0a3d95d5a9384b39bf1a8a59587d11fc3`, après fusion des Marins-Sapeurs. Cette rencontre indépendante développe le bestiaire de la bible et les Vigies, sans exiger les autres chaînes de quêtes.

La visite part du relais existant de Font de Mai (`v042-garlaban-caravan-01`). Le nouvel enclos `v071-relais-faux-midi` reprend cet ancrage comme point de fiction, sans inventer un bâtiment réellement relevé, une route IGN ou une altitude. Le passage à pied est narratif, par chargement. Le paysage compact est un terrain de jeu original, pas une reproduction de Font de Mai.

Les mutations, le programme agricole et ses effets acoustiques relèvent du fan-lore original de Fallout: Mistral. Il ne s’agit ni de canon officiel de Fallout, ni d’une explication scientifique du comportement des cigales réelles.

## Ce que la machine appelle encore midi

Avant la guerre, le relais synchronisait des consignes agricoles et des relevés sonores. Sa procédure de remise sous tension vérifiait les haut-parleurs en rejouant un signal court. Après la perte de ses capteurs et de son horloge, il s’est mis à recommencer la vérification au lieu de la terminer.

Ce comportement n’a pas créé toute la faune mutante. Il entretient une perturbation locale dans un habitat déjà marqué par la Pluie Blanche, les câbles enterrés et les anciennes cultures expérimentales. Abattre les trois adultes ne répare donc pas le relais ; arrêter le relais ne décontamine pas les sols.

Les habitants appellent ce signal **le faux midi**. Ils n’entendent pas un prédateur unique qui aurait pris le contrôle de la colline : ils entendent une machine qui amplifie une réponse qu’elle provoque elle-même.

## Aline Richaud, une vigie qui observe aussi les machines

> « Les tuer ne coupera pas cette machine. Je veux un constat, pas une collection de trophées. »

Aline tient un poste protégé près de l’entrée. Elle relève les mues, les déplacements et les reprises du signal. Sa tâche n’est pas de garantir que toute créature mutante est inoffensive, mais de distinguer un danger naturel d’une installation qui l’aggrave.

Elle explique les murets et le sectionneur, puis attend les résultats. Elle ne condamne pas automatiquement une personne qui s’est défendue, et n’efface pas non plus les morts du carnet. Les 65 capsules rémunèrent le constat et la suppression de la cause locale, pas le nombre d’insectes abattus.

Aline est un acteur local de cette scène. Elle n’est pas une nouvelle compagne recrutable et n’administrera pas seule tous les incendies et toutes les migrations du Garlaban.

## Trois adultes déjà issus du bestiaire régional

Le code utilise le **modèle régional `mistralCicada` existant**, agrandi avec ses volumes de ciblage. Les termes suivants nomment les individus de cette rencontre, sans prétendre implémenter trois nouvelles espèces ou trois modèles inédits :

| Individu | Place dans la scène | Identité |
|---|---|---|
| Crisseuse des restanques | Perchoir ouest | Individu associé au premier passage latéral. |
| Cymbalier du relais | Perchoir central | Individu le plus directement placé face à la boucle sonore. |
| Porteuse de chaux | Perchoir est | Palette plus claire ; ce n’est pas une nouvelle armure générale attribuée à l’espèce. |

Les ailes, pattes, tête, corps et tymbal conservent les parties ciblables du modèle. Aucun humanoïde recoloré ne sert de remplacement. Une enveloppe vide près du poste d’observation représente une mue ; elle n’est ni un quatrième ennemi ni un objet revendable.

L’observation rappelle que les mues ne prouvent pas l’existence d’une reine. Ce lot **n’implémente pas Midi-Zéro**, ni toutes les variantes de cigales annoncées dans la bible, ni une colonie reproductrice simulée.

## Une attaque qui peut manquer sa cible

Les trois adultes restent sur leurs perchoirs tant que le relais émet. Lorsqu’un joueur est visible et assez proche, l’insecte prépare un crissement pendant **1,4 seconde**. La direction est enregistrée au début de cette préparation, et non recalculée au dernier instant pour suivre automatiquement le joueur.

Des lignes ambrées, un message et l’animation existante indiquent l’axe. Le signal sonore utilise le générateur audio déjà disponible. Il ne s’agit pas d’un nouveau cri enregistré ou d’un doublage.

Au déclenchement, le moteur contrôle la direction, la portée et la ligne de vue. Une esquive latérale, un muret ou une sortie de portée peuvent éviter l’impact. Les dégâts de base sont **6 PV et 12 PA**, modulés par les blessures de l’individu et, pour les PV, par les protections ordinaires du joueur. Une récupération sépare les attaques.

Ce pouvoir acoustique est une abstraction de combat Fallout. Il n’ajoute ni maladie, ni irradiation ni paralysie permanente. Le mode menu suspend le comportement ; un chargement ne produit pas une attaque déjà arrivée à sa dernière image.

## Deux observations et une coupure concrète

Les mues et le câblage se lisent sur place. Le joueur peut explorer et même couper le signal avant d’avoir accepté formellement le constat : l’ordre du journal ne doit pas rendre un interrupteur artificiellement inutilisable. Il faudra néanmoins accepter la demande et réunir les deux observations pour la conclure.

Le sectionneur se trouve derrière les trois perchoirs. Des passages latéraux évitent les murets et permettent de l’atteindre sans tirer. La coupure manuelle est gratuite ; une alternative **Intelligence 5 + 1 circuit** ajoute la méthode technique au carnet. Elle n’accorde pas de butin ou de soin supplémentaire.

Une fois la coupure sauvegardée, le voyant de la balise s’éteint et les adultes cessent leurs crissements. Les survivants avancent réellement vers les fissures, à un maximum de 2 mètres par seconde, sur des trajets de 10 mètres. La collision est vérifiée avant chaque déplacement. Il ne s’agit pas d’un système général de vol ou de recherche de chemin.

Les blessures aux pattes et le ralentissement peuvent prolonger ce retrait. Les effets ordinaires de brûlure et de ralentissement restent pris en compte et sauvegardés. Les compagnons cessent de sélectionner automatiquement ces individus après la coupure ; le joueur peut toujours les attaquer tant qu’ils n’ont pas quitté la scène. Une brûlure déjà appliquée n’est pas effacée pour embellir le résultat.

## Le constat ne réécrit pas la rencontre

Le résultat dépend de l’état des trois individus, pas d’un bouton de dialogue qui choisit rétroactivement ce qui s’est passé.

**Retrait :** les trois adultes ont rejoint les fissures. Certains peuvent avoir été blessés ; le texte ne prétend pas qu’aucun tir n’a été effectué.

**Pertes partielles :** une ou deux cigales ont été abattues, les survivantes se sont retirées. Couper le relais ne ressuscite pas les morts.

**Trois adultes abattus :** les pertes sont inscrites, mais le relais doit encore être arrêté pour ne pas répéter le problème.

Les trois résultats donnent **65 capsules une seule fois**, après les observations et la résolution. Ces spécimens ne donnent ni butin renouvelable ni prime individuelle d’expérience. Leurs corps peuvent rester visibles ; il ne s’agit pas d’un nouveau système général de dépouillage.

## Sauvegarde, combat et anciennes campagnes

Le registre `v071Cigales`, schéma 1, conserve la santé en centièmes, les blessures, les durées d’effets, les positions de retrait en millimètres, les observations et la coupure. Les objets du moteur sont reconstruits à partir de ces valeurs, sans référence à des acteurs d’une ancienne scène.

Les impacts passent par le ciblage et les armes natifs. La sauvegarde de santé refusée annule le changement de l’acteur ; **elle ne rembourse pas automatiquement une balle que le moteur a déjà tirée**. Les ressources de dialogue, la coupure et la récompense sont transactionnelles. Une arrivée non sauvegardée suspend le retrait et peut être retentée auprès d’Aline. Les sauvegardes manuelles conservent aussi le déplacement intermédiaire.

Les anciens registres politiques, contrats, actes, repas, caisses et secours ne sont pas réécrits. La logique du reste du bestiaire reste inchangée en dehors de cette instance. Les sauvegardes anciennes sans le nouveau champ reçoivent un carnet neuf ; les données contradictoires ou futures sont refusées plutôt que de réinitialiser silencieusement les morts.

## Interfaces et limites

Départ : représentant de Font de Mai, sujet **Vigies · Le faux midi**. Carnet : **DATA → CIGALES · LE FAUX MIDI**. Journal, suivi, objectifs locaux et bulletin radio textuel sont présents. La sortie reste accessible pour interrompre une visite.

| Livré | Non revendiqué |
|---|---|
| Rencontre avec trois individus, perchoirs, balise et murets | Renouvellement complet du bestiaire ou de l’IA mondiale |
| Crissement annoncé, esquive, ciblage natif, blessures et effets | Nouveau moteur audio, projectile physique sonore ou vol libre |
| Retrait progressif et trois constats persistants | Migration écologique de toute la Provence ou purification des sols |
| Modèle insecte existant et nouveau niveau original | Trois nouveaux modèles HD, Midi-Zéro ou reproduction de l’espèce |
| Parcours navigateur avec vrai moteur et vrai tir | Campagne humaine complète, accès IGN à froid ou certification GPU |

Les tests utilisent un relais extérieur synthétique conservant l’identité de Font de Mai, un stockage isolé et des positions scriptées. Ils contrôlent le véritable intérieur et une voie latérale avec la fonction native de déplacement. Les scénarios de pertes multiples emploient l’adaptateur de dégâts du jeu ; le test de tir utilise séparément l’arme native et son coût en munition. Les rapports distinguent ces contrôles.

## Suite du bestiaire

Le boss Midi-Zéro, les nymphes fouisseuses, les grandes émergences, les déplacements de colonies et les interactions entre espèces restent des chantiers. Cette rencontre fournit un premier cas où comprendre un habitat et son équipement change réellement le comportement d’un ennemi, sans prétendre solder tous ces manques.
