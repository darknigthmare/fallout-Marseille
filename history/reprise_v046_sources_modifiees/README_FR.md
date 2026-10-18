# FALLOUT : MISTRAL — v0.46 « Continuité vérifiable »

**Projet complet intégré, repris depuis la v0.42 réellement récupérée.**
Le binaire v0.44 et un projet complet v0.45 n’étaient pas disponibles dans cette session. La v0.46 conserve les sources et les 248 implantations de la v0.42, reconstruit les corrections de continuité, le HUD, le ciel et une partie explicitement décrite du lore français. Ce n’est pas un patch à appliquer à la main.

## Lancer

Décompresser, puis utiliser `LANCER_APP_WINDOWS.bat`, `LANCER_APP_LINUX.sh` ou `LANCER_APP_MAC.command`. Python est nécessaire pour ce serveur local. Il n’écoute que sur 127.0.0.1.

L’HTML `JOUER_FALLOUT_MISTRAL_v0.46.html` reste autonome pour les menus, la campagne historique et le banc de test. Le serveur local est préférable pour la lecture d’un pack cartographique et le stockage du navigateur.

## Corrections

Une seule scène extérieure et un seul repère Lambert-93 : changer de macro-région ne reconstruit plus les maisons ou la nature. Le nom de région change, pas la géométrie déjà affichée.

Le streaming prépare un halo de ressources au-delà de la distance visible. Les tuiles générales, les bâtiments cadastraux et toutes les grilles de relief nécessaires doivent être lus et validés avant publication. Un fichier absent maintient le chargement, avec Réessayer et Annuler. Une annulation ne déplace pas le joueur et une réponse tardive ne peut plus modifier sa scène.

Les empreintes cadastrales conservent leurs anneaux et leurs cours. Le recollage par enveloppe convexe est désactivé. La végétation utilise des cellules globales et les masques d’occupation du sol lus ; elle n’est pas répartie au hasard sur toute la région.

La barre de raccourcis ne détruit plus ses boutons toutes les 220 ms. Le panneau arme et la recharge ont une taille stable. Le ciel est projeté depuis des directions monde ; il ne suit pas l’orientation du joueur.

## Données territoriales : distinction importante

**Le ZIP contient le programme complet, pas le pack réel intégral de 5 884 coordonnées et huit grilles.** Ces fichiers ne sont pas présents dans cette livraison. Les anciens rapports cloud inclus dans l’historique ne prouvent pas leur disponibilité actuelle.

Les installateurs historiques restent inclus. Leur service distant n’a pas été vérifié pendant cette passe ; une machine possédant déjà le pack local peut le conserver dans `data/map_pack/`.

```sh
python3 tools/validate_real_map_v046.py --require-complete
```

Sans ressources géographiques nécessaires, l’extérieur réel reste bloqué plutôt que remplacé par un quartier inventé. Le rapport `verification/v046/LOCAL_DATA_STATE.json` expose les comptes réellement constatés.

## Vérifier les coutures immédiatement

Depuis le jeu : **Ctrl + Maj + F9** ouvre le banc synthétique de continuité. Cinq bâtiments, une cour, des routes et une forêt servent à reproduire la frontière. Un bandeau indique en permanence qu’il ne s’agit pas de Marseille. Ce mode inhibe les sauvegardes de campagne. Recharger le jeu revient à la campagne sauvegardée.

Les tests ont exécuté trois allers-retours, un échec réseau, une annulation et un réessai, ainsi que 600 changements d’affichage du HUD. Le détail se trouve dans `docs/RAPPORT_QA.md`.

## Lore réintroduit

`DATA → FRANCE EN CENDRES` contient neuf factions, huit dossiers reliés à des sites existants, récompenses uniques, réputation locale et pétanque COCHONNET. Les noms de créatures/automates enrichissent les témoignages ; ils ne représentent pas 25 nouveaux modèles. Voir `docs/LORE_RECONSTRUIT_V046.md`.

## Limites

Pas de traversée humaine de Marseille à La Ciotat ni de validation cartographique parcelle par parcelle dans cette session. Les bâtiments conservent une hauteur estimée lorsque la source ne la donne pas. Les modèles restent ceux du prototype. Fan-game non officiel : aucune affiliation Bethesda n’est revendiquée.
