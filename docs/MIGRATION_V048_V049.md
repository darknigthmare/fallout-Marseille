# Migration v0.48 → v0.49

Les clés actives deviennent `fallout_mistral_save_v049`, `fallout_mistral_settings_v049` et `fallout_mistral_sandbox_v049`. La v0.48 reste dans la liste des sources héritées. Les emplacements manuels de carrière gardent leur format v0.35.

Le nouveau champ `state.v049` contient un schéma 1 et un dictionnaire d’acteurs. Les sauvegardes antérieures démarrent avec ce journal vide. À la première réinstanciation, les blessures/santés déjà présentes dans les systèmes historiques sont reprises si possible. Les données de position jamais sauvegardées auparavant ne peuvent pas être récupérées rétroactivement.

Les corps territoriaux historiques sont rassemblés par identité canonique. En cas de reliquats contradictoires, le minimum par objet est conservé pour éviter les duplications. Cette politique peut retirer un reliquat contesté ; elle ne donne aucun objet gratuit.

Les imports filtrent les acteurs inconnus, valeurs non finies, positions invalides et effets non reconnus. La campagne, les 248 sites, les quêtes, l’inventaire et les monnaies restent gérés par les systèmes historiques.
