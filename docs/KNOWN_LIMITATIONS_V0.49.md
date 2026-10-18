# Limites connues v0.49

## Géographie et visuels
Le pack territorial réel n’est pas présent : 0/5 884 coordonnées vectorielles et 0/8 grilles. Aucun contrôle rue par rue de Marseille, Aubagne ou La Ciotat n’est revendiqué. Les captures extérieures utilisent le banc synthétique identifié à l’écran, avec des rencontres réelles du jeu placées pour la vérification. Les modèles restent ceux du prototype.

## Persistance
Le journal couvre les acteurs territoriaux v0.42 reconnus, pas chaque acteur arbitraire d’une extension inconnue. Les PNJ éloignés et les effets ne sont pas simulés en continu : leur état est suspendu. Les anciens doublons de corps sont fusionnés vers le reliquat minimum pour prévenir la duplication ; un ancien reliquat contradictoire peut donc être réduit.

Les importations ont une borne de 2 Mio et 2 048 entrées pour le journal. Au-delà, les entrées excédentaires sont filtrées. Le catalogue actuel de 1 176 identités possibles est testé sous cette borne ; une extension du catalogue nécessiterait une nouvelle validation.

## Environnement de test
Le CLI agent-browser n’est pas installé et la navigation native Chromium vers le serveur local est bloquée par ERR_BLOCKED_BY_ADMINISTRATOR. Les tests exécutent le vrai HTML avec Playwright set_content et des adaptateurs mémoire pour le stockage. Le serveur est vérifié séparément par HTTP Python.

IndexedDB natif, la persistance disque native du navigateur, l’installation PWA native, les performances sur un vrai GPU et celles du pack géographique complet ne sont pas certifiés dans cette passe. Les tentatives d’accès externe ont échoué sur la résolution DNS. Aucun push ou déploiement distant n’a été fait.

Prototype de fan non officiel. Aucune qualité « jeu commercial terminé » n’est revendiquée.
