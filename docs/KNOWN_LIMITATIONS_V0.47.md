# Limites et vérifications non réalisées — v0.47

## Géographie
Le pack lourd n’est pas installé : 0 PBF territorial sur 5 884 coordonnées et 0 grille sur 8. Les essais DNS de récupération ont échoué dans cet environnement. Les anciens rapports de cache distant ne prouvent pas que ces services soient actuellement disponibles.

Les captures et traversées de continuité utilisent le banc synthétique explicitement signalé. Ce sont des captures du jeu exécuté, pas des images conceptuelles, mais elles ne représentent pas des rues réelles de Marseille.

## Performance
Les budgets LRU estiment les objets conservés, pas la totalité de la mémoire navigateur ni celle du GPU. Des éléments actifs épinglés peuvent dépasser leur budget ; cet état est exposé. La construction reste en JavaScript sur le thread principal, avec rendus interrompus seulement aux étapes prévues : une machine lente peut toujours subir des pauses de calcul.

Aucun débit global, temps de chargement ou gain FPS pour la carte entière n’est annoncé. Les nouveaux tests démontrent la logique et le réemploi, pas les performances finales de toutes les communes.

## Environnement navigateur
La navigation native de Chromium est bloquée par la politique de cet environnement. Les tests de jeu utilisent Playwright/set_content et des réponses contrôlées. Le serveur est contrôlé séparément par de vraies requêtes HTTP Python sur loopback. L’installation PWA et IndexedDB natif ne sont donc pas certifiés par cette livraison.

## Contenu
Les 248 sites et le lore reconstruits de la v0.46 sont conservés. La v0.44 d’origine n’est pas déclarée récupérée. Les intérieurs et modèles restent ceux de la branche existante ; la v0.47 ne les transforme pas en productions artistiques uniques.
