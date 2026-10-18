# Architecture — v0.29

`src/core-v017.js` reste la base historique. `tools/build_single.py` applique les correctifs puis assemble les modules précédents et `src/v029/`, dans l'ordre. `src/game.js` et le HTML sont générés : ne pas les éditer directement.

- `00_state.js` : définitions, tables de mots déterministes par contrôleur/cycle, migrateur borné, enregistrements.
- `01_terminal.js` : dialogue natif, sessions locales à époque invalide, déduction, aides, commandes avec confirmation, raccord des hacks relay/ship.
- `02_perception.js` : perception orientée et progressive, position sonore, état d'enquête, exclusion des automates en veille de la boucle offensive, HUD.
- `03_world.js` : contrôleurs, alcôves, volets/collisions, poignées intérieures, badges, personnage et pièce de quête.
- `04_story.js` : journaux, bande, dialogue d'Adrien, deux conclusions, suivi et bilan.
- `05_interface.js` : copies Pip-Boy en lecture seule, modal et focus, démarrage séparé, ponts d'export/import, instrumentation de tests.
- `style.css` : terminal CRT original et fenêtres étroites.

Le builder remplace une condition d'acquisition initiale du noyau par `v029Observe`. Il vérifie l'unicité de cette cible avant modification. Les autres blocs d'alerte/attaque sont conservés ; cela évite une réécriture silencieuse des anciens comportements.

`v029ApplyWorld` applique l'état logique aux vrais draws/colliders et au robot identifié. Une invalidation du cache de navigation accompagne un volet ouvert. La poignée intérieure exige une position à l'intérieur des limites du local, pas simplement un clic visible à travers la porte.

Les tests de déduction utilisent des réponses connues pour vérifier la mécanique, pas une prétention d'intelligence d'un joueur. Les tests des accès physiques, tentatives au clic, tactiles, trajets, import et refus sont séparés. Les captures sont issues du HTML exact, avec caméras et quelques états préparés.
