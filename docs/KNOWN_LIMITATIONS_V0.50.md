# Limites connues — v0.50

**Rapport de la livraison initiale v0.50.** Pour l’extension communale actuelle, ses façades, ses intérieurs et leurs limites, consulter [Marseille entière](MARSEILLE_ENTIERE.md) et le [bilan de validation distinct](../verification/expansion/city/CITY_INTEGRATION.json).

La v0.50 a passé **83 contrôles natifs**, **95 contrôles ciblés**, **42 tests unitaires d’installateurs** et **434 contrats hérités**, soit **654 assertions**. Ces groupes emploient des méthodes différentes. L’agrégateur conserve leurs sources et leurs périmètres ; le total ne doit pas être présenté comme 654 parcours de jeu natifs. [QA_GLOBAL.json](../verification/v050/QA_GLOBAL.json)

## Territoire et représentation

Les fichiers géographiques sont présents : 5 884 coordonnées, dont 4 557 PBF non vides et 1 327 réponses officiellement vides, plus huit grilles de relief. L’audit indépendant ne relève aucun fichier manquant ou invalide. La présence complète des fichiers ne certifie pas la qualité de chaque rue, de chaque emprise cadastrale ou de chaque destination du catalogue. [Audit local](../verification/v050/LOCAL_DATA_STATE.json)

Les routes et les emprises proviennent des données géographiques livrées. Les bâtiments affichés sont des volumes interprétés par le moteur ; les hauteurs de toiture non renseignées restent estimées. Les décors, repères, acteurs et situations de jeu ne constituent pas un relevé du terrain réel.

Les huit grilles IGN comportent chacune 161 × 161 positions, avec **174 944 altitudes valides** et **32 424 valeurs NoData** au total. Le pas varie selon le secteur et l’axe, d’environ 48 à 162 m. Le moteur échantillonne et interpole ce relief ; la livraison n’est pas le raster IGN natif à sa résolution maximale. Les valeurs NoData restent manquantes et peuvent empêcher un chargement ou une arrivée dans les zones concernées. [Inventaire des grilles](../data/map_pack/acquisition_v050.json)

Le snapshot géographique a été récupéré le 18 octobre 2026 depuis les relais configurés ; ses manifestes et ses grilles portent des dates historiques, notamment du 19 septembre 2026. Il ne s’agit pas d’une nouvelle collecte officielle intégrale à la date de livraison. Le contrôle direct IGN distinct a porté sur quatre points près d’Aubagne. [Provenance v0.50](PROVENANCE_V050.md) · [Échantillon IGN](../verification/v050/IGN_OFFICIAL_SMOKE.json)

## Campagne et scènes narratives

La sortie du sas conduit désormais à l’extérieur géographique d’Aubagne. Une balise relie cet extérieur aux **Ateliers d’Aubagne — scène narrative** ; le retour rétablit le point géographique conservé. Le décor des ateliers et les scènes historiques de campagne sont des créations du jeu. Ils ne doivent pas être présentés comme des reconstructions cadastrales.

Le parcours natif vérifie le prologue, la sortie, la balise, le dialogue de Mireille jusqu’à l’étape principale 3 et le retour avec les acquis. Il ne représente pas une partie complète de toute la campagne. Le test ciblé ajoute les cas d’échec, de réessai, d’annulation et de changement de sauvegarde. [Parcours natif](../verification/v050/NATIVE_REAL_MAP.json) · [Contrats du raccord](../verification/v050/QA_CAMPAIGN_MAP.json)

## Méthode de la QA native

Chromium 134 ouvre le serveur HTTP local. Les fichiers du jeu, les requêtes PBF et terrain, ainsi que le stockage du navigateur sont réels. Le pilote n’injecte pas de HTML, ne remplace ni réseau ni stockage et n’emploie pas le laboratoire synthétique.

La méthode reste assistée : les approches et actions du prologue, certaines positions de mesure, l’heure jour/nuit et la découverte préalable de deux lieux passent par des API de diagnostic déjà présentes dans le jeu. Les déplacements contrôlés appellent la collision de production. La balise extérieure est d’abord vérifiée avec simulation active ; un gel de simulation est ensuite utilisé pour stabiliser les mesures.

Le contrôle de continuité franchit réellement 28,06 m d’une frontière cadastrale dans les deux sens. Le pilote demande ensuite une fenêtre anticipée réelle à moins de 120 m, ce qui modifie les tuiles publiées. Il compare l’identité de scène et la géométrie commune. Cette preuve n’est pas une randonnée manuelle intégrale, ni une validation de tous les mécanismes de prévision à toutes les vitesses.

Le cas de cour provient d’un anneau intérieur réellement décodé dans un PBF. Son image est une inspection élevée, explicitement étiquetée, et non une vue de déplacement du joueur. Les 20 captures originales portent leur empreinte dans le rapport natif.

Le menu a été contrôlé sur une largeur de 390 px ; ce contrôle n’est pas une certification de l’ensemble des commandes tactiles, des performances mobiles ou de tous les dialogues à cette largeur. [Méthode et captures](../verification/v050/NATIVE_REAL_MAP.json)

## Voyage rapide et sauvegardes

Deux destinations ont été déclarées découvertes par l’action de diagnostic existante, puis rejointes avec les boutons réels du Pip-Boy : **Belvédère · Aubagne** et **Épave · Galeries de l’Huveaune**. L’annulation d’une confirmation, l’application unique des durées, la conservation des objets, de l’expérience et des capsules, ainsi que l’arrivée libre ont été vérifiées.

Cette preuve ne signifie pas que tous les lieux du catalogue ont été découverts à pied ou visités. Les tests ciblés de voyage utilisent un banc synthétique identifié et des erreurs provoquées pour examiner les refus, les absences de terrain, l’eau, les collisions, les réponses tardives et les changements de contexte. [Voyages natifs](../verification/v050/NATIVE_REAL_MAP.json) · [Cas ciblés](../verification/v050/QA_POI_TRAVEL.json)

Le bouton Continuer et le stockage natif ont été vérifiés par un rechargement réel du navigateur. Le classement des sauvegardes est aussi testé avec des données datées préparées par un adaptateur privé. La sauvegarde reste liée à l’origine et au profil du navigateur ; une synchronisation entre appareils n’est pas certifiée par ces tests. [Contrats de reprise](../verification/v050/QA_CONTINUE_SAVE.json)

Le journal hérité couvre les acteurs territoriaux reconnus. Les acteurs lointains ne sont pas tous simulés en permanence. Les bornes et règles de persistance des versions précédentes restent celles du moteur conservé ; l’extension arbitraire du catalogue n’est pas couverte par la QA actuelle.

## Performances observées

Le parcours a été exécuté avec le moteur graphique logiciel **SwiftShader**, via WebGL dans Chromium. Sur le point mesuré :

| Mesure | Valeur |
|---|---:|
| Échantillons de cadence | 26 |
| Durée médiane d’une image | 133,4 ms |
| 95e percentile | 150,1 ms |
| Cadence correspondant à la médiane | Environ 7,5 images/s |
| Groupes de rendu | 4 732 |
| Triangles déclarés | 169 949 |

Cette cadence limite le confort dans cet environnement. Elle ne prédit pas les performances d’un GPU matériel, d’un téléphone ou de l’ordinateur du joueur. Aucun seuil de fluidité matérielle n’est revendiqué. Le contrôle de cadence atteste seulement que les images continuent à être produites pendant l’affichage de l’extérieur réel. [Mesure native](../verification/v050/NATIVE_REAL_MAP.json)

## Réseau et installation

Le navigateur a relevé **18 erreurs <code>ERR_CERT_AUTHORITY_INVALID</code>** sur des sondes HTTPS de services Supabase historiques. Les politiques TLS n’ont pas été relâchées. Ces sondes externes n’ont pas fourni les cartes du parcours : les ressources utiles provenaient du pack local. Aucune requête de PBF ou de relief installé n’a échoué et aucune exception JavaScript n’a été observée. [Événements réseau natifs](../verification/v050/NATIVE_REAL_MAP.json)

L’installation hors réseau à partir des 24 ZIP et des huit grilles fournis a été vérifiée dans un dossier vide avec zéro appel réseau et comparaison des fichiers. Les 42 tests d’installateurs utilisent quant à eux des fixtures pour les réponses incorrectes ou tronquées, les archives corrompues, le transport gzip borné et les reprises ; ils ne garantissent pas la disponibilité future des relais distants. [Installation hors réseau](../verification/v050/INSTALL_OFFLINE.json) · [Tests unitaires](../verification/v050/QA_INSTALLERS.json)

Le dépôt GitHub transporte les mêmes 24 archives logiques sous la forme de **23 ZIP et un ZIP enveloppé en gzip**, <code>base_00060_100.zip.gz</code>. Ce conditionnement répond à une contrainte de transfert ; il ne modifie pas les données. L’installateur décompacte l’enveloppe avec une taille bornée, puis exige le SHA-256 du ZIP original. Le projet complet distribué sur Drive conserve les 24 ZIP d’origine ; le jeu complet contient déjà les cartes extraites.

Le chemin gzip a été vérifié dans une copie isolée où le ZIP original était absent : 5 884 coordonnées, 1 327 preuves de vide et huit grilles comparées, sans tentative réseau. Cette installation constitue une preuve supplémentaire et n’augmente pas le total d’assertions unitaires. [INSTALL_OFFLINE_GZIP.json](../verification/v050/INSTALL_OFFLINE_GZIP.json)

Le HTML seul ouvert avec <code>file://</code>, l’installation PWA native, une synchronisation distante des sauvegardes et une exécution sur tous les navigateurs n’ont pas été certifiés par ce parcours.

## Statut du projet

FALLOUT : MISTRAL reste un prototype de fan non officiel. Aucune approbation ou affiliation de Bethesda n’est revendiquée. Les rapports historiques décrivent leur propre version ; leurs mentions anciennes d’un pack absent ou de limitations du navigateur ne remplacent pas les preuves v0.50.
