# Le carnet des ateliers — armes et noms du pays

Création de fan non officielle. Période : 2297. Ce chapitre prolonge les arsenaux des sections 37 à 44, sans transformer chaque proposition de la bible en arme terminée.

> « On a repeint trois fois le nom. La chambre, elle, n’a pas changé. » — note anonyme recopiée au bas d’une fiche d’atelier.

## Une provenance locale, pas un catalogue de miracles

Les armes du Mistral restent liées aux métiers et aux pénuries de la région : pièces réfractaires d’Aubagne, outils navals de La Ciotat, équipements des relais, sûreté du rail, récupérations portuaires. Les factions entretiennent ou détournent des objets dont la fonction survit parfois à l’institution qui les a commandés. Un nom prestigieux, une formule administrative ou une peinture neuve ne change pas l’alimentation réelle.

Le carnet est une copie documentaire accessible depuis **DATA → ATELIERS · ARMES**. Aucun nouveau archiviste n’est placé, aucune connaissance confidentielle n’est prétendument découverte et aucune arme n’est reçue en le lisant. Il ne remplace pas les marchands, recettes et conditions d’obtention existants.

Les **55 identifiants régionaux** étaient déjà déclarés dans `MISTRAL_WEAPON_IDS`. Cette livraison fixe leur association visuelle par identifiant, au lieu de laisser leur seul nom français choisir le type de silhouette. Les armes non régionales gardent leur présentation antérieure. Ce ne sont ni 55 nouveaux équipements, ni 55 modèles uniques.

## Trois présentations supplémentaires

### Aiguilles pneumatiques

L’Aiguille du Mistral et l’Aiguille des Veilleurs utilisent désormais un petit tiroir et trois fenêtres de dards représentatives plutôt que la cassette de rivets générique. Le tiroir suit la main et l’emplacement de rechargement existants. Les trois fenêtres ne sont pas un compteur du nombre exact de projectiles : le HUD conserve la quantité autoritaire.

L’Aiguille du Mistral consomme les **seringues** de son catalogue ; celle des Veilleurs utilise les **dards du Mistral**. Leur ancienne origine médicale ne rend pas leurs tirs non létaux et ne soigne pas une cible. Le ralentissement et les dégâts restent ceux du système de combat déjà présent.

### Scie céramique d’Aubagne

La scie reçoit un moteur compact, un carter, une poignée et un disque réfractaire, à la place de la longue lame générique. Les fentes des deux faces suivent l’impulsion visuelle de l’attaque ; la réduction des mouvements conserve le disque sans cette rotation.

La scie reste une arme de mêlée. Aucun stock de carburant, nouveau dommage continu, projectile volant ou démontage du décor n’est créé. La portée et les cinq impulsions de sa définition historique ne sont pas reparamétrées par ce travail de présentation.

### Mortier du Garlaban

Pendant le rechargement, le mortier présente une **courte charge de 40 mm** sur la trajectoire de main existante, et non une longue roquette. La silhouette de base reste partagée avec les lanceurs. Les dimensions visuelles sont stylisées ; ce chapitre n’est ni un plan de fabrication ni une simulation balistique nouvelle.

Le mortier conserve son magasin d’un coup, son alimentation `grenade40`, ses dégâts et son souffle existants. La charge de présentation disparaît à la fin du rechargement ; elle n’ajoute aucun objet à l’inventaire.

## Identités visuelles corrigées

L’**Arc salin** est représenté comme un projecteur énergétique alimenté par ses cellules à proton, pas comme un fusil ordinaire. Le **Juge civique**, explicitement décrit comme un revolver dans sa donnée historique, retrouve cette famille, même si son nom ne contient pas le mot « revolver ». Le **Pistolet CONCORDE** garde sa silhouette énergétique courte. Les copies modifiées d’une arme conservent le même identifiant de présentation.

Le harpon, les bobines, la saumure et plusieurs outils restent associés à des familles communes : une association juste ne vaut pas modèle propre, mécanisme d’alimentation détaillé ou bruitage particulier. Les armes à lame longues gardent encore des limites de proportion et de pose.

## Ce que le joueur peut lire

La recherche accepte les accents ou leur absence. La liste est paginée et peut montrer uniquement les armes effectivement possédées. L’étiquette « équipée » vient de l’équipement courant. Une fiche non possédée n’annonce jamais qu’un vendeur voisin la détient.

Les munitions viennent de `AMMO_INFO`. Les valeurs affichées sont les **valeurs de référence avant état, améliorations, protection de la cible et difficulté**, pas une promesse de dégâts finaux. Salve, rafale et alimentation sont distinctes. Le bouton d’une arme possédée rejoint sa fiche d’inventaire existante ; il ne la remplace pas et ne l’équipe pas automatiquement. Aucune sauvegarde parallèle n’est ajoutée.

## Inventaire de la conception et état réel

L’[inventaire lisible](INVENTAIRE_ARSENAL_BESTIAIRE.md) et son [registre JSON](INVENTAIRE_ARSENAL_BESTIAIRE.json) rapprochent les 55 IDs régionaux, **49 noms d’armes des sections 38–42** et **98 désignations de créatures ou automates** des sections 29–36 et du catalogue de témoins v0.46.

Ces 98 désignations ne sont pas 98 espèces nouvelles : des variantes de nom, singuliers et pluriels restent distincts tant qu’un alias n’est pas attesté. Une correspondance exacte avec une donnée ne prouve ni acquisition, ni apparition en jeu. Le module de bestiaire conserve ses **neuf assemblages existants : cinq régionaux et quatre figures récurrentes**, pas 98 modèles.

Le Général Biset n’est pas l’un des deux pigeons neutres de Poste Restante. Une cigale ordinaire ne réalise pas Midi-Zéro. Le Rat-couronné possède déjà son rig quadrupède, mais pas l’agrégat conçu dans la bible. La Pique de la République et le Mousquet voltaïque de l’An 220 ne sont pas arbitrairement assimilés à une arme homonyme ou de rôle voisin. Les armes de la PR parallèle COCHONNET demeurent hors de ce lot.

## Vérifications et limites

`tools/audit_regional_content.py` génère l’inventaire depuis les sources locales et enregistre leurs empreintes. `--check` refuse les documents périmés. Les tests vérifient notamment les 55 associations, les copies modifiées, l’absence de mutation numérique, les volumes finis, les fenêtres de rechargement, les filtres et le maintien des anciennes familles.

Le parcours navigateur manipule les vrais menus, le tir et le rechargement, mais utilise un départ d’atelier préparé, des armes accordées pour inspection, des pas de temps pilotés et un stockage mémoire isolé. Il ne certifie ni l’obtention naturelle des 55 armes, ni une campagne humaine, ni toutes les résolutions ou toutes les manettes. Les captures sont celles du moteur compilé. Les résultats courants et l’empreinte exacte du programme sont publiés dans `verification/arsenal/QA.json` lorsqu’ils ont été exécutés.

Le doublage, le catalogue d’armures, l’équilibrage global, les alimentations propres à chaque arme et l’incarnation des créatures seulement conçues restent ouverts.
