# Migration v0.30 → v0.35

La v0.35 utilise `fallout_mistral_save_v035`, `fallout_mistral_settings_v035` et une clé d’exploration v035. Les clés v0.30 à v0.18 restent des sources de migration.

Le nouveau bloc `state.v035` ajoute carrière, opérations, hub, prologue, session et emplacement actif. Une sauvegarde ancienne reçoit des valeurs neutres : aucun record, aucune prime et aucun NG+ inventé.

Les sauvegardes manuelles sont des enveloppes séparées sous `fallout_mistral_slot_v035_1` à `_3`. L’autosave utilise `fallout_mistral_autosave_v035`.
