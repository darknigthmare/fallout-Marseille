# Migration v0.36 → v0.37

La v0.37 utilise les clés `fallout_mistral_save_v037`, `fallout_mistral_settings_v037` et `fallout_mistral_sandbox_v037`. Les clés v0.36 et antérieures restent des sources de migration.

Le nouveau bloc `state.v037` conserve les préférences de préchargement, le budget local et les compteurs de session. Les sauvegardes v0.36 reçoivent des valeurs prudentes : cache automatique activé, anticipation limitée et aucun fichier déclaré acquis sans lecture réelle.

Le cache IndexedDB v0.36 est mis à niveau vers la version 2 avec métadonnées. Les anciennes entrées binaires valides restent lisibles ; les compteurs détaillés apparaissent à mesure de leur réutilisation.
