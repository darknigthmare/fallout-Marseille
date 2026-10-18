# Provenance et intégrité — v0.50

La v0.50 prolonge le projet v0.49 déjà présent dans le dépôt [darknigthmare/fallout-Marseille](https://github.com/darknigthmare/fallout-Marseille). La base Git de cette reprise est le commit <code>a642ac360877621c05bacc083c736aeb8e1266c9</code>, intitulé « Publier FALLOUT : MISTRAL v0.49 complet ».

Les preuves actuelles sont regroupées dans <code>verification/v050/</code>. Les rapports et fichiers historiques sont conservés comme traces de leurs versions ; une affirmation ancienne sur l’absence du pack ou sur une méthode de test ne décrit pas automatiquement la v0.50.

## Programme canonique vérifié

| Fichier | Taille | SHA-256 |
|---|---:|---|
| index.html | 2 339 906 octets | <code>ac473edc0ecd222db0ed0dd3b29f30b245dfb2f27a967c7d588a200b11d784e5</code> |
| JOUER_FALLOUT_MISTRAL_v0.50.html | 2 339 906 octets | <code>ac473edc0ecd222db0ed0dd3b29f30b245dfb2f27a967c7d588a200b11d784e5</code> |

Le pilote natif compare les octets servis par HTTP, le document reçu par Chromium et le fichier présent sur disque. Il contrôle également que le programme n’a pas changé pendant le parcours. [Preuve native](../verification/v050/NATIVE_REAL_MAP.json)

Le catalogue conservé <code>data/fallout_layer_v042.json</code> fait 246 138 octets. Son SHA-256 actuel est <code>fa02b2b6eaf85abef39983c0605d4fd8bab5983fa6f7e367d2589c28d079b1b8</code>, identique à celui consigné dans la provenance v0.49. [Provenance historique](../verification/v049/PROVENANCE.json)

Les modules v0.50 ajoutent le classement du bouton Continuer, le raccord de campagne, le voyage vers les lieux découverts et l’interface de statut. Les versions des modules historiques conservés ne sont pas réétiquetées artificiellement. Cette version n’affirme pas avoir récupéré les fichiers v0.44 originaux absents de la provenance précédente.

## Origine du snapshot géographique

L’inventaire <code>data/map_pack/acquisition_v050.json</code> consigne une récupération au **18 octobre 2026 à 12:47:32 UTC** depuis les relais authentifiés de lecture configurés par le projet. Il décrit un snapshot historique ; les manifestes et les dates internes des grilles indiquent notamment le **19 septembre 2026**. Il ne s’agit pas d’une nouvelle acquisition exhaustive auprès des services officiels à la date de publication.

L’inventaire conserve les SHA-256 des **24 archives ZIP** et des **huit grilles de relief**, leurs tailles, les dates disponibles et les pas d’échantillonnage. Son empreinte est <code>b777d04b2402ef87870e3d8ff3a9835c4e35f6827dd4e641834bfc0862feff48</code>. [Inventaire d’acquisition](../data/map_pack/acquisition_v050.json)

### Conditionnement de transport pour GitHub

Le dépôt GitHub contient **24 archives logiques : 23 fichiers ZIP et un ZIP enveloppé en gzip**. L’enveloppe permet le transfert de la plus grosse archive sans changer son contenu décompressé. Le projet complet distribué sur Drive conserve les **24 ZIP originaux** ; l’inventaire historique et leurs empreintes restent inchangés.

| Fichier | Taille | SHA-256 |
|---|---:|---|
| base_00060_100.zip.gz — enveloppe de transport GitHub | 7 271 970 octets | <code>8e5c14d3ff5600622792fb33a83994c3527de014c544094cd0578e2715ca9862</code> |
| base_00060_100.zip — ZIP original conservé et vérifié | 13 437 755 octets | <code>bdfe4439f082f4a6e9d8b1c0472a4a1cefcd4e215457eec465620bedb619df94</code> |

L’installateur décompacte automatiquement l’enveloppe gzip avec une taille bornée, puis valide le SHA du ZIP original et son contenu avant installation. Il ne remplace pas l’empreinte d’acquisition par celle de l’enveloppe de transport.

Ce chemin a été exercé dans une copie isolée contenant l’enveloppe gzip et aucun fichier ZIP original correspondant. L’installation hors réseau confirme les mêmes 5 884 coordonnées, les 1 327 preuves de vide et les huit grilles. [Preuve du transport gzip](../verification/v050/INSTALL_OFFLINE_GZIP.json)

### Sources et attributions

| Couche | Fichier de référence | Attribution déclarée dans le projet |
|---|---|---|
| Routes, eau et autres vecteurs de fond | manifest_v038.json, source france-vector, zoom 14 | OpenStreetMap contributors — ODbL 1.0 |
| Emprises cadastrales | manifest_v038.json, source cadastre, zoom 16 | Cadastre Etalab / DGFiP — Licence Ouverte 2.0 |
| Altitudes du terrain | terrain/manifest_v039.json, ressource ign_rge_alti_wld | RGE ALTI IGN — Licence Ouverte 2.0 |

Références conservées pour les sources et attributions :

- [OpenStreetMap — copyright et contributeurs](https://www.openstreetmap.org/copyright) ;
- [Cadastre Etalab](https://cadastre.data.gouv.fr/datasets/cadastre-etalab) ;
- [Service altimétrique IGN / Géoplateforme](https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json).

Les attributions sont celles déclarées par les manifestes livrés. Les données géographiques gardent leurs conditions propres. Les textes historiques de licence portant sur une ancienne livraison sans données doivent être lus avec leur version ; la présente livraison inclut le snapshot décrit ci-dessus.

## Disponibilité réellement vérifiée

Le contrôle du disque ne se fonde pas sur le statut de cache distant inscrit dans les anciens manifestes.

| Élément | Résultat de l’audit actualisé |
|---|---:|
| Coordonnées vectorielles attendues | 5 884 |
| PBF non vides décodés | 4 557 |
| Coordonnées officiellement vides, avec attestation | 1 327 |
| Données vectorielles décompressées | 86 973 739 octets |
| Fichiers vectoriels manquants ou invalides | 0 |
| Grilles de relief valides | 8 / 8 |
| Altitudes valides | 174 944 |
| Valeurs NoData | 32 424 |
| Grilles manquantes ou invalides | 0 |

Le fichier <code>LOCAL_DATA_STATE.json</code> résulte d’une exécution actualisée du validateur conservé. Son champ de version <code>0.46.0</code> identifie cet outil ; l’agrégateur v0.50 signale explicitement cette convention. L’audit concorde avec celui demandé au serveur pendant le parcours natif. [Audit actuel](../verification/v050/LOCAL_DATA_STATE.json) · [Audit natif du serveur](../verification/v050/NATIVE_REAL_MAP.json)

Les données déclarées sans mesure restent NoData. Le relief est un ensemble de grilles de 161 × 161 points, avec interpolation pour le moteur, et non le produit raster IGN natif complet. Les bâtiments et repères du prototype utilisent ces données comme support ; leurs apparences et leurs hauteurs estimées restent des interprétations.

## Installation hors réseau et échantillon officiel

Une installation dans un dossier vide a utilisé **24 archives**, représentant **89 347 499 octets**, et les grilles fournies. Les 5 884 coordonnées ont été comparées par SHA-256 ; les 1 327 attestations de vide et les huit grilles ont été comparées octet pour octet. Le contrôle des processus a relevé **zéro tentative réseau**. [INSTALL_OFFLINE.json](../verification/v050/INSTALL_OFFLINE.json)

Un test distinct a interrogé l’API officielle IGN près d’Aubagne et reçu quatre valeurs mesurées : **112,38 m, 115,41 m, 110,52 m et 111,35 m**. Cette preuve concerne quatre points et le chemin d’acquisition officiel. Elle ne remplace pas les huit grilles historiques livrées et ne certifie pas tout le territoire. [IGN_OFFICIAL_SMOKE.json](../verification/v050/IGN_OFFICIAL_SMOKE.json)

## Origine des preuves de fonctionnement

| Groupe | Assertions | Méthode |
|---|---:|---|
| Parcours natif | 83 | Chromium, serveur HTTP, PBF, relief et stockage réels ; assistance d’API de diagnostic existantes, sans injection HTML |
| Voyage ciblé | 36 | HTML instrumenté, banc synthétique identifié, réseau et stockage contrôlés ; refus et erreurs provoqués |
| Raccord de campagne ciblé | 41 | Données locales réelles et adaptateur privé pour les échecs, réessais et changements de contexte |
| Sélection de sauvegarde ciblée | 18 | Chromium et localStorage natifs ; fixtures datées privées ; vrai bouton et chargeur |
| Installateurs | 42 | Fixtures unitaires d’intégrité, gzip borné, HTTP, reprise, réponses vides et conservation sur échec |
| Contrats hérités | 434 | Contrats du programme actuel, avec bancs synthétiques et réseau contrôlé selon chaque test |

Total : **654 assertions réussies, zéro échec**. Les installations hors réseau, y compris le chemin gzip isolé, et l’échantillon IGN sont des preuves complémentaires ; ils ne sont pas ajoutés artificiellement à ce total. [Agrégateur vérifiable](../verification/v050/QA_GLOBAL.json)

Les contrats hérités ont été adaptés au comportement v0.50, notamment le nouvel accès aux cartes, le pack effectivement installé, le choix explicite de la scène narrative et la priorité d’une sauvegarde courante plus récente. Le contrôle produit vérifie que cette sélection conserve la source et reprend la progression correcte ; il ne maintient pas l’ancienne priorité systématique d’un emplacement.

### Convention de SHA du test ciblé de voyage

Le champ <code>html_sha256</code> de <code>QA_POI_TRAVEL.json</code> vaut :

<code>4ddbffe1324f4e779d6a75fa4f2b25537f65066c2e7244538638299803c5a3cd</code>

Cette empreinte porte sur le HTML **après** l’insertion d’inspecteurs privés du test. Le champ <code>in_memory_module_insertion=false</code> signifie que le module de jeu était déjà intégré ; il ne signifie pas que le test ne contient aucun inspecteur.

L’agrégateur lit la chaîne littérale d’inspecteurs dans l’AST de <code>tests/v050/poi_travel.py</code>, reproduit son insertion dans le HTML canonique, puis vérifie cette empreinte. Il n’importe pas le pilote et ne lance aucun navigateur. Les rapports natif, campagne, Continuer et hérités utilisent le SHA du programme canonique selon leurs conventions respectives.

## Captures, rapports et limites observées

Les **20 captures natives originales** sont listées dans <code>NATIVE_REAL_MAP.json</code> avec leurs empreintes. Le rapport visuel en sélectionne **huit**, intégrées directement dans le HTML sous forme de PNG. La version PNG du rapport est une composition Pillow des mêmes captures, redimensionnées sans recadrage ; les fichiers originaux restent inchangés.

Le générateur <code>tools/report_v050.py</code> contrôle le programme canonique, les résultats et les empreintes des 20 captures avant d’écrire les rapports. Il conserve aussi les SHA-256 des JSON de preuve dans <code>QA_GLOBAL.json</code>. [Rapport HTML autonome](../RAPPORT_VISUEL_V0.50.html) · [Rapport PNG autonome](../RAPPORT_VISUEL_V0.50.png)

Les captures montrent les vrais fichiers géographiques et le rendu du prototype. Les ateliers sont une scène narrative identifiée ; la vue de cour est une inspection élevée. L’assistance de diagnostic, les découvertes préparées pour les deux voyages, le gel de simulation et la demande de fenêtre anticipée sont décrits dans les rapports.

La mesure de cadence provient de SwiftShader : **133,4 ms de médiane**, **150,1 ms au 95e percentile**, sur 26 échantillons. Le parcours conserve également les **18 erreurs de certificat des sondes externes Supabase**, sans les effacer ni relâcher TLS. Les ressources locales utiles ont chargé et aucune exception JavaScript n’a été observée. [Limites détaillées](KNOWN_LIMITATIONS_V0.50.md)

## Livraisons de la version

Le dossier de livraison prévu pour cette version est [Google Drive — v0.50](https://drive.google.com/drive/folders/1xE5VpELY64tz5GV9CHHrlsIb_rfahRnQ).

L’archive <code>JEU_COMPLET</code> contient le programme, les cartes extraites, le relief, les lanceurs et les preuves. L’archive <code>PROJET_COMPLET</code> ajoute les sources, tests, historique et les 24 ZIP de données. Les empreintes des archives et de leurs éventuelles parties sont fournies avec les fichiers de livraison ; le SHA du HTML ci-dessus n’est pas celui d’un ZIP.

La présente provenance décrit les artefacts locaux contrôlés. La disponibilité distante et les empreintes d’archives finales doivent être établies par les manifestes de livraison et les résultats de publication correspondants.
