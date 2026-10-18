# v0.46 — Continuité vérifiable

## Une scène, un repère

Toutes les macro-régions partagent une origine Lambert-93 fixe. Les projections d’un même point WGS84 sont donc identiques. Le franchissement d’une limite administrative change le libellé régional et non l’objet scène, ses empreintes ou ses PNJ actifs.

Les sources sont préparées dans un périmètre d’environ 940 mètres autour du prochain centre de chargement. L’affichage est limité à 720 mètres et le prochain cycle est demandé au-delà de 170 mètres du centre préparé. Ces marges évitent d’afficher un voisin que le gestionnaire n’a pas encore validé.

## Chargement transactionnel

Le noyau `MistralIntegrity.Gate` possède un numéro de génération et un AbortController. Au plus quatre demandes s’exécutent en parallèle. Les réponses validées sont conservées pour les réessais. La nouvelle géométrie est assemblée hors de la scène vivante, puis publiée en une fois. Une erreur de fichier, de géométrie ou une annulation interdit la publication. Une réponse associée à un ancien numéro ne peut modifier la scène courante.

Un écran de chargement expose le nombre de ressources contrôlées. En cas d’échec il propose Réessayer et Revenir sans déplacer le joueur. Les ressources sont cherchées dans le pack local, puis le cache navigateur quand possible, puis les endpoints existants. La PWA ne renvoie jamais `index.html` à la place d’un PBF ou d’une grille manquante.

## Relief

Chaque grille doit avoir une macro, une emprise, des dimensions et une provenance compatibles. Les sentinelles et NoData restent absents. Aucun échantillon extérieur à l’emprise n’est extrapolé. Pour une position couverte par plusieurs grilles, l’ensemble requis et les poids sont déterminés par la position, non par l’ordre de réception ou le nom de région courant.

Les tuiles déjà présentes conservent leurs objets de géométrie au prochain chargement. Les nouveaux triangles terrain suivent une grille métrique globale. Les anciens caches géographiques bruts sont bornés à 128 entrées actives/récentes ; cela n’est pas une certification de mémoire sur toutes les configurations.

## Bâtiments et passages

Seul le cadastre produit les empreintes bâties dans l’extérieur canonique ; un bâtiment simplifié de la couche générale n’est plus montré comme promesse de ce qui existera ensuite. Les trous et cours sont conservés dans les faces et les collisions. Le rapprochement par enveloppe convexe est supprimé. Les doublons stricts sont dédupliqués ; les fragments qui ne sont pas identiques ne sont pas fusionnés arbitrairement.

Les hauteurs non documentées restent des estimations signalées par la structure de rendu. Cela ne prétend pas restituer chaque toiture réelle.

## Forêts et couche fictionnelle

Les cellules de décoration ont des identifiants métriques globaux. La forêt est autorisée par les polygones de couvert végétal réellement lus. Routes, bâtiments, eau et cellules sans altitude empêchent certains placements.

Les 248 sites fictionnels conservent leurs identifiants v0.42. Leurs placements compatibles avec la géométrie sont mémorisés dans la sauvegarde. Ils sont activés par distance globale, pas uniquement selon le nom de macro-région. Les intérieurs restent des instances intentionnelles.

## HUD et ciel

Le correctif de la barre de raccourcis est effectué à sa source (`src/v020/05_runtime.js`) : pas de réécriture de `innerHTML` tant que les favoris et l’arme n’ont pas changé. Le bouton Sac est conservé. Le panneau de munitions et le texte de recharge sont séparés du flux de mise en page.

Le soleil et les nuages ont des directions monde. La caméra ne fait que projeter ces directions ; leur phase évolue avec le temps.
