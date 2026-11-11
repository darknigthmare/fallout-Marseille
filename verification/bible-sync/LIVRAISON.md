# Bible consolidée et cour habitée — 11 novembre 2026

## Ce qui était réellement publié

Au début de cette reprise, main était encore sur les rats (`8924be65`) ; les oiseaux, restitutions et gestes attendaient dans la PR 18, et la cour n’existait que dans le ZIP local. La PR 18 a été fusionnée après ses deux contrôles finaux réussis : `cfa5edd4439e214331323c3a3f1b9833ff464942`.

Cette suite part de ce main fusionné. Elle publie **Une place dans la cour**, reconstruit le programme depuis les sources complètes et consolide la bible centrale. Elle ne réécrit pas la branche parallèle COCHONNET nº 17.

## Bible, index et règles

La bible documentaire 1.2 garde ses fondations, ses factions, son bestiaire et ses arsenaux. Sa section 68 rassemble vingt ensembles narratifs et vingt et une annexes. `REGISTRE_LORE.json` relie ces ensembles à vingt-sept modules `src/v050/10*.js`, aux modèles et aux tests de logique. Le vérificateur refuse notamment module non documenté, chapitre absent, modèle absent, lien manquant ou doublon. Dix-neuf tests, dont des cas volontairement invalides, vérifient ce contrôleur.

Ce contrôle est structurel, pas une preuve que tout concept est jouable, tout récit compatible avec le canon officiel ou chaque arme terminée. Les limites figurent dans chaque entrée. Le Rat-couronné est correctement distingué : son rig `giantRat` existe déjà, mais n’incarne pas l’agrégat conçu dans la section 30. Aucun asset n’a été inventé pour masquer cet écart.

La page d’accueil du dépôt renvoie directement vers la bible, l’index, les manques et les preuves courantes.

## Programme et validations terminées

Publication initiale des sources et sorties : `d7e235b4c7db213c21c44f5bfcab5b233d7e3150`.
Run canonique : **43072219598**, job **130702818376**.
Révision documentaire : `7c0e1c3a85756e1052b839af0b1d392b497046bf`, run **43074250029**, job **130709821562**.

Résultats du programme canonique : 727 tests de logique, 19 tests de traçabilité, compilation complète et contrôle déterministe, quatre commandes de régression territoriale, 927 contrôles dans dix-sept parcours, 40 contrôles des trois reprises de cour, 65 contrôles des six reprises d’oiseaux et 26 contrôles historiques des rats. Aucune exception JavaScript dans les parcours terminés.

Les artefacts **13880201560** (programme/sources) et **13878434387** (preuves) ont été téléchargés ; leurs empreintes, les rapports et leurs programmes ont été comparés. Le HTML canonique est identique à l’édition locale de la cour : `43fc553655c5e06c19f592c27dbd67552f2a914ccfaa93e4e39a35eb56e8029b`. Cette reprise lève donc les anciennes limites de reconstruction complète et de trois reprises à froid non exécutées, sans attribuer des résultats historiques à un autre programme.

La précision documentaire a répété les 727 tests et les 19 contrôles, vérifié l’identité des quatre sorties et recalculé les empreintes documentaires. `QA.json` garde le registre au moment du test du jeu et le registre documentaire révisé. `DOCUMENTATION_REVIEW.json` détaille cette différence. Les répétitions ne sont pas additionnées comme tests indépendants.

## Portée et installation

La cour conserve trois invitations facultatives, trajets physiques, attente/reprise, dialogues à la position réelle et souvenirs. Sa prime historique de 45 capsules ne se renouvelle pas. Il n’y a toujours ni ferry, ni départ hors champ, ni voix enregistrée, ni animation d’assise de Mina.

Les essais ordinaires utilisent des positions scriptées et des départs synthétiques. Les reprises à froid utilisent un profil Chromium sur disque, une fermeture normale puis Continuer sur le programme inchangé ; elles ne certifient pas une coupure électrique, tous les navigateurs, une campagne humaine complète ou tous les accès IGN.

Le paquet est une mise à jour sans grandes archives géographiques. Exporter la sauvegarde, conserver les packs IGN, lanceurs et origine de lancement. Ne pas écraser une installation binaire de COCHONNET ou une branche plus récente avec ces sorties. Les sources de compilation, les tests et la bible sont fournis ; les données géographiques ne sont pas recréées.

Le workflow temporaire est retiré. Le workflow permanent teste désormais la bible, les dix-sept parcours et les trois suites de reprise à froid. Les contrôles de la PR après ce nettoyage et son statut de fusion doivent être lus dans GitHub ; ce document ne les anticipe pas.
