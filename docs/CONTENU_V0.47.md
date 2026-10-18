# Contenu v0.47 — Le territoire en avance

## Préparation en marchant
Le moteur conserve la scène extérieure commune de la v0.46. Il observe le déplacement réel et prépare une fenêtre située 100 mètres devant le joueur dès que celui-ci s’éloigne suffisamment de l’ancre chargée (65 mètres). Le préchargement reste non bloquant à l’intérieur de la marge validée.

Si le joueur atteint la limite de sécurité avant la fin, la même demande devient bloquante : elle n’est pas relancée depuis zéro. Le joueur ne traverse pas une zone non validée. Une préparation lancée pour une direction abandonnée peut être rejetée au lieu de remplacer la scène dans son dos.

L’algorithme ne relance pas une demande opposée quand le joueur s’immobilise autour d’une ancre située devant lui. Un échec impose une courte temporisation avant un nouvel essai automatique.

## Relief transactionnel
La banque de terrain en cours de préparation est séparée de celle qui porte le joueur. Le décodage et la construction de la géométrie peuvent échouer sans modifier le relief actuel. La publication échange uniquement des tableaux prêts. L’annulation conserve aussi le mode d’interface utilisé avant l’attente.

## Réutilisation et budgets
Trois caches LRU sont utilisés : ressources 48 Mio / 128 entrées, géométrie 40 Mio / 96 entrées, maillages terrain 12 Mio / 64 entrées. Les ressources actives sont prioritaires ; le diagnostic signale le dépassement quand les entrées épinglées empêchent de respecter le budget. Ce ne sont pas des plafonds de mémoire totale du navigateur ou du GPU.

Les maillages de terrain sont découpés selon une grille globale de 512 m. Les tuiles identiques sont réutilisées lorsqu’elles conservent leur contenu et leur référence altimétrique. Un retour en arrière ne force donc pas systématiquement leur reconstruction.

## Nature cohérente
Une indexation spatiale accélère les vérifications sol, eau, routes et collisions. La génération conserve des identifiants cellule + numéro de pièce. Elle utilise les masques d’occupation du sol lus et ne revendique pas une carte botanique exhaustive. Aucune forêt réelle nouvelle n’a été téléchargée dans cette passe.

## Téléchargements
Les tailles déclarées et effectivement reçues sont contrôlées. Les corps trop volumineux sont interrompus, les réponses HTML sont rejetées, les annulations sont propagées et une empreinte SHA-256 fournie est vérifiée. Une implémentation de repli vérifiée contre Node est utilisée quand WebCrypto n’est pas disponible.

## Diagnostic et laboratoire
Le serveur HTTP local dispose d’une route en lecture seule qui audite les fichiers présents. Le service worker ne transforme pas cette route ni les données manquantes en page HTML de secours. Le banc de coutures conserve la scène de campagne et sa banque de ressources, y compris lors de deux entrées/sorties successives et après les callbacks différés de démarrage.

## Contenu préservé
Le fichier du catalogue de 248 implantations est identique à celui de l’archive v0.46. Les neuf factions, huit dossiers et COCHONNET reconstruits dans cette branche restent présents. Cette passe ne revendique aucun nouvel ennemi animé, abri unique ou territoire téléchargé.
