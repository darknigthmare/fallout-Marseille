# Reprise du chantier — 10 novembre 2026

Base narrative : `38a0bd2aff02303dc6c80357915eaf45225eeef2`. Source des rats : `eef2a6176dfd13126a8420d819b59b476af3c060`. Sorties générées : `afbf2541d78353571e78195f0cf4172b89dbf6ad`.

Le run 42519872719, interrompu dans le compte rendu précédent mais pas dans GitHub, s'est terminé avec succès. Il a reconstruit le jeu, vérifié les tests de lore, les régressions de territoire et les douze parcours navigateur.

## Contrôles effectués pendant la reprise

- Programme de cet artefact repris sans réécriture du gameplay.
- Parcours `rats_browser_smoke.py` relancé localement : 81 contrôles réussis, aucune exception JavaScript.
- Première relance des tests sur l'archive seule : 534/536 réussis, deux échecs ENOENT dus aux fichiers `src/v049` non livrés. Ce n'était pas une validation complète réussie.
- Dépendances v049 restaurées depuis le programme avec vérification des empreintes Git d'origine : `00_encounters.js`, `01_persistence.js`, `02_bodies_lifecycle.js`.
- Relance après restauration : 536/536 tests de lore réussis. Le workflow inclut désormais `src/v049/*.js` dans l'artefact pour reproduire ces tests sans extraire des morceaux du programme.

## Nouvelle vérification de reprise à froid

`tests/expansion/rats_cold_save_smoke.py` prépare deux points de sauvegarde par les interfaces et modèles existants : retraite avec une blessure, un mort et des effets actifs ; dépôt terminé après remise de la récompense.

Le test ferme complètement Chromium, conserve son profil disque, remplace la page de préparation par le HTML de production inchangé au même chemin local, relance Chromium et clique sur le bouton **Continuer**. Il n'injecte aucun état ni faux LocalStorage dans la page de reprise. Un observateur met en pause immédiatement après Continuer pour comparer le point exact avant la frame suivante.

Ce scénario est exécuté en CI ; son résultat est dans `RATS_COLD_SAVE.json`. L'environnement local de reprise refusait les navigations HTTP et file avec `ERR_BLOCKED_BY_ADMINISTRATOR` : aucun résultat local de reprise à froid n'est revendiqué, et aucune politique locale n'a été modifiée pour les contourner.

La vérification porte sur une URL de fichier hors ligne avec un profil persistant, pas sur une coupure électrique, toutes les configurations de navigateur ou un retour géographique à froid sur l'intégralité des données IGN.

## Reproduire

```sh
node --test tests/expansion/lore_*.cjs
python tests/expansion/rats_browser_smoke.py --html index.html
python tests/expansion/rats_cold_save_smoke.py --html index.html
```

Les dépendances Playwright/Chromium sont les mêmes que dans le workflow de lore. Les rapports locaux et GitHub peuvent répéter les mêmes tests ; ne pas additionner les répétitions comme s'il s'agissait de scénarios indépendants.
