# Migration 0.29 → 0.30

Clés : `fallout_mistral_save_v030`, `fallout_mistral_sandbox_v030`, `fallout_mistral_settings_v030`. Les anciennes clés demeurent lisibles, non supprimées ; les paramètres et l’exploration v0.29 sont cherchés avant les versions précédentes.

L’objet `v030` ajoute six pièces par modèle assisté possédé, configuration, cœur installé, réserve bornée de cœurs entamés, historique et enquête. Sans cet objet, l’intégrité moyenne historique initialise chaque plaque. Aucun cœur, châssis supplémentaire ou résultat d’enquête n’est fabriqué par la migration.

Les charges doivent être numériques, finies et positives, plafonnées à 100 ; les cellules vides/inconnues sont rejetées. Les régions sont limitées aux six clés reconnues. Les devis, sélections de confirmation, animations et références de scène ne sont pas sauvegardés. Importer ou changer de lieu les invalide.

La migration conserve les champs inconnus du document général traités par le socle, ainsi que les quêtes, les choix, les compétences et le matériel existants. Les métadonnées d’occasion des vendeurs sont bornées et nettoyées. Le schéma de test inclut une reprise v0.29 puis une écriture v0.30 sans modification de la chaîne originale v0.29.

Sauvegarder depuis DATA → SYSTÈME et exporter un JSON avant d’abandonner une ancienne version. Le dialogue du départ séparé précise quelle exploration sera remplacée.
