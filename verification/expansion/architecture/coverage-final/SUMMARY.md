# Comparaison externe de l’architecture : données IGN réelles

Comparaison des modules figés avec les snapshots exacts du commit `cac50f305db69fcd4827da2c8ac34295e8b68d7a`. Aucun fichier de production, aucune donnée source et aucun livrable généré n’ont été modifiés par cette QA. Projection Lambert-93 et origine `(43.285, 5.51)` identiques à la production ; hauteurs issues du vrai `buildingProfile`.

La sélection ciblée lit 109 chunks distincts (356,136,598 octets) déjà référencés par l’audit précédent ; le corpus complet n’a pas été rescanné. Les résultats détaillés et les empreintes figurent dans `ATTRIBUTES_COMPARE.json` et `CURVES_COMPARE.json`.

| Cas réel vérifié | Baseline | Après correction |
| --- | ---: | ---: |
| Faux rejets à 1,95 m, acceptés sans changer hauteur ni niveaux | 0/27 | 27/27 |
| Exemples `nombre_d_etages=0` attribués à tort à IGN | 12/12 | 0/12 |
| Vrais conflits de hauteur toujours refusés, niveaux déclarés conservés | 18/18 | 18/18 |
| Contours courts avec porte passant les contraintes intérieures contrôlées | 0/191 | 188/191 |
| Contours courts avec fenêtres générées | 0/191 | 183/191 |
| Arêtes exclues du premier parcours de 64 candidats, retrouvées et rendues | 0/72 dans la sélection initiale | 72/72 avec proximité/préférence |

Les sept catégories d’usage ambigu ont été comparées sur des objets réels : les usages explicitement résidentiel, commercial et sportif prennent désormais priorité sur la nature générique « Industriel, agricole ou commercial ». Ces exemples ne constituent pas un nouveau comptage individuel des 2 504 objets concernés dans l’audit initial. De même, les 12 exemples de niveaux zéro ne sont pas une nouvelle vérification de l’ensemble des 355 valeurs zéro de l’atlas.

Les 27 cas de seuil sont isolés par une matrice croisée : le module intérieur actuel les accepte avec les niveaux de façade baseline, tandis que le module intérieur baseline les refuse avec les niveaux actuels. Le résultat provient de la tolérance numérique et conserve les dimensions source. Les véritables conflits de hauteur retenus dans le rapport attributaire restent distingués des arrondis.

La tribune `batiment.39111842` passe de 22 niveaux inventés à un volume fonctionnel inventé ; le bâtiment religieux `batiment.49696442` passe de 15 à un volume de nef inventé. Le volume commercial de 143,9 m `batiment.26019993` conserve son niveau source déclaré. Ces choix ne sont pas des relevés d’étages ou de pièces.

## Contours courts : résultats et limites restantes

Les 191 contours avaient chacun un point intérieur avec au moins 0,43 m de dégagement, une enveloppe suffisamment haute et une bbox minimale de 2 m. Leur compatibilité géométrique ne documente pas un usage habitable. Aucun span d’ouverture contrôlé ne dépasse les segments source ; les anneaux et hauteurs sont inchangés.

| Objet sans candidat porte | Motif observé |
| --- | --- |
| `batiment.10611104` | 88 segments, maximum 0.200 m ; 26 virages >45° ; aucune chaîne admissible. Limite conservatrice du modèle, pas preuve d’impossibilité physique. |
| `batiment.10626012` | 89 segments, maximum 0.142 m ; 35 virages >45° ; aucune chaîne admissible. Limite conservatrice du modèle, pas preuve d’impossibilité physique. |
| `batiment.9609229` | 6 segments, maximum 1.273 m ; 6 virages >45° ; aucune chaîne admissible. Limite conservatrice du modèle, pas preuve d’impossibilité physique. |

Absences de fenêtres : candidate-clearance-height-or-door-overlap : 2; no-three-segment-chain-with-turns-at-most45deg : 3; technical-typology-without-window-register : 3. Les silos techniques sans registre de fenêtres suivent un programme cohérent ; une absence de fenêtre inventée n’est pas un défaut documentaire mesuré.

Le contrôle négatif `batiment.10615286`, exclu des 191 parce qu’aucun point avec dégagement suffisant n’avait été trouvé, possède des candidats de façade mais aucun candidat passant le contrôle intérieur. Les résultats ne transforment pas un décor de porte en promesse d’accès.

## Exemple à 84 segments

`batiment.9375075` conserve ses 84 segments, environ 6,10 m de diamètre, 7.6 m de hauteur et deux niveaux estimés. Sa nature est « Indifférenciée », son usage principal « Indifférencié » ; usage secondaire, nombre d’étages et nombre de logements sont absents. Le programme résidentiel est donc une hypothèse inventée.

Le modèle passe de zéro ouverture à 1 porte et 11 fenêtres ; 12 ouvertures sont entièrement rendues dans le budget de 512 quads. La porte est découpée sur plusieurs segments d’origine, avec 0.950 m de dégagement à son point intérieur.

Le plan intérieur reste inventé : mobilier placé `sanitary, kitchen, wardrobe, washbasin` ; fonctions demandées omises : bed (metric-fit-or-access), sofa (metric-fit-or-access), dining (metric-fit-or-access). Pièces encloses : 1, aire enclose 5.76 m² sur 29.22 m². Le contrôle de navigation échantillonné rapporte 0 nouvelle cellule inaccessible. Cela ne certifie pas un ameublement résidentiel complet ni une circulation native exhaustive.

## Pagination et accès sur grandes emprises

| Objet réel | Niveaux baseline → actuels | Échantillon actuel plafonné à 4 096 | Inventaire complet paginé |
| --- | ---: | ---: | ---: |
| `batiment.49696442` | 15 → 1 | 1814 | 1814 |
| `batiment.49696644` | 12 → 12 | 4096 | 12588 |
| `batiment.49693149` | 2 → 2 | 1129 | 1129 |
| `batiment.39111842` | 22 → 1 | 339 | 339 |

Les tailles de page 31, 128 et 4 096 produisent la même séquence sans doublon ; chaque parcours atteint le dernier slot et examine exactement l’inventaire déclaré. Les 72 approches testées couvrent des arêtes réellement absentes de la sélection baseline sur six contours complexes. Chaque porte retrouvée passe les contrôles métriques de dégagement/hauteur et est présente dans le rendu borné.

## Portée de la preuve

Aucun navigateur, déplacement natif, terrain de seuil, collision avec les voisins, droit d’accès public ou plan réellement documenté n’a été certifié ici. Les façades et les intérieurs générés sont fictifs ; seuls les contours, attributs et hauteurs cités proviennent de la source IGN. Le rapport constate une amélioration quantifiée et ses résidus, sans annoncer une fidélité documentaire intégrale.

Modules figés :

- `07_facades.js` : `9ccc2c01a9c91d5b1c2f0611f8d18c814f2616e0ec9711b37393c2cb78ec8335`
- `08_city_interiors.js` : `94fc240ce308f71c0618ae1c1fec611b00b9867b2a91355579c3615b33cf7ce5`

Reproduction : définir `MISTRAL_REPO_ROOT` vers le clone et `MISTRAL_BASELINE_DIR` vers le dossier `coverage-initial`, puis lancer `node curves_compare.cjs --final`, `node attributes_compare.cjs` et `python summarize.py` depuis ce dossier. `MISTRAL_AUDIT_OUTPUT_DIR` permet de choisir un autre dossier de rapports ; par défaut, les rapports sont écrits à côté des scripts. Les valeurs par défaut conservent le premier environnement de QA.
