# Façades : menuiseries métriques et persiennes

La poursuite du **2 novembre 2026** complète les menuiseries inventées par des
assemblages en relief : moulures des panneaux de porte, poignées à face relevée
et retours chanfreinés, feuillures de châssis et montants, cadres d’atelier en
métal stylisé et ferrures de persiennes. Les appuis, tableaux et lames inclinées
déjà présents sont conservés. Ces ajouts restent des choix artistiques ; un usage
IGN n’atteste ni leur matériau, ni leur dessin, ni leur période de construction.

Les nouvelles surfaces possèdent de vraies différences de profondeur et de
normale. Les poignées atteignent 7,4 cm du plan du mur, sous la limite existante
de **7,5 cm** ; leurs quatre retours et leur face avant sont triangulés. Les
ferrures comportent une platine et deux faces opposées pour le gond. Elles
restent dans les panneaux de persiennes déjà acceptés, sans empiéter sur une
baie voisine. Aucun mur IGN, seuil physique, collision ou passage n’est modifié.

Les assemblages suivent les usages : panneaux moulurés pour l’habitat,
feuillures vitrées pour les commerces et bâtiments publics, cadres emboutis pour
les portes de service et ateliers, cadres de nef pour les volumes religieux.
Une baie documentée ne reçoit aucun de ces assemblages inventés : ses cotes et
son enveloppe restent celles du document. Les entourages extérieurs inventés
préexistants gardent leur provenance distincte.

Au niveau rapproché, **douze baies inventées au plus par bâtiment** sont
candidates, avec priorité aux entrées puis aux baies basses. Une réserve de 25 %
du budget encore libre après les menuiseries ordinaires, plafonnée à **64 quads**,
finance les nouveaux assemblages. Chaque kit est réservé en entier avant
émission, y compris sur les contours quantifiés. Ce plafond s’inscrit dans les
512 quads par bâtiment, les 8 192 quads de scène et le cache existants ; il ne
s’y ajoute pas. La réservation peut reporter un entourage ou une ferrure, avec
une raison comptabilisée. Les faces d’ouvertures conservent leur inventaire, et
les deux niveaux de détail gardent exactement leur passage. Le niveau bas
n’ajoute aucune quincaillerie.

Les diagnostics `joinery` ajoutent les types `joinery-relief` et
`shutter-hardware`, leurs variantes, plages de sommets et réservations.
`detailCoverage.joineryCoverage` expose `joineryReliefQuads`,
`maximumJoineryReliefQuads` et `joineryReliefEnabled` ; le compteur de quads
comprend les vrais fragments sur les segments source. L’API en lecture seule
`v055FacadeProfileGeometry` renvoie aussi ces véritables triangles publiés.

La nouvelle commande `node tests/expansion/facades_hardware.cjs` a exécuté
**18 contrôles de modèle** sur les cinq mêmes empreintes IGN et des cas
documentaires, de cour et de pente explicitement synthétiques. Elle vérifie les
retours et normales, les ferrures, les réservations de 8 à 4 096 quads, les
anneaux inversés, les documents, le cache et l’identité complète de l’inventaire
des baies avec le modèle précédent. Les quatre suites antérieures sont
conservées. Ces contrôles de géométrie ne constituent pas des captures de jeu ni
une validation humaine des façades ; le parcours navigateur de la livraison
intégrée porte son propre HTML et ses propres captures.

## Validation native actuelle : phase B du 2 novembre 2026

Le [parcours natif des assemblages](../verification/expansion/city_continuation_20261102/facades/FACADE_HARDWARE_NATIVE.json)
se termine avec **98/98 contrôles réussis**, un code de sortie réel de 0 et
**12 captures brutes**, toutes ouvertes pour revue et vérifiées par SHA-256.
Il utilise le HTML final
`4581c0c29ce5c74da3aba7430227fba844aed1eb40f1b1fc4d7965c7a6600d78`
et les cinq profils IGN acquis ci-dessous. Un seul contexte Chromium est créé ;
le serveur local est fermé à la fin. Les contrôles couvrent les triangles
réellement publiés, les budgets, l'inventaire des ouvertures et le passage
inchangés, ainsi qu'une entrée par la touche E et un retour effectifs.

Les coordonnées WGS84, les CLEABS et l'identité commune du composant natif,
de la façade et du portail sont comparés strictement. Chaque sommet projeté
est contrôlé dans son ordre avec une tolérance de **1e−7 m**. Les écarts entre
les projections Node et Chromium restent inférieurs à **2 nm** : le maximum
mesuré est de `1,862645149230957e−9 m`. La projection Chromium et les sommets
natifs concordent exactement. Ces différences numériques sont publiées ;
aucune géométrie source ni identité du jeu n'est modifiée pour les effacer.

Les gros plans résidentiels supplémentaires, commercial et industriel montrent
les retours, persiennes ou poignées inventés. Le contexte résidentiel fixe est
largement masqué par un mur ; le gros plan du contour micro-courbe montre surtout
le sol et une façade coupée en haut, sans preuve visuelle lisible de sa petite
quincaillerie. Les détails et l'intérieur restent inventés, et ces captures ne
certifient ni un relevé des façades, ni une reproduction visuelle exhaustive de
Marseille.

Les baies inventées possèdent désormais une menuiserie visible : panneaux et
poignées de portes, entrées vitrées, doubles vantaux de service, montants et
traverses de fenêtres, vitrines à imposte et paires de persiennes à lames ouvertes.
Ces éléments complètent les emprises et hauteurs disponibles ; leurs formes,
couleurs, assemblages et positions ne constituent pas un relevé architectural.

L’usage IGN choisit une famille cohérente : panneaux pour l’habitat, vitrage pour
les commerces et équipements publics, vantaux de service pour l’industrie,
vitrages rectangulaires pour les volumes religieux. Une largeur disponible de
1,65 m déclenche deux vantaux. Un usage résidentiel principal reste prioritaire
sur la mention secondaire « Annexe » ; une annexe sans usage plus précis reçoit
une porte de service et aucune persienne résidentielle. Ces choix restent
explicitement inventés, même lorsque l’usage provient d’IGN.

Une porte décorée conserve sa largeur, sa hauteur, son altitude et sa largeur
projetée de passage. Les ajouts n’introduisent aucune collision. Chaque rectangle
suit le segment source auquel il appartient, y compris sur les contours courbes
quantifiés ; aucun segment, angle, anneau ou cour n’est redressé. Les détails
restent dans la hauteur du volume et à 7,5 cm au plus du plan de façade.

Les persiennes sont placées sur le mur de part et d’autre d’une baie. Elles ne
recouvrent ni le vitrage, ni une autre ouverture retenue, ni une ouverture
documentée, ni une paire de persiennes déjà allouée. Une largeur de mur
insuffisante laisse la paire entière absente, avec une raison explicite.

Les portes et fenêtres documentées conservent exactement leur enveloppe. Elles
ne reçoivent ni meneau, ni dessin de vitrage, ni persienne inventés à l’intérieur
de cette enveloppe. Les entourages éventuellement ajoutés sont identifiés
séparément comme détails inventés ; l’attribution du document est conservée.
Le modèle expose `documentary-joinery-not-supplied` lorsqu’aucune menuiserie
documentaire n’est disponible.

Toutes les surfaces de baies retenues sont réservées avant le décor. Chaque
ensemble de menuiserie, d’entourage ou de persiennes est ensuite réservé en
entier : il ne s’arrête pas à mi-vantail lorsque le budget est atteint. Une part
bornée du budget restant, plafonnée à 128 quads, permet aux persiennes d’apparaître
au niveau de détail rapproché. Les reports distinguent manque de budget,
réservation pour les persiennes, conflit voisin et manque de mur. Le niveau bas
conserve les faces d’ouverture et indique explicitement l’absence de menuiserie.
Les plafonds de scène, de bâtiment et de cache restent ceux du moteur.

Les entourages rapprochés possèdent maintenant une profondeur géométrique :
les tableaux chanfreinés relient un bord extérieur à 1,2 cm du mur à une arête
intérieure à 7,1 cm. Les appuis de fenêtre comportent une face inclinée et un
dessus horizontal réellement triangulé, orienté vers le haut. Les lames des
persiennes sont inclinées entre 4,1 et 7,3 cm, devant leur panneau à 3,8 cm ;
elles ne sont plus de simples bandes coplanaires. La projection maximale reste
7,5 cm et ces ajouts restent entièrement dans la hauteur existante du volume.
Ces profils sont inventés, sans attribution de matériau ou de période mesurée.

Les profils suivent les mêmes segments source, avec interpolation de leurs
profondeurs lorsque leur largeur traverse une courbe quantifiée. Une inversion
d'anneau conserve leur position physique et l'orientation supérieure des
appuis. Aucun obstacle ni collision de seuil n'est ajouté aux portes. Les baies documentées
gardent leur enveloppe ; seul leur entourage extérieur, déclaré inventé, peut
recevoir un profil. La réservation des persiennes tient aussi compte du coût
d'une paire entière sur les contours courbes, dans le plafond existant de
128 quads réservés.

`v050FacadeBuilding(id)` expose les ensembles rendus, leurs plages de sommets,
leur provenance et les raisons des reports dans `joinery` et
`detailCoverage.joineryCoverage`. Les listes de diagnostic restent limitées et
signalent leur troncature.

`v055FacadeProfileGeometry(id, openingIndex)` renvoie des copies des véritables
plages de sommets et de triangles déjà publiées pour une seule baie. L'export
reste borné par le budget natif du bâtiment, au plus 2 048 sommets au niveau
rapproché actuel ; il ne régénère pas un modèle à la place de la géométrie du
jeu. Les compteurs distinguent les profils réellement rendus des reports.

Les codes bruts de matériaux IGN ne sont pas transformés en matériaux supposés.
Les dates de création de la base ne sont pas traitées comme des dates de
construction. Les 299 790 occurrences de bâtiments des partitions locales
inspectées ne fournissent aucun champ `roof:shape`, `roof:height` ou
`roof:direction` : cette évolution ne modifie donc aucune toiture ou collision
de toiture. Les occurrences incluent des objets répétés entre partitions.

Les tests exécutent le module livré sur cinq objets IGN acquis sous Licence
Ouverte 2.0, avec coordonnées, attributs, provenance et empreintes conservés dans
[les fixtures](../tests/expansion/fixtures/facades_joinery_ign.json) :

Le tableau suivant conserve les observations du lot de menuiseries initial,
avant les assemblages du 2 novembre ; il ne réattribue pas ses captures au
nouveau programme.

| Cas | Identifiant source | Observation initiale au budget 512 quads |
| --- | --- | --- |
| Résidentiel, usage secondaire Annexe | `batiment.10610455` | Porte à panneaux, 65 menuiseries, 8 paires de persiennes |
| Commercial et services | `batiment.10618211` | Entrée vitrée et vitrines à imposte |
| Industriel | `batiment.9618398` | Porte de service à deux vantaux et trames d’atelier |
| Église | `batiment.10612440` | Panneaux d’entrée et vitrages de nef |
| Contour micro-courbe quantifié | `batiment.10611104` | 12 menuiseries et une paire de persiennes entière sur segments source |

Les plans documentaires des régressions sont synthétiques et identifiés comme
tels. La nouvelle suite couvre aussi les réservations, conflits, inversions
d’anneaux, cours et budgets de cache. Commandes :

```sh
node tests/expansion/facades_model.cjs
node tests/expansion/facades_coverage.cjs
node tests/expansion/facades_joinery.cjs
node tests/expansion/facades_relief.cjs
node tests/expansion/facades_hardware.cjs
node tests/expansion/facades_joinery.cjs --camera-points
```

Les quatorze contrôles de relief vérifient les profondeurs, normales des
appuis, lames inclinées, réservations courbes, copies du diagnostic, cours,
enveloppes documentaires et budgets sur les cinq mêmes objets IGN.

## Historique : parcours architectural du 26 octobre 2026

Le parcours natif architectural du 26 octobre conserve ses 135 contrôles
antérieurs et ajoute seize contrôles de profils, soit **151/151**, avec treize
captures brutes, dans un contexte de navigateur unique. Les vraies plages de
sommets publiées confirment les chanfreins, les dessus d'appui et douze lames
inclinées sur une paire résidentielle. La vue commerciale rapprochée et la vue
résidentielle d'entrée montrent les détails ; un zoom de baie basse mal cadré,
sous le relief voisin plus grossier, reste conservé et n'est pas présenté comme
une preuve visuelle des persiennes. Ce parcours assisté ne certifie pas une
visite exhaustive ni un relevé documentaire de toutes les façades.

Les [points de contrôle épinglés du lot initial](../tests/expansion/fixtures/facades_joinery_cameras.json)
conservent les SHA-256 historiques du module, du générateur et des fixtures IGN.
La commande actuelle ci-dessus calcule les points et empreintes du module
courant sans modifier cette preuve antérieure.
La dernière commande fournit les coordonnées géographiques, identités, vues
d’entrée et de fenêtre, ainsi que les limites de rendu. Ce sont des points de
contrôle du modèle destinés à la QA native ; l’entrée choisie par le moteur doit
être revérifiée après la liaison au relief. Ces points ne sont pas des captures
de jeu ni une preuve d’accès au bâtiment.
