# FALLOUT: MISTRAL — Une place dans la cour

**Notice historique du lot local du 11 novembre 2026.** Pour la publication ultérieure et la compilation complète, lire `docs/AUDIT_BIBLE_2026_11_11.md` et le rapport `verification/bible-sync/QA.json`. Les limites ci-dessous décrivent le lot local initial, pas une nouvelle validation distante.

## Jouer cette mise à jour

Ce paquet reprend les sources de lore et le programme de la livraison « Les gestes retrouvés », puis ajoute les promenades facultatives et souvenirs des trois propriétaires. C'est une mise à jour cumulative de la branche oiseaux/consigne, **pas une installation géographique ni un dépôt source complet**.

1. Exporter la sauvegarde et conserver une copie du dossier de jeu actuel.
2. Appliquer le paquet sur une copie compatible de l'installation de la PR 18, en conservant les packs IGN, assets et lanceurs non fournis. Ne pas effacer le stockage du navigateur. Pour retrouver une sauvegarde locale, garder l'origine de lancement habituelle, ou utiliser son export avec le mécanisme d'import du jeu.
3. Lancer avec le lanceur habituel. `index.html` et `JOUER_FALLOUT_MISTRAL_v0.50.html` sont identiques ; le service worker fourni a une nouvelle empreinte de cache.
4. Rejoindre la consigne depuis le Vieux-Port. Après une remise personnelle sauvegardée, parler de nouveau à Éloi, Mina ou Rachid et choisir la nouvelle proposition. Ils restent dans la cour ; on peut leur demander d'attendre, de reprendre et écouter un nouveau souvenir à destination.

Sur une ancienne sauvegarde où les objets sont déjà remis, aucune nouvelle restitution n'est nécessaire : l'invitation est disponible, mais la promenade ne commence qu'après votre choix. Les anciennes conclusions et la prime unique de 45 capsules restent acquises. Sauvegarder à mi-chemin conserve la distance ; une attente explicite est aussi enregistrée.

**Ne pas écraser l'installation COCHONNET (PR 17), une branche différente ou une révision plus récente avec ces binaires.** Pour cumuler des travaux, intégrer le patch source après revue, reconstruire le dépôt complet et relancer les tests. La version binaire de ce paquet ne contient pas COCHONNET.

## Contenu nouveau

Éloi rejoint une table où le souvenir de sa cabine prend la forme d'un croquis. Mina souffle debout près du banc de fin de quart et parle du moment où sa journée s'arrête. Rachid rejoint l'ardoise « PAS D'HORAIRE CONFIRMÉ » : son sifflet ne fait pas apparaître un ferry. Les trois trajets ont des collisions, l'interaction native et des arrêts/reprises. La bague de Mina suit maintenant sa main pendant la marche. Le journal suit leurs emplacements et les souvenirs écoutés.

## Résultats de cette édition

- **727 tests de logique réussis, 0 échec, dont 76 nouveaux.**
- **927 contrôles réussis sur 17 parcours navigateur**, dont 54 pour cette extension ; aucune exception JavaScript dans ces parcours.
- Assemblage incrémental et contrôle d'identité déterministes réussis ; syntaxe du programme vérifiée.
- **Reprises après fermeture : bloquées avant scénario par `ERR_BLOCKED_BY_ADMINISTRATOR`.** Les trois scénarios nouveaux sont préparés, pas validés. Les anciens tests à froid rats/oiseaux sont aussi bloqués. Ne pas reprendre leurs résultats historiques comme résultats de cette édition.
- Compilation canonique `tools/build_single.py`, quatre suites territoriales, campagne humaine et traversée IGN exhaustive **non exécutées** sur ce lot local.

Les tests navigateur ordinaires emploient des positions pilotées, un extérieur synthétique et un stockage mémoire isolé. Sauvegarder/recharger dans ces tests n'est pas une preuve de reprise après fermeture du processus. Le rapport actuel est `verification/consigne-vie/QA.json`. Les rapports sous `verification/gestes`, `verification/retrouvailles`, etc. sont historiques.

## Intégrité et sources

`python VERIFIER_ARCHIVE.py --strict` contrôle l'archive extraite seule. Dans une installation contenant d'autres fichiers, omettre `--strict`. Aucun identifiant ou accès distant n'est nécessaire.

Le patch `delivery/UNE_PLACE_DANS_LA_COUR_SOURCE.patch` contient les changements de sources, documentation, tests et workflow, **sans remplacer les binaires générés**. Il est destiné à la base `a589d8de0da349a0bcdfc6d1636eb41a1595a02e`. Examiner les changements, appliquer seulement à une branche de travail propre et compatible ; ne pas forcer en cas de conflit. Puis, depuis le dépôt complet :

```sh
git apply --check /chemin/UNE_PLACE_DANS_LA_COUR_SOURCE.patch
git apply /chemin/UNE_PLACE_DANS_LA_COUR_SOURCE.patch
python3 tools/build_single.py
python3 tools/build_single.py --check
node --test tests/expansion/lore_*.cjs
python tests/expansion/consigne_vie_browser_smoke.py --html index.html
python tests/expansion/consigne_vie_cold_save_smoke.py --html index.html
```

Le workflow local étendu conserve les suites de régression précédentes et ajoute les nouveaux scénarios. Il n'a pas été publié ni exécuté ici. Un environnement navigateur non bloqué est nécessaire aux reprises à froid. Un échec ne doit pas être remplacé par les résultats d'une autre édition.

L'outil `tools/build_consigne_delivery.py --base /chemin/FALLOUT_MISTRAL_LES_GESTES_RETROUVES_MISE_A_JOUR.zip --check` reproduit uniquement l'assemblage incrémental de ce paquet à partir de l'archive précédente vérifiée. Il n'est pas un remplacement du compilateur complet du dépôt.

## Limites

Trois trajets scénarisés dans une cour, pas de navigation libre ou d'emploi du temps régional. Mina n'est pas assise ; le dessin et le panneau n'ont pas de geste de réalisation détaillé. Pas de nouveau doublage, animation des doigts, transfert continu d'objet entre les mains ou ferry. Prototype de fan non officiel ; aucune qualification commerciale n'est revendiquée.
