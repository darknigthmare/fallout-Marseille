# HUD en exploration

Le suivi de quête, la boussole, les jauges et les munitions occupent des zones distinctes. La santé et les PA sont à gauche, le chargeur et les réserves à droite, les commandes de terrain en bas. Les jauges d’état de l’arme et de l’armure restent dans leur panneau, même au format portrait. Les anciennes dimensions fixes du panneau de munitions sont remplacées pour permettre cette adaptation.

La boussole suit réellement l’orientation du joueur. Son losange indique la direction de l’objectif présent dans la même scène ; les flèches en bordure signalent une direction située hors de la bande visible. Un objectif d’une autre scène garde son indication de destination, sans faux repère local.

Le bouton **Suivi** masque ou affiche les cartes d’objectif. **Options → Affichage en jeu** propose aussi un HUD compact. Ces préférences sont conservées dans le stockage local du navigateur. Un échec de stockage annule le changement de préférence et affiche un message. Les quêtes et leurs progrès ne sont pas modifiés.

Le bouton **Visée** se maintient comme X ou le clic droit. Son état suit la présentation de l’arme ; il se désactive en vue extérieure, en bateau et avec une arme de mêlée. Les relâchements, annulations du pointeur, changements d’interface et pertes de focus libèrent le maintien. Les [mains et armes](VUE_FPS.md) partagent la même commande, sans changer la direction ni la précision des tirs.

Le panneau de munitions distingue chargeur vide, rechargement actif et mêlée. La santé basse et la posture accroupie proviennent des valeurs du joueur. Le HUD ne déplace pas le personnage, ne modifie pas son volume de collision et ne fournit pas d’information sur un adversaire caché.

En extérieur géographique, le grand cartouche technique de tuiles et de hauteurs laisse place à une ligne d’attribution séparée sous les raccourcis. Elle conserve les contributeurs OpenStreetMap, le cadastre et l’IGN ; son activation ouvre Cartes & territoire. Les mesures et diagnostics détaillés restent accessibles depuis ce panneau. Un banc synthétique affiche explicitement ses données de test.

Le pilote [fps_hud_native.py](../tests/expansion/fps_hud_native.py) contrôle les rectangles des groupes et des commandes, les jauges, les préférences et les commandes réelles sur quatre tailles d’écran et un contexte tactile émulé. Il utilise une scène narrative et des positions de diagnostic déclarées. Les captures ne certifient ni un téléphone physique, ni l’accessibilité de chaque interface du jeu.
