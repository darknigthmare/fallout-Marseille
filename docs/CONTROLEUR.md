# Manette : commandes de terrain et préférences

La manette utilise l’API Gamepad standard du navigateur. Les correspondances et la compatibilité matérielle dépendent aussi du navigateur et du système. Les tests automatisés simulent cette API ; ils ne certifient aucun modèle de manette physique.

## En jeu

| Commande | Action |
| --- | --- |
| Stick gauche / droit | Marcher / regarder |
| L3 / LT / RT | Courir / visée fine / tirer |
| A / B / X / Y | Sauter / s’accroupir / interagir / recharger |
| LB / RB / R3 | V.A.T.S. / soin / caméra |
| Select / Start | Pip-Boy / pause |
| Croix haut / bas | Lampe / plan de terrain |
| Croix gauche / droite | Arme favorite précédente / suivante |

La lampe et le plan passent par leurs commandes existantes. Le cycle des armes consulte les quatre favoris et saute les emplacements vides, les armes non possédées ou inconnues et l’arme déjà portée. Il utilise l’équipement habituel ; il ne crée ni favori, ni arme, ni munition. Une direction maintenue ne répète pas l’équipement en jeu.

## Gaucher et menus

Dans **Options → Manette**, « Gaucher » échange les rôles des deux sticks pendant le jeu. Les menus gardent le stick gauche physique pour déplacer le focus, avec la croix. A valide, B revient ; gauche/droite règlent les curseurs et les listes. Les commandes existantes du Pip-Boy, du V.A.T.S. et des activités restent disponibles.

Les boutons maintenus doivent être relâchés après une connexion, un changement de manette, d’écran ou de disposition. Chacun des deux sticks doit revenir dans sa zone morte avant de fournir une nouvelle commande. Changer directement de direction ne suffit pas. Cette neutralisation empêche un stick déjà incliné de déplacer le personnage, tourner la vue ou parcourir un menu lors de la reprise.

## Déconnexion et reprise

L’option **Mettre en pause si la manette utilisée se déconnecte** est activée par défaut. Elle concerne la manette sélectionnée et seulement une partie active, visible, avec un personnage vivant, lorsque le dernier périphérique utilisé est la manette. Une seconde manette déconnectée, un menu, un chargement bloquant ou un dernier usage au clavier, à la souris ou au tactile ne déclenchent pas cette pause. Une préparation de secteur en arrière-plan reste du jeu actif.

La pause attend une reprise explicite par le bouton « Reprendre » ou les commandes de pause habituelles. Une reconnexion ne reprend pas la partie. Les sticks inclinés et les gâchettes maintenues restent neutralisés jusqu’à leur relâchement. La déconnexion ne vide jamais les touches physiques du clavier et ne remplace pas les commandes tactiles.

## Conservation des préférences

La clé `mistral_controller_v1` est conservée. Les réglages existants `enabled`, `deadZone`, `look` et `invertY` sont validés comme auparavant. Les nouvelles valeurs par défaut sont `leftHanded: false` et `pauseOnDisconnect: true`. Les modifications et le rétablissement des réglages passent par les options habituelles.

## Vérification

```bash
node tests/expansion/controller_model.cjs
```

Le modèle vérifie notamment la sélection du périphérique, les boutons, les deux sticks, les changements de contexte et de disposition, les favoris et les préférences.

Après génération et gel du programme, le pilote DOM utilise le vrai jeu servi en HTTP, ses écrans et ses callbacks :

```bash
python tests/expansion/controller_browser.py \
  --url http://127.0.0.1:8765/index.html?skipboot=1 \
  --expected-html-sha256 SHA_DU_PROGRAMME_GELE \
  --output /chemin/exterieur/controleur
```

Ce pilote remplace explicitement `navigator.getGamepads` par des échantillons contrôlés et émet un événement PointerEvent tactile pour vérifier le suivi du dernier périphérique. Les événements clavier, le DOM, le stockage et les actions du jeu sont réels. Le diagnostic en lecture seule `v050ControllerInfo()` expose les commandes filtrées, les sticks bloqués, le dernier périphérique et l’origine de la pause.
