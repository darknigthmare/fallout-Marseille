# Migration v0.35 → v0.36

La v0.36 utilise :

- `fallout_mistral_save_v036`
- `fallout_mistral_sandbox_v036`
- `fallout_mistral_settings_v036`

Les clés v0.35 et antérieures restent parmi les sources de migration.

Le nouveau bloc `state.v036` conserve la préférence relais/direct, le transfert automatique entre macro-régions et des compteurs de session. Il ne supprime aucune quête, conclusion, carrière ou sauvegarde manuelle de la v0.35.

Une ancienne partie continue de fonctionner dans les instances scénarisées. Entrer dans un extérieur réel active simplement le nouveau pipeline de streaming.
