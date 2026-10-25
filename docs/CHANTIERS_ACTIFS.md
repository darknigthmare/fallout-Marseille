# Chantiers du 25 octobre 2026

Cette itération prolonge le commit `48418cc`. Les travaux portent en parallèle sur le monde, l’architecture, les systèmes de jeu et le lore. Les sources géographiques existantes restent séparées des aménagements et objets fictifs.

| Chantier | Travail livré | Validation du périmètre |
|---|---|---|
| Façades | Ouvertures sur les trois contours courts résiduels, passage utile des portes courbes, budgets et diagnostics explicites. | Modèles et comparaisons source validés : 191/191 portes dans les cas ciblés ; aucun décompte exhaustif des portes de la commune. |
| Intérieurs | Nouveau programme version 3 pour petites emprises ; visites enregistrées des versions 1 et 2 conservées ; circulation avant remplissage. | Modèles, sauvegardes et parcours architectural validés, avec omissions d’aménagement déclarées. |
| Monde et chargement | Réponses maritimes périmées écartées ; placements sauvegardés revalidés contre terrain, eau et collisions avant réapparition. | Régressions de modèle et chargements des parcours natifs validés. |
| Lore des factions | Quatre dossiers complémentaires, preuves physiques, décisions persistantes, retours des habitants et bulletins radio textuels. | Modèles et périmètre du parcours intégré validés ; aucune récupération de conversation non lue. |
| Bestiaire régional | Trois espèces du canon conservé incarnées par des variantes originales ; identités, dégâts et butin existants préservés. | Trois variantes testées sur banc contrôlé ; une espèce capturée dans le pilote natif. Le Gabian conserve une IA de sol. |
| Armures assistées | Conservation du système existant, opérations atomiques et entretien chez les techniciens des relais. | Régressions de simulation et périmètre armure du parcours intégré validés. |
| Objets emblématiques | Figurines SPECIAL, magazines et boissons Nuka-Cola, avec effets de jeu et acquisitions finies. | Modèles et boucles du parcours intégré validés, avec conservation après Continuer. |
| Diagnostics locaux | Invalidation immédiate de l’audit après modification des données ; fermeture d’un panneau sans faux diagnostic d’erreur serveur. | Régressions HTTP isolées et diagnostics des parcours natifs validés. |

## Validation livrée

Le [bilan courant](../verification/expansion/continuation/CONTINUATION_INTEGRATION.json) regroupe **1 847 contrôles réussis** sur le HTML `ea8ba2e3d9ba9ed1925628672f4c596475ff2437de06bfa7979ee03f6f59f0bf` :

| Méthode | Contrôles |
|---|---:|
| Unités et outils : 27 suites, sans test ignoré | 1 080 |
| Contrats hérités : quinze processus sans échec | 434 |
| Parcours natif architectural | 101 |
| Parcours natif intégré : lore, armure, collections et Continuer | 206 |
| Pilote natif de bestiaire : une espèce capturée | 23 |
| Sorties identiques de la reconstruction indépendante | 3 |

Les méthodes peuvent couvrir les mêmes mécanismes ; leur somme n’est pas un nombre de parcours équivalents. Les **23 captures natives** sont conservées avec les aides de placement et de simulation déclarées. Les trois variantes du bestiaire sont testées sur banc contrôlé, tandis que le pilote natif en capture une seule.

Les comparaisons de façades sont **hors du total de 1 847** : 191/191 contours courts ciblés avec porte conforme aux contrôles, 187/191 avec fenêtres, 72/72 approches complexes retrouvées, aucun débordement des segments source contrôlés et jusqu’à 12 624 ouvertures inventées paginées sur un objet. Elles ne constituent pas un inventaire des portes physiques de toute la commune. Les [1 492 contrôles du 24 octobre](../verification/expansion/architecture/ARCHITECTURE_INTEGRATION.json) restent historiques.

## Origine du lore

Les neuf factions, huit dossiers et vingt-cinq noms conservés dans la v0.46 constituent le canon disponible dans le dépôt. Le projet ChatGPT correspondant a été retrouvé dans l’application. La lecture de son historique renvoie actuellement une limitation temporaire de débit ; les archives ChatGPT ne sont pas accessibles depuis cette tâche cloud. Aucun contenu de conversation non lu n’est présenté comme récupéré.

Les dossiers ajoutés ici sont des prolongements écrits à partir de ce canon conservé. Ils restent distingués des éléments établis et des anciens fichiers v0.44 non récupérés. Les conversations privées et les autres projets de l’utilisateur ne sont pas copiés dans Git.

## Travaux de plus longue durée

La couverture des requêtes IGN sur la commune ne certifie pas chaque construction réelle ni chaque détail de façade ou de pièce. Les relevés absents, limites de circulation, programmes partiels et budgets de rendu restent déclarés. Le travail artistique final, les voix enregistrées, l’équilibrage complet, les performances sur matériel varié et une visite humaine exhaustive de la campagne restent des chantiers distincts. Cette itération ne les présente pas comme achevés.
