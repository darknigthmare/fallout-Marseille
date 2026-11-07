# A‑03, M.A.D.A.M.E. et le registre des sept réseaux

## Objet

Cette extension approfondit le prologue historique **« Un vivant de trop »** sans le remplacer. L’abri A‑03, Odette Ferraud, la borne de rationnement et le relais AUB‑04 existaient déjà dans le cœur du jeu. Le nouveau module `src/v050/10b_a03_madame.js` transforme leurs décisions en un état civique durable, compatible avec les anciennes sauvegardes.

Le système ne crée pas une seconde campagne parallèle. Il observe les choix déjà accomplis dans les six chapitres, calcule l’état des sept réseaux et produit une **projection institutionnelle**. Cette projection n’est pas encore une cinématique finale : elle constitue la base vérifiable d’une future conclusion régionale.

## Le dossier 04‑771‑C

Au début d’une partie scénarisée, la borne A‑03 déclare le protagoniste décédé et suspend :

- la ration ;
- les soins ;
- le droit de passage ;
- la capacité à contester le dossier.

Le registre `v059Madame` conserve désormais :

- le statut civique actuel ;
- l’étape de la contradiction ;
- la pression exercée par M.A.D.A.M.E. ;
- les preuves obtenues ;
- la requête formulée à la borne ;
- la forme du témoignage d’Odette ;
- la méthode employée au relais AUB‑04 ;
- les décisions régionales ultérieures ;
- l’état calculé des sept réseaux ;
- les scores et la projection politique.

## Chaîne de preuves

Le registre reconnaît dix familles de preuves, selon la progression réelle de la partie :

1. **Présence corporelle constatée à A‑03** ;
2. **Avis de décès automatique 04‑771‑C** ;
3. **Trace du relais d’Aubagne à 05 h 57** ;
4. **Journal des listes falsifiées d’A‑03** ;
5. **Témoignage d’Odette Ferraud** ;
6. **Présence provisoire reconnue par AUB‑04** ;
7. **Chaîne régionale des signatures CONCORDE** ;
8. **Témoignages et registres communaux** ;
9. **Registres reliant identité et droit à l’eau** ;
10. **Images postérieures au décès administratif**.

Ces preuves ne sont pas équivalentes. Une présence physique contredit la mort, mais ne corrige pas seule un registre régional. Un sceau administratif peut rétablir un dossier tout en laissant intact le pouvoir qui l’a supprimé. Une pluralité de témoins augmente la légitimité, mais demande des institutions capables de conserver leurs désaccords.

## Requêtes adressées à M.A.D.A.M.E.

Après le premier refus, une nouvelle interaction avec la borne permet de fixer une requête exclusive.

### Présence physique provisoire

M.A.D.A.M.E. constate le corps vivant, mais refuse de remplacer seule la décision du relais régional.

Effet politique principal : reconnaissance rapide, dépendance encore forte à l’administration centrale.

### Traçabilité contradictoire

Le protagoniste exige que la source du décès, l’heure, l’auteur et les modifications ultérieures restent visibles.

Effet politique principal : légitimité par l’audit, renforcement de la mémoire administrative sans lui abandonner la décision finale.

### Pluralité des preuves

Le protagoniste demande qu’aucune base unique ne puisse prononcer une mort civile.

Effet politique principal : fondement de la Charte des Vivants et des registres distribués.

Une requête validée ne peut pas être remplacée silencieusement. Elle reste dans la sauvegarde et participe aux calculs ultérieurs.

## Témoignage d’Odette

Odette peut désormais choisir une forme de preuve au lieu de répéter un dialogue identique.

### Attestation signée

Elle assume publiquement les falsifications et identifie les familles protégées.

- légitimité élevée ;
- exposition personnelle importante ;
- conservation d’une preuve attribuée.

### Protection des familles

Elle confirme les manipulations sans publier les noms des habitants sauvés.

- accès et protection renforcés ;
- preuve moins facile à vérifier publiquement ;
- cohérence avec les dossiers anonymisés de la campagne.

### Registre contradictoire

Elle exige que la version CONCORDE et la version A‑03 restent visibles ensemble.

- forte résistance à l’effacement ;
- base de recours durable ;
- augmentation de la complexité administrative assumée.

### Silence protecteur

Elle refuse une preuve nominative afin de protéger les survivants.

- sécurité immédiate ;
- légitimité publique plus faible ;
- risque de laisser M.A.D.A.M.E. conserver la version dominante.

Le choix est exclusif et sauvegardé. Le départ vers Aubagne reste possible quelle que soit la décision.

## Relais AUB‑04

Les quatre solutions historiques restent intactes :

- réparation de la ligne de validation ;
- procédure 17‑B de présence physique ;
- falsification d’un sceau interne ;
- remise sous tension forcée.

Le registre civique leur donne maintenant des conséquences différentes en matière de légitimité, coercition et centralisation. La mission principale continue de fonctionner comme auparavant ; le nouveau système en conserve simplement la trace politique.

## Les sept réseaux calculés

Chaque réseau reçoit quatre mesures bornées de 0 à 100 :

| Mesure | Signification |
|---|---|
| **Accès** | proportion de la population pouvant réellement utiliser le service |
| **Légitimité** | capacité à justifier, documenter et contester ses décisions |
| **Coercition** | niveau de contrainte, d’exclusion ou de monopole |
| **Résilience** | capacité à continuer malgré panne, conflit ou changement d’autorité |

Les réseaux suivis sont :

1. identité ;
2. eau ;
3. santé ;
4. transport ;
5. énergie ;
6. communication ;
7. approvisionnement.

Le contrôleur affiché n’est pas choisi arbitrairement. Il dérive des décisions sauvegardées : CONCORDE, communes, travailleurs, services publics, concessions, Amirauté, Commissariat ou structures distribuées.

## Sources de calcul

Le registre observe notamment :

- le choix du relais AUB‑04 ;
- la conclusion du chapitre I ;
- la charte des routes ;
- la charte régionale de l’eau ;
- la charte du littoral ;
- la charte de Marseille ;
- la charte d’Aubagne ;
- les quatre dossiers de services de `v054Services` ;
- les preuves collectées au cours de la campagne ;
- plusieurs décisions locales qui augmentent ou réduisent accès, audit et coercition.

Les anciennes sauvegardes sont migrées par dérivation : le module lit les quêtes, drapeaux et dossiers existants puis reconstruit le registre sans annuler les choix du joueur.

## Projections politiques

Huit orientations sont comparées :

- Charte des Vivants ;
- République des Services ;
- Continuité administrative ;
- Fédération des Communes ;
- Gouvernement des travailleurs ;
- Autorité du Levant ;
- Technocratie atomique et contractuelle ;
- Fragmentation régionale.

Le panneau indique :

- l’orientation dominante ;
- l’alternative la plus proche ;
- la marge entre les deux ;
- un indice de confiance ;
- les raisons principales ;
- le détail des scores.

La projection est descriptive. Elle ne remplace pas encore un conseil final jouable et ne déclenche pas une fin à elle seule.

## Intégration dans le jeu

Le registre est accessible dans le Pip‑Boy :

**DATA → M.A.D.A.M.E. ET SEPT RÉSEAUX**

Il ajoute également :

- une entrée de journal pour le dossier 04‑771‑C ;
- une fréquence radio textuelle de cohérence civique ;
- des réactions enrichies de la borne et d’Odette ;
- des outils de debug sous `__MISTRAL_DEBUG` ;
- une synchronisation avant chaque sauvegarde ;
- une migration défensive pour les parties existantes.

## Garanties techniques

- schéma versionné ;
- données sérialisables uniquement ;
- choix exclusifs validés ;
- calculs déterministes ;
- valeurs bornées ;
- absence de mutation de l’état d’entrée dans le modèle pur ;
- restauration de l’état si une écriture intégrée échoue ;
- aucune fausse promesse de train, flotte, réacteur ou bâtiment créé.

## Limites restantes

Cette tranche rend M.A.D.A.M.E. systémique dans le prologue, le Pip‑Boy, la radio et le calcul politique. Restent à produire :

1. un conseil final régional utilisant officiellement cette projection ;
2. les épilogues et diapositives propres aux sept réseaux ;
3. les conséquences visuelles persistantes dans les lieux ;
4. une présence scénique plus forte de Madame la Préfète hors des terminaux ;
5. des recours jouables lorsque deux réseaux appliquent des décisions incompatibles.
