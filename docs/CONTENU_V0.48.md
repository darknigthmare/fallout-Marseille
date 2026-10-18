# v0.48 — Reprises sans rupture

## Préparer sans bloquer un long bloc de calcul
La préparation des tuiles est découpée par groupes de huit entités MVT. L’indexation des surfaces et collisions, la construction des rangées de terrain et la création des cellules de nature comportent également des points d’interruption.

Le budget cible est 6 ms entre opérations, avec une limite de 512 unités avant de rendre la main. Ce n’est pas une promesse de FPS : une entité complexe, la validation d’un fichier ou le rendu lui-même peuvent dépasser ce budget.

Les vérifications d’annulation précèdent chaque étape. L’ancienne scène ne reçoit ni géométrie, ni terrain partiel. Le constructeur est comparé à celui de la v0.47 sur les mêmes ressources du banc : bâtiments, routes, collisions, relief et nature donnent la même signature.

## Retrouver le même extérieur après une visite
Un seul secteur extérieur validé peut rester en mémoire pendant un intérieur territorial. Sa géométrie, son relief et ses acteurs sont conservés par référence. Le retour réutilise cette scène sans demande réseau, même lorsque le fournisseur de données est en échec.

Le portefeuille, les objets et les quêtes acquis à l’intérieur ne sont pas restaurés à un état antérieur. La mémoire de retour est libérée après usage ou changement de destination. Le plafond estimatif de rétention est 48 Mio, distinct de la mémoire totale du navigateur. Un contexte de sauvegarde différent ou une position de retour incompatible invalide cette rétention.

## Sortie en échec
Sans scène retenue, le chargement normal reste obligatoire. Le site intérieur n’est plus effacé avant validation de l’extérieur. Une annulation laisse le joueur et sa sauvegarde dans un intérieur valide ; le bouton Réessayer termine la même sortie après réception des données.

## Cloisons intérieures
Les générateurs historiques employaient parfois des segments Z descendants (34 → 14). Leur traitement pouvait supprimer la cloison entière. Les segments sont désormais normalisés et les ouvertures bornées au mur. Les quatre portes testées restent libres et leurs murs voisins solides. L’entrée de l’instance fait regarder vers les salles, et non vers la sortie.

## Contenu conservé
Le catalogue des 248 sites, les neuf factions et les huit dossiers reconstruits de la branche, COCHONNET, la campagne, le prologue A-03, le HUD et le ciel sont conservés. Il n’y a pas de nouvelle collection de lieux ou d’assets artistiques annoncée dans cette version.
