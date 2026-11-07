# États généraux du Mistral — Conseil régional jouable

## Objet

Cette tranche transforme la projection politique de `v059Madame` en une véritable conclusion jouable. Les six conclusions locales de campagne restent intactes ; elles sont agrégées après le chapitre VI afin que treize délégations débattent de quatre garanties communes puis votent une charte régionale.

Le système se trouve dans :

- `src/v050/10c_conseil_regional.js` ;
- `tests/expansion/lore_conseil_regional.cjs` ;
- l’état sauvegardé `v060Council`.

Il ne prétend pas modifier physiquement toute la carte au moment du vote. Les conséquences finales sont des épilogues textuels calculés à partir des réseaux déjà enregistrés, des clauses adoptées et de la charte ratifiée.

## Déverrouillage

Le conseil devient disponible lorsque les six chapitres sont conclus :

1. identité ;
2. routes ;
3. eau ;
4. industrie et littoral ;
5. Marseille ;
6. Aubagne.

Après l’écran de fin du chapitre VI, **Continuer à explorer** ouvre la proposition de Mireille. Le conseil reste ensuite accessible auprès d’elle et dans le Pip‑Boy :

**DATA → CONSEIL RÉGIONAL**

Une ancienne sauvegarde ayant déjà terminé Aubagne obtient automatiquement le statut `available` lors de la migration.

## État `v060Council`

Le registre versionné conserve :

- le statut du conseil : `locked`, `available`, `convened`, `deliberating` ou `ratified` ;
- la date de convocation ;
- les quatre clauses adoptées ;
- la charte ratifiée ;
- le résultat du vote ;
- l’indice de légitimité ;
- les votes rejetés ;
- les neuf diapositives finales ;
- la projection M.A.D.A.M.E. au moment du conseil ;
- le journal des motions et votes.

Une ratification réussie est définitive. Un vote rejeté ne ferme pas la partie : le joueur peut amender les clauses et soumettre une autre orientation.

## Les quatre motions

### Motion I — Qui peut prouver une existence ?

- **Pluralité obligatoire des preuves** : aucune base unique ne peut prononcer une mort civile.
- **Registre régional unifié avec recours** : une autorité unique conserve les versions et statue après recours.
- **Témoignages et registres territoriaux** : communes et relais se reconnaissent mutuellement.

### Motion II — Quel minimum est inconditionnel ?

- **Eau, soins et passage d’urgence universels**.
- **Droits garantis par contribution ou service**.
- **Quotas publics décidés par territoire**.

### Motion III — Qui peut arrêter une décision ?

- **Audit public et recours contradictoire**.
- **Veto des équipes et usagers du réseau**.
- **Commandement régional en situation critique**, limité et journalisé.

### Motion IV — Quelle force protège les réseaux ?

- **Services sans armée propre**.
- **Gardes locales coordonnées**.
- **Force régionale unifiée**.

Les clauses peuvent être modifiées tant qu’aucune charte n’a été ratifiée.

## Les treize délégations

1. A‑03 et Odette Ferraud ;
2. les Sans‑Dossier ;
3. la Direction de la Continuité — CONCORDE ;
4. la Convention des Cendres ;
5. les Communes du Mistral ;
6. les Gilets de Cendre ;
7. le Syndicat Perpétuel ;
8. les Vigies des Crêtes ;
9. les Insulaires du Lazaret ;
10. La Sociale ;
11. les Aiguilleurs du Réseau ;
12. le Commissariat des Atomes ;
13. l’Amirauté du Levant.

Chaque délégation possède :

- une préférence de fond entre les huit orientations ;
- des clauses appréciées ;
- des clauses refusées ;
- un réseau prioritaire ;
- une réaction aux décisions déjà inscrites dans `v059Madame`.

Le vote est déterministe : la même sauvegarde, les mêmes clauses et la même orientation produisent le même résultat.

## Les huit projets de charte

### Charte des Vivants

Aucune base unique ne peut retirer l’existence civile ni les droits vitaux.

### République des Services

Les sept réseaux deviennent des institutions autonomes, liées par des obligations communes et dépourvues d’armée propre.

### Continuité administrative

Une autorité régionale unifie les registres, les priorités et les recours.

### Fédération des Communes

Les territoires conservent leurs réseaux et délèguent seulement les compétences réellement communes.

### Gouvernement des travailleurs

Les équipes qui entretiennent les réseaux disposent du pouvoir de décision et de veto.

### Autorité du Levant

Une autorité maritime et logistique coordonne secours, voies, énergie et approvisionnements.

### Technocratie atomique et contractuelle

Experts, seuils techniques et contrats deviennent la principale source de légitimité.

### Fragmentation régionale

Les territoires refusent une constitution unique et conservent leurs accords locaux.

Toutes les orientations ne sont pas automatiquement éligibles. L’éligibilité dépend de la projection `v059Madame`, des conclusions de campagne et des motions adoptées. La fragmentation reste une issue politique possible, pas un bouton permettant d’ignorer les décisions précédentes.

## Vote et légitimité

La majorité requise est de **sept voix sur treize**.

Le résultat conserve :

- voix pour ;
- voix contre ;
- abstentions ;
- choix de chaque délégation ;
- indice de légitimité de 0 à 100.

La légitimité tient compte notamment :

- de l’écart entre pour et contre ;
- du nombre de motions réellement résolues ;
- de la confiance de la projection M.A.D.A.M.E. ;
- des abstentions.

Un rejet est inscrit dans `failedVotes`. Il ne consomme pas la conclusion de campagne et laisse les motions amendables.

## Épilogues

Une ratification produit neuf diapositives :

1. résultat de la charte ;
2. synthèse des quatre garanties ;
3. identité ;
4. eau ;
5. santé ;
6. transport ;
7. énergie ;
8. communication ;
9. approvisionnement.

Chaque réseau indique :

- la règle constitutionnelle retenue ;
- le contrôleur au jour du vote ;
- les valeurs avant et après projection pour l’accès, la légitimité, la coercition et la résilience.

Ces nombres sont bornés entre 0 et 100. Ils décrivent une trajectoire institutionnelle ; ils ne prétendent pas qu’une pompe, un train, une flotte, un hôpital ou un réacteur a été physiquement créé par le vote.

## Intégration dans le jeu

Le conseil ajoute :

- un dialogue final de Mireille après Aubagne ;
- un panneau Pip‑Boy complet ;
- une entrée de journal ;
- une station radio textuelle des États généraux ;
- un écran final utilisant le système historique `endingScreen` ;
- des outils de debug sous `__MISTRAL_DEBUG` ;
- une synchronisation avant chaque sauvegarde.

Les écrans de fin des six chapitres restent inchangés. Le conseil intervient après eux et ne réécrit pas rétroactivement leurs choix.

## Garanties techniques

- schéma versionné et migration défensive ;
- modèle pur sans mutation de l’entrée ;
- déterminisme des votes ;
- ratification exclusive ;
- rejet non bloquant ;
- valeurs bornées ;
- restauration atomique si la sauvegarde échoue ;
- texte échappé avant insertion dans l’écran final ;
- absence de fausse promesse de transformation physique du monde.

## Limites restantes

Le conseil règle la conclusion politique et les épilogues des réseaux. Restent encore à approfondir :

1. les transformations visuelles persistantes dans les lieux après ratification ;
2. des épilogues dédiés à chaque compagnon ;
3. la présence physique de Madame la Préfète hors des écrans ;
4. des crises post‑campagne lorsque deux réseaux interprètent différemment la charte ;
5. une mise en scène audio et cinématique plus développée du vote.
