# FALLOUT : MISTRAL — v0.42.0
## Couche Fallout territoriale

Prototype de fan non officiel. Aucune affiliation ou approbation Bethesda n’est revendiquée.

## Jouer

Ouvrez `JOUER_FALLOUT_MISTRAL_v0.42.html` ou utilisez les lanceurs d’application locale.

## Couche territoriale

La v0.42 ajoute 248 implantations persistantes au-dessus de la carte réelle : 16 abris, 24 colonies, 24 avant-postes, 48 autres intérieurs, 64 nids, 24 repaires élites, 8 boss régionaux, 24 repères et 16 haltes caravanières.

Dans le jeu : **Pip-Boy → MAP → COUCHE FALLOUT**.

Le moteur n’instancie que les sites proches du joueur. Les positions Fallout sont fictives et stables ; elles ne remplacent ni les routes OpenStreetMap, ni le cadastre, ni le relief IGN.

## Carte lourde

L’installation du pack territorial reste disponible avec :

```bash
python3 tools/install_local_pack_v041.py --workers 3
```

Puis :

```bash
python3 tools/install_local_pack_v041.py --verify-only
python3 tools/benchmark_map_v041.py
```

## Validation

La couverture des huit macro-régions, les placements, le streaming, les PNJ, les contrats, les élites, boss, intérieurs et sauvegardes sont vérifiés par les suites v0.42. Voir `docs/RAPPORT_QA.md`.
