# FALLOUT Marseille — MISTRAL


[Raccords routiers et livraison synchronisée — 29 octobre 2026](docs/QA_STREAMING_2026-10-29.md) : correction des fragments complémentaires, HTML reconstruits, contrôle du cache hors ligne et captures réellement exécutées.

## v0.50 · Les routes retrouvées

La poursuite du **1er novembre 2026** affine la **vue FPS** : prises mieux cadrées, treize profils dans neuf familles et rechargements distincts selon huit alimentations. Le HUD suit les touches et neutralisations réelles, les PV perdus et le vrai délai de rechargement ; les sous-titres cherchent une bande libre. La manette standard maintient aussi la présentation de visée avec LT. [Vue FPS](docs/VUE_FPS.md) · [HUD](docs/HUD_FPS.md).

En parallèle : surfaces MNS mesurées de la chapelle de la Vieille Charité et du Pharo, deux fenêtres IGN du nord (Estaque/Saint-Antoine), dépôts persistants dans les meubles intérieurs, suites aux décisions des Communes et des Gilets, et distributeurs Nuka-Cola réparables à stock fini. Les anciens lieux, services, dossiers, grenades et mines sont conservés. [Chantiers et limites](docs/CHANTIERS_ACTIFS.md).

L’intégration de `7ab5043` conserve aussi les fragments routiers complémentaires et leur identité entre partitions, les annulations de chargement et les diagnostics de géométries distinctes. Les quatre fichiers générés sont contrôlés ensemble ; le cache hors ligne prend son identité dans l’empreinte du HTML. Les [preuves du 29 octobre](docs/QA_STREAMING_2026-10-29.md) restent historiques et la nouvelle campagne vérifie le programme intégré.

Le jeu couvre **toute la commune officielle de Marseille, îles comprises**, avec les données IGN acquises : 291 001 identifiants d’objets bâtiment et 55 449 tronçons routiers. La précision du relief varie selon la couverture. Les détails architecturaux et intérieurs sans relevé restent inventés. L’échelle métrique ne certifie pas une reproduction documentaire et visuelle intégrale **1:1**. [Portée de la ville](docs/MARSEILLE_ENTIERE.md).

Le [bilan courant](verification/expansion/continuation_20261101_integrated/CONTINUATION_INTEGRATION.json) rattache les vérifications au HTML intégré `c0f13de317f1678cd20a2ed9ea3f2ee687054eb67f3815026357707828ff77b1` : **3 312 contrôles descriptifs réussis et 76 captures**, répartis entre 13 méthodes. L’[état de production](docs/STATUT_PRODUCTION.md) présente les résultats confirmés et distingue les preuves complémentaires hors de cette somme. Les modèles d’armes restent stylisés, les aménagements non relevés sont inventés et les entrées Gamepad/tactiles émulées ne certifient pas de matériel physique. Les méthodes et parcours assistés sont distingués.

Le [bilan avant intégration](verification/expansion/continuation_20261101/CONTINUATION_INTEGRATION.json), **3 310 contrôles et 76 captures** sur le HTML `98a78a1c…`, reste historique. Il ne valide pas automatiquement le programme intégré.

La livraison `29df190` conserve ses [2 892 contrôles et 55 captures](verification/expansion/immersion/IMMERSION_INTEGRATION.json) sur son HTML `844376c0…`. Les [2 887 contrôles et 62 captures de `f4a7337`](verification/expansion/wasteland/WASTELAND_INTEGRATION.json), sur `ed6e4103…`, et les [2 324 contrôles et 42 captures de précision](verification/expansion/precision/PRECISION_INTEGRATION.json) restent historiques. Ces résultats ne sont pas réattribués au nouveau programme.

[Installation](docs/INSTALLATION_V050.md) · [Ancienne distribution Drive](https://drive.google.com/drive/folders/1xE5VpELY64tz5GV9CHHrlsIb_rfahRnQ). Le lien Drive et le rapport visuel initial n’ont pas été actualisés pour cette poursuite.

## Jouer

Python 3 est nécessaire au serveur local. Aucun paquet npm n’est requis pour jouer.

- **Windows :** lancer `LANCER_APP_WINDOWS.bat`.
- **Linux :** `bash LANCER_APP_LINUX.sh`.
- **macOS :** `bash LANCER_APP_MAC.command`.

Le navigateur s’ouvre sur `http://127.0.0.1:8765/index.html`. Au premier lancement depuis GitHub, le serveur prépare les cartes à partir des 24 archives de base, de l’enrichissement d’Aubagne et du nord et du sud de Marseille, de l’archive communale et des **six ZIP de relief natif**, **sans téléchargement**. La plus volumineuse des archives de base est transportée en `.zip.gz` puis reconstituée automatiquement, avec contrôle du SHA-256 du ZIP d’origine. La préparation et la validation du nouvel atlas communal peuvent prendre plusieurs minutes selon l’ordinateur ; attendre l’ouverture du navigateur. Le relief central natif ajoute 157 896 379 octets d’archives (environ 150,58 Mio) et 192 328 140 octets après extraction (environ 183,42 Mio), en plus des données précédentes conservées. Le MNS des monuments est fourni comme maillage attribué ; les fenêtres nord et sud rééchantillonnées rejoignent l’archive d’enrichissement. Le ZIP initial proposé sur Drive précède ces extensions.

```bash
git clone https://github.com/darknigthmare/fallout-Marseille.git
cd fallout-Marseille
python3 tools/serve_game.py
```

Utiliser le lanceur de l’application pour lire les données cartographiques. Le fichier `JOUER_FALLOUT_MISTRAL_v0.50.html` contient le programme ; une ouverture directe en `file://` ne donne pas au navigateur l’accès HTTP requis par le pack.

## Ce qui change

- **Mains, armes et HUD FPS.** Treize profils originaux dans neuf familles : revolver et barillet articulé, double canon basculant, pistolet à énergie court et lance-missiles tubulaire s’ajoutent aux formes existantes. Huit alimentations ont leur pièce et leur geste de recharge, avec conservation des munitions ordinaires. Les prises remontent en portrait ; les poignets peuvent encore passer derrière le HUD translucide. Visée maintenue avec X, clic droit, Visée ou LT ; FOV, direction et dégâts du monde conservent leurs règles.
- **Surfaces supérieures de quatre sites connus.** Major/Garde conservées, chapelle de la Vieille Charité et Pharo ajoutés à partir de vrais MNS IGN natifs de 0,50 m : dix-huit composantes admissibles sur dix-neuf. Ces surfaces mesurent le sursol ; elles ne relèvent ni les façades ni les pièces. L’association du Pharo reste contextuelle. [MNS des monuments](docs/SILHOUETTES_MNS.md).
- **Relief du nord.** Estaque et Saint-Antoine : 206 240 nœuds au pas demandé de 1 m, rééchantillonnés au plus proche depuis les GeoTIFF IGN de 0,50 m. La région communale charge ces imports ; les anciens lots sud/Aubagne restent conservés. [Relief nord](docs/RELIEF_NORD_MARSEILLE.md).
- **Commune entière disponible.** Les requêtes officielles couvrent Marseille et ses îles ; le voisinage est chargé à la demande, avec des caches bornés. Les objets de bordure sont conservés entiers.
- **Façades et intérieurs jouables.** Portes à panneaux, entrées vitrées, menuiseries et persiennes inventées suivent les segments source et leurs budgets, avec passage conservé. Le **layout 5** conserve les programmes par usages et ajoute les portes coulissantes. Il adapte commerces, ateliers, bureaux, enseignement et santé aux usages explicites : caisse, tables et tableau scolaires, photocopieur, armoire à outils et paravent complètent les équipements existants. Les visites sauvegardées **1/2/3/4** conservent leurs cloisons et meubles ; les plans documentés gardent leurs cotes. Lits, cuisines et établis admissibles proposent désormais des services physiques par E : repos, recettes ordinaires et fabrication avec fournitures finies, sauvegardés sans changer les plans. Les armoires, caisses et rayonnages admissibles permettent aussi de déposer/reprendre des fournitures par E, avec capacité réelle, registre local sauvegardé et réserves initialement vides. Circulation, budgets et omissions restent exposés. [Menuiseries](docs/FACADES_MENUISERIES.md) · [Programmes intérieurs](docs/INTERIEURS_USAGES.md).
- **Dossiers et réactions des factions.** Huit dossiers complémentaires sont disponibles, dont les nouveaux engagements des Communes du Mistral et des Gilets de Cendre ; les six dossiers antérieurs sont conservés. Les preuves sur place, décisions exclusives, retours des habitants et bulletins radio textuels gardent leurs conséquences sauvegardées. Après les choix des Communes/Gilets, une copie du reçu se remet à l’autre relais nommé ; le retour au donneur fournit un contre-don unique propre à l’issue. [Continuité du lore](docs/LORE_CONTINUITE.md).
- **Armures assistées conservées et sécurisées.** Les plaques, cœurs et configurations du système existant gardent leur propriétaire. Les opérations matérielles sont atomiques ; les techniciennes de relais proposent aussi l’entretien à proximité. [Armures assistées](docs/ARMURES_ASSISTEES.md).
- **Collections et consommables.** Figurines S.P.E.C.I.A.L., magazines temporaires et Nuka-Cola conservent leurs acquisitions finies. Jet, Buffout, Mentats et Psycho ajoutent des effets temporaires, une tolérance, une dépendance et un retrait sauvegardés, avec un soin local auprès de Sofia. [Objets emblématiques](docs/CONTENU_EMBLEMATIQUE.md) · [Consommables et dépendances](docs/CONSOMMABLES_ET_DEPENDANCES.md).
- **Distributeurs Nuka-Cola.** Deux machines originales dans les scènes d’Aubagne et de Marseille, liées au même stock que leur relais géographique. E ouvre le monnayeur ; réparation avec 2 ferrailles et 1 circuit, puis achat de bouteilles classiques/Quantum en capsules. Stocks finis, placement physique, volume du joueur respecté et sauvegarde atomique. [Distributeurs](docs/DISTRIBUTEURS_NUKA_COLA.md).
- **Cinq espèces régionales et deux créatures emblématiques incarnées.** Rat-câble, Gabian bombardier, CERFA-77, Rat-couronné et Cigale du Mistral utilisent des silhouettes originales ciblables, avec leurs identités, statistiques et butins existants. Le Radscorpion et le Fangeux disposent de modèles, pinces ciblables et attaques spécifiques. Le Gabian vole et largue un projectile réel ; son vol reste limité à huit mètres au-dessus du sol source, avec contrôle des volumes et des obstacles. Les apparitions exigent des sources et un emplacement admissibles. [Bestiaire régional](docs/BESTIAIRE_REGIONAL.md).
- **Relief central natif et fond communal.** Douze dalles officielles LiDAR HD, découpées en 48 morceaux, apportent 12 km² à 0,50 m en Lambert-93/NGF-IGN69, sans rééchantillonnage des cellules source. Le fond de 25 m, les partitions de 10 m et les anciens relevés locaux restent disponibles ailleurs. Deux fenêtres autour du Vélodrome et de Borély ajoutent 384 832 nœuds MNT reprojetés au pas demandé de 1 m par échantillonnage au plus proche ; elles ne prolongent pas le treillis natif central. La mer suit les géométries IGN. [Relief précis](docs/RELIEF_PRECIS.md) · [Relief sud](docs/RELIEF_SUD_MARSEILLE.md).
- **Commandes de manette complétées.** Favoris d’armes, lampe et plan de terrain, disposition gaucher, neutralisation des commandes maintenues et pause à la déconnexion de la manette utilisée. Les tests Gamepad simulés restent distingués des essais matériels. [Commandes et réglages](docs/CONTROLEUR.md).
- **Mines à fragmentation.** P pose une mine sur un support admissible ; E la désamorce et la récupère. Armement et avertissement précèdent un souffle occulté ; stocks, recette et nombre de mines sont finis. Le stockage conserve chaque scène, étage et phase. [Mines](docs/MINES_A_FRAGMENTATION.md).
- **Grenades à fragmentation.** Achat en stock fini, fabrication à un établi, lancer avec N ou le bouton tactile, trajectoire et rebonds, dégâts occultés et reprise d’une fusée armée. [Grenades à main](docs/GRENADES_A_MAIN.md).
- **Carte réelle disponible localement.** Les fichiers sont validés, les vides officiels portent leur preuve et les huit grilles de relief de base sont incluses.
- **Sortie de campagne reliée à la carte.** Le sas propose la sortie géographique et un accès direct explicitement nommé « scène narrative ». La balise des ateliers permet de retrouver Mireille ; la sortie des ateliers retrouve le point géographique enregistré, y compris après recharge.
- **Voyage rapide vers les lieux découverts.** Dans le Pip-Boy, ouvrir **MAP → LIEUX ET VOYAGES**, sélectionner un lieu, préparer puis confirmer le voyage. L’arrivée est contrôlée contre le relief, l’eau, les murs et une marge de marche libre. Le temps avance seulement après réussite.
- **Continuer reprend la sauvegarde la plus récente.** La sauvegarde courante est comparée aux autosauvegardes et emplacements manuels. Les données des versions antérieures restent migrables.
- **Installation plus robuste.** Gzip borné, contrôle des archives, reprise, conservation des fichiers précédents en cas d’erreur et repli direct vers l’IGN pour le relief. Le mode `--offline` interdit le réseau.
- **Menu accessible sur les petites fenêtres.** Les boutons restent atteignables ; l’état des cartes provient de l’audit du serveur local.

Les 248 lieux du catalogue, les rencontres persistantes, les blessures, les dépouilles à butin fini, les intérieurs et le lore des versions précédentes sont conservés. Les bâtiments et routes communs restent attachés à une scène extérieure persistante lorsque la fenêtre de tuiles se déplace.

## Données et portée

Le pack de base comprend **4 557 fichiers PBF**, **1 327 coordonnées officiellement vides**, **8 grilles de 161 × 161 points**, **174 944 altitudes valides** et **32 424 points sans mesure**. L’audit ne relève aucun fichier attendu manquant ou invalide. Une grille complète peut contenir des points sans mesure ; le jeu conserve ces absences.

Le pack de base repose sur les sources OpenStreetMap, cadastrales et IGN ; l’extension communale ajoute les objets BD TOPO et le littoral IGN avec leurs preuves distinctes. Les décors, détails inconnus de façade et plans non documentés sont interprétés par le jeu. La campagne historique utilise encore des scènes narratives distinctes, clairement indiquées. La couverture géographique complète ne certifie pas une reproduction photoréaliste ni une visite vérifiée de chaque rue et intérieur.

Le projet ChatGPT correspondant a été retrouvé et consulté ; les éléments accessibles ne contiennent pas de lore supplémentaire exploitable. Les archives ne sont pas accessibles depuis cet environnement cloud. Les neuf factions, huit dossiers historiques et vingt-cinq noms déjà conservés dans le dépôt restent la source du canon ; les nouvelles histoires sont des prolongements écrits du jeu.

Les essais comprennent des parcours dans Chromium avec **vrais fichiers HTTP et stockage natif**, ainsi que des tests de régression sur bancs synthétiques distincts. Le rapport visuel v0.50 présente les captures de la livraison initiale v0.50 ; il reste historique, comme les rapports v0.49 et antérieurs. La validation des extensions actuelles est détaillée plus bas.

## Vérifier et reconstruire

```bash
python3 tools/build_single.py
python3 tools/build_single.py --check
node --check src/game.js
python3 tools/validate_real_map_v046.py --require-complete --report verification/v050/LOCAL_DATA_STATE.json
python3 tests/v050/test_installers.py
python3 tests/v050/test_installers.py --offline-integration
python3 tools/check_expansion.py
python3 tools/check_v050.py
python3 tests/v050/poi_travel.py
python3 tests/v050/campaign_map.py
python3 tests/v050/continue_save.py
python3 tests/v050/native_real_map.py
python3 tools/report_v050.py
python3 tools/package_v050.py
```

Les tests de navigateur nécessitent les dépendances de `requirements-dev.txt` et Chromium installé par Playwright, ou `CHROMIUM_PATH` pointant vers un navigateur existant. Le rapport de livraison regroupe les résultats et précise leur périmètre. Les PBF extraits sont ignorés dans Git parce que les archives vérifiées qui les reconstituent sont déjà suivies ; ils figurent dans les archives de jeu distribuées sur Drive.

Prototype de fan non officiel. © contributeurs OpenStreetMap — ODbL · Cadastre Etalab / DGFiP — Licence Ouverte 2.0 · IGN RGE ALTI — Licence Ouverte 2.0. [Sources et provenance](docs/PROVENANCE_V050.md).

## Acquisition précédente d’Aubagne et exploration

Cette section décrit la livraison précédente `bb122d0`. L’état courant figure dans [Marseille entière](docs/MARSEILLE_ENTIERE.md) et le [suivi des chantiers](docs/CHANTIERS_ACTIFS.md). Les bilans des livraisons précédentes gardent leurs empreintes et ne valident pas automatiquement le programme courant.

Des sources IGN ont réellement été acquises et intégrées autour d’Aubagne, en complément du pack de base :

- **1 404 objets bâtiment et 472 tronçons de route BD TOPO**, sur une emprise d’acquisition demandée de `[43.293, 5.565, 43.300, 5.576]` (sud, ouest, nord, est). Les objets intersectants sont conservés entiers.
- **174 777 altitudes RGE ALTI**, interrogées au pas demandé d’environ **2 m** sur ce secteur.
- **145 396 nœuds MNT LiDAR HD** sur le plus petit extrait `[43.2956, 5.5698, 43.2976, 5.5718]`. Le GeoTIFF source possède des pixels natifs de **50 cm** ; la grille WGS84 du jeu est reprojetée par échantillonnage **au plus proche (`nearest`)**, explicitement déclaré dans sa provenance.

Le pas d’échantillonnage ne garantit pas une précision absolue de 50 cm. Les précisions XY et Z et les dates restent celles des sources. Cette acquisition antérieure n’apportait pas de plans de façades ou d’intérieurs ; l’extension communale actuelle ajoute des créations cohérentes pour les parties inconnues. Ce seul secteur ne constitue pas une reproduction exhaustive de Marseille « 1:1 ». Les formes de toiture prises en charge, à deux pans ou à un pan, explicitement cotées et orientées, disposent d’une collision par faces et de surfaces accessibles ; les bâtiments BD TOPO sans forme de toiture renseignée conservent une enveloppe estimée.

Le conditionnement reproductible des enrichissements utilise `tools/world_source_bundle.py`. Au lancement normal, le serveur restaure **sans réseau** les sources dont l’archive est fournie, avec vérification du reçu et des fichiers, tout en conservant les imports utilisateur déjà valides. L’archive fournie et sa restauration ont été vérifiées. Le [bilan de cette livraison](verification/expansion/real_sources/REAL_SOURCE_INTEGRATION.json) regroupe 397 contrôles de logique et d’outils, 434 contrats hérités et 84 contrôles du parcours natif ; les autres essais et leurs fixtures restent séparés. Les rapports v0.50 et le bilan précédent associé au HTML `8f4619bc…22d5aaa` restent historiques et ne valident pas automatiquement cette livraison enrichie.

Dans le Pip-Boy, **STAT → BIVOUAC** permet de construire un kit portable puis de le déployer sur un sol mesuré, cuisiner, purifier et se reposer avec des réserves finies. **DATA → ENTRAIDE** permet d’apporter des fournitures aux habitants des relais découverts. Le matériel, le camp et les livraisons sont conservés dans la sauvegarde. Les commandes et réglages de manette sont disponibles dans les options.

- [Sources publiques identifiées : IGN, BD TOPO et LiDAR HD](docs/SOURCES_GEOGRAPHIQUES_PUBLIQUES.md)
- [Importer des sources locales et convertir un GeoTIFF](docs/IMPORT_SOURCES_REELLES.md)
- [État d’Aubagne — livraison antérieure](docs/ETAT_TERRITOIRE_ET_JEU.md)

Pour préparer le plan du secteur RGE ALTI acquis, sans faire de requête réseau :

```bash
python3 tools/acquire_public_world.py terrain --region geo_huveaune \
  --bbox 43.293,5.565,43.300,5.576 --spacing 2 --dry-run
```

Retirer `--dry-run` demande les altitudes à l’IGN et importe seulement une acquisition complète et validée. Les commandes `buildings`, `roads` et `layers` utilisent les capacités WFS courantes ; les imports successifs conservent les autres couches. Une nouvelle acquisition dépend des services distants et peut recevoir une autre édition ; les données préparées pour le jeu restent utilisables localement. La documentation distingue la présence des fichiers, leur résolution et la validation de leur comportement.
