# Matrice d’intégration du lore — audit du 7 novembre 2026

## Référence auditée

- dépôt : `darknigthmare/fallout-Marseille` ;
- branche auditée : `main` ;
- commit de départ : `1d1833a4cb320a2075cba5b57c4504e99b206fe3` ;
- version déclarée : v0.50 ;
- chaîne de build : `tools/build_single.py` ;
- module de continuité existant : `src/v050/10_lore_continuity.js` ;
- module ajouté par cette extension : `src/v050/10a_lore_services.js` ;
- sorties de jeu régénérées sur la branche par le commit `6f73a08d7bd770d3347df5623b550b7b331d2903`.

Cette matrice distingue volontairement quatre choses différentes :

1. un concept écrit dans un document ;
2. un code présent dans les sources ;
3. un contenu inclus dans le HTML généré ;
4. un comportement réellement validé par des tests ou une exécution navigateur.

## Synthèse

Avant cette extension, le dépôt contenait déjà une intégration de lore plus avancée que ne le laissait penser le README : neuf identités de faction, huit dossiers jouables, des coûts finis, des choix exclusifs, une sauvegarde versionnée, des réactions textuelles et des tests dédiés.

Le manque principal était l’absence d’une bible unique et l’absence en jeu des quatre grandes puissances de services développées dans la conception récente.

La branche de la PR contient maintenant le code, la documentation, les tests et les quatre sorties générées attendues : `src/game.js`, `JOUER_FALLOUT_MISTRAL_v0.50.html`, `index.html` et `sw.js`.

## Matrice générale

| Élément | Bible | Source de jeu | Sauvegarde | Tests automatisés | HTML v0.50 du commit de départ | Build généré de la PR | Statut après cette extension |
|---|---:|---:|---:|---:|---:|---:|---|
| Convention des Cendres | oui | oui | oui | oui | oui | oui | jouable |
| CONCORDE / formulaire impossible | oui | oui | oui | oui | oui | oui | jouable |
| Vigies des Crêtes | oui | oui | oui | oui | oui | oui | jouable |
| Insulaires du Lazaret | oui | oui | oui | oui | oui | oui | jouable |
| Syndicat Perpétuel | oui | oui | oui | oui | oui | oui | jouable |
| Sans-Dossier | oui | oui | oui | oui | oui | oui | jouable |
| Communes du Mistral | oui | oui | oui | oui | oui | oui | jouable |
| Gilets de Cendre | oui | oui | oui | oui | oui | oui | jouable |
| COCHONNET / pétanque | oui | oui | oui | partiel | oui | oui | jouable, à approfondir |
| La Sociale | oui | oui, nouveau | oui, nouveau | oui, nouveau | non | oui | jouable dans le build de la PR |
| Aiguilleurs du Réseau | oui | oui, nouveau | oui, nouveau | oui, nouveau | non | oui | jouable dans le build de la PR |
| Commissariat des Atomes | oui | oui, nouveau | oui, nouveau | oui, nouveau | non | oui | jouable dans le build de la PR |
| Amirauté du Levant | oui | oui, nouveau | oui, nouveau | oui, nouveau | non | oui | jouable dans le build de la PR |
| M.A.D.A.M.E. / Madame la Préfète | oui | fragments | non comme arc complet | non | partiel | partiel | canon, arc principal à produire |
| Abri A‑03 — Les Fontaines | oui | socle narratif partiel | non comme prologue complet | non | partiel | partiel | priorité narrative |
| Sept réseaux | oui | quatre dossiers reliés | oui pour les quatre | oui pour les quatre | non pour les nouveaux | oui pour quatre réseaux | système partiellement jouable |
| Arsenal de La Ciotat | oui | présence géographique/mentions | non comme faction complète | non | partiel | partiel | canon documentaire |
| Francs du Large | oui | réputation/mentions | partiel | partiel | partiel | partiel | à consolider |
| Commune de la Rade | oui | présence régionale | partiel | non | partiel | partiel | à consolider |
| Cohorte Viénot | oui | non | non | non | non | non | canon documentaire |
| Cour du Lys d’If | oui | non comme campagne | non | non | non | non | canon documentaire |
| Maquis des Treize Vents | oui | non | non | non | non | non | canon documentaire |
| Poste Restante | oui | non comme système complet | non | non | non | non | chantier prioritaire |
| Confrérie du Vœu | oui | mentions de veille/secours | non | non | partiel | partiel | canon documentaire |
| Mutuelle Phocéenne | oui | non | non | non | non | non | accroche de quêtes |
| Copropriété Radieuse | oui | ville et bâtiments seulement | non | non | partiel | partiel | arc local à produire |
| Plan-de-Campagne / Enseignes | oui | géographie générale | non | non | partiel | partiel | arc local à produire |
| Bestiaire régional | oui | plusieurs familles incarnées | oui pour les acteurs existants | oui selon espèces | oui | oui | partiellement incarné |
| Armes locales | oui | inventaire partiel | oui selon armes existantes | variable | partiel | partiel | catalogue à normaliser |
| Pigeons et rats mutants | oui | plusieurs variantes présentes | oui | oui selon variante | oui | oui | continuer diversité/IA |
| Radio Mistral / Canal 13 | oui | bulletins textuels | oui | oui | oui | oui | jouable, à enrichir audio |
| Fins politiques | oui | non comme finale systémique | non | non | non | non | grand chantier de campagne |

## Ce qui est réellement fort

### Dossiers v0.50

Le module de continuité existant possède les caractéristiques attendues d’un système RPG robuste :

- contact physique et site découvert ;
- coûts vérifiés ;
- décision exclusive ;
- récompense unique ;
- journal sauvegardé ;
- migration des anciennes sauvegardes ;
- annulation atomique si la sauvegarde échoue ;
- formulations qui ne prétendent pas créer un élément visuel absent.

### Carte et relais

Les quatre nouveaux dossiers utilisent des lieux sûrs déjà présents dans le catalogue :

- Vieux-Port ;
- Saint-Charles ;
- vallée de l’Huveaune ;
- La Ciotat.

Ils n’inventent donc pas un nouveau territoire parallèle.

### Livraison générée

Le workflow spécialisé a reconstruit le jeu, vérifié la syntaxe du bundle et contrôlé que `tools/build_single.py --check` ne trouvait plus de différence après génération. Les quatre fichiers de livraison ont ensuite été commités sur la branche. Cette validation ne remplace pas un parcours humain complet dans le navigateur.

## Ce qui restait faible

### 1. Bible dispersée

Le canon était réparti entre `LORE_RECONSTRUIT_V046.md`, `LORE_CONTINUITE.md`, le bestiaire, les textes de code et les conversations de conception. Il manquait une hiérarchie claire.

**Correction :** ajout de `LORE.md` et de la bible générale.

### 2. Factions de services absentes

La Sociale, les Aiguilleurs, le Commissariat et l’Amirauté existaient dans la conception, mais pas dans la boucle jouable.

**Correction :** quatre dossiers à deux choix, état `v054Services`, migration et panneau Pip-Boy.

### 3. Arc principal insuffisamment raccordé

M.A.D.A.M.E., A‑03 et la suppression administrative du protagoniste sont le meilleur axe du projet, mais ne forment pas encore un prologue/arc principal entièrement jouable.

**Priorité suivante :** construire un prologue en plusieurs scènes, avec preuve d’existence, première sortie, choix d’Odette et conséquences dans les réseaux.

### 4. Concepts français encore décoratifs

La copropriété, la poste, les pharmacies de garde, la Mutuelle, les notaires et la Cour du Lys sont canoniques mais n’ont pas encore leur boucle de jeu.

**Priorité suivante :** transformer chaque référence en système : courrier, assurance, propriété, horaires, assemblées, recours.

### 5. Fins non systémiques

La Charte des Vivants, la République des Services, la Continuité, la Fédération et les autres fins existent en texte mais ne sont pas calculées à partir d’un état régional commun.

**Priorité suivante :** créer un registre des sept réseaux, avec contrôle, légitimité, accès universel et niveau de coercition.

## Tests ajoutés

`tests/expansion/lore_services.cjs` vérifie :

1. quatre dossiers et sept réseaux ;
2. l’existence et la sûreté des quatre relais ;
3. la migration défensive ;
4. l’obligation d’un contact ;
5. l’exclusivité des décisions ;
6. le refus sans ressources ;
7. l’absence de fausses promesses de simulation ;
8. les bulletins ;
9. le câblage statique du Pip-Boy et du debug.

## Condition de livraison

Le nouveau module est automatiquement pris en compte par `tools/build_single.py`, qui concatène les fichiers triés de `src/v050`.

Une intégration honnête annonce séparément :

- **source et tests ajoutés** — effectué ;
- **build GitHub validé** — effectué ;
- **quatre sorties générées commitées** — effectué ;
- **régression générale sur la tête finale de la PR** — à confirmer par le workflow ;
- **smoke test navigateur humain** — non réalisé dans cet audit.

## Backlog priorisé

### P0 — campagne et identité

- prologue complet d’A‑03 ;
- M.A.D.A.M.E. comme antagoniste systémique ;
- registre des sept réseaux ;
- première version des fins politiques calculées.

### P1 — France jouable

- Poste Restante et lettres persistantes ;
- Pharmacie de garde dynamique ;
- Cité Radieuse et votes de copropriété ;
- Cour du Lys d’If ;
- Mutuelle et sinistres ;
- train/gares avec conséquences réellement incarnées.

### P2 — densité locale

- Plan-de-Campagne et guerre des Enseignes ;
- Vélodrome et Virages ;
- fête de la musique ;
- Tour des Ruines ;
- événements de pétanque approfondis ;
- rencontres de pigeons, rats, gabians et robots civils.
