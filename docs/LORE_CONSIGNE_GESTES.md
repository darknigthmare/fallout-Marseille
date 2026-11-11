# Les gestes retrouvés — les affaires restent avec leurs propriétaires

## Place dans le récit

Suite visuelle de **De main en main**, à la consigne de Nora Ferrand. Les objets n'ajoutent ni une nouvelle quête obligatoire ni une seconde prime. Leur intérêt est de montrer ce que signifie retrouver quelque chose qui ne vaut presque rien pour un marchand.

Éloi lève la clef tordue, en retrouve la forme et la garde à sa ceinture. Le Demain reste un bateau de son passé : aucune serrure, cabine ou embarcation n'est créée par cette restitution.

Mina regarde la bague et sa gravure, puis la remet à sa main. Elle reste devant le comptoir après son quart. Le geste ne crée ni conjoint supplémentaire, ni maison visitable, ni bonus d'équipement pour le joueur.

Rachid examine son sifflet et le conserve sur un cordon. Il ne déclenche ni alarme, ni départ de ferry : les deux appels courts et l'appel long appartiennent encore au dialogue, pas à un effet sonore implémenté.

## Ce qui est effectivement joué

Une remise validée par les boutons existants déclenche un geste continu de 2,9 secondes : réception déjà effectuée, reconnaissance, conservation de l'objet, retour du bras au repos. La clef, la bague et le sifflet gardent trois silhouettes différentes. Le corps, le visage, le costume et le bras gauche conservent le modèle natif du propriétaire ; seul le bras droit reçoit la pose articulée.

La séquence commence **après la sauvegarde réussie**. Elle ne retarde pas le reçu et ne peut jamais conditionner la progression à la fin d'une animation. Les objets se voient ensuite sur les personnages, y compris après chargement d'une ancienne partie ayant déjà enregistré une remise personnelle.

Il s'agit du geste du destinataire **après réception**, pas d'une cinématique complète reliant physiquement les deux paumes. Les mains du joueur et le transfert depuis la position du plateau ne sont pas animés. Les personnages ne quittent pas leur point d'attente.

## Persistance et accessibilité

Le registre `v073Gabians` reste au schéma 2. Aucun nouveau champ persistant, aucun objet vendable, aucune capsule et aucun changement de coût n'est ajouté. Les 45 capsules historiques restent uniques. Les remises directe et depuis Nora conservent leur provenance.

Le geste est transitoire ; son résultat visuel est reconstruit depuis la remise déjà sauvegardée. Recharger pendant le geste montre l'objet conservé sans rejouer la restitution. Un refus de sauvegarde ou une conversation périmée ne déclenche pas le geste.

Le réglage joueur existant **Réduire les mouvements** affiche immédiatement l'objet conservé. L'animation peut rester visible pendant le dialogue, mais se suspend dans le Pip-Boy, les notes, les menus, un chargement et les situations invalides. Un retour d'onglet ne fait pas bondir le bras d'une pose à une autre. Aucun bouton de développement n'est ajouté aux menus joueur.

## Sortie de la consigne

Une fois la mission et les trois remises facultatives terminées, le repère vise la sortie réelle de la cour. Le HUD n'envoie plus le joueur vers Nora pour toucher une prime déjà reçue. Si la mission est close mais que des remises restent possibles, le HUD les présente explicitement comme facultatives et sans nouvelle récompense.

## Contrat de développement et preuves

Base source : PR 18, `348a3cb2385b91771112f8c772def4cb82bd8c36`.

Fichiers de code : `src/v050/10x_consigne_gestes.js`, `tests/expansion/lore_consigne_gestes.cjs`, `tests/expansion/gestes_browser_smoke.py`. Le workflow permanent ajoute le seizième parcours. Les modules de règles gabians/pigeons, les coordonnées IGN et les fichiers de COCHONNET ne sont pas modifiés.

Principes appliqués : contrat `AGENTS.md`, séparation état autoritaire/présentation et sauvegardes versionnées du skill `save-systems` à la révision gamedev-skills `19d93f97c9c1ea0f8b306e77aa81e0d3e352d3e9`. Aucun moteur n'est remplacé et aucun outil tiers n'est annoncé comme installé.

Le rapport actuel est `verification/gestes/QA.json` lorsque la compilation canonique est vérifiée ; `QA_LOCAL.json` distingue les essais locaux. Les captures proviennent du moteur. Les parcours utilisent des positions scriptées, une origine portuaire synthétique et, hors essais à froid, MemoryStorage. Ils ne certifient ni une partie humaine complète, ni un trajet IGN, ni les performances sur tout matériel.

## Reste ouvert

Transfert complet entre mains, animations des doigts, doublage, routines et départ des propriétaires, bruit du sifflet, navigation maritime et transports régionaux. Les pigeons hostiles, le Général Biset, les territoires des factions et l'inventaire complet du bestiaire restent des chantiers distincts. COCHONNET (PR 17) n'est pas inclus dans cette branche.
