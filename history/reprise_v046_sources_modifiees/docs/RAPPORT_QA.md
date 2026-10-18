# Rapport QA — v0.46

HTML final : `a0556ee0ac1e55f7862c6b29502bcadfcce0a634fbf6c757f803ff2605115a63`.

**153 contrôles exécutés sur 153, aucun échec.**

| Ensemble | Résultat |
|---|---:|
| Noyau de validation et transactions | 23/23 |
| Contrat de distribution et service worker | 8/8 |
| Scène, coutures, erreurs, HUD, lore et migration | 49/49 |
| Campagne, sauvegardes, hub et opérations | 41/41 |
| Prologue A-03 | 22/22 |
| Interface produit | 10/10 |

## Ce qui a réellement été exercé

Le vrai moteur est chargé dans Chromium avec `set_content`. Le banc injecte des couches MVT décodées et des grilles explicitement synthétiques dans la même préparation que l’extérieur réel. Trois allers-retours via `tryPlayerMove` changent le libellé de région sans changer la scène. Les signatures complètes des bâtiments, routes et éléments naturels sont comparées ; la cour est libre et les murs possèdent encore leurs collisions.

Le test force ensuite des ressources en échec, observe l’écran réel de chargement, tente de déplacer le joueur, annule et vérifie sa position inchangée. Il teste aussi un réessai et l’arrivée tardive d’une réponse annulée. Le noyau Node contrôle de plus les erreurs de géométrie et deux chargements concurrents.

La barre de raccourcis est observée pendant 600 mises à jour : aucune destruction des boutons inchangés ; tailles du HUD constantes. La caméra change de direction sans changer l’azimut solaire monde. Une ancienne sauvegarde géographique et sa porte de retour sont converties une seule fois au repère commun. L’entrée/sortie d’un abri conserve la position et les empreintes extérieures.

Neuf factions et huit dossiers sont accessibles dans le Pip-Boy. Une récompense ne peut être obtenue qu’après accomplissement et une seule fois. Le banc ne sauvegarde pas la campagne.

## Ce que les tests ne prouvent pas

Aucune traversée humaine du Marseille réel, aucun téléchargement des 5 884 tuiles et aucun contrôle du relief de la région entière. Les données de laboratoire ne sont pas des images satellitaires ou un quartier acquis. La vérification du service worker est exécutée dans Node, pas via une inscription native dans un navigateur. Les scripts de régression utilisent un stockage mémoire explicitement installé quand l’origine opaque interdit le stockage natif.

Les figures sont des captures du programme, y compris de l’échec volontaire. Le graphique du monde de test n’est pas une illustration de la vraie carte.
