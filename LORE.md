# Fallout: Mistral — Lore canonique

> **« En Provence, on ne meurt pas lorsque le cœur s’arrête. On meurt lorsque le registre vous efface. »**

Ce fichier est la porte d’entrée du lore de **Fallout: Mistral / Fallout Marseille**. Le projet est une création de fan non officielle située dans l’univers de Fallout ; il ne constitue pas un contenu canon de Bethesda/ZeniMax.

## Source de vérité

L’ordre de priorité est le suivant :

1. [`docs/BIBLE_LORE_FALLOUT_MISTRAL.md`](docs/BIBLE_LORE_FALLOUT_MISTRAL.md) — canon narratif général ;
2. [`docs/MATRICE_INTEGRATION_LORE.md`](docs/MATRICE_INTEGRATION_LORE.md) — état réel de l’intégration, sans confondre texte, code source, build généré et validation ;
3. [`docs/LORE_A03_MADAME.md`](docs/LORE_A03_MADAME.md) — chaîne de preuves du prologue, registre civique, sept réseaux et projections politiques ;
4. [`docs/LORE_CONTINUITE.md`](docs/LORE_CONTINUITE.md) — dossiers jouables de continuité ;
5. [`docs/LORE_SERVICES_PUBLICS.md`](docs/LORE_SERVICES_PUBLICS.md) — sept réseaux et quatre factions de services ;
6. [`docs/BESTIAIRE_REGIONAL.md`](docs/BESTIAIRE_REGIONAL.md) — créatures effectivement suivies par le dépôt ;
7. les documents spécialisés et les textes en jeu.

En cas de contradiction, la bible générale fixe le canon, tandis que la matrice indique ce qui existe réellement dans le jeu.

## Statuts employés

| Statut | Signification |
|---|---|
| **Jouable** | Le joueur peut ouvrir, faire progresser et conclure le contenu dans le programme, avec sauvegarde. |
| **Systémique** | Le contenu observe plusieurs décisions de campagne et calcule un état régional persistant. |
| **Câblé en source** | Le code est intégré à la chaîne de build, mais le HTML distribué doit être reconstruit pour le contenir. |
| **Canon documentaire** | Le concept appartient au monde, mais ne dispose pas encore d’un système jouable complet. |
| **Accroche** | Le concept est approuvé comme direction, mais demande encore lieux, PNJ, quêtes, assets ou règles. |
| **Proposition** | Idée à arbitrer avant d’entrer dans le canon. |

## Le cœur du monde

L’action principale se déroule en **2297**, deux cent vingt ans après le Jour des Six Sirènes. La Provence n’est pas une copie du désert américain : elle reste lumineuse, maritime, administrative, industrielle et traversée par des institutions qui refusent de mourir.

Le protagoniste sort de l’abri **A‑03 — Les Fontaines** après avoir été déclaré mort par erreur — ou plutôt par calcul. Son identité a été supprimée pour équilibrer les rations. Il découvre une région où l’eau, les soins, les voies, les archives, le courrier et les machines possèdent chacun leur propre souveraineté.

La question centrale n’est pas simplement « qui contrôlera un réacteur ? », mais :

> **Qui a le pouvoir de reconnaître qu’un être vivant existe, et quels droits découlent de cette reconnaissance ?**

## A‑03 et M.A.D.A.M.E.

Le prologue **« Un vivant de trop »** est suivi par un registre civique persistant. Il conserve l’avis de décès 04‑771‑C, la présence corporelle, la trace du relais, le journal d’A‑03, le témoignage d’Odette, la solution employée à AUB‑04 et les preuves réunies ensuite dans la campagne.

M.A.D.A.M.E. ne remplace plus seulement une menace écrite : son interface confronte les versions contradictoires et calcule comment les décisions du joueur transforment l’accès, la légitimité, la coercition et la résilience des sept réseaux. Le résultat produit une projection politique, sans prétendre déclencher une fin qui ne serait pas encore mise en scène.

## Les sept réseaux

La région survit grâce à sept réseaux interdépendants :

1. **Identité** — archives, témoignages, santons civiques et droit d’exister ;
2. **Eau** — pompes, citernes, assainissement et quotas ;
3. **Santé** — triage, médicaments, maternités et dettes de soin ;
4. **Transport** — rail, routes, tunnels, ports et droits de passage ;
5. **Énergie** — réacteurs, cellules, barrages et exposition aux radiations ;
6. **Communication** — radio, poste, Minitel, sirènes et preuves publiques ;
7. **Approvisionnement** — chantiers, marchés, cargaisons, vivres et pièces.

Aucune faction ne doit pouvoir contrôler durablement les sept sans devenir un nouvel État.

## Factions déjà raccordées au jeu

Les dossiers de continuité raccordent notamment :

- la **Convention des Cendres** ;
- la **Direction de la Continuité — CONCORDE** ;
- les **Vigies des Crêtes** ;
- les **Insulaires du Lazaret** ;
- le **Syndicat Perpétuel** ;
- les **Sans-Dossier** ;
- les **Communes du Mistral** ;
- les **Gilets de Cendre** ;
- la **Ligue des Cent Trêves / COCHONNET-3**.

Les dossiers de services rendent également jouables :

- **La Sociale** ;
- les **Aiguilleurs du Réseau** ;
- le **Commissariat des Atomes** ;
- l’**Amirauté du Levant**.

## Règles de cohérence

- Toute faction possède une qualité réelle, un danger réel et des besoins matériels.
- Toute créature possède une origine, un habitat et un rôle écologique.
- Une référence française doit produire du gameplay, pas seulement une plaisanterie visuelle.
- Les administrations, syndicats, communes et services ne sont ni entièrement héroïques ni entièrement maléfiques.
- La diversité sociale et culturelle de Marseille fait partie du monde ; les accents et clichés ne remplacent jamais des personnages.
- Une conséquence textuelle ne doit jamais prétendre qu’un train, une flotte, une pompe ou une colonie a été physiquement créé si le programme ne le fait pas.
- Le beau temps, la mer et la couleur ne diminuent pas l’horreur : en Provence, l’apocalypse peut se produire sous un ciel bleu.

## Audit de référence

La consolidation initiale partait de `main` au commit `1d1833a4cb320a2075cba5b57c4504e99b206fe3` du 4 novembre 2026. La matrice d’intégration suit désormais les ajouts fusionnés, les validations du build et les chantiers encore ouverts.
