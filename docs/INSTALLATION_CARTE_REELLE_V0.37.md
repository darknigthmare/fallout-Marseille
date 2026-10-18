# Installation de la carte réelle v0.37

## Prérequis

- Python 3 ;
- espace disque suffisant ;
- connexion Internet pour le téléchargement ;
- lancement en mode application locale pour servir les PBF au navigateur.

## Installation complète

```sh
python3 tools/install_real_map_v037.py --endpoint auto --workers 6
```

Le mode `auto` tente la source officielle puis le cache territorial borné.

## Cache territorial uniquement

```sh
python3 tools/install_real_map_v037.py --endpoint relay --workers 5
```

## Exemples ciblés

```sh
# Fond général de l’Huveaune
python3 tools/install_real_map_v037.py --source base --macro geo_huveaune

# Cadastre de Marseille
python3 tools/install_real_map_v037.py --source cadastre --macro geo_marseille

# Vérifier sans télécharger
python3 tools/install_real_map_v037.py --verify-only

# Simuler la sélection
python3 tools/install_real_map_v037.py --dry-run
```

## Garanties de l’installateur

- reprise des fichiers déjà valides ;
- écriture temporaire puis renommage atomique ;
- décodage MVT obligatoire ;
- rejet des réponses HTML/JSON invalides par le parseur ;
- plafond de 8 Mo ;
- nouvelles tentatives avec temporisation ;
- rapport JSON détaillé.

## Audit

```sh
python3 tools/audit_real_map_v037.py --output verification/AUDIT_CARTE_REELLE_V037.json
```

Un code retour `2` signifie que le pack reste incomplet ou possède une anomalie confirmée. Un voisin absent reste « en attente » et n’est pas compté comme rupture.

## Mode application

Après installation :

- Windows : `LANCER_APP_WINDOWS.bat`
- Linux : `LANCER_APP_LINUX.sh`
- macOS : `LANCER_APP_MAC.command`

Une page `file://` ne peut généralement pas lire librement les PBF adjacents ; le serveur local est limité à `127.0.0.1`.
