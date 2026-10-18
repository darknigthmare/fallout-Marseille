# FALLOUT : MISTRAL — v0.47.0
## Le territoire en avance

Projet de fan non officiel. Reprise directe du projet complet v0.46 fourni ; cette branche conserve sa provenance historique v0.42, sans revendiquer les fichiers perdus de la v0.44.

## Lancer
Décompressez l’archive, puis utilisez `LANCER_APP_WINDOWS.bat`, `LANCER_APP_LINUX.sh` ou `LANCER_APP_MAC.command`. Python est nécessaire au serveur local. Le HTML autonome reste disponible, mais une origine HTTP locale est préférable pour le stockage du navigateur et les fichiers géographiques.

## Changements
Le secteur suivant se prépare pendant le déplacement dans la zone déjà validée. La limite de sécurité reste bloquante si les ressources ne sont pas prêtes. Une préparation ratée, annulée ou devenue inutile après un demi-tour ne doit pas modifier la scène active.

Le relief est construit dans une banque isolée avant publication. Les géométries déjà valides et les maillages de relief sont réutilisés dans des caches à budget limité. Les pièces de végétation conservent des identifiants propres à leur cellule. L’occupation du sol, l’eau, les routes et le bâti guident leur placement.

Le diagnostic CONTINUITÉ compte les ressources de l’exécution actuelle, leurs origines et les fichiers réellement installés ; il ne reprend pas les anciens compteurs cloud comme s’ils étaient actuels.

## Données réellement incluses
Les 248 implantations fictionnelles et les ressources du jeu sont conservées. Le pack cartographique lourd n’est pas inclus : **0/5 884 coordonnées vectorielles et 0/8 grilles territoriales** sont installées dans cette distribution. Les deux minuscules PBF du dossier fixtures sont des données de test, pas des quartiers jouables complets.

## Banc de continuité
**Ctrl + Maj + F9** ouvre le banc synthétique identifié à l’écran. Il exerce le vrai moteur de chargement avec des données de test. Son bouton de retour restaure la scène, la position, l’inventaire et les données conservées avant l’entrée. La progression du banc n’est pas une progression de campagne sauvegardée.

## Vérifications
Le rapport final sous `verification/v047/QA_GLOBAL.json` agrège les tests exécutés sur cet HTML. Les limites du navigateur de test et l’absence de pack géographique complet sont consignées dans `docs/KNOWN_LIMITATIONS_V0.47.md`.
