# Architecture des ajouts v0.30

Les fichiers `src/v030/` sont assemblés après les modules v0.29 dans l’IIFE existante, avant init. Le HTML est totalement autonome. `tools/build_single.py` génère aussi `src/game.js`.

- `00_state.js` : modèle de six plaques, définitions, migration, limites et fonctions de lecture.
- `01_power.js` : charge conservée, conditions de manipulation, ponts avec déplacement/saut/V.A.T.S., usure régionale, réparations et configurations. Les échanges gardent les six états. Les ajustements globaux anciens utilisent un delta borné et ne nivellent plus les pièces.
- `02_visuals_world.js` : assemblage original partagé, représentation portée, décor de la baie, objets de quête et collisions persistantes.
- `03_story.js` : enquête, prérequis physiques, devis de restauration, manivelle alternative, deux accords, six scènes, cinq segments d’holodisque et suivi.
- `04_interface.js` : STAT → ARMURE, HUD, touches U/Tab, adaptation des entrées existantes, reprise et scénario séparé. Les fonctions debug de capture et de test sont explicites.
- `style.css` : boîtier existant réutilisé, pièces sélectionnables, phosphore hérité, adaptation étroite, HUD sans chevauchement du suivi.

Le cœur est un pourcentage de 0 à 100 non reconstitué à l’éjection. Un cœur neuf retiré des munitions devient ce pourcentage ; les cellules entamées ne retournent pas à la pile des cellules neuves. Les transactions et réparations vérifient à nouveau état, scène, proximité et ressources avant mutation.

La représentation 3D utilise le renderer existant. Les captures sont effectuées via les fonctions de rendu du jeu ; pas de remplacement de décor par une image. Les tests de combat utilisent une arène explicitement synthétique ; les montées d’escalier et traversées sont séparément effectuées dans les scènes écrites.

Les outils historiques de QA conservés ont été adaptés seulement pour leur fichier cible, leurs clés/titres attendus et le nombre d’espaces du lieu effectivement agrandi. `data/ADAPTATION_TESTS_V030.json` trace ces changements. Les fichiers de référence v0.29 demeurent immuables.
