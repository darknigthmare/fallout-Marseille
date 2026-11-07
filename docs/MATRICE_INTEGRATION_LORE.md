# Matrice d’intégration du lore — audit continu du 7 novembre 2026

## Référence

- dépôt : `darknigthmare/fallout-Marseille` ;
- base de cette tranche : `main` au commit `8944f963de8de1cfd69cf34d959636ad3c853520` ;
- version déclarée : v0.50 ;
- chaîne de build : `tools/build_single.py` ;
- continuité : `src/v050/10_lore_continuity.js` ;
- services : `src/v050/10a_lore_services.js` ;
- A‑03, M.A.D.A.M.E. et sept réseaux : `src/v050/10b_a03_madame.js` ;
- conseil régional et épilogues : `src/v050/10c_conseil_regional.js` ;
- intégration du modèle et des tests : commit `a203a5f466d895fd81396b5c9ba012885600ab37` ;
- sorties jouables reconstruites : commit `b30ae362339bfdd7180f19e7b1f09b9c6fbfc7b0` ;
- régression finale du bundle livré : commit `8742e30ca28f53c879b841cb9d8cc7752b1f16bb`.

Cette matrice distingue :

1. le canon documentaire ;
2. le code source ;
3. l’état réellement sauvegardé ;
4. les tests de modèle ;
5. le bundle généré ;
6. la mise en scène ou conséquence visuelle.

## Synthèse

Le prologue A‑03, ses preuves et les six conclusions locales sont désormais reliés à une conclusion régionale. Après Aubagne, Mireille peut convoquer treize délégations. Quatre motions amendables fixent les garanties communes ; huit projets de charte sont comparés à la campagne et à la projection `v059Madame`. Une majorité de sept voix ratifie une conclusion exclusive et produit neuf diapositives, dont un épilogue pour chaque réseau.

Un vote rejeté est conservé mais ne bloque pas la partie : les motions restent modifiables et un nouveau projet peut être présenté. Les effets annoncés sont institutionnels et chiffrés ; le texte ne prétend pas créer physiquement une flotte, un train, une pompe, un hôpital ou un réacteur.

Les quatre sorties distribuées sont reconstruites et synchronisées : `src/game.js`, `JOUER_FALLOUT_MISTRAL_v0.50.html`, `index.html` et `sw.js`.

## Matrice générale

| Élément | Bible | Source | Sauvegarde | Tests | Bundle | Mise en scène | Statut |
|---|---:|---:|---:|---:|---:|---:|---|
| Convention des Cendres | oui | oui | oui | oui | oui | textuelle et lieux existants | jouable |
| CONCORDE / formulaire impossible | oui | oui | oui | oui | oui | textuelle et relais | jouable |
| Vigies des Crêtes | oui | oui | oui | oui | oui | repères existants | jouable |
| Insulaires du Lazaret | oui | oui | oui | oui | oui | relais existants | jouable |
| Syndicat Perpétuel | oui | oui | oui | oui | oui | chantiers existants | jouable |
| Sans‑Dossier | oui | oui | oui | oui | oui | relais et conseil | jouable |
| Communes du Mistral | oui | oui | oui | oui | oui | relais, reçus et conseil | jouable |
| Gilets de Cendre | oui | oui | oui | oui | oui | relais, reçus et conseil | jouable |
| COCHONNET / pétanque | oui | oui | oui | partiel | oui | mini-jeu existant | jouable, à approfondir |
| La Sociale | oui | oui | oui | oui | oui | relais et délégation | jouable |
| Aiguilleurs du Réseau | oui | oui | oui | oui | oui | relais et délégation | jouable |
| Commissariat des Atomes | oui | oui | oui | oui | oui | liaison et délégation | jouable |
| Amirauté du Levant | oui | oui | oui | oui | oui | relais et délégation | jouable |
| Abri A‑03 — Les Fontaines | oui | oui | oui | oui | oui | scène historique enrichie | jouable |
| Odette Ferraud | oui | oui | oui | oui | oui | dialogue et délégation | jouable |
| M.A.D.A.M.E. | oui | oui | oui | oui | oui | borne, Pip‑Boy, radio | systémique |
| Chaîne de preuves 04‑771‑C | oui | oui | oui | oui | oui | journal/Pip‑Boy | systémique |
| Sept réseaux | oui | oui | oui | oui | oui | tableau et épilogues | systémique |
| Projections politiques | oui | oui | oui | oui | oui | critères du conseil | systémique |
| Quatre motions constitutionnelles | oui | oui | oui | oui | oui | panneau du conseil | jouable |
| Treize délégations | oui | oui | oui | oui | oui | votes nominatifs | jouable |
| Conseil régional final | oui | oui | oui `v060Council` | oui | oui | Mireille, Pip‑Boy, radio | jouable |
| Huit projets de charte | oui | oui | oui | oui | oui | ratification déterministe | jouable |
| Épilogues des sept réseaux | oui | oui | oui | oui | oui | neuf diapositives | jouable |
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

## Conseil régional `v060Council`

### Déverrouillage

Le conseil devient disponible après les six chapitres. Les anciennes sauvegardes déjà arrivées après Aubagne sont migrées automatiquement au statut `available`.

### Motions

Le joueur adopte une clause pour chacun des quatre sujets :

- preuve d’existence ;
- minimum vital ;
- contrôle et recours ;
- force chargée de protéger les réseaux.

Les clauses restent amendables jusqu’à la ratification.

### Délégations

Treize délégations votent selon :

- leurs affinités politiques ;
- les clauses adoptées ;
- leurs préférences et refus ;
- le réseau qu’elles représentent ;
- les décisions de campagne inscrites dans `v059Madame`.

Le calcul est déterministe et la majorité requise est de sept voix.

### Ratification et rejet

Un projet inéligible ne peut pas être présenté. Un vote rejeté est inscrit dans `failedVotes`, puis les clauses peuvent être amendées. Une ratification réussie fixe définitivement :

- la charte ;
- le résultat nominatif ;
- la légitimité ;
- la projection au jour du conseil ;
- les neuf diapositives finales.

### Épilogues

Chaque réseau reçoit une règle constitutionnelle et une projection avant/après pour :

- accès ;
- légitimité ;
- coercition ;
- résilience.

Les valeurs sont bornées entre 0 et 100 et restent des projections politiques honnêtes.

## Tests

`tests/expansion/lore_conseil_regional.cjs` vérifie quatorze points :

1. quatre motions ;
2. huit orientations ;
3. treize délégations ;
4. sept réseaux ;
5. déverrouillage après Aubagne ;
6. migration sans mutation ;
7. convocation et statuts ;
8. motions amendables ;
9. éligibilité des orientations ;
10. vote déterministe à treize voix ;
11. ratification et neuf diapositives ;
12. rejet sans blocage ;
13. exclusivité après ratification ;
14. câblage de Mireille, du Pip‑Boy, de la radio, du journal et de l’écran final.

## Validation de livraison

- **module et tests du conseil** — effectués ;
- **documentation** — effectuée ;
- **reconstruction des quatre sorties** — effectuée ;
- **présence du conseil et des États généraux dans le bundle** — vérifiée ;
- **cache hors ligne et déterminisme du build** — validés ;
- **streaming, annulations, coutures et identité géométrique** — validés sur le bundle reconstruit ;
- **smoke test humain prolongé** — non réalisé dans cet audit.

## Backlog priorisé après la conclusion régionale

### P0 — monde post‑ratification

- conséquences visuelles persistantes des chartes dans les lieux ;
- crises post‑campagne lorsque deux réseaux interprètent différemment la charte ;
- présence scénique de Madame la Préfète hors des terminaux ;
- épilogues propres aux compagnons ;
- mise en scène audio et cinématique plus développée du vote.

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
