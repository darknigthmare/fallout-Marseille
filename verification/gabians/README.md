# Vérification — Les objets trouvés

Base : `8924be65a69f7335364b09934bc908bf17d0973e` (rats-câbles fusionnés).
Livraison locale du 10 novembre 2026. Aucun commit ni nouveau run GitHub n'est annoncé.

## Résultats terminés

- `node --test tests/expansion/lore_*.cjs` : **578/578**, dont **42** nouveaux tests de la consigne.
- `gabians_browser_smoke.py` : **66 contrôles**, aucune exception JavaScript.
- Douze anciens parcours : **656 contrôles** sur le même HTML ; total navigateur **722**, sans additionner les répétitions.
- Vérification syntaxique du programme assemblé et des nouveaux modules.
- Comparaison exacte avec le programme de base après retrait des deux modules ajoutés ; catalogue et couche de lore géographique d'origine inchangés.
- HTML de lancement et `index.html` identiques ; cache du service worker renouvelé depuis l'empreinte du nouvel HTML.

Les rapports JSON donnent le SHA-256 du programme utilisé. `QA.json` synthétise les comptes et les limites. `build_receipt.json` identifie les entrées et sorties.

## Nature des preuves

Les interactions E, les choix de dialogue, le tir du pistolet, le ciblage du rig régional, les collisions, les effets et les opérations de sauvegarde/reconstruction passent par le code du jeu. Les positions, les visées et certains appels d'adaptateur sont pilotés par le test. L'extérieur de départ est synthétique et réutilise l'identité du relais du catalogue. Le stockage des parcours navigateur est isolé en mémoire et le rendu est logiciel.

Le parcours des gabians vérifie notamment les quatre réactions au projectile (impact, esquive, couvert, menu), le refus d'un prélèvement en hauteur, le vol progressif et interrompu, une arrivée dont l'écriture échoue, l'arrêt du panier sous une personne, la reprise en plein mouvement, les objets transportés puis rendus, la récompense unique et les trois issues de mortalité. Les deux issues avec pertes passent par l'adaptateur natif de dégâts et de quête ; le parcours sans abattage utilise les dialogues visibles.

**Non vérifié pour les gabians :** fermeture complète/reprise du navigateur avec stockage disque, parcours extérieur IGN intégral, coupure électrique, longue campagne humaine, performances matérielles. Le test à froid des rats est conservé mais son ancien résultat n'est pas attribué à la consigne.

## Incidents de préparation

Une première position de test de sortie dépassait la limite de la cour ; l'interaction a été reculée dans le volume jouable. Une exécution regroupée a été interrompue pendant le test des voisins par l'environnement (EPIPE). Cette exécution n'est pas comptée comme réussie ; la reprise isolée du même parcours s'est terminée correctement. Les rapports retenus sont uniquement ceux des exécutions terminées sur l'empreinte finale.

## Reproduire

Depuis le paquet, avec Node et les dépendances Playwright/Chromium déjà installées :

```sh
node --test tests/expansion/lore_*.cjs
node --check src/game.js
python tests/expansion/gabians_browser_smoke.py --html index.html
```

Dans le dépôt complet, le correctif source ajoute les modules dans l'ordre de construction existant :

```sh
python tools/build_single.py
python tools/build_single.py --check
node --test tests/expansion/lore_*.cjs
python tests/expansion/gabians_browser_smoke.py --html index.html
```

Le programme livré ici a été assemblé de manière incrémentale depuis l'artefact CI exact des rats ; ce n'est pas une reconstruction locale de tous les fichiers du dépôt. Pour reproduire cet assemblage précis, utiliser `tools/build_gabians_from_artifact.py --baseline <archive-CI-rats-originale.zip> --output <dossier>`. L'option `--check` ne modifie pas les sorties. Une base différente est refusée par ses empreintes.
