# Architecture v0.41

## Cloud
- Bucket privé `fallout-mistral-local-pack-v041`.
- 24 objets Base64 immuables construits à partir du cache vectoriel privé.
- Fonction Edge JWT `fallout-mistral-local-pack-v041` : `/manifest` et `/chunk/{name}` seulement.
- Décodage Base64 côté Edge et réponse binaire ZIP.
- Constructeur, index et fenêtre de liens temporaires neutralisés en HTTP 410.

## Client Python
- Téléchargement parallèle borné.
- Cache de chunks reprenable.
- Validation ZIP et anti-Zip-Slip.
- Validation de chaque entrée contre le manifeste interne.
- MVT réellement décodé avant extraction.
- Installation atomique.
- Installation terrain v0.39 chaînée.

## Jeu
- Snapshot embarqué pour le mode hors ligne.
- Statut local lu depuis `data/map_pack/local_pack_v041_status.json`.
- Benchmark lu depuis `data/map_pack/benchmark_v041.json`.
- Absence de fichier = état « non installé », jamais 100 % fictif.
