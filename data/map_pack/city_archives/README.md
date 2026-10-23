# Sources géographiques de Marseille

Le reçu `manifest.json` épingle une archive ZIP adressée par son SHA-256 et chaque fichier qu’elle contient. `tools/city_sources.py` vérifie les tailles, empreintes, membres, géométries, sources et la couverture administrative avant restauration. Les extractions dans `data/map_pack/city/` sont régénérables et ne doivent pas être ajoutées directement dans Git.

```bash
python3 tools/city_sources.py install
python3 tools/city_sources.py audit
```

Le serveur normal appelle cette restauration hors réseau. Un ensemble utilisateur déjà valide est conservé ; un ensemble corrompu n’est pas remplacé silencieusement. L’archive des enrichissements historiques autour d’Aubagne reste distincte.

La limite de référence est l’objet officiel IGN BD TOPO de la commune **13055, Marseille**, comprenant ses îles. Chaque rectangle intersectant ce polygone est interrogé intégralement pour les bâtiments et tronçons routiers, puis subdivisé lorsque le budget du streaming l’exige. L’index vérifié ne peut annoncer une couverture complète si une sous-partition manque. Tous les objets retournés par ces requêtes sont conservés entiers, y compris les rares retours conservateurs de l’index spatial de l’IGN. Les compteurs incluent donc une bordure hors de Marseille et décrivent des objets BD TOPO, pas des adresses ni un nombre d’immeubles physiques ; ils ne garantissent pas que chaque objet touche géométriquement le territoire communal.

Les reliefs, lorsqu’ils sont présents, conservent leur espacement demandé, leurs absences de mesure et leur provenance. Le pas d’échantillonnage et le nombre de décimales ne garantissent pas une précision absolue identique. Les hauteurs, matériaux et usages inconnus restent inconnus dans l’archive. Les façades et intérieurs inventés par le jeu sont distincts de ces données officielles.

L’atlas d’eau facultatif conserve ses deux réponses sources IGN, son trait de côte des plus hautes eaux et les découpes exactes de ses polygones. Son niveau de rendu nominal à zéro n’est pas une mesure instantanée de la marée. L’archive complète est bornée à 1 Gio décompressé ; chaque partition vectorielle reste limitée à 3 000 objets et 8 Mio.

Pour effectuer une nouvelle acquisition, qui peut recevoir une édition différente des services distants :

```bash
python3 tools/acquire_city_world.py --workers 3
python3 tools/acquire_city_terrain.py --help
python3 tools/city_sources.py pack
```

Une acquisition entière est validée avant publication de l’index. `--replace` doit être donné explicitement pour remplacer un index ou un reçu existant. Le cache des réponses HTTPS originales et leurs reçus restent dans `/workspace/.cloud-setup/fallout-marseille/city-acquisition/` ; les preuves publiques synthétiques sont sous `implementation/city-sources/`.

Sources : **IGN — Géoplateforme**, **Licence Ouverte 2.0**. Les dates de téléchargement et celles des objets ou relevés restent séparées dans les données et reçus.
