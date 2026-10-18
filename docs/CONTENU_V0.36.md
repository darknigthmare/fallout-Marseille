# Contenu v0.36 — Territoire réel

## Couverture déclarée

Huit macro-régions : Marseille, Huveaune/Aubagne, Garlaban, Calanques/Cassis, La Ciotat, Frioul, Étoile et Sainte-Baume.

Le manifeste exhaustif contient 367 tuiles `france-vector` à z14 et 5 517 tuiles `cadastre` à z16. Une tuile commune à plusieurs macro-régions n’est téléchargée qu’une fois.

## Sources

### OpenStreetMap / france-vector

Routes, chemins, rails, eau et occupation du sol. Attribution ODbL visible dans le HUD, le Pip-Boy, le statut et les crédits.

### Cadastre Etalab / DGFiP

Empreintes de bâtiments. Les polygones irréguliers et cours intérieures déjà supportés par le moteur sont conservés dans le pipeline MVT.

### IGN

Le service WMTS est vérifié accessible, mais cette build ne possède aucun MNT numérique. `terrain_real_v036.py` attend des GeoTIFF officiels et refuse une couverture incomplète.

## Relais de streaming

La fonction Supabase `fallout-mistral-map-v036`, authentifiée par clé publique, limite les requêtes :

- à l’emprise WGS84 Mistral ;
- aux zooms 14 et 16 attendus ;
- aux deux sources ouvertes autorisées ;
- à 8 Mo par tuile.

Elle ne constitue pas un pack hors ligne et ne modifie pas les données.

## Ordre des sources côté jeu

1. pack local servi par l’application ;
2. cache binaire IndexedDB ;
3. relais authentifié ;
4. source officielle directe.

Les PBF valides reçus en ligne sont ensuite stockés dans le cache lorsque celui-ci est disponible.

## Continuité territoriale

Le passage d’une macro-région à une autre conserve la latitude et la longitude. Il ne déclenche ni temps de voyage scénaristique ni production régionale. Les portiques historiques restent disponibles comme solution de secours et repères visuels.

## Outils

- `build_map_manifest_v036.py` : reconstruit le plan de 5 884 tuiles.
- `install_real_map_v036.py` : télécharge et valide le pack hors ligne.
- `mvt_audit_v036.py` : décodeur/auditeur MVT sans dépendance.
- `audit_real_map_v036.py` : couverture, couches et raccords inter-tuiles.
- `terrain_real_v036.py` : import de terrain numérique officiel.

## Ce qui n’est pas encore livré

- les 5 884 fichiers PBF dans les ZIP ;
- huit MNT numériques officiels ;
- audit visuel commune par commune ;
- certification de tous les raccords de routes et bâtiments ;
- profilage d’un pack complet sur plusieurs machines ;
- orthophotographie distribuée comme texture.
