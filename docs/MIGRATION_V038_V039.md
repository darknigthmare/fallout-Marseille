# Migration v0.38 → v0.39

La v0.39 ajoute `state.v039` pour mémoriser l’état du cache terrain, la dernière macro chargée et la provenance du relief. Les sauvegardes v0.38 et antérieures restent lisibles.

Une ancienne sauvegarde n’obtient aucune altitude inventée. À l’entrée dans une macro-région, le moteur tente le pack, IndexedDB puis le cache privé. En cas d’échec, le sol de référence historique reste actif et l’interface indique que le relief n’a pas été chargé.
