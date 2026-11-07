# Pharmacies de Garde — La croix verte ne ferme pas les yeux

## Reprise et portée

Extension du fan-lore de Fallout: Mistral à partir de `6f3e4629741baf39077f668bdbad247d82fdf5a7`, après les PR A‑03/M.A.D.A.M.E., États généraux et Poste Restante. Ces systèmes restent conservés.

Ce chapitre rend jouable une institution de la bible : la pharmacie de garde. Il ne prétend pas reproduire des officines réelles ni ouvrir la Timone. Les comptoirs et leurs croix vertes sont des ajouts fictionnels aux relais existants, indépendants des données IGN.

## Doctrine

> « La croix dit que quelqu’un répond. Elle ne dit pas que tout est en stock. »

Les Pharmacies de Garde ont refusé de confier leur totalité à SÉCURA. La Sociale centralise les urgences ; les officines conservent les lots, les signatures de remise et la responsabilité de ce qu’elles distribuent. Cette indépendance protège contre une décision médicale unique, mais multiplie les calendriers incompatibles.

Chaque comptoir conserve une copie de son planning. Un échange de garde doit être transmis au destinataire, à l’expéditeur et au relais public. Les vieilles machines n’acceptent parfois qu’une signature, lorsque deux équipes doivent justement se remplacer. C’est ainsi qu’une garde peut être correcte dans chaque registre et fausse pour tous les voyageurs.

### Qualité et danger

Les équipes connaissent leurs réserves et acceptent de protéger un lot destiné à une personne sans dossier. Leur fragilité n’est pas une cruauté gratuite : elles manquent de pièces, de contenants, de personnel et d’informations fiables. Le danger vient du monopole de quelques scellés et de la tentation de transformer chaque urgence en dette familiale.

## Les voix des comptoirs

Ces identités sont incarnées par les conversations des représentants déjà présents. Elles ne sont pas annoncées comme trois nouveaux compagnons ou trois nouveaux acteurs autonomes.

| Voix | Relais | Position |
|---|---|---|
| Lise Ravel | Vieux-Port | Elle défend le secret des personnes soignées, mais exige une traçabilité des quantités. |
| Sofiane Tabet | Saint-Charles | Il maintient les reçus contradictoires et refuse de brûler l’ancien planning pour simplifier l’enquête. |
| Bérénice Fabre | Aubagne Haute | Elle accueille la garde nocturne et refuse les dettes héréditaires ; elle réclame néanmoins des fournitures concrètes. |

**Longchamp** est le point de départ et de remise au dispensaire. Ses représentants ne constituent pas une quatrième boutique illimitée.

## Planning réellement utilisé

L’horloge du jeu, et non l’heure réelle de l’ordinateur, détermine la garde quotidienne :

| Relais | Créneau | Identifiant stable |
|---|---|---|
| Vieux-Port | 06:00 inclus à 14:00 exclu | `v042-marseille-caravan-01` |
| Saint-Charles | 14:00 inclus à 22:00 exclu | `v042-marseille-caravan-02` |
| Aubagne Haute | 22:00 inclus à 06:00 exclu | `v042-huveaune-caravan-02` |
| Longchamp | Demande et remise du lot | `v042-marseille-settlement-02` |

Le passage de minuit, le repos et les voyages modifient la garde. Ils ne régénèrent jamais le stock.

## Quête — La pharmacie de garde

### 1. Une personne ne peut pas être renvoyée vers une heure

À Longchamp, une personne reste surveillée par le dispensaire. Le joueur accepte de chercher un lot scellé. Le reçu conserve le comptoir de garde à cet instant ; il ne change pas secrètement de destination pendant le trajet.

Il n’existe pas de minuterie cachée entraînant la mort d’un personnage hors écran.

### 2. Les deux plannings

Le représentant du comptoir annoncé retrouve le contre-reçu d’un échange de garde non transmis. La copie initiale demeure une preuve et n’est pas remplacée rétroactivement. Le joueur reçoit le nom du dépositaire réel.

### 3. Le lot réservé

Le dépositaire conserve le lot même lorsque son créneau de vente est terminé. Le joueur ne doit donc pas poursuivre une boutique qui change continuellement d’endroit.

Trois méthodes permettent le retrait :

| Méthode | Condition ou coût réel |
|---|---|
| Fournir l’équipe | 2 eaux + 2 tissus |
| Réparer le coffret | 2 ferrailles + 1 circuit |
| Contrôler les scellés | Intelligence 5 et 1 produit chimique |

Le contrôle est une mécanique fictive de jeu, pas une procédure médicale réelle. Le lot n’est pas ajouté comme médicament consommable ou vendable dans le sac : sa garde est suivie par la quête, empêchant de le dépenser puis d’en réclamer une seconde copie.

### 4. Deux façons de rendre des comptes

**Remise directe, reçu anonymisé.** Le lot est confié au dispensaire. Le registre public conserve les quantités, pas le nom du patient. Récompense unique : 35 capsules et 1 Stimpak.

**Réserve mutualiste sans dette héréditaire.** La personne soignée reçoit sa part en premier. Le reste devient une réserve à usage limité. Récompense unique : 20 capsules et trois prises en charge restaurant chacune au maximum 30 PV.

Le soin de réserve s’effectue auprès du comptoir actuellement de garde. Il ne retire ni radiation, ni infection, ni autre effet. Il ne consomme pas un crédit lorsque les PV sont déjà au maximum.

La quête conserve une conclusion exclusive. Elle ne réécrit pas les votes, les sept réseaux ou les diapositives déjà ratifiées.

## Commerce fini

Chaque comptoir vend au maximum :

- 2 Stimpaks à 25 capsules chacun ;
- 1 antibiotique à 18 capsules.

Le stock est individuel, persistant et distinct du lot réservé. Fermer puis rouvrir un dialogue, changer de créneau, voyager ou recharger la partie ne renouvelle rien. Le bouton disparaît lorsque la réserve est épuisée.

## Incarnation dans le monde

Chaque relais admissible reçoit un petit meuble et une croix verte. Le comptoir de garde affiche sa croix active ; les autres restent reconnaissables avec une teinte éteinte. Il ne s’agit pas d’un projecteur dynamique ni d’une pharmacie complète avec nouvel intérieur.

Un colis visible est posé chez le dépositaire pendant la réservation et disparaît après le retrait. E ouvre le planning ; les achats et les décisions exigent un représentant vivant, proche et visible.

Le placement vérifie le sol et ses coins, les collisions, les autres interactions, les PNJ et l’espace du joueur. Un site sans terrain utilisable conserve son dialogue mais ne reçoit pas de meuble flottant. Les props sont retirés au déchargement du relais, sans modifier routes, bâtiments ou relevés source.

## Interfaces et sauvegarde

- DATA → **PHARMACIES DE GARDE** : planning, stock, prochaine étape et suivi ;
- journal : demande, planning vérifié, lot récupéré et remise ;
- RADIO : bulletin textuel **La croix verte — garde et recours** ;
- registre `v062Pharmacy`, schéma 1 ;
- états `new → announced → redirected → carrying → done` ;
- stockage du comptoir annoncé, du dépositaire, de la méthode, de l’issue, des stocks et des crédits de soin ;
- aucune écriture dans `v060Council` ou `v061Poste` ;
- échec de sauvegarde : retour à l’état précédent sans paiement conservé.

Les dialogues des autres quêtes restent accessibles. Une réponse provenant d’une ancienne scène ou d’une ancienne partie ne peut modifier la nouvelle session.

## Matrice de portée de cette passe

| Élément | État |
|---|---|
| Institution et doctrine | Documentées dans cette annexe canonique |
| Quête en plusieurs étapes | Implémentée et testée |
| Trois horaires et stocks séparés | Implémentés et testés aux limites des créneaux |
| Colis et comptoirs conditionnels | Rendus par le moteur existant, placement prudent |
| Deux conclusions et soins finis | Implémentés, coûts/récompenses réellement appliqués |
| Sauvegardes anciennes | Nouveau registre ajouté sans effacer les précédents |
| Parcours navigateur | Instrumenté, relais plats synthétiques et stockage isolé |
| Validation de toutes les rues IGN | Non effectuée dans cette passe |
| Nouveaux intérieurs / nouveaux compagnons | Non ajoutés |
| Modification systémique des fins régionales | Non ajoutée ; résultat local conservé séparément |

## Vérification reproductible

```bash
node --check src/v050/10e_pharmacie_garde.js
node --test tests/expansion/lore_pharmacie_garde.cjs
python3 tools/build_single.py
python3 tools/build_single.py --check
python3 tests/expansion/pharmacie_browser_smoke.py --chromium /usr/bin/chromium
```

Le script navigateur exige Playwright et Chromium déjà installés. Il utilise le HTML réellement construit, mais injecte un pont de test, un terrain plat et des relais synthétiques en mémoire. Il n’altère pas le fichier de production ni une sauvegarde personnelle.

29 tests de modèle/adaptateur ont été exécutés localement ; 19 contrôles de navigateur ont validé notamment les vrais boutons de dialogue, E, l’épuisement du stock, le retrait hors garde, les coûts et le rechargement. Le rapport JSON lie ces observations à l’empreinte précise du HTML testé. Le rendu local utilisé est `SoftwareRenderer` ; ce n’est pas une certification GPU matérielle.

## Suite encore ouverte

L’arc de la Cité Radieuse, les assurances et litiges de la Mutuelle, la Cour du Lys, les épilogues de compagnons et la présence scénique de Madame la Préfète restent distincts. Cette livraison ferme la première boucle de pharmacie de garde, pas l’ensemble du lore français.
