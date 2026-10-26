# Installer des annotations architecturales

Le jeu lit facultativement [data/map_pack/architecture/index.json](../data/map_pack/architecture/index.json). L’atlas livré contient **12 associations à un site IGN**, sans plan de façade ni d’intérieur : onze volumes religieux du site Notre-Dame de la Garde et un bâtiment du Centre de Conservation et de Ressources du Mucem. Le [catalogue des sources](CATALOGUE_ARCHITECTURE_MARSEILLE.md) décrit les critères d’association et leurs limites. Une association de site ne documente pas les fenêtres ou les pièces.

## Validation et installation

Un atlas utilisateur peut contenir des ouvertures cotées, des plans intérieurs et leurs références. Node.js est nécessaire uniquement pour cet outil de préparation ; le jeu conserve son lancement habituel par Python, sans npm.

```bash
node tools/architecture_documents.cjs validate --input mon-atlas.json
node tools/architecture_documents.cjs install --input mon-atlas.json
```

La validation utilise les mêmes modèles de façade et d’intérieur que le jeu. L’installation remplace le fichier local après validation et écriture temporaire ; une erreur laisse l’ancien fichier intact. Le fichier installé remplace l’atlas, donc inclure aussi les associations que l’on souhaite conserver. Recharger la page du jeu après installation.

Le fichier est facultatif. Son absence laisse jouer avec les volumes disponibles et leurs compléments inventés. Un fichier présent mais invalide n’est pas appliqué ; le panneau des cartes signale le problème. Aucun plan n’est téléchargé implicitement.

## Attacher un document au bon bâtiment

L’enveloppe possède `schemaVersion: 1`, `frame: "engine-lambert93-metre"` et un tableau `records`. Chaque enregistrement possède un `id` unique, une `target`, une `source` attribuée et au moins une annotation.

La cible contient l’identifiant IGN `cleabs` et la **géométrie GeoJSON originale exacte** `rawGeometry`. Les plans exigent aussi un `component` : `id`, `baseY`, `height`, `levels` et `rings` métriques ordonnés. Le diagnostic `window.__MISTRAL_DEBUG.v052ArchitectureTarget(cleabs)` exporte cette liaison depuis un bâtiment actuellement chargé ; seules les clés `cleabs`, `rawGeometry` et `component` constituent la cible. Les annotations de diagnostic retournées à côté n’ajoutent aucune cote.

Les anneaux gardent leur ordre et leur point de départ. Un identifiant géométrique stable peut être identique après rotation d’un anneau, alors qu’un numéro d’arête désignerait une autre façade. Le moteur refuse donc un plan dont les arêtes ou le volume ne correspondent plus à la liaison enregistrée. Il refuse également une géométrie source différente ; il ne recale pas silencieusement un document.

La `source` contient `url` HTTPS sans identifiants, `title`, `license`, `attribution`, `accessedAt` au format ISO et, si disponible, `responseSha256`. Elle doit décrire le document réellement utilisé et ses droits de réutilisation.

## Façades

`facadeDocument` utilise `schemaVersion: 1`, `source` (URL), `license`, `attribution`, `acquiredAt` et `openings`. Une ouverture possède :

- `type` : `door`, `window` ou `shopfront` ;
- `ringIndex`, `edgeIndex` : anneau et arête **dans l’ordre de la cible** ;
- `offset` : distance depuis le début de l’arête ;
- `bottom` : altitude relative à la base du bâtiment ;
- `width`, `height` : dimensions en mètres.

`completeEdges` peut déclarer les paires `{ringIndex, edgeIndex}` entièrement documentées, y compris une façade aveugle. Le moteur n’y ajoute pas de baies inventées. Une ouverture hors arête ou hors volume est refusée. Les segments courbes inventés ne renumérotent pas les arêtes documentaires originales.

## Intérieurs

`interiorDocument` utilise `schemaVersion: 1`, `frame: "building-local-metre"`, `buildingId` égal au composant, une `source` attribuée et `levels`. Le repère local est centré sur l’enveloppe XY du composant : X et Z horizontaux, élévations relatives à sa base. Un niveau décrit `level`, `elevation`, `height`, ses `walls` et ses `rooms`, avec éventuellement une `entry`.

Un mur est décrit par `a: [x,z]`, `b: [x,z]` et `thickness`. Une pièce possède `id`, `use` et un anneau `ring`. Les éléments documentés doivent tenir dans le vrai contour et respecter les cours ; les niveaux ne doivent pas dépasser le volume. Les murs, anneaux et cotes documentés sont conservés. Le mobilier reste inventé et doit laisser des accès utilisables. Un plan de rez-de-chaussée ne documente pas les étages absents.

## Sauvegardes et limites

L’atlas est limité à **128 enregistrements**, à **1 Mio lu sur disque** et à **1 Mio de représentation JSON estimée en UTF-16**. Ces bornes concernent les annotations installées ; les centaines de milliers de volumes géographiques et les compléments inventés ne dépendent pas de cette limite.

Les plans enregistrés par `v050CityRegisterDocument()` sont propres à la sauvegarde : **32 bâtiments et 512 Kio au maximum**, validés avant écriture. Une modification enregistrée pendant une visite s’applique à la prochaine entrée, pour ne pas déplacer les murs autour du personnage. La visite active conserve son instantané, y compris après **Continuer**. Les plans de l’atlas ne sont pas copiés en bloc dans ce registre utilisateur.

Les nouvelles entrées utilisent le programme de pièces **version 5**. Les visites sauvegardées des versions **1, 2, 3 et 4** sont reprises avec leur disposition précédente, y compris leur ancien mobilier documentaire. Les [programmes par usage](INTERIEURS_USAGES.md) décrivent les équipements spécialisés, leur provenance et leurs limites. Dans les petits résidentiels inventés, une variante de lit simple et un WC séparé peuvent laisser davantage de place aux fonctions essentielles. Le programme compact contrôle aussi jusqu’à 256 points proches du contour source pour repérer des recoins qui seraient isolés par les cloisons proposées. Les niveaux documentés conservent leurs murs, pièces et cotes, sans remplacement par ces variantes ni ajout de portes coulissantes inventées. Les nouvelles portes du layout 5 concernent seulement les pièces générées ; leurs états ouverts ou fermés vivent dans un registre propre à la sauvegarde et ne modifient aucun document.

Les espaces qui ne permettent pas une pièce fermée ou un meuble accessible restent des volumes ouverts ; les omissions et budgets sont exposés dans l’inspection du bâtiment. Une absence de pièce close n’est pas présentée comme un plan complet. Cette génération conserve l’échelle et l’emprise, sans certifier la disposition réelle des pièces. Le [bilan de validation du 26 octobre](../verification/expansion/wasteland/WASTELAND_INTEGRATION.json) distingue les modèles contrôlés, les parcours natifs et leurs limites ; [les chantiers actifs](CHANTIERS_ACTIFS.md) récapitulent le périmètre livré.
