# Limites vérifiées — v0.48

## Données géographiques
0/5 884 coordonnées vectorielles et 0/8 grilles territoriales sont installées. La tentative de connexion à la source vectorielle officielle échoue à la résolution DNS. Aucun ancien compteur cloud n’est considéré comme preuve actuelle d’acquisition.

Les extérieurs des captures sont ceux du banc synthétique identifié à l’écran. Ce sont des captures du programme exécuté, pas des rues réelles de Marseille. La continuité parcelle par parcelle et les traversées humaines de la carte complète ne sont pas certifiées.

## Temps et mémoire
Le budget coopératif de 6 ms est une cible entre opérations. Une opération atomique lourde peut le dépasser. Le chargement terrain, les ressources et le rendu peuvent encore produire des pauses sur des machines lentes.

Le secteur retenu garde de la mémoire pendant la visite : un seul extérieur, dans un plafond estimatif de 48 Mio. Aucun gain de FPS global ni temps de téléchargement du pack complet n’est annoncé. La rétention est de session seulement ; après fermeture/rechargement de l’application, un retour doit repasser par les données installées ou le réseau.

## Plateforme
La navigation Chromium directe vers le serveur local retourne `ERR_BLOCKED_BY_ADMINISTRATOR`. Le jeu est exécuté via Playwright/set_content. Le serveur HTTP est testé séparément par Python. IndexedDB natif, la PWA installée nativement et une machine Windows physique ne sont pas certifiés.

## Artistique
Les gabarits intérieurs et modèles du prototype restent procéduraux. Cette version corrige leurs cloisons et les retours ; elle ne transforme pas les 248 lieux en environnements artistiques uniques.
