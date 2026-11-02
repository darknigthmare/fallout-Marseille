# Chantiers du 2 novembre 2026

La poursuite de `c3cd2a3` travaille les menuiseries, les habitations, les holobandes, deux créatures récurrentes, les surfaces MNS et la présentation FPS/HUD. Elle conserve les corrections routières, annulations indépendantes et contrôles des quatre sorties générées déjà intégrés. Les sources géographiques ne sont pas remplacées par les créations du jeu.

| Chantier | Comportement livré et vérifié | Portée et limite |
| --- | --- | --- |
| FPS et HUD | Visée progressive, rotation cyclique et notifications de 12 px placées dans l’espace libre, avec défilement si nécessaire. | Présentation liée aux commandes et événements réels ; profils, munitions et règles de tir conservés. Les formats exécutés et le repli faute de place sont explicités dans le bilan. |
| Menuiseries | Moulures, poignées en relief, feuillures et ferrures des baies inventées. | Kits entiers dans les budgets existants ; cotes documentées et passage inchangés, détails absents au niveau bas. |
| Habitations | Programme domestique layout 6 pour les nouvelles visites inventées admissibles ; salle d’eau privée, chambre et cuisine selon place et circulation. | Registres bornés sans éviction et porte retenue stable. Anciennes visites 1–5 préservées, nouvelles visites documentées en 5 ; omissions visibles, douche et réfrigérateur hors service. |
| Holobandes | Trois textes originaux de cinq segments chacun, présents dans les scènes et relais correspondants. | Collecte physique unique, lecteur RADIO → HOLODISQUES et marque-pages existants ; aucune voix ni nouvelle récompense de dossier. |
| Bestiaire | Goule sauvage et Griffe de la mort articulées, blessures et préparation visuelle de leurs attaques existantes. | Mêmes identités, PV, règles et butins ; assemblages originaux, sans nouvel ennemi créé par la présentation. |
| Surfaces connues | Quatre composantes MNS supplémentaires dans les contextes Bourse/Opéra ; cinq reçus sources au total. | 23 enregistrements, 22 admissibles, lot de 142 427 triangles supérieurs. Pas de façade ou d’intérieur mesuré, ni nouvelle association documentaire certifiée pour la Bourse. |

## Ce qui reste ouvert

- **Fidélité de Marseille.** Étendre les relevés, documenter les façades et pièces, traiter les absences et visiter les accès. Les contours IGN, le MNT et le MNS supérieur ne constituent pas un modèle architectural complet.
- **Art et mise en scène.** Développer les finitions, animations, voix et effets. Les armes, créatures et équipements actuels restent stylisés.
- **Intérieurs et circulation.** Approfondir les usages inventés et les grands volumes, avec omissions explicites. Les nouvelles habitations gardent leurs limites de pièces et d’équipement ; les anciens plans ne sont pas réécrits pour recevoir le nouveau programme.
- **Collection des bandes.** Les trois nouveaux identifiants sont inclus dans le compteur global de bandes. Leur collecte ne déclenche toutefois pas encore les badges hérités des seuils **10, 30, 60 et 81**, dont le déclenchement appartient à l’ancien collecteur. Ce raccordement cosmétique reste ouvert ; aucune capsule, expérience ou ressource n’est liée à ces badges.
- **Campagne et équilibrage.** Développer le canon, les branches et les conséquences avec réserves finies. Les holobandes complètent le récit sans décider à la place du joueur.
- **Matériel et parties continues.** Mesurer les performances et tester tactile/manettes sur appareils physiques, puis les parcours humains complets. Les aides et API émulées restent identifiées.

Les services et dépôts, distributeurs, dossiers et contre-dons, armures assistées, collections, consommables, grenades, mines, bivouac et entraide restent dans le programme existant. Les cartes municipales conservent 290 partitions, 291 001 identifiants d’objets bâtiment, 55 449 tronçons routiers et 118 partitions d’eau.

## Preuves de la poursuite

Le [bilan du 2 novembre](../verification/expansion/city_continuation_20261102/CITY_INTEGRATION.json) rattache **3 318 contrôles descriptifs réussis, 13 méthodes et 100 événements de capture native**, sans échec, au HTML `4581c0c29ce5c74da3aba7430227fba844aed1eb40f1b1fc4d7965c7a6600d78`. Les modèles avec fixtures, comparaisons de sources, parcours assistés et entrées émulées gardent leurs périmètres ; leur somme ne représente pas autant de parties humaines. Les six contrôles supplémentaires de livraison du service worker restent hors de ces totaux.

Les deux phases QA conservent le même HTML et les mêmes données du jeu. Dix reçus de phase A gardent leurs scripts exécutés et archives d’origine. En phase B, seul le pilote de façade corrige une comparaison brute Node/Chromium : les relations WGS84, CLEABS et identités natives restent strictes, avec l’EPS métrique préexistant de 10⁻⁷ m pour des écarts de projection inférieurs à deux nanomètres. Ses 98 contrôles sont rattachés à cette phase. Aucune source de jeu ni donnée géographique ne change entre les phases.

Le [bilan intégré du 1er novembre](../verification/expansion/continuation_20261101_integrated/CONTINUATION_INTEGRATION.json) conserve **3 312 contrôles et 76 captures** sur `c0f13de3…` à titre historique. Le [bilan avant intégration](../verification/expansion/continuation_20261101/CONTINUATION_INTEGRATION.json) garde ses 3 310 contrôles sur `98a78a1c…`. Les scripts, sources, captures, aides et événements réseau de chaque campagne gardent leur identité. Leur somme ne représente pas autant de parties humaines ; aucun ancien succès ne sera attribué à un autre HTML.

La reproduction intégrale 1:1 de toutes les façades et intérieurs de Marseille reste non certifiée. Les créations cohérentes et les relevés partiels sont distingués ; la distribution Drive n’a pas été actualisée pour cette poursuite.

La livraison `29df190` conserve ses [2 892 contrôles descriptifs et 55 captures](../verification/expansion/immersion/IMMERSION_INTEGRATION.json) sur le HTML `844376c014575111f268f292c8307bb3f47ac33629604406f5e0da00104c5a34`. Les [2 887 contrôles et 62 captures de `f4a7337`](../verification/expansion/wasteland/WASTELAND_INTEGRATION.json), sur le HTML `ed6e4103b23a45c413fef182862a93accb72ec25c6e1d8b101251822bfd5c670`, restent historiques. Le [bilan de précision antérieur](../verification/expansion/precision/PRECISION_INTEGRATION.json) conserve ses 2 324 contrôles, 42 captures et ses propres sources ; ses 288 comparaisons de cellules ne sont pas recomptées. Aucun de ces bilans ne valide automatiquement le programme courant. La distribution Drive n’a pas été actualisée pour cette poursuite.

[État de production](STATUT_PRODUCTION.md) · [Marseille entière](MARSEILLE_ENTIERE.md) · [Commandes](CONTROLES.md).
