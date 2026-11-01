# HUD en exploration

Le suivi de quête, la boussole, les jauges et les munitions occupent des zones distinctes. La santé et les PA sont à gauche, le chargeur et les réserves à droite, les commandes de terrain en bas. Les jauges d’état de l’arme et de l’armure restent dans leur panneau, même au format portrait. Les anciennes dimensions fixes du panneau de munitions sont remplacées pour permettre cette adaptation.

La boussole suit réellement l’orientation du joueur. Son losange indique la direction de l’objectif présent dans la même scène ; les flèches en bordure signalent une direction située hors de la bande visible. Un objectif d’une autre scène garde son indication de destination, sans faux repère local.

Le bouton **Suivi** masque ou affiche les cartes d’objectif. **Options → Affichage en jeu** propose aussi un HUD compact. Ces préférences sont conservées dans le stockage local du navigateur. Un échec de stockage annule le changement de préférence et affiche un message. Les quêtes et leurs progrès ne sont pas modifiés.

Le bouton **Visée** se maintient comme X ou le clic droit. Son état suit la présentation de l’arme ; il se désactive en vue extérieure, en bateau et avec une arme de mêlée. Les relâchements, annulations du pointeur, changements d’interface et pertes de focus libèrent le maintien. Les [mains et armes](VUE_FPS.md) partagent la même commande, sans changer la direction ni la précision des tirs.

Le panneau de munitions distingue chargeur vide, rechargement actif et mêlée. La santé basse et la posture accroupie proviennent des valeurs du joueur. Le HUD ne déplace pas le personnage, ne modifie pas son volume de collision et ne fournit pas d’information sur un adversaire caché.

Une confirmation statique près du réticule suit les dégâts réellement appliqués par le tir ou le coup de mêlée du joueur. Elle distingue touche, critique et neutralisation ; un tir manqué, une cible déjà morte ou un impact sans perte de PV ne crée pas de confirmation. Une même victime ne compte qu’une fois dans un tir de zone. Les dégâts des compagnons et les explosions différées ne sont pas attribués au tir du joueur. Cette indication s’efface après 0,75 seconde, dans une interface ou lors d’un changement d’arme, de scène ou de partie.

Les PV effectivement perdus après protection s’affichent brièvement au-dessus des jauges, sans position ni identité supposée de l’attaquant. Le rechargement présente ses secondes restantes et une petite barre qui suit le vrai délai, y compris ses modificateurs. La pause conserve le délai, une annulation retire la barre, et le panneau distingue chargeur plein et réserve vide. Les retours n’ajoutent aucun état sauvegardé ; la réduction des flashes conserve les textes statiques.

La gâchette **LT** de la manette standard maintient également la présentation de visée. La connexion, le changement d’interface et la déconnexion conservent les règles existantes de relâchement des commandes. Le retour **B** ferme le distributeur par sa commande normale. Les tests avec l’API Gamepad simulée ne certifient pas une manette physique.

En extérieur géographique, le grand cartouche technique de tuiles et de hauteurs laisse place à une ligne d’attribution séparée sous les raccourcis. Elle conserve les contributeurs OpenStreetMap, le cadastre et l’IGN ; son activation ouvre Cartes & territoire. Les mesures et diagnostics détaillés restent accessibles depuis ce panneau. Un banc synthétique affiche explicitement ses données de test.

Le pilote [fps_hud_native.py](../tests/expansion/fps_hud_native.py) contrôle les rectangles des groupes et des commandes, les jauges, les préférences et les commandes réelles sur quatre tailles d’écran et un contexte tactile émulé. Il utilise une scène narrative et des positions de diagnostic déclarées. Les captures ne certifient ni un téléphone physique, ni l’accessibilité de chaque interface du jeu.

Le pilote [fps_feedback_native.py](../tests/expansion/fps_feedback_native.py) exerce les tirs sur une créature déjà présente dans la scène d’Aubagne, le rechargement par R et la chaîne réelle de dégâts reçus. Ses placements, gels et appels de diagnostic restent décrits dans le script ; ils ne représentent pas un parcours humain continu. Les [contrats contrôlés](../tests/expansion/fps_hud.cjs) vérifient notamment les pertes de PV, le surdommage et les touches multiples.

Les sous-titres cherchent une bande verticale libre entre les groupes HUD réellement visibles, y compris en portrait. Si un écran très encombré ne laisse aucune bande de hauteur suffisante, la position CSS ordinaire est conservée : le message n’est ni supprimé ni tronqué pour simuler une absence de chevauchement.

Les neuf vues de régression incluent un contexte tactile émulé. Une notification transitoire de l’armure peut passer sous assistance/suivi en petit paysage ; les contrôles principaux vérifiés restent séparés. La capture immédiate de maintien de visée sous gel de simulation ne démontre pas, seule, son interpolation animée : les états et relâchements réels sont contrôlés séparément. Les huit captures des retours de combat utilisent un pré-rendu avant événement et un encodage PNG sans perte, avec états DOM avant/après et temps enregistrés ; aucune horloge ni durée de vie du jeu n’est remplacée.
