# Publication GitHub et Google Drive — 18 octobre 2026

## Livraison actuelle : v0.50

La version v0.50 « Les routes retrouvées » est publiée sur la branche principale. Le [dossier Drive v0.50](https://drive.google.com/drive/folders/1xE5VpELY64tz5GV9CHHrlsIb_rfahRnQ) contient le jeu complet en un ZIP et le projet complet en cinq parties. Le dossier `distribution/` contient les consignes, le manifeste et les scripts correspondant exactement à cette livraison.

Le texte ci-dessous conserve le compte rendu historique de l’import v0.49. Ses tailles et constats concernent cette ancienne version.

## Historique : import v0.49

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

Les instructions et scripts de cette ancienne livraison restent accessibles dans [l’historique Git de distribution](https://github.com/darknigthmare/fallout-Marseille/tree/1e7ef8dc958bda56c573715ccf4c7ebdc791f241/distribution).
