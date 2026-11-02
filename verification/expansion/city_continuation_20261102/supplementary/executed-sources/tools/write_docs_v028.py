from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];D=R/'docs';D.mkdir(exist_ok=True)
def out(name,text):(D/name).write_text(text.strip()+'\n',encoding='utf-8')
(R/'README_FR.md').write_text('''# FALLOUT : MISTRAL — v0.28.0
## Tenir debout

Prototype de fan non officiel. Livraison locale : aucun dépôt ou déploiement distant modifié.

## Jouer
Décompresser l’archive sur ordinateur et ouvrir `JOUER_FALLOUT_MISTRAL_v0.28.html` dans un navigateur récent. Les lanceurs Windows et Linux/macOS ouvrent le même fichier ; aucun téléchargement, compte ou serveur n’est nécessaire au contenu scénarisé.

Le bouton **Soins, lampe & circuits · exploration séparée** commence à l’Annexe des Veilleurs. Une confirmation protège la campagne et les clés des versions antérieures ; seule l’exploration v0.28 précédente peut être remplacée. Le personnage commence sans traumatisme, avec une attelle et une trousse, deux armes et la tenue A-03.

**Tab** : Pip-Boy. **STAT → ÉTAT** : six régions et soins ciblés. **STAT → SURVIE** : poids/besoins facultatifs. **L** : lampe portable. Approcher Sofia et interagir avec **E** pour l’enquête et le médecin. Trouver la cassette près de son poste pour ouvrir **RADIO → JEUX**.

La carte réelle complète n’est pas incluse. Les anciens intérieurs et cours sont des lieux fictifs ; le mode géographique reste incomplet et n’est pas le point de départ conseillé.

## Livré
Six régions corporelles persistantes avec effets sur le déplacement, le saut, la précision, la mêlée, le rechargement et la récupération des PA. Soins ciblés, médecin avec devis, deux recettes ajoutées aux dix-huit existantes. Lumière locale appliquée aux surfaces, avec occultation échantillonnée. Besoins et poids facultatifs raccordés aux consommables et au repos. Holodisque-jeu original à six circuits, et enquête La veille des soins à deux conclusions.

Le V.A.T.S. directement sur les ennemis, les quêtes, dialogues, compagnons, commerces, fouilles et interfaces précédentes sont conservés.

## Limites
Rendu et personnages procéduraux. Pas de doublage. Pas d’animation de poignet 3D ni de boiterie individualisée. Les traumatismes reçus sont attribués par famille d’attaque, pas par une simulation de balles contre six hitboxes du joueur. Éclairage échantillonné, pas de shadow maps/PBR. Le soigneur de cette passe traite les traumatismes uniquement, pas les PV, radiations ou infections.

Tests : Chromium logiciel. Origines localhost/fichier bloquées dans l’environnement ; HTML exact injecté pour essais, stockage natif opaque refusé puis adaptateur mémoire explicitement déclaré. Pas de certification GPU/iPhone, ni de parcours humain complet de toutes les quêtes.

## Sources et vérifications
`python3 tools/build_single.py` reconstruit le monofichier. `node --check src/game.js` contrôle la syntaxe. `python3 tools/run_all_qa_v028.py` exécute les suites ciblées (Python, Playwright et Chromium requis pour les tests seulement). `python3 tools/capture_v028.py` puis `python3 tools/make_report_v028.py` génèrent les captures et rapports.

Les 89 références v0.27 conservées se trouvent dans `history/v0.27_source/`, avec leurs empreintes sous `data/BASE_V027.json`. Le monofichier source de cette version est conservé dans `history/v0.27_reference.html`.
''',encoding='utf-8')
(R/'LANCER_JEU.bat').write_text('@echo off\nstart "" "%~dp0JOUER_FALLOUT_MISTRAL_v0.28.html"\n',encoding='utf-8')
(R/'LANCER_JEU.sh').write_text('''#!/usr/bin/env sh
set -eu
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if command -v xdg-open >/dev/null 2>&1; then xdg-open "$DIR/JOUER_FALLOUT_MISTRAL_v0.28.html"
elif command -v open >/dev/null 2>&1; then open "$DIR/JOUER_FALLOUT_MISTRAL_v0.28.html"
else printf '%s\\n' "Ouvrir $DIR/JOUER_FALLOUT_MISTRAL_v0.28.html dans votre navigateur."
fi
''',encoding='utf-8');(R/'LANCER_JEU.sh').chmod(0o755)
pkg=json.loads((R/'package.json').read_text());pkg['version']='0.28.0';pkg['scripts'].update(qa='python3 tools/run_all_qa_v028.py',captures='python3 tools/capture_v028.py',report='python3 tools/make_report_v028.py');(R/'package.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
out('CONTENU_V0.28.md','''# v0.28 — Tenir debout

## 1. Traumatismes du personnage
Six régions : tête, torse, bras gauche/droit, jambe gauche/droite. Chaque intégrité va de 0 à 100. Au-dessus de 70, la région n’ajoute pas de pénalité ; sous 70, son effet augmente progressivement ; de 0 à 25, l’interface indique une atteinte sévère.

Le calcul suit les PV effectivement perdus après la protection. Un impact significatif atteint une seule région, attribuée selon la famille d’attaque. Les petites attaques de faune privilégient les jambes ; les attaques ordinaires alternent les régions. Cette attribution n’est pas une simulation anatomique de l’impact d’une balle. Les micro-dégâts et états continus ne cassent pas un nouveau membre à chaque tick.

- Tête : jusqu’à −14 points de précision V.A.T.S. et dispersion accrue en tir libre. Une cible bloquée reste à 0 %.
- Torse : récupération naturelle des PA jusqu’à 45 % du rythme normal.
- Deux bras fortement atteints : temps de rechargement jusqu’à ×1,65 et mêlée jusqu’à 72 % des dégâts. Une seule atteinte a un effet partiel.
- Deux jambes fortement atteintes : mouvement jusqu’à 58 %. Le saut est interdit si les deux sont à 25 ou moins ; soigner l’une rétablit le saut.

Les dégâts ennemis localisés et leur V.A.T.S. restent les systèmes précédents. Aucune animation individuelle de boiterie ou de poignet n’est ajoutée.

## 2. Soigner, sans tout effacer
STAT → ÉTAT possède un schéma sélectionnable, six boutons et les effets calculés.

Le Stimpak ciblé consomme un exemplaire pour rendre 35 points à une région, sans rendre des PV. L’usage standard dans AIDE garde son rôle de soin général. Une attelle rétablit un bras ou une jambe à 100 ; une trousse rétablit une région quelconque à 100. Ces deux dernières actions exigent l’absence de danger proche. Le Stimpak ciblé demeure possible dans une situation dangereuse.

Aucun débit si la région est intacte, si le consommable manque ou si l’attelle vise tête/torse. La prestation de Sofia se fait à son poste, après devis et confirmation. Elle restaure les régions, mais ne traite pas les PV, radiations ou infections. Une modification du bilan, une sortie du boîtier ou un changement de scène invalide le devis.

Deux recettes complètent les 18 existantes : attelle (3 tissus, 2 ferrailles), trousse (4 tissus, 4 produits chimiques, 1 eau). Atelier physique et sécurité requis ; pas d’XP pour la fabrication.

## 3. Lampe locale et visibilité
L et le bouton du HUD partagent le contrôle avec le Pip-Boy. La lampe agit dans les scènes sur les surfaces à proximité du poignet virtuel, avec décroissance et contrôle de visibilité. Son phosphore suit vert/ambre/blanc. Aucune consommation de batterie n’est simulée.

Le moteur logiciel calcule la lumière par faces et subdivise certaines surfaces proches. Le chemin WebGL reçoit des uniforms et des morceaux échantillonnés, mais son rendu sur pilote matériel n’a pas été validé ici. Les masquages se font contre les colliders, pas par une carte d’ombres exhaustive : les ombres fines et la précision du contact restent limitées.

Une menace proche et avec ligne de vue peut repérer plus facilement le joueur allumé. Éteindre la lampe ne supprime pas sa mémoire de l’alerte. Les dialogues et interfaces suspendent les actions normales.

## 4. Charge et besoins facultatifs
Le total inclut les cartouches présentes dans les chargeurs des armes détenues, sans recompter la réserve. Les poids restent des valeurs de jeu par familles. Surcharge et besoins sont des options ; pas d’objet jeté automatiquement ni de pénalité ajoutée par défaut aux anciennes collections.

Les besoins progressent en jeu actif, pas dans le boîtier. Eau : −35 soif ; nourriture : −25 faim ; ration : −40 faim. Avec besoins actifs, manger à PV pleins reste pertinent. Une heure de repos payé retire 30 de fatigue, sans effacer les blessures, radiations ou infections. Les variations après consommation sont sauvegardées, pas seulement affichées.

## 5. Aiguilleur Mistral
Une cassette double à trouver près de Sofia débloque RADIO → JEUX et un message de cinq segments sous-titrés. Le jeu de raccordement original contient six grilles 5×5 composées à la main. Les conduites tournent de 90 degrés ; une propagation de signal vérifie les connexions réciproques, fuites et sortie.

Les bornes et isolants ne sont pas tournables. Indices sans rotation automatique. Réinitialisation confirmée, record conservé. Disposition et scores enregistrés par circuit ; aucun gain de capsules, ressources ou expérience pour le personnage. Les circuits sont tous accessibles après découverte de la cassette, sans grind ni minuterie.

## 6. La veille des soins
Enquête facultative entre Sofia, son annexe et la galerie des Archives de la Traverse. Le plan doit être récupéré physiquement à l’étage, puis le départ L-4 identifié et consigné. L’ancienne intervention C-2 de chambre froide conserve ses étapes et ses propres résultats.

Deux accords : remise en service permanente de la pharmacie (3 ferrailles, 2 circuits), ou organisation mobile sans réparer le circuit fixe. Le premier modifie réellement l’éclairage de la partie ouest ; le second la laisse sombre. Chacun apporte 50 capsules et 60 XP une seule fois. Le fixe remet une trousse ; le mobile remet deux attelles. Les choix ne sont pas interchangeables après validation.

Deux scènes textuelles propres par accord, soit quatre scènes ; pas de voix enregistrée. Relire n’accorde aucune récompense. Le suivi est intégré à DATA → QUÊTES sans abandonner les dossiers précédents.

## Limites non résolues
Aucune carte officielle, aucun MNT, aucune fusion régionale nouvelle. Pas de démembrement ou de ragdoll du joueur, pas de blessures 3D anatomiques ni de doublage. Le contenu est ajouté aux lieux existants ; pas de nouvelle commune inventée en guise de données réelles.
''')
out('STATUT_PRODUCTION.md','''# Statut réel — v0.28

## Base et livraison
Base : ZIP v0.27 « Le terminal au poignet », SHA-256 `49d8c745ac50dc58993bfe43284528053e18282f4d0f820b8ba167f4bd107242`. Des messages antérieurs présentent d’autres variantes sous le même numéro ; cette passe ne prétend pas les fusionner. Sources et outils réellement récupérés, puis modifiés localement. Aucun dépôt GitHub ni déploiement Vercel modifié.

## Réalisé
Traumatismes persistants du personnage, effets réels sur le contrôleur et le combat, consommables ciblés, deux recettes, consultation avec devis. Éclairage local rendu, option et visibilité ennemie. Poids des chargeurs et besoins raccordés. Un jeu d’holodisque à six grilles. Une quête physique à deux conclusions, quatre textes d’épilogue et une bande de cinq segments. Pip-Boy étendu sans supprimer ses fonctions précédentes.

## Vérifié et non vérifié
Tests et captures dans Chromium avec rendu logiciel. Les captures ont des caméras et certains états préparés, indiqués dans le rapport. Les circuits sont réellement résolus par clics ; le plan de quête est rejoint par le contrôleur de mouvement. Les 86 anciennes instances sont chargées structurellement dans la régression, pas toutes parcourues par un joueur humain.

Origines localhost et fichier bloquées par l’administrateur de l’environnement. Refus réel du stockage opaque testé, puis adaptateur mémoire déclaré pour les écritures réussies. Pas de certification de stockage natif sur ordinateur personnel ou iPhone, ni de GPU matériel. L’export JSON historique est exercé dans la régression.

## Limites graphiques
Interface de Pip-Boy 2D CSS/SVG et représentations procédurales existantes. Aucun modèle de poignet 3D, doublage, nouvelle animation unique ou ombre dynamique complète. Les lésions reçues sont attribuées par famille d’attaque, pas par six hitboxes du corps du joueur. Les surfaces éclairées sont échantillonnées ; artefacts de précision possibles au bord des colliders et sur les grands volumes.

## Carte et périmètre
Aucune tuile officielle ni relief réel ajouté. Le chantier géographique reste incomplet. Les scènes historiques sont fictives et le mode strict ne les présente pas comme une vraie reconstruction cadastrale.

## Complétude
Cette version complète une partie des fonctionnalités demandées ; ce n’est pas un jeu AAA achevé. Les animations, intérieurs et scénarios historiques nécessitent toujours des passes individuelles. Les fonctions génériques communes ne signifient pas que chaque arme ou ennemi possède un asset unique.
''')
out('MIGRATION_V027_V028.md','''# Migration v0.27 → v0.28

Nouvelles clés : `fallout_mistral_save_v028`, `fallout_mistral_sandbox_v028`, `fallout_mistral_settings_v028`. Les lectures cherchent ensuite les versions précédentes, avec v027 prioritaire ; les clés sources ne sont ni supprimées ni remplacées.

Le bloc `v028` ajoute les six intégrités initialisées à 100, l’état éteint de la lampe, un historique borné, la quête non engagée et le jeu non acquis. Aucun objet de soin, preuve ou récompense n’est créé par la migration. Seul le départ d’exploration volontaire possède l’équipement d’essai annoncé.

Les valeurs numériques et tableaux sont bornés ; régions et niveaux inconnus ignorés. Le compteur de coups et l’historique sont limités. La conclusion, les scores, orientations et blessures existants sont préservés par l’import. Les besoins invalides sont nettoyés.

Les préférences des versions v018–v027 sont maintenant recherchées avant celles de v017 lorsque la clé courante manque. Les préférences du Pip-Boy continuent d’appartenir à la sauvegarde. Activer les besoins ou l’encombrement reste facultatif.

Les devis médicaux et caches de lumière sont transitoires : pas de validation d’un ancien devis après transition ou import. Les points de retour et les états des autres quêtes restent ceux des modules existants.

Exportez la partie existante avant remplacement du fichier sur votre machine. L’import JSON est disponible dans DATA → SYSTÈME. Les essais d’écriture réussie de cette livraison utilisent un adaptateur mémoire déclaré ; ils ne certifient pas un navigateur matériel précis.
''')
out('ARCHITECTURE_V0.28.md','''# Architecture des ajouts v0.28

`tools/build_single.py` assemble le noyau historique et les modules ordonnés. Le jeu distribué contient son JS et son CSS ; aucune bibliothèque réseau n’est chargée pour les scènes narratives.

- `src/v028/00_state.js` : schéma, migration, seuils, objets, masse des chargeurs et recettes.
- `01_body.js` : traumatismes reçus, contrôleur, effets de combat, soins et devis.
- `02_light.js` : source portable, couleurs, occultation, subdivision limitée, logiciel et branche WebGL.
- `03_hologame.js` : six chemins 5×5, rotation des masques, propagation, fuites, scores et interface.
- `04_story.js` : Sofia, circuit L-4, plan à l’étage, conclusions, récompenses et contenu de scène.
- `05_interface.js` : schéma de santé, survie, commandes, HUD, sauvegarde et démarrage séparé.
- `style.css` : layouts et contrastes des nouveaux écrans.

Deux points d’intégration au rendu sont volontairement modifiés dans les sources héritées : `src/v021/02z_renderer.js` envoie la couleur des faces à l’échantillonneur local ; `src/patches/01_geometry.js` renseigne les uniforms et la visibilité par pièce sur le chemin WebGL. Les fichiers de référence v027 restent intacts dans l’historique.

Pas de nouvelle connexion distante, de services payants ou de collecte de données personnelles. La sélection anatomique du joueur est une représentation d’état ; les volumes de V.A.T.S. visent les ennemis selon le module v025 conservé.

Cache de visibilité limité à 6 000 échantillons, réinitialisé par image/transition. Maillages secondaires mis en cache par WeakMap, sans ajout permanent à la scène. Ombres fines non garanties. Les essais logiciels ne certifient pas un pilote WebGL matériel.
''')
out('CONTROLES.md','''# Contrôles principaux — v0.28

ZQSD ou WASD pour se déplacer ; souris pour regarder ; clic gauche pour tirer ; R pour recharger ; E pour interagir ; Maj pour courir ; Espace pour sauter si les jambes le permettent.

Tab ouvre/range le Pip-Boy. I ouvre son inventaire. L contrôle la lampe portable. STAT → ÉTAT sélectionne une région et son traitement ; STAT → SURVIE contient charge, besoins et halte. RADIO → JEUX apparaît après la découverte de la cassette près de Sofia.

Les conduites du jeu tournent au clic ou au toucher. Bornes et isolants restent fixes. Les six niveaux se choisissent par leurs boutons ; recommencer demande confirmation.

V ouvre le V.A.T.S. dans le monde. Cliquer une zone ou son étiquette sélectionne le membre, E réserve, C ajoute un critique lorsque disponible, Espace exécute. Les commandes historiques de suivi, plan local et carnet restent disponibles.

Sur mobile, utiliser les boutons tactiles et le défilement des panneaux. Les essais ont été effectués en fenêtre tactile simulée 390 × 844, pas sur un iPhone réel.
''')
out('RAPPORT_VISUEL_V0.28.md','''# Rapport visuel — Tenir debout

`RAPPORT_VISUEL_V0.28.html` est autonome et incorpore les 23 captures. Les PNG sources sont dans `verification/`; `CAPTURES_V028.json` enregistre l’empreinte du HTML, la caméra, le contexte et les limites de chaque vue.

La planche `RAPPORT_VISUEL_V0.28.png` regroupe huit vues. `LUMIERE_AVANT_APRES_V0.28.png` conserve la même caméra pour comparer lampe éteinte, lampe allumée, puis remise en service du circuit fixe.

Toutes les images viennent du jeu exécuté. Les vues de santé utilisent des blessures et stocks préparés pour la lisibilité ; leurs effets sont testés séparément. La montée vers le plan utilise le contrôleur réel, et le sixième jeu est résolu par clics pour la capture. Aucune image conceptuelle ni carte réelle n’est présentée comme un rendu de production.
''')
print('Documentation écrite')
