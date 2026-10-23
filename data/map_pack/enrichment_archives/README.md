# Extraits IGN fournis

`manifest.json` épingle le ZIP local par son nombre d’octets et son SHA-256, puis chaque fichier extrait. Il contient les attributions et licences des fournisseurs. Le ZIP ne contient que l’index actif et le lot régional validé ; les anciennes versions locales ne sont pas distribuées.

Le lot comprend 1 404 objets bâtiment et 472 tronçons routiers BD TOPO interrogés sur `[43.293, 5.565, 43.300, 5.576]`, ainsi que deux grilles de relief : 174 777 nœuds RGE ALTI à environ 2 m sur ce secteur, et 145 396 nœuds d’un extrait MNT LiDAR HD à environ 0,5 m sur `[43.2956, 5.5698, 43.2976, 5.5718]`. Les bornes sont dans l’ordre sud, ouest, nord, est. Le relief LiDAR provient d’un relevé de 2021, édition 2025, reprojeté explicitement par échantillonnage au plus proche. Le pas ne certifie pas la précision du relevé.

Depuis la racine du dépôt :

```bash
python3 tools/world_source_bundle.py install
python3 tools/serve_game.py --no-browser
```

Le lancement normal restaure aussi cette archive avant d’ouvrir le serveur. Une installation existante validée est conservée. Un fichier corrompu ou un conflit arrête la restauration sans remplacer l’import utilisateur. `--no-prepare` saute la restauration des deux packs ; il est réservé aux dossiers déjà préparés.

Pour produire un nouveau lot à partir de sources réelles validées, dans un autre dossier de sortie :

```bash
python3 tools/world_source_bundle.py pack \
  --directory data/map_pack/enrichment \
  --archive /tmp/nouveau-lot/sources.zip \
  --receipt /tmp/nouveau-lot/manifest.json
```

Le nom final du ZIP dépend de son contenu. `pack` refuse un reçu existant sans `--replace`. L’index et les données extraites restent ignorés dans Git ; l’archive, son reçu et les [preuves d’acquisition](../../../implementation/real-sources/) sont distribués. Les scripts de test utilisent des fixtures temporaires distinctes.

Consulter les [sources publiques](../../../docs/SOURCES_GEOGRAPHIQUES_PUBLIQUES.md) et le [format d’import](../../../docs/IMPORT_SOURCES_REELLES.md) pour les projections, NoData, hauteurs, couvertures et limites. Ces extraits ne couvrent pas toute Marseille et ne fournissent ni façades ni intérieurs réels.
