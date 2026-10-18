# Architecture v0.48

- `00_budget.js` : primitives testables dans Node (budget coopératif, annulation, correspondance de retour, segments de cloisons).
- `01_preparation.js` : préparation transactionnelle par petits lots. Les entités, index, maillages et cellules restent séparés de la scène active jusqu’à publication.
- `02_returns.js` : une scène extérieure retenue en mémoire, gardes de contexte et de budget, retour par la chaîne historique de chargement.
- `02b_passages.js` : cloisons de gabarits dans les deux sens, entrées orientées vers l’intérieur.
- `02c_door_transactions.js` : métadonnées d’instance conservées tant que la sortie n’est pas validée, réessai et annulation cohérents.
- `03_interface.js` : étapes réellement exécutées, diagnostic des pauses et de la mémoire retenue.

## Invariants
Aucune préparation annulée ne publie sa banque de relief. Le rendu courant reste lié à l’ancienne banque. Les acteurs conservés ne sont pas clonés à chaque retour. Un retour n’annule jamais les gains du joueur. Le banc dispose d’un emplacement de rétention séparé et ne sauvegarde pas la campagne.

## Ordonnanceur
Le travail rend la main par tâches de temporisation, pas seulement par microtâches. Le budget s’évalue entre opérations indivisibles. Les caches v0.47 restent en place ; leur réemploi évite de reconstruire un terrain ou une tuile validés.

## Références techniques
Le modèle d’exécution JavaScript documenté par MDN distingue les tâches de l’événement en cours : une pause de temporisation n’est pas une garantie de temps réel. Aucun nouveau système IndexedDB n’est ajouté dans cette passe. La navigation native étant bloquée dans l’environnement de vérification, les résultats navigateur sont explicitement limités à l’exécution du HTML et aux réponses contrôlées.
