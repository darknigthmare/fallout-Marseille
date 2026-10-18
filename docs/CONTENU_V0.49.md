# Contenu v0.49 — Le quartier se souvient

## Défaut reproduit
Dans la v0.48 fournie, un ennemi extérieur de 85 PV descend à 68,35 PV après un tir à la jambe. Après déchargement de son implantation et retour, le même identifiant revient à 85 PV. La reproduction utilise le HTML v0.48 exact, le combat et les fonctions de streaming du jeu. Le rapport BASELINE_V048.json distingue cette régression d’une reconstruction entière du monde, qui bénéficiait déjà de certains mécanismes de sauvegarde historiques.

## État des rencontres
Le journal v0.49 conserve les acteurs des implantations réellement visitées. Il est indexé par site, acteur et contexte intérieur/extérieur, et non par le nom de macro-région affiché.

Les ennemis retrouvent leur santé, santé maximale, position, point de retour, orientation, blessures aux membres, effets actifs, moral, état d’alerte/recherche et délais d’attaque. Les statistiques ne sont pas recalculées à la hausse simplement parce que le joueur a changé de niveau pendant son absence. Les habitants retrouvent leur position, orientation et champs de routine déjà gérés par le jeu.

Les acteurs éloignés restent suspendus. Cette version n’ajoute pas de simulation permanente de combats ni de population hors écran.

## Dépouilles et prises de butin
La clé d’une dépouille territoriale n’est plus dérivée du libellé de région. Le corps redevient accessible lorsque le site est chargé, avec uniquement son contenu restant. Intérieur et extérieur sont distincts ; les dépouilles d’un intérieur ne sont pas réutilisées par un autre intérieur partageant le même gabarit.

Les anciens doublons sont réunis de façon conservatrice : pour chaque objet, le plus petit reliquat est retenu. Cela empêche de recréer des objets déjà pris, au prix possible d’une réduction du reliquat lorsque deux anciens états se contredisent.

## Respawns
Les sites ordinaires autorisés à repeupler suivent toujours leur délai de jeu déclaré dans le catalogue. À l’ouverture légitime d’un nouveau cycle, l’ancien journal, les blessures et les anciennes dépouilles de ce site sont retirés ensemble. Les boss et sites uniques sont exclus de cette remise à zéro.

## Décor et habitants
Le générateur synchrone des accessoires d’un site utilise désormais une graine stable liée au site. Un aller-retour ne change plus aléatoirement cette composition. Les routines de PNJ existantes ne sont pas remplacées par une nouvelle IA.

## Sauvegardes
Le jeu capture les acteurs actifs avant l’écriture d’un emplacement ou d’un instantané. Le propriétaire de la scène est vérifié afin qu’une ancienne scène ne contamine pas une sauvegarde nouvellement chargée.

Les sauvegardes manuelles et automatiques sont explicitement interdites dans le banc synthétique. En le quittant, les propriétaires de scène et les références des habitants sont réassociés à la campagne restaurée.

## Diagnostic
MAP → CONTINUITÉ affiche le nombre de rencontres mémorisées, blessés, dépouilles, habitants, restaurations et la taille du journal. Ce sont des mesures de la session, pas un total fictif d’acteurs simulés sur toute la carte.
