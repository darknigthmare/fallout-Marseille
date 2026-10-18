# Architecture v0.49

## Modules ajoutés
- `src/v049/00_encounters.js` : sérialisation en liste blanche, identités validées, bornes et fusion conservatrice des reliquats.
- `src/v049/01_persistence.js` : journal des acteurs, capture avant déchargement, réapplication à l’instanciation, compatibilité des blessures et cycles de respawn.
- `src/v049/02_bodies_lifecycle.js` : dépouilles indépendantes du libellé régional, rattachement des interactions, sauvegardes et isolation du banc.
- `src/v049/03_interface.js` : diagnostic en lecture seule et hooks de tests limités au banc.
- `src/v049/style.css` : présentation du journal.

## Identité et ownership
Le catalogue résout les identifiants d’acteurs autorisés. Chaque entrée porte `id`, `site`, `scope` (inside/outside) et `kind` (enemy/npc). Une WeakMap lie les scènes à leur objet de sauvegarde propriétaire. Un checkpoint d’une scène appartenant à un autre état est refusé.

Le journal ne stocke pas de géométrie ni de closures. Les corps conservent les inventaires finis du système v0.26 ; seule leur identité territoriale devient stable.

## Cadence
Checkpoint à la sortie de proximité, après les dégâts, avant les sauvegardes et une fois par seconde de jeu actif. La restauration intervient au moment où le constructeur historique crée l’acteur. Les effets en cours sont suspendus hors écran.

## Bornes
À l’import : 2 048 fiches maximum et budget sérialisé de 2 Mio. Les positions finies, la santé, les membres et les états autorisés sont filtrés. Le catalogue actuel résout 1 176 identités possibles, contextes intérieurs compris ; un test vérifie que ce jeu maximal de fiches reste sous le budget. Ce n’est pas le nombre d’acteurs simultanément actifs.

Le corps du journal ne peut contenir que des clés/valeurs autorisées. La validation globale des sauvegardes reste responsable du rejet des clés de prototype interdites.

## Compatibilité
Les modules sources v0.46, v0.47 et v0.48 sont conservés octet pour octet. La v0.49 s’intègre après eux dans le build. Les anciennes données d’ennemis sont reprises de façon conservatrice lorsqu’elles existent ; aucun historique de position absent n’est inventé.
