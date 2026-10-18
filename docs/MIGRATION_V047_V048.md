# Migration v0.47 → v0.48

Les clés actives deviennent `fallout_mistral_save_v048`, `fallout_mistral_settings_v048` et `fallout_mistral_sandbox_v048`. Les clés v0.47 demeurent dans la chaîne de lecture héritée.

La v0.48 n’ajoute pas de données volumineuses aux sauvegardes. La préparation et la rétention de scène restent en mémoire de session. Une sauvegarde d’intérieur qui n’a plus de scène retenue utilise le chargement validé normal. Le catalogue et les progrès de campagne ne sont pas remplacés.
