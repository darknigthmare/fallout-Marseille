# Lore — point de reprise après De main en main

> **Lecture actuelle :** Éloi, Mina et Rachid sont présents et les remises personnelles sont jouables. Six scénarios de reprise à froid des oiseaux sont ajoutés ; leurs résultats et le programme exact figurent dans `verification/retrouvailles/QA.json`. Les sections antérieures ci-dessous conservent leur état historique, avant les actualisations placées en fin de document. Elles ne doivent pas être relues comme la liste actuelle des manques.

## Historique des audits et des étapes précédentes

Base examinée : `da8e4f99b5d08480101910088c64a4012bbca301`, après la première audience du Lys. Ce suivi prolonge les anciens audits sans attribuer leurs résultats à un nouveau programme. Un arc local jouable ne clôt pas une faction entière.

## Boucles présentes et limites

| Domaine | État de la source | Limite |
|---|---|---|
| A‑03 / M.A.D.A.M.E. | Registre civique, preuves, réseaux, projections | Pas une preuve de campagne humaine complète |
| Conseil régional | Motions, délégations, ratification, épilogues | Pas de transformation physique automatique de toutes les villes |
| Continuité / services | Dossiers, coûts, choix, retours et bulletins | Les factions n’ont pas toutes leur territoire ou campagne complète |
| Poste Restante | Sept lettres, copies, mobilier et contre-dons | Pas de facteurs, véhicules autonomes ou Camille recrutée |
| Pharmacies | Garde, lot réservé, stocks et soins finis | Pas d’hôpital complet ni de guérison illimitée |
| Cité Radieuse | Intérieur, cinq habitants, vote et trois travaux | Ni tour entière ni restitution architecturale 1:1 |
| Mutuelle | Sinistre local, trois accords et colis | Ni siège complet ni assurance mondiale |
| Notaires | Coffre, preuves, actes et reçus | Pas de justice nationale ou propriété mondiale |
| Fête des voisins | Repas, son, dispositions, portions et conclusions | Pas de marche autonome vers la table, doublage ou animations de repas |
| Compagnons | Deux relais, montage, épreuve et fabrication finie | Pas de maisons de métiers complètes ou de grades |
| Cour du Lys | Audience indépendante, quatre habitants, LOUIS, archives et trois règlements | Pas de campagne de succession, conquête de la rade ou navigation libre |
| La part des absents | Quai fictionnel, trois acteurs, six caisses persistantes, deux accès et trois répartitions | Ni flotte, ni faim quotidienne, ni campagne de faction complète |

| Marins-Sapeurs | Première intervention indépendante, feu/câble et deux évacuations accompagnées | Ni caserne complète, ni propagation mondiale, ni navigation générale |

## Priorité 1 — territoires et effets concrets

**Cour du Lys d’If : audience et premier ravitaillement incarnés, faction encore ouverte.** La part des absents reconnaît le règlement choisi (serment, commune ou régence), fait intervenir un délégué révolutionnaire et Maëlle des Francs dans une manutention physique. Restent la succession, la campagne de l’opposition, les opérations maritimes et les effets quotidiens sur les familles. Ne pas réinstaller silencieusement l’ancienne monarchie pour répéter l’audience.

**Arsenal / Francs du Large / Amirauté.** Les dossiers existants et le clapet des Compagnons ne constituent pas des chantiers navals complets. La cale possède désormais Maëlle, un lot fini et un treuil manipulable, mais restent les équipages complets, opérations, autres lieux et navires incarnés. Une traversée narrative par chargement n’est pas une flotte simulée.

**Missions extérieures.** Développer des objectifs explorables et des obstacles réels hors de la Cité. Les deux relais des Compagnons et les deux points de départ du Lys sont raccordés aux identités du catalogue, mais ne certifient pas tous les trajets sur les routes IGN.

**Conséquences régionales.** Ajouter des effets mesurables sans réécrire les anciennes ratifications. Une décision locale ne remplace pas la fin politique de toute la région.

## Priorité 2 — profondeur et inventaire

**Compagnons.** Maisons de métiers, plusieurs ouvrages, reconnaissance, circulation des plans, conflits d’accès au savoir. Les correspondants restent des voix dans les relais existants.

**Pétanque / COCHONNET.** Auditer le mini-jeu et les arbitrages déjà présents avant de les approfondir. Un nouvel intitulé ne constitue pas une mécanique ou un recrutement.

**Bestiaire / armes.** Produire un inventaire reliant chaque entrée de la bible à une identité de code, un habitat, une apparence, un comportement, un butin et des preuves de test. La liste documentaire n’est pas une couverture intégrale du jeu.

**Compagnons recrutables.** Distinguer les personnes présentes dans une scène des alliés réellement recrutables avec suivi, combat et sauvegarde. Les nouvelles scènes ne ferment pas ce chantier.

## Priorité 3 — factions encore principalement documentaires

Plan-de-Campagne et les Enseignes ; Virages du Vélodrome ; Maquis des Treize Vents ; Cohorte Viénot ; Confrérie du Vœu ; Félibres ; Tour des Ruines. Vérifier l’existant avant d’annoncer une intégration ou d’écraser des lieux et systèmes déjà présents.

Doublage, animations des métiers et des repas, identité visuelle détaillée des personnages, mise en scène des voyages et performances matérielles restent distincts des dossiers de quêtes.

## Géographie et validation

Aucun relevé IGN n’a été changé par l’audience du Lys ou sa cale de ravitaillement. Son ancrage est un point approximatif du catalogue existant, explicitement distingué d’une porte relevée. Les scènes de port synthétiques testent les dialogues et le retour, pas une traversée maritime réelle.

Une passe de géographie doit encore vérifier les accès, collisions, annulations et retours sur les données complètes, dans les deux sens. Une altitude absente ne doit pas être remplacée par une mesure inventée.

Ce suivi ne signifie ni « jeu fini » ni « commercialisable ». Les rapports du lot décrivent seulement le programme et les scénarios réellement vérifiés.


## Mise à jour — Marins-Sapeurs, premier secours accompagné

Base `3d0c3ef0fc8334289759f707dc107792acfc5270` : la manutention des six caisses est fusionnée. L’annexe [Marins-Sapeurs](LORE_MARINS_SAPEURS.md) décrit une mission indépendante avec feu et câble actifs, deux portes et un accompagnement réellement déplacé et sauvegardé. Le secours d’une goule consciente et d’une humaine n’est pas soumis à la conformité d’un registre.

**Ce qui est ajouté :** une scène séparée, Farah, Lila et Rémi, deux voies d’extinction, des trajets d’évacuation contrôlés par proximité/visibilité/collisions, attente/reprise, points de sauvegarde, deux arrivées et une récompense unique. Le modèle de trajet est scénarisé ; ce n’est pas encore un système général de compagnons libres.

**Ce qui demeure ouvert :** caserne et flotte des Marins-Sapeurs, campagne régionale de triage, propagation d’incendie, interventions sur les quartiers IGN, recrutement, retour géographique à froid certifié. Le développement des territoires de l’Arsenal et de l’Amirauté, l’inventaire bestiaire/armes, les factions documentaires et la géographie réelle restent prioritaires ; une première mission de secours ne les clôt pas.


## Actualisation après Le faux midi

Base : `9757fad0a3d95d5a9384b39bf1a8a59587d11fc3`, Marins-Sapeurs fusionnés après leurs contrôles finaux. La nouvelle [rencontre des cigales](LORE_CIGALES_FAUX_MIDI.md) donne au modèle régional existant une rencontre indépendante : crissements esquivables, balise coupable, contournement gratuit, retrait des survivantes et pertes persistantes. Ce n’est pas un nouveau catalogue complet.

**Bestiaire restant ouvert :** Midi-Zéro, nymphes et émergences, diversité des comportements hors instance, interactions entre habitats, variantes visuelles réellement distinctes, inventaire complet des espèces et armes promises. Le présent lot ne valide pas toute la carte IGN, les anciens boss ou les comportements des autres espèces.

**Institutions encore à approfondir :** campagnes de la Convention et de ses courants, succession du Lys, Confrérie du Vœu, territoires et opérations de l’Arsenal/Francs/Amirauté, Plan-de-Campagne, Virages du Vélodrome et recrutements. Les boucles locales livrées ne ferment pas ces factions entières.


## Actualisation après Les dents du réseau

Base : `38a0bd2aff02303dc6c80357915eaf45225eeef2` (Le faux midi fusionné après ses contrôles). La [rencontre des rats-câbles](LORE_RATS_CABLES.md) met le modèle régional existant en situation dans un dépôt original de maintenance : patrouille bornée, morsure esquivable, santé et blessures persistantes, refuge accessible, appât réservé, gaines et éclairage restaurés. Une élimination des animaux ne dispense pas de réparer.

**Ce qui reste ouvert dans le bestiaire :** Rat-couronné, Roi des Égouts, nouveaux comportements urbains hors des scènes dédiées, pigeons et gabians avec interactions de récupération, nymphes et Midi-Zéro, habitats reliés et inventaire complet des armes/espèces. Trois individus nommés ne sont pas trois modèles ou espèces supplémentaires.

**Ce qui reste ouvert chez les Aiguilleurs :** fonctionnement des trains, trafic, dépôts supplémentaires et campagne de souveraineté ferroviaire. Les circuits de cette annexe ne remettent aucun train en service. Les campagnes politiques, opérations maritimes, recrutements et vérification réelle des accès IGN demeurent des chantiers distincts.


## Actualisation — Les objets trouvés (livraison locale)

Base confirmée : `8924be65a69f7335364b09934bc908bf17d0973e`. Le nouveau [chapitre des gabians](LORE_GABIANS_OBJETS_TROUVES.md) incarne la récupération de trois objets personnels dans une consigne fictionnelle raccordée au relais existant du Vieux-Port. Nora est le seul nouveau PNJ ; les deux gabians réutilisent le modèle régional et les trois propriétaires sont des personnes évoquées, pas trois acteurs déjà placés.

**Implémenté dans le paquet :** déplacement aérien borné et soumis aux collisions, ailes ciblables, brûlure/ralentissement, lâcher annoncé et projectile sauvegardé, deux appâts réservés, deux palans réellement déplacés, arrêt sous charge occupée, prise puis restitution de chaque objet, silhouettes distinctes, trois constats, 45 capsules uniques, DATA/journal/HUD/radio. Les ressources ordinaires du joueur ne sont pas volées.

**Vérifié :** tests de logique et parcours navigateur détaillés dans `verification/gabians/QA.json`. La reprise à froid des rats n'est pas réattribuée aux gabians. Les tests externes utilisent un relais synthétique, pas un parcours complet IGN. Le correctif du workflow ajoute le treizième parcours mais aucun nouveau run GitHub n'a été déclenché ici.

**Encore ouvert :** Biset de plomb, Pigeon-paratonnerre, Général Biset, écologie hors instance, caches dynamiques et vol d'inventaire sûr, restitution aux propriétaires incarnés, nouveaux rigs détaillés, doublage et géographie réelle. Ce lot ne clôt ni l'inventaire complet du bestiaire ni les campagnes des factions. Succession du Lys, opérations maritimes, territoires de l'Arsenal/Amirauté/Francs, factions documentaires et compagnons recrutables restent ouverts.

**Publication :** paquet local et patch source seulement ; `main` n'a pas été modifié par ce lot.

## Actualisation — Poste Restante et pigeons de voisinage

La suite **La bonne adresse** ajoute une cour indépendante, trois personnages, deux plis et deux pigeons neutres. Chaque oiseau retourne à un colombier fixe ; l’arrivée, la signature et la clôture sont des états distincts. Le portage à pied reste gratuit. Les reçus et l’affichage public sont des conséquences locales, pas une reconstruction des services de toute la ville.

**Restent ouverts :** les pigeons hostiles, le Général Biset, les réseaux de livraison entre véritables territoires IGN, les transports des oiseaux vers les relais, le recrutement de Camille, le doublage, les simulations d’accueil des destinataires et la navigation animale libre. Les gabians restent dans la même livraison ; leurs essais à froid après fermeture complète du navigateur ne sont pas certifiés par les anciennes validations des rats.

**Livraison :** les versions locales Gabians/Pigeons sont réunies pour publication. Le statut exact de la PR et les empreintes canoniques se trouvent dans le rapport de livraison, pas dans une déclaration anticipée de fusion.

## Actualisation — De main en main et reprises des oiseaux

Base : PR 18, `9849cb57512b93379e27070f8145c23180005cd4`. **Propriétaires incarnés :** Éloi, Mina et Rachid sont maintenant présents à la consigne ; remise directe, remise depuis le comptoir, trois souvenirs, reçus matériels et épilogue facultatif. La prime originale reste unique. Le schéma 2 conserve les données du schéma 1 sans inventer des remises personnelles.

**Vérification ajoutée :** six scénarios de reprise à froid propres aux oiseaux, distincts du test historique des rats, et un parcours des restitutions. Le résultat exact (local, CI, programme et empreinte) figure dans `verification/retrouvailles/QA.json` ; la présence du test ne vaut pas à elle seule réussite.

**Restent ouverts :** animations de remise, doublage, routines et départ des propriétaires, vol dynamique de ressources, variantes hostiles des pigeons/Général Biset, réseau postal sur les vrais territoires IGN, écologie hors instance et navigation animale générale. La branche COCHONNET reste séparée. Les campagnes politiques, territoires maritimes et recrutements ne sont pas clos par cet épilogue.
