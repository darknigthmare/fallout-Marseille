# Installation cartographique v0.40

La v0.40 utilise le même format de pack vectoriel et terrain que la v0.39.

```bash
python3 tools/install_real_map_v039.py --endpoint cloud
python3 tools/audit_real_map_v039.py --require-local
```

Les preuves de corridor sont déjà intégrées dans `data/corridors/` et dans le HTML autonome. Elles n’ajoutent pas les tuiles elles-mêmes au ZIP compact.
