# Migration v0.28 → v0.29

Campagne : `fallout_mistral_save_v029`. Exploration : `fallout_mistral_sandbox_v029`. Réglages : `fallout_mistral_settings_v029`. Les anciennes clés ne sont pas supprimées. La nouvelle exploration demande confirmation et ne remplace que l'exploration v029 ; la campagne reste distincte.

Le champ `v029` ajoute les essais, cycles, mots essayés, séquences utilisées, habilitations, volets, veilles, journaux lus, délai de jeu actif et état de l'enquête. L'ancienne sauvegarde démarre sans accès acquis ni récompense imposée. Les nouvelles clés sont normalisées ; les champs inconnus des anciennes versions restent gérés par le migrateur précédent.

Quitter puis rouvrir le terminal conserve la table ; importer une sauvegarde conserve les essais et ferme la session ouverte. Les commandes obsolètes sont invalidées. Un badge ne donne pas l'expérience d'un piratage. L'état de la veille ne réanime jamais un automate déjà mort.

Le soupçon et la position sonore sont transitoires dans la scène chargée : ils ne sont pas annoncés comme une mémoire globale d'ennemis hors écran. Les dégâts et décès hérités conservent leur propre persistance.

Le navigateur associe son stockage à une origine. Lors d'un changement de dossier, de navigateur ou de serveur, conserver un export JSON depuis DATA → SYSTÈME avant de changer d'environnement. Le jeu signale les refus d'écriture ; ne pas les interpréter comme une sauvegarde réussie.
