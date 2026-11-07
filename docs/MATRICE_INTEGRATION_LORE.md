# Matrice d’intégration du lore — audit continu du 7 novembre 2026

## Référence

- dépôt : `darknigthmare/fallout-Marseille` ;
- base de cette tranche : `main` au commit `180526e2b40abe9d6fcd91423c5d309ec781d41b` ;
- version déclarée : v0.50 ;
- chaîne de build : `tools/build_single.py` ;
- continuité : `src/v050/10_lore_continuity.js` ;
- services : `src/v050/10a_lore_services.js` ;
- A‑03, M.A.D.A.M.E. et sept réseaux : `src/v050/10b_a03_madame.js` ;
- sorties générées synchronisées : commit `abe3d3f8b3793d42e35e1db6be51a30e9b42b900` ;
- contrôle final du bundle, du cache, du streaming et des coutures : commit `1f26ec4c40be72d4f047905e433becb1a4b2b53b`.

Cette matrice distingue :

1. le canon documentaire ;
2. le code source ;
3. l’état réellement sauvegardé ;
4. les tests de modèle ;
5. le bundle généré ;
6. la mise en scène ou conséquence visuelle.

## Synthèse

Le dépôt possédait déjà un véritable prologue A‑03 : borne de rationnement, décès administratif, Odette, journal falsifié, sortie vers Aubagne, relais AUB‑04 et quatre méthodes de reconnaissance provisoire. Le manque n’était donc pas l’existence du prologue, mais son absence de mémoire politique durable.

La nouvelle tranche ajoute :

- une requête exclusive adressée à M.A.D.A.M.E. ;
- quatre formes de témoignage d’Odette ;
- une chaîne de dix preuves dérivée de la campagne ;
- un registre versionné `v059Madame` ;
- le calcul des sept réseaux ;
- huit projections politiques ;
- une entrée Pip‑Boy, une entrée de journal et une fréquence radio ;
- une migration rétroactive des anciennes parties.

Les quatre sorties distribuées sont reconstruites et synchronisées : `src/game.js`, `JOUER_FALLOUT_MISTRAL_v0.50.html`, `index.html` et `sw.js`.

## Matrice générale

| Élément | Bible | Source | Sauvegarde | Tests | Bundle | Mise en scène | Statut |
|---|---:|---:|---:|---:|---:|---:|---|
| Convention des Cendres | oui | oui | oui | oui | oui | textuelle et lieux existants | jouable |
| CONCORDE / formulaire impossible | oui | oui | oui | oui | oui | textuelle et relais | jouable |
| Vigies des Crêtes | oui | oui | oui | oui | oui | repères existants | jouable |
| Insulaires du Lazaret | oui | oui | oui | oui | oui | relais existants | jouable |
| Syndicat Perpétuel | oui | oui | oui | oui | oui | chantiers existants | jouable |
| Sans-Dossier | oui | oui | oui | oui | oui | relais et textes | jouable |
| Communes du Mistral | oui | oui | oui | oui | oui | relais et reçus | jouable |
| Gilets de Cendre | oui | oui | oui | oui | oui | relais et reçus | jouable |
| COCHONNET / pétanque | oui | oui | oui | partiel | oui | mini-jeu existant | jouable, à approfondir |
| La Sociale | oui | oui | oui | oui | oui | relais du Vieux-Port | jouable |
| Aiguilleurs du Réseau | oui | oui | oui | oui | oui | relais de Saint-Charles | jouable |
| Commissariat des Atomes | oui | oui | oui | oui | oui | liaison Huveaune | jouable |
| Amirauté du Levant | oui | oui | oui | oui | oui | relais de La Ciotat | jouable |
| Abri A‑03 — Les Fontaines | oui | oui | oui | oui | oui | scène historique enrichie | jouable |
| Odette Ferraud | oui | oui | oui | oui | oui | dialogue à quatre orientations | jouable |
| M.A.D.A.M.E. | oui | oui | oui | oui | oui | borne, Pip‑Boy et radio | systémique |
| Chaîne de preuves 04‑771‑C | oui | oui | oui | oui | oui | journal/Pip‑Boy | systémique |
| Sept réseaux | oui | oui, tous calculés | oui | oui | oui | tableau textuel | systémique |
| Projections politiques | oui | oui, huit orientations | oui | oui | oui | projection textuelle | calculées, pas encore finales |
| Arsenal de La Ciotat | oui | présence et décisions | partiel | partiel | oui | lieux existants | à consolider comme faction |
| Francs du Large | oui | réputation et décisions | partiel | partiel | oui | mer et île | à consolider |
| Commune de la Rade | oui | décisions de chapitre | oui | partiel | oui | Marseille | jouable comme orientation |
| Cohorte Viénot | oui | non | non | non | non | non | canon documentaire |
| Cour du Lys d’If | oui | non comme campagne | non | non | non | non | canon documentaire |
| Poste Restante | oui | non comme système complet | non | non | non | non | chantier prioritaire |
| Mutuelle Phocéenne | oui | non | non | non | non | non | accroche de quêtes |
| Copropriété Radieuse | oui | bâtiments seulement | non | non | partiel | partiel | arc local à produire |
| Plan-de-Campagne / Enseignes | oui | géographie générale | non | non | partiel | partiel | arc local à produire |
| Bestiaire régional | oui | plusieurs familles | oui | oui selon espèce | oui | plusieurs rigs | partiellement incarné |
| Armes locales | oui | inventaire partiel | oui | variable | oui | oui selon arme | catalogue à normaliser |
| Radio Mistral / Canal 13 | oui | oui | oui | oui | oui | textuelle | jouable, audio à enrichir |

## A‑03 : ce qui était déjà réel

Le cœur historique contenait déjà :

- la pièce d’ouverture d’A‑03 ;
- la borne refusant ration et soins ;
- l’avis de décès automatique ;
- Odette et sa cache ;
- le journal des listes falsifiées ;
- la sortie vers Aubagne ;
- le relais AUB‑04 ;
- les solutions réparation, négociation, falsification ou force ;
- le retour à Mireille et le premier conseil régional.

La nouvelle tranche ne duplique aucun de ces éléments. Elle les enveloppe afin de conserver leurs conséquences.

## Registre `v059Madame`

### Identité

Le registre conserve :

- statut et étape ;
- requête à la borne ;
- choix d’Odette ;
- méthode du relais ;
- conclusion du chapitre I ;
- niveau de contradiction ;
- pression de M.A.D.A.M.E. ;
- dix familles de preuves.

### Réseaux

Chaque réseau dispose de quatre valeurs bornées entre 0 et 100 :

- accès ;
- légitimité ;
- coercition ;
- résilience.

Le contrôleur et les raisons du calcul sont également conservés.

### Projections

Les scores comparent :

- Charte des Vivants ;
- République des Services ;
- Continuité administrative ;
- Fédération des Communes ;
- Gouvernement des travailleurs ;
- Autorité du Levant ;
- Technocratie atomique et contractuelle ;
- Fragmentation régionale.

La projection indique un gagnant, une alternative, une marge et un niveau de confiance. Elle ne déclenche pas encore une fin.

## Compatibilité des sauvegardes

La migration ne suppose pas qu’une ancienne partie possède `v059Madame`. Elle lit les drapeaux et décisions historiques, notamment :

- refus de ration ;
- journal A‑03 ;
- activation du relais ;
- conclusion du chapitre I ;
- chartes des routes, de l’eau, du littoral, de Marseille et d’Aubagne ;
- dossiers de services `v054Services` ;
- archives et témoignages ultérieurs.

Le registre est ainsi reconstruit sans modifier les décisions d’origine.

## Tests de cette tranche

`tests/expansion/lore_a03_madame.cjs` vérifie dix points :

1. sept réseaux et huit projections ;
2. migration sans mutation de l’entrée ;
3. exclusivité de la requête M.A.D.A.M.E. ;
4. exclusivité du choix d’Odette ;
5. différences entre les quatre conclusions du chapitre I ;
6. influence des dossiers de services ;
7. projection République des Services pour une campagne cohérente ;
8. déterminisme et bornage des valeurs ;
9. refus des actions invalides ;
10. câblage statique de la sauvegarde, du Pip‑Boy, de la radio et des jalons.

## Validation de livraison

- **module et tests** — effectués ;
- **documentation** — effectuée ;
- **reconstruction des quatre sorties** — effectuée ;
- **présence du module et de l’entrée Pip‑Boy dans le bundle** — vérifiée ;
- **cache hors ligne et déterminisme du build** — validés ;
- **streaming, annulations, coutures et identité géométrique** — validés sur la livraison reconstruite ;
- **smoke test humain prolongé** — non réalisé dans cet audit.

Le workflow du lore exécute ensemble les anciens tests de continuité, les dossiers de services et le registre A‑03. Le workflow de streaming contrôle ensuite le bundle déjà livré au lieu d’un résultat temporaire non commité.

## Backlog priorisé après cette tranche

### P0 — conclusion politique

- conseil régional final fondé sur `v059Madame` ;
- fins et diapositives propres à chaque réseau ;
- recours jouables lorsque deux réseaux se contredisent ;
- présence scénique de Madame la Préfète hors des terminaux ;
- conséquences visuelles persistantes des chartes.

### P1 — France institutionnelle jouable

- Poste Restante et lettres persistantes ;
- Pharmacie de garde dynamique ;
- Cité Radieuse et votes de copropriété ;
- Cour du Lys d’If ;
- Mutuelle et sinistres ;
- train et gares avec changements physiques réellement incarnés.

### P2 — densité locale

- Plan-de-Campagne et guerre des Enseignes ;
- Virages du Vélodrome ;
- fête de la musique ;
- Tour des Ruines ;
- pétanque approfondie ;
- rencontres régionales supplémentaires.
