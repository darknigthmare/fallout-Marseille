# Installer FALLOUT : MISTRAL v0.50 — poursuite du 1er novembre 2026

La version v0.50 fournit les cartes locales nécessaires au parcours géographique : **5 884 coordonnées vectorielles**, dont 4 557 PBF non vides et 1 327 réponses officiellement vides, ainsi que **huit grilles de relief**. Le jeu se lance avec un serveur local Python et un navigateur compatible WebGL. Python 3.11 ou plus récent est recommandé ; Node.js et Playwright servent au développement et aux tests, pas au jeu compilé. [Audit des fichiers livrés](../verification/v050/LOCAL_DATA_STATE.json)

L’extension actuelle est fournie dans le dépôt GitHub ; la distribution Drive décrite ci-dessous reste celle de la livraison initiale et n’a pas été actualisée pour cette poursuite. Le serveur restaure aussi l’enrichissement d’Aubagne et du nord et du sud de Marseille, l’archive communale et les **six ZIP de relief natif**, hors réseau, avant d’ouvrir le navigateur. Cette validation et l’extraction peuvent prendre plusieurs minutes. Voir [Marseille entière](MARSEILLE_ENTIERE.md).

Le nouveau [relief précis](RELIEF_PRECIS.md) couvre **12 km² centraux**, douze dalles et 48 morceaux au pas natif de 0,50 m Lambert-93/NGF-IGN69. Il ajoute **157 896 379 octets d’archives (environ 150,58 Mio)** et **192 328 140 octets extraits (environ 183,42 Mio)** ; ces tailles s’ajoutent aux cartes précédentes, conservées ailleurs. Prévoir l’espace pour les archives et les données extraites. Il ne s’agit pas d’un LiDAR de 0,50 m sur toute la commune.

Les deux fenêtres autour du Vélodrome et de Borély totalisent **384 832 nœuds MNT** ; celles de l’Estaque et de Saint-Antoine ajoutent **206 240 nœuds**. Ces fenêtres sont reprojetées et rééchantillonnées au plus proche depuis des GeoTIFF natifs de 0,50 m sur un pas WGS84 demandé de **1 m**. L’archive d’enrichissement active les fournit avec le lot Aubagne conservé ; elles restent distinctes des 12 km² de treillis central natif. Les surfaces MNS de Major/Garde, de la chapelle de la Vieille Charité et du contexte du Pharo sont fournies en maillage attribué dans `data/map_pack/landmark_surfaces/` ; les quatre TIFF sources restent dans le cache d’acquisition externe. Le jeu n’a besoin ni de ces TIFF originaux ni de bibliothèques géographiques supplémentaires pour jouer. [Relief nord](RELIEF_NORD_MARSEILLE.md) · [Relief sud](RELIEF_SUD_MARSEILLE.md) · [Surfaces des monuments](SILHOUETTES_MNS.md).

## 1. Choisir l’archive

Les livraisons de cette version sont regroupées dans le [dossier Google Drive v0.50](https://drive.google.com/drive/folders/1xE5VpELY64tz5GV9CHHrlsIb_rfahRnQ). Le projet est également disponible dans le [dépôt GitHub](https://github.com/darknigthmare/fallout-Marseille).

| Archive | Contenu et usage |
|---|---|
| FALLOUT_MISTRAL_v0.50_JEU_COMPLET.zip | Jeu compilé, lanceurs, cartes déjà extraites, relief, notices et preuves v0.50. C’est le choix pour jouer. |
| FALLOUT_MISTRAL_v0.50_PROJET_COMPLET.zip | Projet complet, sources, tests, historique, cartes extraites et 24 archives de données permettant leur réinstallation hors réseau. |

L’archive du jeu contient les mêmes données géographiques utiles à l’exécution. Elle omet les sources, les tests, l’historique et les 24 ZIP de données en double. Le dossier de livraison fournit les empreintes et, lorsque nécessaire, les fichiers de recomposition. Les résultats de publication distante se vérifient dans le dossier de livraison ; les rapports locaux ne constituent pas à eux seuls une attestation d’envoi.

### Si le projet complet est proposé en plusieurs parties

Les fichiers terminés par <code>.zip.001</code>, <code>.zip.002</code>, etc. sont les morceaux d’une même archive. Téléchargez **toutes les parties**, ainsi que <code>ARCHIVE_PARTS.json</code>, <code>RECONSTRUIRE_ARCHIVE.py</code> et le lanceur de recomposition adapté à votre système. Placez-les dans un même dossier.

Lancez le programme de recomposition fourni, ou utilisez :

~~~bash
python3 RECONSTRUIRE_ARCHIVE.py
~~~

Sous Windows, utilisez <code>python</code> si cette commande désigne votre installation de Python. La recomposition vérifie les empreintes de chaque partie, le SHA-256 final et l’intégrité CRC du ZIP. Elle refuse d’écraser une archive différente déjà présente. Décompressez ensuite le ZIP reconstitué ; il ne faut pas décompresser séparément les fichiers <code>.001</code> et suivants.

## 2. Décompresser puis lancer

Décompressez l’archive dans un dossier où vous pouvez écrire. Conservez ensemble le HTML, les lanceurs et les dossiers fournis, en particulier <code>data/</code> et <code>tools/</code>.

| Système | Lanceur |
|---|---|
| Windows | Double-cliquer sur <code>LANCER_APP_WINDOWS.bat</code> |
| Linux | Exécuter <code>sh ./LANCER_APP_LINUX.sh</code> dans le dossier du jeu |
| macOS | Ouvrir <code>LANCER_APP_MAC.command</code>, ou exécuter <code>sh ./LANCER_APP_MAC.command</code> |

Le lanceur démarre le serveur local et ouvre le jeu. Gardez sa fenêtre ouverte pendant la partie. Pour lancer le serveur manuellement depuis le dossier du jeu :

~~~bash
python3 tools/serve_game.py
~~~

L’adresse par défaut est **http://127.0.0.1:8765/**. Si elle est occupée, choisissez un autre port :

~~~bash
python3 tools/serve_game.py --port 8766
~~~

Le serveur peut aussi être lancé sans ouvrir automatiquement le navigateur :

~~~bash
python3 tools/serve_game.py --no-browser
~~~

Le premier lancement depuis un clone GitHub peut extraire les cartes déjà fournies dans le projet. Le dépôt transporte **24 archives logiques : 23 ZIP et une archive <code>base_00060_100.zip.gz</code>**. L’installateur décompacte automatiquement cette enveloppe gzip avec une taille bornée, puis vérifie le SHA-256 du ZIP original avant d’en extraire les données. Aucune conversion manuelle n’est nécessaire.

Les six ZIP natifs et leur manifeste se trouvent dans <code>data/map_pack/precision_archives/</code>. Le serveur les vérifie puis prépare les fichiers <code>data/map_pack/precise/</code>, sans télécharger de GeoTIFF. Pour relancer uniquement cette préparation locale :

~~~bash
python3 tools/precise_terrain_sources.py --prepare
~~~

Un fichier extrait altéré ou une empreinte incorrecte produit un diagnostic explicite ; ne pas remplacer les sources manquantes par des fichiers vides. Les anciennes cartes restent disponibles hors du support natif. Pour relancer la restauration des enrichissements fournis :

~~~bash
python3 tools/world_source_bundle.py install
~~~

Cette commande ajoute les régions fournies absentes d’une installation valide et conserve les imports utilisateur déjà présents. Un import utilisateur associé à `geo_marseille` ou `geo_marseille_commune` garde sa priorité et n’est pas remplacé automatiquement par les fenêtres du sud ou du nord. Le panneau des sources décrit les données effectivement actives.

Cette préparation utilise uniquement les archives locales ; le lancement ne déclenche pas d’installation réseau implicite. Le <code>PROJET_COMPLET</code> distribué sur Drive conserve les **24 ZIP originaux**, dont <code>base_00060_100.zip</code>. Dans l’archive <code>JEU_COMPLET</code>, les cartes sont déjà extraites. [Préparation locale](../tools/prepare_local_pack_v050.py)

Utilisez le serveur local pour le parcours géographique et les sauvegardes vérifiés. L’ouverture du HTML seul avec une adresse <code>file://</code> n’est pas le parcours validé par la QA native.

## 3. Vérifier les cartes dans le menu

Ouvrez **Cartes & territoire**. Pour le jeu complet livré, le statut attendu est :

- **5 884 / 5 884 coordonnées** ;
- **8 / 8 grilles de relief** ;
- **Cartes locales prêtes**.

Ces compteurs décrivent le **socle historique**. L’installation actuelle ajoute les acquisitions communales et le lot natif précis ; leur provenance et leur périmètre sont distincts. L’audit natif central est aussi disponible sur **http://127.0.0.1:8765/__mistral/precise-terrain**. Les enrichissements d’Aubagne, du sud et du nord apparaissent dans **http://127.0.0.1:8765/__mistral/world-sources** ; utilisez le port réellement choisi.

Le statut provient d’un audit du disque par le serveur actif. Les coordonnées officiellement vides sont accompagnées d’une preuve explicite ; un fichier vide arbitraire n’est pas accepté comme une donnée valide.

Une vérification détaillée peut être relancée depuis le dossier du jeu :

~~~bash
python3 tools/validate_real_map_v046.py --require-complete --report verification/v050/LOCAL_DATA_STATE.json
~~~

Le nom et la version interne <code>v046</code> identifient le validateur conservé. Son résultat porte sur les fichiers effectivement présents dans cette installation v0.50.

### Restaurer les fichiers locaux si nécessaire

Dans le projet complet ou un clone contenant <code>data/map_pack/archives/</code>, la réinstallation utilise les 24 archives fournies. Le transport gzip de l’une d’elles sur GitHub est pris en charge automatiquement :

~~~bash
python3 tools/install_local_pack_v041.py --offline --workers 3
~~~

Cette commande ne contacte aucun relais. L’installation hors réseau dans un dossier vide a été vérifiée avec comparaison des 5 884 coordonnées, des 1 327 preuves de vide et des huit grilles. [Preuve d’installation](../verification/v050/INSTALL_OFFLINE.json)

Le chemin de transport GitHub a aussi été installé depuis une copie isolée où <code>base_00060_100.zip</code> est absent et où seul <code>base_00060_100.zip.gz</code> est fourni. Les mêmes données de sortie ont été comparées, avec zéro tentative réseau. [Preuve du transport gzip](../verification/v050/INSTALL_OFFLINE_GZIP.json)

L’archive <code>JEU_COMPLET</code> ne conserve pas ces ZIP en double. Si des données de cette archive ont été supprimées ou endommagées, réextrayez l’archive livrée, ou récupérez le projet complet avant d’utiliser l’installateur hors réseau.

Les installateurs conservent aussi leurs chemins de téléchargement explicites. Leur emploi demande une connexion aux sources configurées ; la disponibilité future de ces services n’est pas garantie par cette livraison. Le lancement normal avec les fichiers fournis n’en dépend pas.

## 4. Commencer la campagne et voyager

Choisissez **Nouvelle campagne**, créez le personnage et suivez le prologue. Au sas, **Sortir vers Aubagne** charge l’extérieur géographique. La balise **Ateliers d’Aubagne — poursuivre la campagne** mène à la scène narrative où se trouve Mireille ; le retour rejoint le point géographique conservé.

Le choix **Rejoindre directement les ateliers — scène narrative** permet également d’entrer dans la campagne historique depuis le sas. Cette scène est un décor construit pour le récit, identifié comme tel à l’écran.

Pour un voyage rapide, ouvrez le Pip-Boy puis **MAP → LIEUX ET VOYAGES**. Sélectionnez un lieu découvert, préparez le voyage et confirmez la durée annoncée. Le départ exige un extérieur praticable et l’absence de danger proche ; la destination est validée avant le déplacement. Le temps annoncé est ajouté lorsque le voyage aboutit. [Contrats ciblés du voyage](../verification/v050/QA_POI_TRAVEL.json) · [Deux voyages natifs](../verification/v050/NATIVE_REAL_MAP.json)

La vue FPS présente treize profils stylisés dans neuf familles et huit alimentations de recharge. Maintenez X, le clic droit capturé, Visée ou LT sur une manette standard pour présenter l’arme dans l’axe. Le HUD suit les impacts, neutralisations, pertes de PV et délai réel de recharge ; ses préférences et la réduction des mouvements se règlent dans Options. Les poignets peuvent encore passer derrière le HUD translucide. [Vue FPS](VUE_FPS.md) · [HUD](HUD_FPS.md).

Dans les intérieurs admissibles, E utilise les services et ouvre les [dépôts de fournitures](INTERIEURS_USAGES.md). Les huit dossiers existants restent dans DATA → RELAIS ET DOSSIERS ; deux [suites des Communes/Gilets](LORE_CONTINUITE.md) demandent une remise au second relais nommé puis un retour au donneur. E ouvre aussi les [distributeurs Nuka-Cola](DISTRIBUTEURS_NUKA_COLA.md), à réparer avec deux ferrailles et un circuit avant les achats à stock fini. Les mines se consultent dans INV → MINES puis se posent avec P en jeu. [Commandes](CONTROLES.md).

## 5. Retrouver une sauvegarde

**Continuer** sélectionne la sauvegarde valide la plus récente parmi le courant, les emplacements, l’autosauvegarde et les versions compatibles. Un rechargement réel de la page après deux voyages a retrouvé la position géographique, la progression et les lieux découverts. [Contrats de sélection](../verification/v050/QA_CONTINUE_SAVE.json) · [Parcours natif](../verification/v050/NATIVE_REAL_MAP.json)

Le navigateur associe son stockage à une origine : navigateur, profil, protocole, hôte et port. Reprenez avec la même adresse locale et le même profil. Une adresse <code>localhost</code> et une adresse <code>127.0.0.1</code>, ou deux ports différents, ne partagent pas automatiquement leurs sauvegardes.

## Développement et reproduction des preuves

Dans le projet complet, les dépendances de développement sont listées dans <code>requirements-dev.txt</code>. Les tests Python utilisent Playwright ; les contrats JavaScript utilisent Node.js.

~~~bash
python3 -m pip install -r requirements-dev.txt
python3 -m playwright install chromium
python3 tools/build_single.py
python3 tools/build_single.py --check
python3 tools/check_v050.py
python3 tests/v050/poi_travel.py
python3 tests/v050/campaign_map.py
python3 tests/v050/continue_save.py
python3 tests/v050/test_installers.py
python3 tests/v050/native_real_map.py
~~~

Le contrôle `tools/build_single.py --check` compare les quatre sorties générées sans les réécrire : `src/game.js`, les deux HTML jouables et `sw.js`. Le nom du cache hors ligne dérive des seize premiers caractères du SHA-256 du HTML ; pour le programme intégré courant, il vaut `fallout-mistral-v050-c0f13de317f1678c`. La vérification des contrats hérités utilise la même règle plutôt qu’un numéro de cache fixe.

Les pilotes Chromium acceptent <code>CHROMIUM_PATH</code>. Le pilote natif ouvre le serveur local et utilise les fichiers installés ; son mode de diagnostic <code>--allow-debug-entry</code> ne doit pas être utilisé pour une validation finale du raccord de campagne.

L’outil du rapport visuel initial v0.50 travaille à partir de ses **preuves historiques identifiées**, sans relancer de navigateur :

~~~bash
python3 tools/report_v050.py
~~~

Pillow et les polices DejaVu Sans / Sans Mono sont requis pour le PNG. Si les polices ne sont pas trouvées automatiquement, ajoutez <code>--font-dir /chemin/vers/les/polices</code>. L’outil vérifie les totaux, les SHA du programme et les captures originales avant d’écrire le rapport. Il distingue l’empreinte du HTML canonique de celle du test de voyage instrumenté. Ce rapport initial ne remplace pas le bilan d’intégration des extensions actuelles.

Le [bilan courant](../verification/expansion/continuation_20261101_integrated/CONTINUATION_INTEGRATION.json) identifie le HTML intégré `c0f13de317f1678cd20a2ed9ea3f2ee687054eb67f3815026357707828ff77b1`, qui conserve les correctifs routiers et de chargement de `7ab5043`. L’[état de production](STATUT_PRODUCTION.md) présente les résultats par méthode ; les scripts, captures originales, sorties réelles de processus et aides déclarées sont rattachés à ce programme. Les comparaisons de sources, modèles, parcours assistés et entrées simulées gardent leur périmètre ; leur somme ne représente pas autant de parties humaines. Les essais interrompus et ceux d’autres HTML restent exclus du résultat courant. Le [bilan avant intégration](../verification/expansion/continuation_20261101/CONTINUATION_INTEGRATION.json), 3 310 contrôles et 76 captures sur `98a78a1c…`, reste historique.

La livraison `29df190` conserve ses [2 892 contrôles descriptifs et 55 captures](../verification/expansion/immersion/IMMERSION_INTEGRATION.json) sur le HTML `844376c014575111f268f292c8307bb3f47ac33629604406f5e0da00104c5a34`. Le [bilan `f4a7337`](../verification/expansion/wasteland/WASTELAND_INTEGRATION.json), **2 887 contrôles et 62 captures** sur `ed6e4103…`, et le [bilan de précision](../verification/expansion/precision/PRECISION_INTEGRATION.json), **2 324 contrôles et 42 captures**, conservent leurs propres versions. Le rapport visuel initial v0.50 et les archives Drive restent antérieurs aux extensions actuelles. Les sources métriques, l’art stylisé et les intérieurs inventés ne certifient pas Marseille intégralement en 1:1 ; les API simulées ne certifient pas du matériel physique.

Consultez aussi les [limites connues](KNOWN_LIMITATIONS_V0.50.md), la [provenance](PROVENANCE_V050.md) et le [rapport visuel autonome](../RAPPORT_VISUEL_V0.50.html).
