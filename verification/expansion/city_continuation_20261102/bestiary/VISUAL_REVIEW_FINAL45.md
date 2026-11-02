# Revue visuelle bestiaire — final45, phase A

Revue manuelle des **15 nouvelles captures** du parcours sur HTML `4581c0c29ce5c74da3aba7430227fba844aed1eb40f1b1fc4d7965c7a6600d78`. Chaque fichier a été ouvert et son SHA vérifié contre le rapport. Les preuves précédentes sur HTML84 restent sous `diagnostic-84` et ne sont pas réattribuées.

Le parcours exécuté par le root termine à **203/203, zéro échec, vrai code 0**. Cette revue ne lance aucun navigateur ni test et ajoute **0 contrôle automatisé** au compteur. Le reçu vérifié certifie que les 474 entrées runtime et le pilote étaient inchangés entre le début et la fin de cette exécution de phase A ; il ne certifie pas les 474 valeurs du workspace après la clôture de cette phase. Contexte et navigateur fermés avant la sortie Playwright ; port 46523 vérifié indépendamment fermé (`connect_ex=111`).

- **01_new_regional_actor.png** : Rat-couronné au centre : couronne, oreilles, incisives, quatre pattes et queue identifiables ; autres acteurs réels à distance.

- **02_true_gabian_flight.png** : Gabian en vol vu de dessous : bec, sac ventral et pattes visibles ; une aile est coupée par le cadre rapproché ; avertissement de lâcher réel.

- **03_real_corrosive_drop.png** : Gabian et projectile vert visibles au-dessus du port et du relief source ; capture de fuite native, sans retouche.

- **04_radscorpion_native.png** : Radscorpion avec pinces, pattes et queue segmentée reconnaissables ; un autre acteur réel apparaît partiellement en haut à droite.

- **04_radscorpion_vats.png** : Pince gauche sélectionnée, coloration et boîte sur le membre rendu ; tête, dard et groupes de pattes séparés.

- **05_radscorpion_windup.png** : Préparation Dard du Radscorpion visible avec yeux, mandibules et pinces ; vue très proche coupant la pointe de queue.

- **04_mirelurk_native.png** : Fangeux entier visible : yeux pédonculés, abdomen, carapace, pinces et pieds ; avertissement actuel provenant ici de l’élite voisine.

- **04_mirelurk_vats.png** : Pince gauche réellement sélectionnée, volumes sur le membre rendu ; carapace/abdomen, yeux et pattes étiquetés.

- **05_mirelurk_windup.png** : Cisaillement des pinces affiché, deux pinces au premier plan ; gros plan coupant une partie du haut et du bas.

- **04_feralGhoul_native.png** : Goule fine et asymétrique de profil, tête, côtes et membres visibles ; avertissement courant provenant ici du Fangeux voisin.

- **04_feralGhoul_vats.png** : Goule : tête, cage thoracique, deux bras et deux jambes ciblables ; bras gauche sélectionné dans son volume réel.

- **05_feralGhoul_windup.png** : Ruée de la Goule affichée ; côtes et doigts distincts, bras en anticipation ; gros plan coupant le sommet de la tête.

- **04_deathclaw_native.png** : Griffe de profil, cornes, épaules, griffes, jambes et queue segmentée visibles ; avertissement provenant ici du Magistrat voisin et recouvrant une partie du haut.

- **04_deathclaw_vats.png** : Griffes gauches sélectionnées sur le membre rendu ; tête/cornes, torse, pattes et queue possèdent leurs volumes.

- **05_deathclaw_windup.png** : Balayage des griffes affiché ; torse et avant-bras articulés au premier plan, gros plan coupant le haut des cornes.

Les six espèces observées sont reconnaissables dans le style procédural existant et les quatre vues VATS sélectionnent le membre rendu attendu. Les gros plans d’anticipation coupent parfois le haut ou les extrémités ; les captures normales/VATS apportent le contexte de silhouette. Les avertissements peuvent correspondre à un ennemi voisin dans les captures normales : les captures de préparation présentent le bon libellé d’attaque du sujet. Aucun problème visuel nouveau imposant une modification source n’a été observé sur cet échantillon.

Cette preuve n’étend pas la couverture à toutes les espèces, tous les slots ou toute la ville. Les aides de caméra, de gel et de simulation sont déclarées par le pilote. Blessures, mises à mort et prélèvements relèvent du harnais contrôlé distinct ; aucune récompense ni élimination native n’est revendiquée ici. L’art reste procédural. Une future phase B du pilote façade sera distincte et ne retague pas cette preuve.

## Delta QA après exécution

La phase A complète est archivée sous `qa-phase-a`, avec son propre gel et les sources exactes exécutées. Après la fin de ce run bestiaire, le seul pilote `tests/expansion/facade_hardware_native.py` a été modifié pour la correction de contrat de précision Node/Chromium à environ 2 nm : le SHA de phase A est `8435e8b232c497963c5b56f3d35e50aac8cbdf408abd071af8816a98374cdd05`, celui observé lors de cette revue est `368baef192ccf76b3ae865eaf5b8c688f4d92a2023455d1bfecf1d030b7409ee`. Une phase B séparée consigne cette évolution QA ; le rapport natif bestiaire et son reçu restent immuables.

Les pins propres au bestiaire (HTML, module 13, pilote bestiaire et index architecture) ont été relus et restent identiques à la phase A. Aucune égalité globale entre les 474 valeurs du gel A et le workspace courant n’est revendiquée par cette revue.
