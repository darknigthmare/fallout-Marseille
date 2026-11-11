# De main en main — les propriétaires de la consigne

## Continuité

Cette extension de **Les objets trouvés** part de la PR 18, révision `9849cb57512b93379e27070f8145c23180005cd4`, après validation des deux missions d’oiseaux. Éloi, Mina et Rachid existaient déjà dans les descriptions des trois objets. Ils deviennent ici trois interlocuteurs présents devant le comptoir de Nora Ferrand ; leurs affaires, leurs noms et leurs propriétaires ne changent pas.

La consigne reste une cour fictionnelle liée au relais du Vieux-Port. Aucun relevé IGN n’est modifié. Il ne s’agit pas de trois nouveaux compagnons recrutables, d’une simulation de propriété régionale ou d’un nouvel arc obligatoire.

## Trois voix plutôt que trois tickets

**Éloi** a connu une cabine dans laquelle il pouvait enfin fermer la porte. Sa clé n’ouvre plus un bateau disponible dans le jeu. La dent tordue permet de reconnaître un souvenir qui n’est pas interchangeable avec un objet de même valeur. Son premier bateau s’appelait le *Demain* : « Pour une fois, ce n’était pas une promesse électorale. » Le bateau appartient à son récit ; aucune coque ou traversée supplémentaire n’est ajoutée.

**Mina** confie sa bague à Nora pendant son quart, puis la remet lorsque le travail est fini. Sa gravure est censée représenter une vague ; elle y voit un haricot. Elle demande seulement que le joueur garde cette remarque pour lui. La bague n’est ni une clef de quête politique, ni un bijou magique. La scène ne lui invente pas un conjoint incarné ou une cérémonie hors écran.

**Rachid** préfère son sifflet à une radio à pile : il annonce le dernier passage à des gens qui reconnaissent son signal. « Deux appels courts, un long. Le dernier passage, pas une alarme. » Ce signal est raconté ; ce lot n’ajoute ni effet sonore de sifflet, ni départ automatisé de ferry.

Nora continue de recevoir ce qu’on lui confie. Son rôle de dépositaire demeure utile : le joueur peut terminer la récupération sans écouter chaque souvenir.

## Deux façons de rendre un objet

Après avoir récupéré un objet dans un panier, le joueur peut le **déposer chez Nora**, comme auparavant, ou le **remettre directement au propriétaire correspondant**. Une proximité réelle et une ligne de vue sont nécessaires ; le Pip-Boy n’effectue pas de remise à distance.

Un objet déjà déposé chez Nora peut être passé à son propriétaire au comptoir. Le registre distingue donc `direct` (depuis le sac de mission) et `consigne` (depuis le dépôt). Le propriétaire reste devant ce même comptoir : aucun transfert à travers la région n’est sous-entendu.

La silhouette de l’objet n’est plus montrée sur le plateau une fois la remise enregistrée. Une feuille de reçu la remplace. Ce changement de mobilier ne prétend pas être une animation détaillée de prise en main ou une signature manuscrite simulée.

La remise a un texte propre à chaque personne. Les questions sur leurs souvenirs restent facultatives, ne coûtent rien et ne modifient aucune ancienne politique régionale.

## Terminer n’est pas recommencer

La quête originale reste terminable avec trois objets rendus, même s’ils sont encore chez Nora. Sa prime reste **45 capsules une seule fois** ; les morts éventuelles des gabians restent dans son constat.

**De main en main** apparaît comme un épilogue facultatif dans le journal. Il suit trois remises personnelles et peut être terminé avant ou après le bilan avec Nora. Il ne remet pas la quête originale en cours et ne paie aucune prime supplémentaire.

La remise ne crée pas d’objet vendable dans l’inventaire courant. Les règles d’appât, de blessures, de projectiles, de palans et de récupération restent celles de la consigne. Les pigeons postaux restent une mission indépendante.

## Sauvegardes

Le registre `v073Gabians` passe au **schéma 2** avec trois champs `handoffs`. Une sauvegarde du schéma 1 conserve tous ses anciens états ; les remises personnelles sont laissées à `null`, car une restitution à Nora ne prouvait pas une remise au propriétaire.

Les anciennes récompenses, les paniers, les blessures, les projectiles et les objets déjà récupérés ne sont ni effacés ni renouvelés. Après une migration, un ancien dossier terminé peut donc recevoir son épilogue sans nouveau paiement.

Une sauvegarde refusée annule la remise et son reçu. Les conversations périmées, les mauvais propriétaires et les répétitions ne peuvent pas transférer l’objet. Le schéma 2 exige des reçus cohérents : un objet encore au nid ou dans le sac ne peut pas être déclaré remis.

## Vérification et limites

Le lot ajoute des tests de logique, un parcours navigateur des propriétaires et six scénarios de fermeture complète de Chromium pour les deux missions d’oiseaux. Le rapport `verification/retrouvailles/QA.json` distingue ce qui a réellement été exécuté en local et dans la compilation canonique.

Les scénarios à froid couvrent un pigeon en vol avec l’autre pli porté à pied, les conclusions publique et privée, un projectile de gabian avec blessure et chute, un panier suspendu sous lequel le joueur se tient et des restitutions personnelles partielles. Leur préparation est instrumentée ; la reprise utilise ensuite le HTML de production inchangé, le véritable stockage sur disque et le bouton **Continuer**, sans réinjection de sauvegarde.

Restent ouverts : remise d’objet animée, doublage, gestes de métiers, départs des propriétaires, transport maritime, réseau postal régional, variantes hostiles des pigeons, Général Biset et parcours géographiques réels. Ce chapitre décrit une création de fan originale, pas le canon officiel de Fallout.
