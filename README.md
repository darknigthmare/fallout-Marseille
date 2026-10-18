# FALLOUT Marseille — MISTRAL

## v0.49 · Le quartier se souvient

Projet complet du prototype : jeu prêt à lancer, sources, ressources disponibles, campagne, prologue, outils, tests, rapports visuels et historique des versions.

**[Téléchargements Google Drive](https://drive.google.com/drive/folders/1XYIrQczKXczburj2Tu0bDs2ZNH10Jxta)** · [Guide français](README_FR.md) · [Rapport visuel](RAPPORT_VISUEL_V0.49.png) · [Limites connues](docs/KNOWN_LIMITATIONS_V0.49.md)

## Lancer le jeu

Python 3 est nécessaire pour le serveur local. Aucun paquet npm n’est nécessaire pour jouer.

- **Windows :** double-cliquer sur `LANCER_APP_WINDOWS.bat`.
- **Linux :** `bash LANCER_APP_LINUX.sh`.
- **macOS :** `bash LANCER_APP_MAC.command`.

Le lanceur ouvre `http://127.0.0.1:8765/index.html`. Pour un lancement manuel :

```bash
git clone https://github.com/darknigthmare/fallout-Marseille.git
cd fallout-Marseille
python3 tools/serve_game.py
```

Le fichier `JOUER_FALLOUT_MISTRAL_v0.49.html` contient également le jeu autonome. Le serveur local est recommandé pour l’inspection des données géographiques et les fonctions de l’application.

## Archive complète

Le ZIP original contient **1 172 fichiers** et pèse **127 071 766 octets**. La limite de transfert vers Drive impose sa distribution en deux parties, avec les lanceurs de recomposition et les empreintes dans le dossier dédié. Les deux parties reconstituent exactement le ZIP original ; aucun fichier n’a été retiré.

Sur Windows, télécharger les deux parties et les scripts dans un même dossier, puis lancer `RECONSTRUIRE_ARCHIVE_WINDOWS.bat`. Sur Linux/macOS : `python3 RECONSTRUIRE_ARCHIVE.py`. Python 3 est aussi utilisé pour lancer le jeu.

SHA-256 du ZIP reconstitué :

```text
172783f2026a1b8537b45a3b91df89bcd6afe425ade8613bb0210aff2ed6477c
```

## Contenu et carte réelle

La v0.49 conserve les rencontres au-delà des changements de secteur : santé, blessures, positions, orientation, états d’alerte et dépouilles avec leur butin restant. Les intérieurs et extérieurs ont des identités séparées ; les boss uniques ne sont pas réinitialisés au retour.

Le catalogue des 248 implantations, la continuité géométrique, les préparations interruptibles, les retours d’intérieur, la campagne, le prologue et le lore reconstruit sont inclus.

**Le pack géographique intégral n’est pas embarqué** : 0/5 884 coordonnées vectorielles et 0/8 grilles territoriales dans cette livraison. Les extérieurs du rapport visuel proviennent du banc synthétique identifié à l’écran. L’accès à la vraie carte nécessite les ressources géographiques ; cette publication ne certifie pas les rues réelles de Marseille, Aubagne ou La Ciotat.

`Ctrl + Maj + F9` ouvre le banc de coutures. Ses sauvegardes de campagne sont désactivées. Le diagnostic est disponible dans **MAP → CONTINUITÉ**.

## Sources et validation

```bash
python3 tools/build_single.py
node --check src/game.js
node tests/v049/kernel.test.cjs
node tests/v049/v048_inherited_legacy_distribution.cjs
```

La reconstruction des deux HTML et de `src/game.js` est identique octet pour octet à la livraison. Les 31 assertions ciblées ci-dessus ont été relancées lors de la publication, avec un contrôle HTTP réel du serveur local. Les 434 contrôles de la livraison initiale restent documentés dans les rapports historiques ; ils n’ont pas tous été relancés pour cet import.

Pour la campagne QA complète, consulter `requirements-dev.txt`, les outils et [le rapport QA](docs/RAPPORT_QA.md). Aucun nouveau rendu Chromium, contrôle PWA native ou test IndexedDB natif n’est revendiqué pendant la publication.

Les 1 172 fichiers d’origine sont conservés à l’identique. Ce README, les fichiers de distribution et la [note de publication](docs/PUBLICATION_2026-10-18.md) complètent l’import. Le [manifeste d’origine](MANIFEST_SHA256.json) conserve son périmètre de livraison v0.49.

Prototype de fan non officiel.
