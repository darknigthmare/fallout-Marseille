# Architecture Marseille : preuves de validation

Build HTML : `72a6230345abd1bfb889896f5923f3c66962148fb70f5d941fd2e58b59a8e817`. Les rapports originaux sont conservés sans modification.

- Unités isolées : **877 assertions**, zéro processus en échec ; voir `UNITS.json` et `units/`.
- Contrats hérités : **434 assertions**, quinze suites avec bancs contrôlés/synthétiques ; voir `legacy/`. Les scripts adaptés sont recréés et vérifiés contre leurs empreintes d’exécution.
- Rebuild indépendant : **3 sorties identiques**, syntaxe JavaScript valide ; voir `REBUILD.json`.
- Navigateur ville assisté : **77 assertions** ; navigateur architecture assisté : **101 assertions**. Les aides et observations réseau restent décrites dans chaque rapport.

Pour le pilote ville hérité, l’identité du script exécuté, du rapport et de stdout est attestée après exécution : `city/EXECUTION_IDENTITY.json` conserve cette limite explicitement ; le rapport original est intact. Le nouveau pilote architecture inscrit le SHA du script dans son rapport d’exécution.

Les deux pilotes natifs utilisent le HTML de production, les données IGN locales, le vrai HTTP et le stockage navigateur. Les placements de caméra, gels QA et déplacements physiques cadencés sont assistés. Les captures sont des rendus WebGL ; le SVG est une vue d’audit dérivée du véritable export de layout et conserve ses liens SHA. Aucun plan documentaire synthétique n’est installé dans ces pilotes.

`coverage-initial/` contient les reproducers baseline, y compris les fixtures documentaires explicitement synthétiques. `coverage-final/` contient les comparaisons sur objets IGN réels et la procédure portable. Leurs cas de couverture ne sont pas comptés comme parcours navigateur. `historical/` conserve les trois tentatives en échec, exclues des totaux finaux.

Les façades/pièces inventées ne sont pas des relevés réels. Cette publication ne certifie pas une reproduction documentaire intégrale de Marseille ni un jeu complet.

`ARCHITECTURE_INTEGRATION.json` sépare toutes les méthodes, totaux et limites. `MANIFEST.json` donne les SHA-256 de tous les fichiers publiés, hors lui-même. Le collecteur ne lance ni test, navigateur, acquisition réseau, ni build : `python scripts/collect_architecture.py --repo CHEMIN --evidence DOSSIER_QA --check-only`. La publication exige `--publish` ; `--replace` permet de remplacer un ancien dossier après validation complète.
