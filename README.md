# FALLOUT Marseille — MISTRAL

## v0.50 · Les routes retrouvées

Le jeu dispose du **pack géographique complet prévu par son manifeste** : 5 884 coordonnées vectorielles et huit grilles de relief. La sortie du sas rejoint le territoire réel d’Aubagne sur un emplacement dégagé. Une balise relie cet extérieur aux ateliers de Mireille et à la campagne existante.

**[Téléchargements Google Drive v0.50](https://drive.google.com/drive/folders/1xE5VpELY64tz5GV9CHHrlsIb_rfahRnQ)** · [Rapport visuel](RAPPORT_VISUEL_V0.50.png) · [Installation](docs/INSTALLATION_V050.md) · [Limites vérifiées](docs/KNOWN_LIMITATIONS_V0.50.md)

## Jouer

Python 3 est nécessaire au serveur local. Aucun paquet npm n’est requis pour jouer.

- **Windows :** lancer `LANCER_APP_WINDOWS.bat`.
- **Linux :** `bash LANCER_APP_LINUX.sh`.
- **macOS :** `bash LANCER_APP_MAC.command`.

Le navigateur s’ouvre sur `http://127.0.0.1:8765/index.html`. Au premier lancement depuis GitHub, le serveur prépare les cartes à partir des 24 archives fournies, **sans téléchargement**. La plus volumineuse est transportée en `.zip.gz` puis reconstituée automatiquement, avec contrôle du SHA-256 du ZIP d’origine. Cette préparation peut prendre environ une minute selon l’ordinateur. Le ZIP « JEU_COMPLET » proposé sur Drive contient les cartes déjà extraites.

```bash
git clone https://github.com/darknigthmare/fallout-Marseille.git
cd fallout-Marseille
python3 tools/serve_game.py
```

Utiliser le lanceur de l’application pour lire les données cartographiques. Le fichier `JOUER_FALLOUT_MISTRAL_v0.50.html` contient le programme ; une ouverture directe en `file://` ne donne pas au navigateur l’accès HTTP requis par le pack.

## Ce qui change

- **Carte réelle disponible localement.** Les fichiers sont validés, les vides officiels portent leur preuve et les huit grilles de relief sont incluses.
- **Sortie de campagne reliée à la carte.** Le sas propose la sortie géographique et un accès direct explicitement nommé « scène narrative ». La balise des ateliers permet de retrouver Mireille ; la sortie des ateliers retrouve le point géographique enregistré, y compris après recharge.
- **Voyage rapide vers les lieux découverts.** Dans le Pip-Boy, ouvrir **MAP → LIEUX ET VOYAGES**, sélectionner un lieu, préparer puis confirmer le voyage. L’arrivée est contrôlée contre le relief, l’eau, les murs et une marge de marche libre. Le temps avance seulement après réussite.
- **Continuer reprend la sauvegarde la plus récente.** La sauvegarde courante est comparée aux autosauvegardes et emplacements manuels. Les données des versions antérieures restent migrables.
- **Installation plus robuste.** Gzip borné, contrôle des archives, reprise, conservation des fichiers précédents en cas d’erreur et repli direct vers l’IGN pour le relief. Le mode `--offline` interdit le réseau.
- **Menu accessible sur les petites fenêtres.** Les boutons restent atteignables ; l’état des cartes provient de l’audit du serveur local.

Les 248 lieux du catalogue, les rencontres persistantes, les blessures, les dépouilles à butin fini, les intérieurs et le lore des versions précédentes sont conservés. Les bâtiments et routes communs restent attachés à une scène extérieure persistante lorsque la fenêtre de tuiles se déplace.

## Données et portée

Le pack comprend **4 557 fichiers PBF**, **1 327 coordonnées officiellement vides**, **8 grilles de 161 × 161 points**, **174 944 altitudes valides** et **32 424 points sans mesure**. L’audit ne relève aucun fichier attendu manquant ou invalide. Une grille complète peut contenir des points sans mesure ; le jeu conserve ces absences.

Les emprises et routes reposent sur les sources OpenStreetMap et cadastrales, le relief sur un échantillonnage de données IGN. Les décors et bâtiments sont interprétés par le jeu ; les hauteurs de toiture non documentées restent estimées. La campagne historique utilise encore des scènes narratives distinctes, clairement indiquées. Il ne s’agit pas d’une reproduction photoréaliste ni d’un relevé de chaque rue validé à pied.

Les essais actuels comprennent des parcours dans Chromium avec **vrais fichiers HTTP et stockage natif**, ainsi que des tests de régression sur bancs synthétiques distincts. Le rapport visuel v0.50 présente les captures de cette exécution. Les anciens rapports v0.49 et antérieurs restent historiques.

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
