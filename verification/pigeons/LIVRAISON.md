# Livraison oiseaux — base et portée

Cette livraison part de `8924be65a69f7335364b09934bc908bf17d0973e`. Elle publie la consigne des gabians, précédemment restée locale, et ajoute **La bonne adresse** : deux pigeons revenant à leurs colombiers, deux plis et deux reçus distincts.

Le run 42885942243 a vérifié le correctif, reconstruit avec `tools/build_single.py`, exécuté 610 tests de lore, quatre régressions territoriales, 791 contrôles des quatorze parcours et 26 contrôles historiques de reprise à froid des rats. Sources et sorties ont été publiées dans `09312a0d0264bf4cf22444747ca2b0ab678287f5`.

Le montage local initial contenait des séparateurs blancs supplémentaires. Son empreinte diffère de la compilation canonique. La livraison finale utilise les fichiers canoniques téléchargés ; le parcours pigeons a aussi été rejoué localement sur ce HTML (69 contrôles réussis). `QA.json` et `QA_LOCAL.json` distinguent les programmes et les résultats, sans additionner les répétitions.

Les fichiers temporaires d’import sont retirés. Le workflow permanent couvre les quatorze parcours. Une fermeture complète du navigateur spécifique aux pigeons et gabians reste à tester ; le résultat historique des rats ne la remplace pas.

La PR parallèle 17, **COCHONNET physique**, reste séparée. Cette archive n’écrase ni n’intègre sa branche. Ne pas remplacer les fichiers d’une installation COCHONNET par ce ZIP : une intégration ultérieure doit fusionner les sources, reconstruire et tester.

Le paquet ne remplace pas les grandes archives IGN, les lanceurs ou le dépôt source complet. Les scènes sont des créations de fan originales et les tests sont instrumentés, non une campagne humaine complète.
