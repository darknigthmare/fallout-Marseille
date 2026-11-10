# Les gestes retrouvés — livraison vérifiée

Base : `348a3cb2385b91771112f8c772def4cb82bd8c36`.
Sources jouables et sorties générées publiées : `71a25c1162f943029631d033559a744bb612017e`.

Éloi reconnaît sa clef puis la garde à sa ceinture ; Mina examine sa bague puis la porte à la main ; Rachid examine son sifflet puis le garde sur son cordon. Les gestes de 2,9 secondes sont une présentation après la transaction de remise réussie. Aucun nouveau champ de sauvegarde, aucune nouvelle récompense, aucun objet d'inventaire en double. Les accessoires sont reconstruits à partir des remises déjà enregistrées ; une ancienne remise n'est pas rejouée. Réduction des mouvements et suspension pendant les menus respectées.

Le marqueur et l'objectif de fin renvoient vers la sortie lorsque mission et épilogue sont terminés. Les rencontres restantes après paiement sont explicitement facultatives.

## Preuves et publication

Le run `42917085993` a réussi les 651 tests de logique (26 nouveaux), la compilation complète et son contrôle déterministe, les quatre commandes de régression territoriale, les 873 contrôles dans seize parcours navigateur (36 nouveaux), 65 contrôles de reprise des oiseaux et 26 des rats. Aucune exception JavaScript dans ces parcours. Sa dernière étape de publication a échoué sur les permissions de modification des workflows : le run global n'est donc PAS annoncé réussi.

Le run de publication séparée `42919475462`, job `130190397343`, a terminé avec succès. Il a téléchargé l'artefact validé, réappliqué les sources contrôlées, répété les 651 tests et les régressions territoriales, reconstruit le programme complet et vérifié l'identité de chacun des quatre fichiers générés avant de publier `71a25c1162f943029631d033559a744bb612017e`. Aucun workflow n'a été modifié par le compte automatique. Le nettoyage du workflow temporaire et l'ajout des seize suites au workflow permanent sont effectués séparément.

Artefacts contrôlés : programme `13809798068`, preuves `13810707308`. Le rapport actuel est `verification/gestes/QA.json`, la traçabilité de reprise est `PUBLICATION_RECOVERY.json`. Les rapports antérieurs et `QA_LOCAL.json` restent historiques. Les répétitions locales ne sont pas comptées comme des tests supplémentaires.

HTML SHA-256 : `8b90aea815826c0442c9742b6279c144043b1db99ef954d967621a054713e677`.

## Limites et installation

Gestes procéduraux stylisés du destinataire, pas transfert continu de la main du joueur ou du plateau, pas animation détaillée des doigts. Aucun doublage, déplacement autonome des propriétaires, ferry ou réseau postal régional ajouté. Les captures et le GIF utilisent le programme identique à la compilation canonique, avec une caméra scriptée ; ils ne mesurent pas les performances matérielles.

Les parcours sont instrumentés, avec positions et départs synthétiques ; les reprises à froid emploient un profil Chromium sur disque et une fermeture normale. Pas de validation humaine complète, de traversée IGN exhaustive, de tous les navigateurs ni de coupure de courant.

Livraison en PR 18, sans fusion de main. La PR 17 COCHONNET est intacte et séparée. Le ZIP est une mise à jour cumulative, pas un dépôt ou une installation géographique complète : exporter la sauvegarde, conserver les packs IGN et ne pas écraser une installation binaire issue de COCHONNET.
