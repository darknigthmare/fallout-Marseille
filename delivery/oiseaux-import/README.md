# Import contrôlé — gabians et pigeons

Base exacte : `8924be65a69f7335364b09934bc908bf17d0973e`.

Les sept fragments contiennent uniquement un correctif source UTF-8 compressé. Le workflow vérifie les SHA-256 du flux XZ et du correctif décompressé, puis utilise `git apply --check` avant toute modification. Il reconstruit le jeu avec le véritable `tools/build_single.py`, exécute les tests et les parcours navigateur et publie seulement sur cette branche.

Aucune donnée géographique, permission de partage, secret ou sauvegarde utilisateur n'est contenue dans ce correctif. Les fichiers temporaires sont retirés avant la proposition finale. La compilation et la validation restent à confirmer par le workflow ; les résultats locaux ne sont pas une réussite CI anticipée.
