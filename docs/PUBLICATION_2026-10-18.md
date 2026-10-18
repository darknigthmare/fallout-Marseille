# Publication GitHub et Google Drive — 18 octobre 2026

Cette publication importe la livraison v0.49 originale dans `darknigthmare/fallout-Marseille`. Le dépôt contenait auparavant uniquement son README, au commit `cc60c2325da40199f109b430c6a3719bb86054c4`.

## Intégrité de la base

- Archive : `FALLOUT_MISTRAL_v0.49_PROJET_COMPLET.zip`.
- Taille : 127 071 766 octets ; 1 172 fichiers ; 171 706 393 octets extraits.
- SHA-256 : `172783f2026a1b8537b45a3b91df89bcd6afe425ade8613bb0210aff2ed6477c`.
- Intégrité ZIP et chemins d’extraction contrôlés ; contenu d’origine conservé.
- Aucun changement de gameplay ni nouvelle version du jeu dans cet import.

## Vérifications relancées

La reconstruction par `python3 tools/build_single.py` produit des fichiers `index.html`, `JOUER_FALLOUT_MISTRAL_v0.49.html` et `src/game.js` identiques octet pour octet aux fichiers livrés. `node --check src/game.js` réussit.

Les suites existantes `tests/v049/kernel.test.cjs` et `tests/v049/v048_inherited_legacy_distribution.cjs` passent leurs 31 assertions (22 + 9).

Le serveur local répond HTTP 200 avec le HTML attendu. Son audit confirme la version 0.49.0 et l’absence des 5 884 coordonnées vectorielles et des huit grilles. L’endpoint d’audit est servi avec `Cache-Control: no-store`.

Les 434 contrôles documentés dans les rapports d’origine restent des contrôles historiques. Aucun nouveau rendu Chromium n’a été obtenu pendant l’import : le navigateur n’était pas installé et son téléchargement a échoué. Les captures d’origine sont conservées avec leur provenance.

## Distribution Drive

[Dossier dédié](https://drive.google.com/drive/folders/1XYIrQczKXczburj2Tu0bDs2ZNH10Jxta).

Le transfert impose une limite de 100 Mio par fichier. L’archive est donc découpée en deux parties binaires, sans recompression ni retrait de contenu. Le script de recomposition vérifie chaque partie et l’empreinte du ZIP final. La recomposition est vérifiée avant publication des parties.

Les instructions et scripts correspondants sont conservés dans `distribution/`.
