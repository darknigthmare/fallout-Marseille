# Contenu v0.37 — Cache territorial

## But de la version

La v0.36 savait adresser les 5 884 coordonnées vectorielles. La v0.37 ajoute la persistance, le contrôle exact du manifeste et un audit global suffisamment prudent pour séparer absence de données et défaut réel.

## Cache territorial cloud

Une Edge Function dédiée sert uniquement les coordonnées inscrites au manifeste :

- source `base`, zoom 14 ;
- source `cadastre`, zoom 16 ;
- emprise Mistral ;
- taille maximale de 8 Mo.

À la première demande, la réponse officielle est vérifiée, hachée et stockée dans un bucket privé. Les métadonnées — taille, SHA-256, ETag, date et compteur d’accès — sont conservées dans une table technique protégée par RLS sans droit `anon` ou `authenticated`.

Les demandes suivantes sont servies depuis le cache. Un ETag permet la revalidation ; une copie valide peut être servie comme secours lorsque la source officielle est temporairement indisponible.

État réel lors de la livraison :

- **367 / 367 tuiles de fond**, 29 456 613 octets ;
- **1 / 5 517 tuile cadastrale**, 3 816 octets ;
- total : **368 PBF**, 29 460 429 octets.

Ce nombre ne vaut pas prétention de couverture complète.

## Cache navigateur

La base IndexedDB comporte deux magasins :

- `tiles` : contenu binaire ;
- `meta` : provenance, poids, coordonnées, SHA, date et dernier accès.

Le jeu mesure la taille réelle du cache, applique un budget configurable et évince d’abord les fichiers les moins récemment utilisés.

Priorité de lecture :

1. pack local ;
2. cache navigateur ;
3. cache cloud ;
4. source officielle directe.

## Filtrage exact

Le moteur refuse les coordonnées qui ne figurent pas dans les plages compactes du manifeste. Le relais applique le même contrat côté serveur.

## Préchargement

Le Pip-Boy permet :

- préchargement autour du joueur ;
- anticipation selon la direction de déplacement ;
- préchargement de la couche générale d’une macro-région ;
- préchargement cadastral avec confirmation ;
- annulation immédiate ;
- réglage du nombre de tuiles anticipées ;
- réglage du budget local.

## Continuité routière

L’audit v0.37 construit un graphe global des segments chargés. Une extrémité en bord de tuile est classée :

- appariée ;
- en attente de la tuile voisine ;
- non appariée avec voisin présent.

Seule la troisième catégorie est une anomalie confirmée.

## Bâtiments

Le moteur et l’auditeur :

- remplacent un volume général par l’empreinte cadastrale lorsque celle-ci est disponible ;
- suppriment les empreintes cadastrales exactement dupliquées ;
- signalent les empreintes coupées aux limites pour fusion ou contrôle ultérieur.

La déduplication géométrique ne prétend pas résoudre toutes les erreurs topologiques du cadastre.

## Tests MVT contrôlés

La QA navigateur utilise deux tuiles synthétiques adjacentes pour vérifier le raccord routier, et une empreinte cadastrale dupliquée pour vérifier remplacement et déduplication. Cette scène est explicitement marquée comme synthétique et n’est jamais présentée comme une vue de Marseille.
