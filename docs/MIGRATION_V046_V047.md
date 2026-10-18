# Migration v0.46 vers v0.47

La v0.47 utilise les clés de sauvegarde et de réglages `fallout_mistral_save_v047` et `fallout_mistral_settings_v047`. La v0.46 reste la première source legacy. La scène géographique conserve le repère commun de la branche ; aucune reprojection supplémentaire d’une sauvegarde v0.46 n’est requise.

Les caches mémoire sont reconstruits au lancement. Le cache de tuiles du navigateur utilise un préfixe v047 afin de ne pas faire confiance implicitement à des entrées anciennes non validées. Le stock, les quêtes, la réputation, les découvertes et les morts persistantes ne sont pas remis à zéro.

Le banc synthétique ne sauvegarde pas de progression dans la campagne. Son retour restaure la scène et le portefeuille conservés avant l’entrée ; cela a été contrôlé deux fois de suite dans une même session, puis répété sur plusieurs lancements.
