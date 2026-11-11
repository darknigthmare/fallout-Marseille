# Audit de continuité de la bible — 11 novembre 2026

## Constat de départ

Au début de cette reprise, `main` restait à `8924be65` (rats), la PR 18 à `a589d8de` contenait les oiseaux et leurs suites jusqu’aux gestes, et « Une place dans la cour » n’existait que dans la livraison locale. Affirmer que tout était déjà dans la bible de la branche principale aurait donc été inexact.

La PR 18 a été fusionnée après ses deux validations finales réussies : `cfa5edd4439e214331323c3a3f1b9833ff464942`. La cour est reprise séparément, sans modifier COCHONNET nº 17.

## Ce qui est préservé

Les sections 1 à 63 de la bible restent la conception générale : chronologie 2297, A‑03, CONCORDE/M.A.D.A.M.E., réseaux, Convention et Bastille, Communes, Gilets de Cendre, Syndicat, forces maritimes, bestiaire, ATLAS, robots, arsenaux et armes de métiers, pétanque, campagne et compagnons. Aucune créature ou arme n’est déclarée jouable seulement parce que son nom figure dans ces sections.

Les annexes jouables ne remplacent pas ces fondations. La version documentaire 1.2 ajoute une table centrale des vingt ensembles narratifs et renvoie directement à leurs vingt et une annexes, plutôt que d’obliger à reconstituer l’état depuis les anciens comptes rendus.

## Ce qui est raccordé et vérifié

`REGISTRE_LORE.json` associe chaque ensemble à son modèle JavaScript, à tous ses modules `10*.js`, à un test de logique et aux chapitres concernés. Le vérificateur contrôle les chemins, l’unicité, les liens depuis l’index et la bible, les symboles et la couverture exhaustive de ce répertoire. Son rapport produit les SHA‑256 des fichiers réellement examinés.

La vérification n’analyse pas les intentions du récit et ne prouve pas la fidélité au canon officiel. Elle empêche des oublis matériels : module ajouté sans documentation, annexe inaccessible depuis la bible ou modèle retiré alors que le registre le promet. Les tests du jeu restent indispensables.

## Extension reprise

« Une place dans la cour » ajoute les promenades facultatives d’Éloi, Mina et Rachid, le dialogue à leur position réelle, l’attente et la reprise, des souvenirs à destination et la persistance `v076Consigne`. Les clefs ne créent pas un bateau, Mina reste debout près du banc et l’ardoise de Rachid ne promet aucun horaire. La prime de 45 capsules reste unique.

## Preuves et limites

Le précédent lot local annonçait correctement 727 tests de logique et 927 contrôles ordinaires, sans reconstruction complète ni reprise à froid validée. Ces preuves restent historiques. Le rapport courant `verification/bible-sync/QA.json` doit provenir des commandes effectivement exécutées sur le programme canonique. Aucune réussite distante n’est déduite du seul passage des tests locaux.

Une visite humaine de toute la carte IGN, tous les matériels, les coupures électriques, la flotte, les emplois du temps régionaux, le doublage et l’intégration COCHONNET restent hors de cette consolidation.

## Précision de lecture du bestiaire

Le chapitre `BESTIAIRE_REGIONAL.md` et `src/v050/13_regional_bestiary.js` décrivent déjà le Rat-couronné sur `giantRat`, avec silhouette, volumes ciblables et attaque. La consolidation ne le classe donc pas parmi les espèces entièrement absentes. Sa représentation actuelle demeure différente de l’agrégat conçu en section 30 ; aucune transformation graphique n’est inventée pour combler cet écart. Cette précision documentaire ne modifie pas les statistiques, les apparitions ou les sauvegardes. Le registre des vingt ensembles couvre les modules narratifs `10*.js`, pas l’inventaire intégral du module de bestiaire 13.
