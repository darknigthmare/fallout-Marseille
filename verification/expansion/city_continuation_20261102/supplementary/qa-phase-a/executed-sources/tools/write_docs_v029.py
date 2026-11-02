#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];docs=R/'docs';docs.mkdir(exist_ok=True)
q=json.loads((R/'verification/QA_GLOBAL_V029.json').read_text());caps=json.loads((R/'verification/CAPTURES_V029.json').read_text());sha=hashlib.sha256((R/'JOUER_FALLOUT_MISTRAL_v0.29.html').read_bytes()).hexdigest()
assert not q['failed'] and not q['errors'] and q['same_html'] and q['html_sha256']==sha and caps['html_sha256']==sha
base=json.loads((R/'data/BASE_V028.json').read_text());bad=[]
for rel,h in base['reference_files'].items():
 p=R/'history/v0.28_source'/rel
 if not p.is_file()or hashlib.sha256(p.read_bytes()).hexdigest()!=h:bad.append(rel)
assert not bad
preserved=len(base['reference_files'])
# Prior documents are kept intact in the reference tree, not presented as this build's QA.
for p in docs.glob('*'):
 if p.is_file():p.unlink()
text={
'CONTENU_V0.29.md':'''# v0.29 — Les portes ont des oreilles

## Ce qui est livré
La v0.28 est reprise depuis l'archive vérifiée, sans fusion supposée d'une autre branche. Cette passe ajoute des contrôleurs locaux, du piratage par déduction et de nouvelles possibilités de contourner les affrontements. Elle ne reconstruit pas le territoire cadastral.

## Terminaux et déduction
Trois contrôleurs physiques : D-4 au Dépôt des transitaires, A-2 aux Archives de la Traverse, Q-8 à la Station des amarres. Deux anciens dispositifs, relais CONCORDE d'Aubagne et mandat du chantier de La Ciotat, utilisent aussi la nouvelle déduction pour leur ancienne option de piratage.
Douze mots par table, de 5, 6 ou 7 lettres. La similitude compte les lettres à la même position. Quatre essais. Deux séquences retirent chacune un leurre ; une troisième restaure les essais une fois (non consommée lorsqu'ils sont déjà pleins). Le résultat, les essais, les séquences et les candidats écartés persistent.
Quatre erreurs entraînent 45 secondes de jeu actif de verrouillage. Les menus ne font pas progresser ce délai ; fermer et rouvrir ne le réinitialise pas. Après le délai, un nouveau cycle est préparé. Un badge reste valable pendant le verrouillage. Science 0 / 35 / 50 pour les trois contrôleurs ; les habilitations permettent une autre voie sans G.O.A.T. Une authentification par déduction apporte 18 XP une seule fois sur chacun des trois nouveaux appareils. Les anciens contrôleurs gardent leur récompense de quête, sans prime ajoutée.

## Commandes locales
L'authentification seule n'ouvre rien. Une confirmation est nécessaire pour ouvrir le volet de service ou consigner un automate. La veille concerne seulement le robot explicitement raccordé : Protectron du dépôt, drone des archives, soudeur des amarres. Elle ne donne pas de butin et ne recrée pas les machines mortes ou neutralisées par les anciennes quêtes. Le carillon crée une position sonore à inspecter, avec 12 secondes actives entre essais. Il n'efface pas un combat déjà engagé.
Les copies dans DATA → CONTRÔLEURS sont en lecture seule. Les commandes exigent la bonne scène, la portée, la hauteur et la visibilité du poste ; import et changement de scène invalident la session. Un dialogue natif conserve le focus et se ferme avec Échap.

## Trois locaux de service
Chaque cour reçoit une alcôve accessible sans chargement. Volet solide avant ouverture, murs et mobilier conservés après. Le dépôt abrite le contact de fin de course ; les deux autres locaux contiennent des notes techniques. Une poignée mécanique ouvre depuis l'intérieur, même sans authentification. Les neuf espaces historiques des trois scènes sont conservés, avec un dixième espace de service.

## Perception et infiltration
L'acquisition initiale requiert vue, orientation, portée et un temps d'observation. Très proche, la proximité permet encore d'être repéré. Le soupçon diminue hors de vue. Les bruits de pas debout et de course peuvent créer une position d'enquête ; les pas accroupis ne l'émettent pas. Une cloison réduit la portée sonore selon un coefficient simple. Les adversaires rejoignent la position avec les collisions historiques, pas par téléportation. Une alerte déjà acquise n'est pas annulée par un leurre.
Le HUD distingue CACHÉ, SOUPÇON, PRUDENCE et DANGER. La règle de révélation de la lampe, les tirs et la propagation des alertes de groupe restent ceux des versions précédentes. Ce n'est pas une simulation acoustique complète ni une refonte de 130 IA uniques.

## Enquête originale
Adrien Pellissier cherche pourquoi une porte a classé une personne comme une palette. Trois journaux (une preuve par contrôleur), une pièce physique dans D-4, trois habilitations alternatives. D-4 est à la cantine ; A-2 dans la galerie haute ; Adrien établit Q-8 après les deux premiers journaux. Neuf entrées techniques originales sont consultables sur les trois nouveaux postes. La bande « La main sous la porte » apporte cinq segments sous-titrés, sans voix.
Deux conclusions, avec prévisualisation réversible puis confirmation. « Les boutons aux équipes » ne consomme aucun composant, donne deux attelles et laisse les accès aux équipes. « Une surveillance sans fichier de personnes » utilise deux ferrailles et un circuit, donne une trousse et répare le contact. Chaque accord ajoute 75 capsules et 90 XP une seule fois, ouvre les trois volets et met en veille leurs trois automates survivants. Les panneaux changent de couleur. Trois scènes textuelles propres par conclusion, donc six au total.
Les choix antérieurs de la relève, du canal six, des archives médicales et de la pharmacie ne sont pas remplacés. Aucune ville entière n'est déclarée transformée par cette enquête.

## Corrections de cette passe
Focus replacé dans le contrôleur après désactivation d'un candidat ; défilement remis en haut à l'ouverture. Enseignes des locaux retournées vers l'approche réelle après vérification des captures. Suivi d'objectif effacé après une nouvelle partie pour ne pas garder un ancien dossier affiché. Les anciens mandats ne peuvent pas être réécrits plusieurs fois pour obtenir des récompenses ou reculer une quête.
''',
'STATUT_PRODUCTION.md':'''# Statut réel — v0.29

Fan project Fallout non officiel. Livraison locale, sans publication GitHub/Vercel.

## Réalisé
HTML autonome construit depuis les sources. Trois contrôleurs nouveaux, deux anciens hacks raccordés, trois petits locaux de service, déduction persistante, habilitations, veille locale, carillon, perception progressive et enquête à deux conclusions. Le contenu narratif, les circuits sur holodisque, blessures, lampe, Pip-Boy et V.A.T.S. précédents restent présents. Les trois scènes concernées et les 86 configurations historiques sont couvertes par les contrôles indiqués dans le rapport QA.

## Non réalisé / limites
Aucune donnée cartographique officielle ou altimétrique ajoutée. Les cours et alcôves sont fictives et schématiques, pas des reproductions d'Aubagne/Marseille/La Ciotat. Les extérieurs géographiques stricts peuvent encore manquer de données ; utiliser la campagne en lieux scénarisés pour le contenu embarqué.
Modèles et animations procéduraux ; Adrien réutilise le modèle humain de métier. Le volet bascule entre ouvert et fermé, sans animation de moteur complexe. Les automates en veille restent debout, sans nouvelle animation mécanique unique. Aucun doublage ou flux radio Internet ajouté.
La perception utilise le point de vue et les collisions existants. La recherche sonore ne planifie pas une propagation acoustique réaliste à travers toutes les salles ; une atténuation de portée remplace cela. L'alerte de groupe et les tirs gardent leur logique historique. Les règles sont partagées entre familles : aucune refonte individuelle des 130 variantes n'est revendiquée.
Le temps de verrouillage progresse dans le jeu actif, pas en attendant dans l'appareil ou par un changement artificiel de l'horloge régionale. Pas de simulation hors écran des populations ou des nouvelles machines.
Tests dans Chromium avec rendu logiciel ; ni GPU matériel ni iPhone physique certifiés. L'origine file:// est refusée par la politique de l'environnement de test ; le HTML exact est donc exécuté via set_content. Le refus natif de stockage opaque est vérifié, puis les scénarios réussis utilisent un adaptateur mémoire déclaré. Aucun résultat de test ne certifie à lui seul un RPG commercial terminé ou un parcours humain de toutes les missions.
''',
'MIGRATION_V028_V029.md':'''# Migration v0.28 → v0.29

Campagne : `fallout_mistral_save_v029`. Exploration : `fallout_mistral_sandbox_v029`. Réglages : `fallout_mistral_settings_v029`. Les anciennes clés ne sont pas supprimées. La nouvelle exploration demande confirmation et ne remplace que l'exploration v029 ; la campagne reste distincte.

Le champ `v029` ajoute les essais, cycles, mots essayés, séquences utilisées, habilitations, volets, veilles, journaux lus, délai de jeu actif et état de l'enquête. L'ancienne sauvegarde démarre sans accès acquis ni récompense imposée. Les nouvelles clés sont normalisées ; les champs inconnus des anciennes versions restent gérés par le migrateur précédent.

Quitter puis rouvrir le terminal conserve la table ; importer une sauvegarde conserve les essais et ferme la session ouverte. Les commandes obsolètes sont invalidées. Un badge ne donne pas l'expérience d'un piratage. L'état de la veille ne réanime jamais un automate déjà mort.

Le soupçon et la position sonore sont transitoires dans la scène chargée : ils ne sont pas annoncés comme une mémoire globale d'ennemis hors écran. Les dégâts et décès hérités conservent leur propre persistance.

Le navigateur associe son stockage à une origine. Lors d'un changement de dossier, de navigateur ou de serveur, conserver un export JSON depuis DATA → SYSTÈME avant de changer d'environnement. Le jeu signale les refus d'écriture ; ne pas les interpréter comme une sauvegarde réussie.
''',
'ARCHITECTURE_V0.29.md':'''# Architecture — v0.29

`src/core-v017.js` reste la base historique. `tools/build_single.py` applique les correctifs puis assemble les modules précédents et `src/v029/`, dans l'ordre. `src/game.js` et le HTML sont générés : ne pas les éditer directement.

- `00_state.js` : définitions, tables de mots déterministes par contrôleur/cycle, migrateur borné, enregistrements.
- `01_terminal.js` : dialogue natif, sessions locales à époque invalide, déduction, aides, commandes avec confirmation, raccord des hacks relay/ship.
- `02_perception.js` : perception orientée et progressive, position sonore, état d'enquête, exclusion des automates en veille de la boucle offensive, HUD.
- `03_world.js` : contrôleurs, alcôves, volets/collisions, poignées intérieures, badges, personnage et pièce de quête.
- `04_story.js` : journaux, bande, dialogue d'Adrien, deux conclusions, suivi et bilan.
- `05_interface.js` : copies Pip-Boy en lecture seule, modal et focus, démarrage séparé, ponts d'export/import, instrumentation de tests.
- `style.css` : terminal CRT original et fenêtres étroites.

Le builder remplace une condition d'acquisition initiale du noyau par `v029Observe`. Il vérifie l'unicité de cette cible avant modification. Les autres blocs d'alerte/attaque sont conservés ; cela évite une réécriture silencieuse des anciens comportements.

`v029ApplyWorld` applique l'état logique aux vrais draws/colliders et au robot identifié. Une invalidation du cache de navigation accompagne un volet ouvert. La poignée intérieure exige une position à l'intérieur des limites du local, pas simplement un clic visible à travers la porte.

Les tests de déduction utilisent des réponses connues pour vérifier la mécanique, pas une prétention d'intelligence d'un joueur. Les tests des accès physiques, tentatives au clic, tactiles, trajets, import et refus sont séparés. Les captures sont issues du HTML exact, avec caméras et quelques états préparés.
''',
'CONTROLES.md':'''# Commandes et accès — v0.29

Déplacements ZQSD / WASD, regard souris, interaction E, course Maj, accroupissement Ctrl, saut Espace. Tab : Pip-Boy ; V : V.A.T.S. ; I : sac ; M : plan local ; L : lampe. Les raccourcis historiques sont conservés.

La nouvelle exploration est accessible par « Piratage & infiltration · exploration séparée » au menu. Elle démarre au dépôt près de la cour. Adrien est près de la porte de la cour. D-4 se trouve au bord ouest, à l'entrée de cette cour. Les deux autres contrôleurs se trouvent au bord est des cours des Archives de la Traverse et de la Station des amarres.

Terminal : E sur place, puis souris/tactile ou Tab et Entrée. Échap ferme. Le monde est en pause dans l'appareil. Le badge est une alternative au piratage ; ni ouvrir le terminal ni trouver le mot de passe ne déclenche automatiquement une commande. DATA → CONTRÔLEURS permet uniquement de relire les copies.

Pour la quête : écouter Adrien, consulter le deuxième journal de D-4/A-2/Q-8, récupérer le contact dans le local D-4, puis revenir comparer les accords. La fiche D-4 est près de la cantine. A-2 se trouve dans la galerie haute est. Adrien signe Q-8 après les deux premiers journaux. Le G.O.A.T. n'est pas obligatoire.
''',
'SOURCES_ET_CREDITS.md':'''# Sources et provenance

Base utilisateur : archive v0.28 vérifiée, empreinte dans data/BASE_V028.json. Les sources de référence sont conservées sans modification dans history/v0.28_source. Le HTML antérieur exact est history/v0.28_reference.html.
Les nouveaux récits, tables de mots et géométries de cette version sont originaux au projet. Aucun fichier de données cartographiques n'a été acquis dans cette passe. Les noms Fallout/RobCo restent utilisés dans le cadre de ce fan project non officiel.

Les contrôles d'accessibilité du dialogue ont été consultés dans la documentation primaire MDN (consultation le 17 septembre 2026) :
- https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-modal
- https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/dialog_role
Le composant utilise un élément HTML dialog natif avec focus maintenu, boutons natifs, statut annoncé et fermeture Échap. Ces liens documentent la technique ; ils ne constituent pas une validation de la fidélité du jeu à une interface commerciale.
'''
}
for name,content in text.items():(docs/name).write_text(content)
(docs/'RAPPORT_QA.md').write_text(f'''# QA v0.29 — HTML exact\n\nSHA-256 : `{sha}`.\n\n**{q['passed']} / {q['total']} contrôles ciblés réussis** : {q['retained']} régressions et {q['new']} vérifications nouvelles, dans 19 rapports/suites. Aucune exception JavaScript dans les rapports finaux. Les quatre rapports nouveaux sont listés dans verification/QA_GLOBAL_V029.json ; la suite tactile est exécutée par le script de perception.\n\nLes contrôles couvrent : mots et similitudes, quatre essais, aides uniques, verrouillage persistant, badges, commandes sur place, fermeture/import/clics obsolètes, focus, planchers/volets, véritable traversée des trois locaux, sortie mécanique depuis l'intérieur, veilles sans morts ni butin, deux anciens mandats sans récompense répétable, trois journaux, chemin d'habilitations complet sans G.O.A.T., deux accords, six épilogues, budgets, lampe, vue, orientation, recherche sonore, pas au clavier et gestes tactiles. Les 86 configurations historiques sont chargées séparément dans les régressions.\n\nDes assertions anciennes ont été adaptées explicitement dans data/ADAPTATION_TESTS_V029.json : clés/version actuelles, nombre d'espaces pouvant dépasser neuf, et exclusion initiale des seuls nouveaux objets derrière un volet verrouillé. Leur inaccessibilité initiale puis leur accessibilité après ouverture sont testées séparément avec le contrôleur de déplacement ; les chemins des anciens objets restent vérifiés. Les anciennes sources des tests sont conservées.\n\n{preserved} fichiers de référence v0.28 comparés et intacts. Captures : {len(caps['images'])}, provenant du HTML exact. Certaines caméras/poses/progressions sont préparées ; elles ne valent pas preuve de tous les prérequis, couverts par des essais dédiés. Aucun faux fond cadastral ou concept art n'est présenté comme import géographique.\n\nExécution : Chromium logiciel via set_content, car file:// est bloqué dans cet environnement. Refus du stockage natif opaque réellement exercé avant adaptateur mémoire explicite pour les écritures réussies. Ni GPU matériel ni iPhone physique testés ; fenêtre mobile 390 × 844 et entrées tactiles simulées. Pas de parcours humain exhaustif de toute la campagne.\n\nRejouer : `python tools/build_single.py`, `node --check src/game.js`, `python tools/run_all_qa_v029.py`. Utiliser CHROMIUM_PATH pour un Chromium installé, ou le navigateur fourni par Playwright. Les résultats de livraison/réextraction sont fournis séparément.\n''')
(R/'README_FR.md').write_text(f'''# FALLOUT : MISTRAL — v0.29\n## Les portes ont des oreilles\n\nFan project non officiel. Version locale, aucune publication distante.\n\n## Jouer\nAprès extraction sur ordinateur, ouvrir `JOUER_FALLOUT_MISTRAL_v0.29.html`. Les lanceurs Windows et Linux/macOS ouvrent ce fichier. Le contenu scénarisé fonctionne sans dépendance à télécharger. Le bouton **Piratage & infiltration · exploration séparée** démarre près d'Adrien dans la cour du dépôt. Il demande confirmation ; campagne et explorations antérieures restent distinctes.\n\nLes visualiseurs de pièces jointes sur téléphone peuvent ne pas exécuter le JavaScript. Les essais mobiles sont une émulation, pas une certification iPhone.\n\n## Nouveautés\nTrois contrôleurs de service et deux anciennes options de piratage, déduction de mots persistante, habilitations alternatives, trois alcôves avec volets et poignées intérieures, veille locale d'automates vivants, carillon de distraction, regard progressif et enquête originale à deux conclusions. DATA → CONTRÔLEURS conserve des copies en lecture seule.\n\n## Contrôles rapides\nZQSD/WASD : marcher. E : interagir. Ctrl : s'accroupir. L : lampe. V : V.A.T.S. Tab : Pip-Boy. M : plan. I : sac. Dans un terminal : boutons cliquables/tactiles, Tab pour parcourir, Entrée pour valider, Échap pour fermer. Quatre erreurs : 45 secondes de jeu actif ; refermer ne restaure pas les essais.\n\n## État et rapports\n{q['passed']} contrôles ciblés finaux réussis, avec les limites dans docs/RAPPORT_QA.md. Rapport visuel autonome : RAPPORT_VISUEL_V0.29.html. Sources préservées : {preserved} fichiers v0.28.\n\nLa carte réelle régionale et son relief ne sont toujours pas intégrés ; les scènes sont fictives et schématiques. Modèles/animations procéduraux, aucun nouveau doublage. Ne pas confondre les locaux de service avec une reconstruction cadastrale.\n\n## Construire et vérifier\n`python3 tools/build_single.py` reconstruit le HTML exact. `node --check src/game.js` vérifie la syntaxe. `python3 tools/run_all_qa_v029.py` lance les régressions et nouveaux essais (dépendances dans requirements-dev.txt). Les captures et le rapport ont leurs scripts respectifs. Le builder garde les modules ordonnés ; ne pas éditer src/game.js, qui est généré.\n\nLire docs/CONTENU_V0.29.md, docs/MIGRATION_V028_V029.md, docs/STATUT_PRODUCTION.md.\n''')
pkg={'name':'fallout-mistral','version':'0.29.0','private':True,'scripts':{'build':'python3 tools/build_single.py','check':'node --check src/game.js','qa':'python3 tools/run_all_qa_v029.py','captures':'python3 tools/capture_v029.py','report':'python3 tools/make_report_v029.py'}};(R/'package.json').write_text(json.dumps(pkg,indent=2))
(R/'data/BUILD_V029.json').write_text(json.dumps({'version':'0.29.0','html_sha256':sha,'source_archive_sha256':base['sha256'],'source_reference_files':preserved,'tests':q['total'],'new_tests':q['new'],'screenshots':len(caps['images']),'official_data_added':0},indent=2))
print('DOCS',q['total'],preserved)
