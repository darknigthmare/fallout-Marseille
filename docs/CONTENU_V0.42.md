# FALLOUT : MISTRAL — v0.42
## Couche Fallout territoriale

La v0.42 pose une couche de jeu persistante au-dessus de la cartographie réelle sans modifier les routes, le cadastre ou le relief officiels. Les implantations Fallout sont fictives mais utilisent des coordonnées WGS84 stables.

## Catalogue global

- **248 sites** au total, soit 31 par macro-région ;
- **16 abris** ;
- **24 colonies** ;
- **24 avant-postes** ;
- **48 autres lieux visitables** ;
- **64 nids de créatures** ;
- **24 repaires élites** ;
- **8 boss régionaux** ;
- **24 points de repère** ;
- **16 haltes caravanières**.

Le catalogue représente **200 postes PNJ potentiels** et **720 emplacements ennemis potentiels**. Ils ne sont jamais tous instanciés en même temps : le moteur charge uniquement les sites proches, avec un budget local réglable.

## Population et factions

Les colonies, haltes et avant-postes génèrent des habitants persistants selon leur faction locale. Les PNJ proposent du contexte régional, du commerce simple et des contrats vers les menaces encore actives de la même macro-région.

## Hostiles

La couche réutilise 41 familles existantes du bestiaire et distingue : groupes ordinaires, élites, escortes et boss régionaux. Les sécurisations, éliminations d’élites et boss vaincus sont enregistrés dans la sauvegarde. Les sites ordinaires peuvent réapparaître après leur délai de respawn ; les boss restent vaincus.

## Lieux visitables

Les 16 abris et 48 autres sites visitables utilisent une architecture intérieure configurable selon leur thème : abri, bunker, hôpital, dépôt, carrière, grotte, station, laboratoire, ouvrage maritime, fort ou abbaye. Chaque instance possède six sous-zones, une route principale, un terminal de lore, des menaces et un objectif persistant.

## Pip-Boy

`MAP → COUCHE FALLOUT` affiche les sites connus, les signatures majeures inconnues, les filtres, le repère actif et la progression par macro-région. Les marqueurs peuvent être suivis depuis le Pip-Boy.

## Streaming

Le catalogue complet reste léger. Props, collisions, PNJ et ennemis ne sont créés que près du joueur. Le budget par défaut est de sept sites actifs et peut être ajusté entre trois et douze.
