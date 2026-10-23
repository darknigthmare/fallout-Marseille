# FALLOUT Marseille — MISTRAL

## v0.50 · Les routes retrouvées

Le jeu couvre désormais **toute la commune officielle de Marseille, îles comprises**, avec des sources IGN acquises : 291 001 identifiants d’objets bâtiment, 55 449 tronçons routiers, relief communal et littoral. Des façades et intérieurs cohérents sont générés dans les emprises disponibles ; les détails sans document restent explicitement inventés. L’échelle est métrique, avec la précision et les absences propres aux relevés. Voir [la portée et le fonctionnement de cette extension](docs/MARSEILLE_ENTIERE.md).

**[Ancienne distribution Google Drive v0.50](https://drive.google.com/drive/folders/1xE5VpELY64tz5GV9CHHrlsIb_rfahRnQ)** · [Rapport visuel initial](RAPPORT_VISUEL_V0.50.png) · [Installation](docs/INSTALLATION_V050.md) · [Validation communale actuelle](verification/expansion/city/CITY_INTEGRATION.json)

L’extension communale est livrée dans ce dépôt et ses archives vérifiées. Le lien Drive et les rapports visuels initiaux n’ont pas été actualisés pour cette extension.

## Jouer

Python 3 est nécessaire au serveur local. Aucun paquet npm n’est requis pour jouer.

- **Windows :** lancer `LANCER_APP_WINDOWS.bat`.
- **Linux :** `bash LANCER_APP_LINUX.sh`.
- **macOS :** `bash LANCER_APP_MAC.command`.

Le navigateur s’ouvre sur `http://127.0.0.1:8765/index.html`. Au premier lancement depuis GitHub, le serveur prépare les cartes à partir des 24 archives de base, de l’enrichissement d’Aubagne et de l’archive communale, **sans téléchargement**. La plus volumineuse des archives de base est transportée en `.zip.gz` puis reconstituée automatiquement, avec contrôle du SHA-256 du ZIP d’origine. La préparation et la validation du nouvel atlas communal peuvent prendre plusieurs minutes selon l’ordinateur ; attendre l’ouverture du navigateur. Le ZIP initial proposé sur Drive précède cette extension.

```bash
git clone https://github.com/darknigthmare/fallout-Marseille.git
cd fallout-Marseille
python3 tools/serve_game.py
```

Utiliser le lanceur de l’application pour lire les données cartographiques. Le fichier `JOUER_FALLOUT_MISTRAL_v0.50.html` contient le programme ; une ouverture directe en `file://` ne donne pas au navigateur l’accès HTTP requis par le pack.

## Ce qui change

- **Commune entière disponible.** Les requêtes officielles couvrent Marseille et ses îles ; le voisinage est chargé à la demande, avec des caches bornés. Les objets de bordure sont conservés entiers.
- **Façades et intérieurs jouables.** Portes accessibles, niveaux, cours préservées, mobilier adapté à l’usage, contenants finis et retour extérieur persistant. Les annotations documentées et les créations procédurales sont distinguées.
- **Relief et littoral communaux.** Un fond au pas demandé de 25 m et 25 partitions au pas de 10 m complètent les relevés locaux plus fins. La mer suit les géométries IGN et bloque la marche hors supports appropriés.
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

Les essais comprennent des parcours dans Chromium avec **vrais fichiers HTTP et stockage natif**, ainsi que des tests de régression sur bancs synthétiques distincts. Le rapport visuel v0.50 présente les captures de la livraison initiale v0.50 ; il reste historique, comme les rapports v0.49 et antérieurs. La validation des extensions actuelles est détaillée plus bas.

## Vérifier et reconstruire

```bash
python3 tools/build_single.py
node --check src/game.js
python3 tools/validate_real_map_v046.py --require-complete --report verification/v050/LOCAL_DATA_STATE.json
python3 tests/v050/test_installers.py
python3 tests/v050/test_installers.py --offline-integration
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

Cette section décrit la livraison précédente `bb122d0`. L’état courant de Marseille, des façades et des intérieurs figure dans [Marseille entière](docs/MARSEILLE_ENTIERE.md) et son [bilan de validation](verification/expansion/city/CITY_INTEGRATION.json).

Des sources IGN ont réellement été acquises et intégrées autour d’Aubagne, en complément du pack de base :

- **1 404 objets bâtiment et 472 tronçons de route BD TOPO**, sur une emprise d’acquisition demandée de `[43.293, 5.565, 43.300, 5.576]` (sud, ouest, nord, est). Les objets intersectants sont conservés entiers.
- **174 777 altitudes RGE ALTI**, interrogées au pas demandé d’environ **2 m** sur ce secteur.
- **145 396 nœuds MNT LiDAR HD** sur le plus petit extrait `[43.2956, 5.5698, 43.2976, 5.5718]`. Le GeoTIFF source possède des pixels natifs de **50 cm** ; la grille WGS84 du jeu est reprojetée par échantillonnage **au plus proche (`nearest`)**, explicitement déclaré dans sa provenance.

Le pas d’échantillonnage ne garantit pas une précision absolue de 50 cm. Les précisions XY et Z et les dates restent celles des sources. Cette acquisition antérieure n’apportait pas de plans de façades ou d’intérieurs ; l’extension communale actuelle ajoute des créations cohérentes pour les parties inconnues. Ce seul secteur ne constitue pas une reproduction exhaustive de Marseille « 1:1 ». Les formes de toiture prises en charge, à deux pans ou à un pan, explicitement cotées et orientées, disposent d’une collision par faces et de surfaces accessibles ; les bâtiments BD TOPO sans forme de toiture renseignée conservent une enveloppe estimée.

Le conditionnement reproductible des enrichissements utilise `tools/world_source_bundle.py`. Au lancement normal, le serveur restaure **sans réseau** les sources dont l’archive est fournie, avec vérification du reçu et des fichiers, tout en conservant les imports utilisateur déjà valides. L’archive fournie et sa restauration ont été vérifiées. Le [bilan de cette livraison](verification/expansion/real_sources/REAL_SOURCE_INTEGRATION.json) regroupe 397 contrôles de logique et d’outils, 434 contrats hérités et 84 contrôles du parcours natif ; les autres essais et leurs fixtures restent séparés. Les rapports v0.50 et le bilan précédent associé au HTML `8f4619bc…22d5aaa` restent historiques et ne valident pas automatiquement cette livraison enrichie.

Dans le Pip-Boy, **STAT → BIVOUAC** permet de construire un kit portable puis de le déployer sur un sol mesuré, cuisiner, purifier et se reposer avec des réserves finies. **DATA → ENTRAIDE** permet d’apporter des fournitures aux habitants des relais découverts. Le matériel, le camp et les livraisons sont conservés dans la sauvegarde. Les commandes et réglages de manette sont disponibles dans les options.

- [Sources publiques identifiées : IGN, BD TOPO et LiDAR HD](docs/SOURCES_GEOGRAPHIQUES_PUBLIQUES.md)
- [Importer des sources locales et convertir un GeoTIFF](docs/IMPORT_SOURCES_REELLES.md)
- [Fonctionnalités, validation et limites actuelles](docs/ETAT_TERRITOIRE_ET_JEU.md)

Pour préparer le plan du secteur RGE ALTI acquis, sans faire de requête réseau :

```bash
python3 tools/acquire_public_world.py terrain --region geo_huveaune \
  --bbox 43.293,5.565,43.300,5.576 --spacing 2 --dry-run
```

Retirer `--dry-run` demande les altitudes à l’IGN et importe seulement une acquisition complète et validée. Les commandes `buildings`, `roads` et `layers` utilisent les capacités WFS courantes ; les imports successifs conservent les autres couches. Une nouvelle acquisition dépend des services distants et peut recevoir une autre édition ; les données préparées pour le jeu restent utilisables localement. La documentation distingue la présence des fichiers, leur résolution et la validation de leur comportement.
