# Consommables, tolérance et dépendances

Le module `src/v050/15_chemistry.js` ajoute Jet, Buffout, Mentats et Psycho à l’inventaire et au commerce existants. Les règles, durées, approvisionnements et soins ci-dessous sont des créations de jeu pour Fallout : Mistral. Ils ne proviennent ni de documents médicaux ni d’une reproduction des règles d’un épisode officiel. Aucun intérieur ou stock commercial réel n’est présenté comme documenté.

## Effets jouables

| Consommable | Bonus d’une première prise | Retrait en cas de dépendance |
| --- | --- | --- |
| Jet | PA maximaux +20 et recharge de 20 PA, limitée au maximum courant | PA maximaux −15 |
| Buffout | PV maximaux +20, recharge de 20 PV et charge transportable +15 kg | PV maximaux −10, charge −10 kg |
| Mentats | Science, Réparation et Éloquence +15, plafond 100 | Ces trois aptitudes −10, plancher 0 |
| Psycho | Dégâts du joueur ×1,25, visée libre et V.A.T.S. | Dégâts du joueur ×0,85 |

Un bonus dure **120 secondes de simulation active**. Menus, dialogue, chargement, laboratoire et simulation gelée conservent les compteurs. La tolérance atteint les paliers 0/1/2/3 après 1/2/4/6 prises rapprochées ; la puissance d’une nouvelle dose vaut 100/80/60/40 %. Une reprise remplace le bonus de sa famille : elle n’empile pas plusieurs maxima. Les familles peuvent coexister. Les Mentats s’ajoutent aux +10 des magazines existants avant le plafond de 100.

La troisième prise rapprochée crée une dépendance déterministe. Elle est affichée immédiatement. À la fin du bonus, le retrait dure **300 secondes actives** ; une nouvelle dose masque ce retrait et conserve la dépendance. Sans reprise, la famille récupère ensuite. Une charge de tolérance disparaît toutes les 180 secondes actives depuis la dernière prise ; la charge est bornée à six. Chaque famille suit ses propres compteurs. Aucun tirage aléatoire ou temps réel hors partie ne change ces états.

Les maxima PV/PA repartent des calculs historiques, puis reçoivent les modificateurs. Changer d’équipement, charger une sauvegarde ou recalculer les caractéristiques n’accorde aucune nouvelle recharge. Une baisse de maximum borne la réserve courante ; un retour à un maximum supérieur ne soigne pas. Les bonus ne modifient pas le S.P.E.C.I.A.L. permanent. Le multiplicateur Psycho s’applique au calcul des attaques du joueur, pas aux attaques de ses compagnons ou ennemis.

## Acquisition et interface

Les quatre IDs (`jet`, `buffout`, `mentats`, `psycho`) restent des objets ordinaires de `state.inventory` : masse 0,1 kg, consommables dans **INV → AIDE**, bouton **Utiliser 1**. Leur valeur, leur description et leurs lignes de vente utilisent les interfaces existantes. Leur revente est plafonnée sous le prix d’achat courant pour empêcher le bénéfice immédiat par aller-retour au comptoir.

Des ajouts finis complètent les comptoirs narratifs :

| Comptoir existant | Ajout initial |
| --- | --- |
| Baptiste Arnaud, Aubagne (`aubagne`) | 3 Mentats, 2 Buffout |
| Marché de Noailles (`noailles`) | 3 Jet, 2 Mentats |
| Comptoir du Vieux-Port, La Ciotat (`ciotatPort`) | 3 Psycho, 2 Buffout |

Un reçu `v054Chems.stocked` accompagne le même stock marchand sauvegardé. Il ne contient aucune quantité d’inventaire supplémentaire. Une quantité déjà présente, y compris zéro après épuisement, est conservée. Visites, achats, reventes, migration et Continue ne réensemencent jamais un reçu enregistré. Les coffres urbains nouvellement créés et non possédés ont une chance déterministe de 1/13 de recevoir une dose. Les coffres déjà enregistrés, dépouilles, réserves de quête et coffres possédés ne sont pas enrichis rétroactivement.

**STAT → DÉPENDANCES** montre les prises historiques, le palier de tolérance, la puissance courante, les bonus, la dépendance et le temps de retrait. **STAT → SANTÉ** ajoute un accès au bilan et les familles actuellement concernées.

## Sofia et paiement local

Le dialogue existant de Sofia Neri conserve ses quatre choix et ajoute une entrée sur les consommables. Son poste reste celui de l’**Annexe des Veilleurs**, scène narrative `relay_cold`, PNJ `relay_cold:npc` à **[-3, 0, 9]** dans ce plan fictif. L’interaction existante `v028:medic` est située à [-3, 1, 9].

Le nouveau soin exige Sofia vivante, à moins de quatre mètres, au même niveau, avec visibilité et passage libre, hors danger et hors chargement. Le devis coûte **40 + 20 capsules par famille concernée** : une famille coûte 60 capsules. La confirmation doit conserver le même personnage, monde, scène, bilan et prix ; fermer le Pip-Boy ou charger une scène invalide le devis. Un manque de capsules ne prélève rien.

Le traitement supprime ensemble bonus actifs, tolérance et dépendances. Il conserve le nombre historique de prises. Il ne restaure pas PV, PA, radiations, infection ou membres blessés ; la fin d’un bonus peut donc abaisser un maximum. Les soins historiques des traumatismes restent accessibles dans le dialogue d’origine.

Les prises, achats, reventes et nouveaux soins sont synchrones et atomiques : une réussite demande une seule sauvegarde finale. Un refus ou une exception de stockage restaure l’état entier, y compris inventaire, bourses, stocks, munitions, métadonnées de sauvegarde, collections, factions et armure assistée. Les wrappers des modules 11 et 12 conservent leurs actions propres ; aucun effet chimique n’est réappliqué à la migration.

## Validation et pilote natif

`node tests/expansion/chems_ecosystem.cjs` exécute 31 cas : simulation bornée, petits/grands pas de temps, tolérance, retrait, récupération, cumul Mentats/magazines, maxima et migration, fonctions de dégâts/commerce/Sofia de production, composition 10/11/12/15, transactions refusées ou levées, approvisionnement fini et devis médical local. Le stockage, les acteurs et le sol plat de ce harnais sont des interfaces de test déclarées ; ce résultat n’est pas une visite native de la ville.

Le hook de construction est `v054ChemsAfterInit()`. Ses diagnostics publics :

- `v054ChemsInfo()` : copie des compteurs, phases, modificateurs, aptitudes réelles, capacité, disponibilité/devis de Sofia et bilan des transactions.
- `v054ChemsCatalog()` : copie des quatre définitions, des stocks initiaux et durées.
- `v054ChemsUse(id)` et `v054ChemsDoctor(confirm)` : mêmes actions gardées que l’interface, sans attribution gratuite.

`tests/expansion/chems_native.py` ne lance aucun navigateur sans `--run`. Après gel du HTML et du module :

```sh
/workspace/.cloud-setup/fallout-marseille/venv/bin/python tests/expansion/chems_native.py \
  --run --output /tmp/chems-native \
  --expect-html-sha SHA_HTML --expect-chems-sha SHA_MODULE_15
```

Le pilote utilise le vrai serveur, le HTML inchangé, un seul contexte Chromium et le stockage natif. Il achète les trois Mentats finis de Baptiste avec une aide déclarée de 300 capsules, les consomme depuis AIDE, vérifie la pause dans le Pip-Boy puis avance la simulation normale par au plus 2 500 appels `v020Tick(.05,true)`. Il rejoint ensuite physiquement Sofia, utilise le nouveau choix de dialogue, demande un devis, paie par les boutons visibles et recharge par Continue. Il contrôle l’historique, les réserves épuisées et les autres systèmes. La navigation de diagnostic sélectionne les scènes narratives ; les approches sont vérifiées par les collisions et lignes de vue de production. Aucune dose, quantité de stock, dépendance ou issue de quête n’est injectée. JSON, captures et SHA sont enregistrés dans le dossier de sortie.

### Exécution native du 25 octobre 2026

Le pilote corrigé passe **74 contrôles sur 74**, code de processus **0**, sur le HTML `5e6895ac4d718ce6547864f5d8fc553a457e04a784c51fd753c72591693425db` et le module `b432076d9f0b3fa4a4c0eeab9b95e5044de8089fb2148b958c130efc417ccd4e`. Aucun défaut JavaScript de page ni réponse HTTP locale en échec n’est enregistré. Le navigateur est fermé en fin d’exécution.

Après achat et consommation réels, l’attente se fait à l’accueil de l’Annexe, point narratif [-3, 1,65, 10,7], libre de collision et avec visibilité vers Sofia. Les 24 tranches de cinq secondes restent en jeu actif, avec 115 PV constants. Le bonus de 120 secondes expire, le retrait applique −10 aux trois aptitudes, puis le soin local prélève exactement 60 capsules. Continue conserve trois prises historiques, un traitement, zéro Mentats dans le sac et dans le stock épuisé d’Aubagne, et les anciens états d’armure/collection.

Les pièces se trouvent dans `/workspace/.cloud-setup/fallout-marseille/precision-expansion/chems-native` : rapport JSON, journal et code de processus, script exécuté, quatre captures. La première tentative est conservée séparément dans `chems-native-attempt-01` : l’attente à Aubagne n’avait avancé que 29,65 secondes actives ; son instrumentation ne permet pas de déterminer la cause de l’interruption. Le harnais a déplacé cette attente dans l’accueil sûr, ajouté le contrôle de mode/PV par tranche et corrigé sa fermeture Playwright. La seconde tentative, également conservée, passe sans modification de production. Ce parcours couvre les Mentats natifs ; les autres familles et les erreurs de stockage sont couvertes par les tests VM décrits plus haut.
