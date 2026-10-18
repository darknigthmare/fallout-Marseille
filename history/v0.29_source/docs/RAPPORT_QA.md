# QA v0.29 — HTML exact

SHA-256 : `804566ac2e8f48b84894549534c103a0b52672b781a0ad5c9e7fa5c4e9c8df31`.

**1334 / 1334 contrôles ciblés réussis** : 1141 régressions et 193 vérifications nouvelles, dans 19 rapports/suites. Aucune exception JavaScript dans les rapports finaux. Les quatre rapports nouveaux sont listés dans verification/QA_GLOBAL_V029.json ; la suite tactile est exécutée par le script de perception.

Les contrôles couvrent : mots et similitudes, quatre essais, aides uniques, verrouillage persistant, badges, commandes sur place, fermeture/import/clics obsolètes, focus, planchers/volets, véritable traversée des trois locaux, sortie mécanique depuis l'intérieur, veilles sans morts ni butin, deux anciens mandats sans récompense répétable, trois journaux, chemin d'habilitations complet sans G.O.A.T., deux accords, six épilogues, budgets, lampe, vue, orientation, recherche sonore, pas au clavier et gestes tactiles. Les 86 configurations historiques sont chargées séparément dans les régressions.

Des assertions anciennes ont été adaptées explicitement dans data/ADAPTATION_TESTS_V029.json : clés/version actuelles, nombre d'espaces pouvant dépasser neuf, et exclusion initiale des seuls nouveaux objets derrière un volet verrouillé. Leur inaccessibilité initiale puis leur accessibilité après ouverture sont testées séparément avec le contrôleur de déplacement ; les chemins des anciens objets restent vérifiés. Les anciennes sources des tests sont conservées.

108 fichiers de référence v0.28 comparés et intacts. Captures : 19, provenant du HTML exact. Certaines caméras/poses/progressions sont préparées ; elles ne valent pas preuve de tous les prérequis, couverts par des essais dédiés. Aucun faux fond cadastral ou concept art n'est présenté comme import géographique.

Exécution : Chromium logiciel via set_content, car file:// est bloqué dans cet environnement. Refus du stockage natif opaque réellement exercé avant adaptateur mémoire explicite pour les écritures réussies. Ni GPU matériel ni iPhone physique testés ; fenêtre mobile 390 × 844 et entrées tactiles simulées. Pas de parcours humain exhaustif de toute la campagne.

Rejouer : `python tools/build_single.py`, `node --check src/game.js`, `python tools/run_all_qa_v029.py`. Utiliser CHROMIUM_PATH pour un Chromium installé, ou le navigateur fourni par Playwright. Les résultats de livraison/réextraction sont fournis séparément.
