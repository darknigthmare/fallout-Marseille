# Arsenal et bestiaire — inventaire lié aux sources

55 IDs explicitement régionaux du catalogue existant ; armes des sections 38–42 ; créatures des sections 29–36 et liste des 25 témoins v0.46. Les autres armes du jeu ne sont pas renommées. Correspondances exactes normalisées, sans alias supposé.

**Une ligne n’est pas une promesse de contenu terminé.** Les nombres décrivent les entrées examinées, pas autant de nouveaux modèles ou de nouvelles missions. Le fichier JSON voisin conserve les identifiants et les empreintes.

## Armes régionales déjà déclarées

| ID | Arme | Présentation | Alimentation |
|---|---|---|---|
| `mistralCarbine` | Carabine du Mistral | `rifle` | Munitions 5,56 mm |
| `ceramicLauncher` | Lance-brique céramique | `industrial` | Projectiles céramiques |
| `concordePistol` | Pistolet CONCORDE | `energy-pistol` | Cellules énergétiques |
| `calanquesGlaive` | Glaive des Calanques | `blade` | Mêlée |
| `releveTorch` | Chalumeau de la Relève | `industrial` | Carburant de lance-flammes |
| `cisternNeedler` | Aiguilleur de la Citerne | `industrial` | Rivets industriels |
| `saltScatter` | Éparpilleur de sel | `shotgun` | Cartouches calibre 12 |
| `gardianArc` | Arc des Veilleurs | `energy` | Cellules énergétiques |
| `provenceRevolver` | Revolver des Communes | `revolver` | Munitions .44 |
| `transferCarbine` | Carabine des Correspondances | `rifle` | Munitions 5,56 mm |
| `hearthHammer` | Marteau du Foyer témoin | `melee` | Mêlée |
| `floodGun` | Canon de la Crue | `industrial` | Rivets industriels |
| `rootSpear` | Lance des Racines | `blade` | Mêlée |
| `seasonRifle` | Fusil des Saisons | `rifle` | Munitions .308 |
| `keelCannon` | Canon de Quille | `heavy` | Munitions .50 |
| `echoPistol` | Pistolet de l’Écho | `energy-pistol` | Packs de charge électronique |
| `mercyLaser` | Laser du Répit | `energy` | Cellules à microfusion |
| `civicJudge` | Juge civique | `revolver` | Munitions .357 Magnum |
| `stageGun` | Arme de scène T-05 | `pistol` | Munitions 9 mm |
| `radeRepeater` | Répétiteur de la Rade | `rifle` | Munitions .357 Magnum |
| `mistralNeedler` | Aiguille du Mistral | `needle` | Seringues balistiques |
| `ceramicSaw` | Scie céramique d’Aubagne | `ceramic-disc` | Mêlée |
| `garlabanMortar` | Mortier du Garlaban | `mortar40` | Grenades 40 mm |
| `municipalLaser` | Laser municipal | `energy` | Cellules énergétiques |
| `saltArc` | Arc salin de La Ciotat | `energy` | Cellules protoniques |
| `m13_archivistPistol` | Pistolet de l’Archiviste | `energy-pistol` | Cellules d’archive |
| `m13_notaryCarbine` | Carabine notariale | `rifle` | Munitions 5,56 mm |
| `m13_mistralDerringer` | Derringer du Mistral | `pistol` | Munitions .44 |
| `m13_seilleGauss` | Gauss de la Seille | `energy` | Cartouches 2 mm EC |
| `m13_longchampLaser` | Laser de Longchamp | `energy` | Cellules d’archive |
| `m13_huveauneRebarGun` | Lance-fer de l’Huveaune | `industrial` | Boulons réfractaires |
| `m13_garlabanFlareRifle` | Fusil de vigie du Garlaban | `rifle` | Capsules de signal |
| `m13_calanqueSpeargun` | Arbalète des Calanques | `industrial` | Harpons |
| `m13_ciotatPlasmaCutter` | Découpeur plasma de La Ciotat | `energy` | Cartouches plasma |
| `m13_aubagneKilnHammer` | Marteau des fours d’Aubagne | `melee` | Mêlée |
| `m13_bastideRifle` | Fusil des Bastides | `rifle` | Munitions .308 |
| `m13_radeScattergun` | Éparpilleur de la Rade | `shotgun` | Cartouches calibre 12 |
| `m13_transitPulseGun` | Pistolet à impulsions du Transit | `energy-pistol` | Capsules de signal |
| `m13_concordeStampGun` | Poinçon CONCORDE | `industrial` | Boulons réfractaires |
| `m13_mistralReelGun` | Canon-bobine du Mistral | `energy` | Cellules de fusion lourdes |
| `m13_oliveBlade` | Lame d’olivier | `blade` | Mêlée |
| `m13_brineCaster` | Projeteur de saumure | `energy` | Charges de saumure |
| `m13_quarryAutocannon` | Autocanon des Carrières | `heavy` | Obus de carrière |
| `m13_sirenCarbine` | Carabine-Sirène | `energy` | Capsules de signal |
| `m13_refugeNeedler` | Aiguille des Veilleurs | `needle` | Dards du Mistral |
| `m13_ceramicGauntlet` | Gantelet céramique | `fist` | Mêlée |
| `m13_vineyardRepeater` | Répétiteur des Vignes | `rifle` | Munitions .45-70 |
| `m13_mugelDeckGun` | Canon de pont du Mugel | `heavy` | Obus de carrière |
| `m13_islandSignalPistol` | Pistolet de l’Île Verte | `energy-pistol` | Capsules de signal |
| `m13_canailleRailRifle` | Fusil-rail de Canaille | `rifle` | Clous ferroviaires |
| `m13_noaillesCompact` | Compact de Noailles | `pistol` | Munitions 9 mm |
| `m13_saintCharlesSMG` | P.-M. Saint-Charles | `rifle` | Munitions 10 mm |
| `m13_vieuxPortRevolver` | Revolver du Vieux-Port | `revolver` | Munitions .44 |
| `m13_firewatchLance` | Lance des Vigies | `blade` | Mêlée |
| `m13_memoryRecorderGun` | Enregistreur de mémoire | `energy` | Bandes mémorielles |

Les 55 associations vers des profils partagés sont explicites. La scie et le mortier ont chacun une présentation supplémentaire ; le profil pneumatique est partagé par les deux aiguilles. Les valeurs de dégâts/rechargement sont lues dans le catalogue, pas inventées par le carnet.

## Armes conçues dans la bible

| Nom de la bible | Section | Correspondance exacte dans les données |
|---|---|---|
| Pistolet de four d’Aubagne | 38. Arsenal d’Aubagne et des collines | `aubagneKilnPistol` |
| Éparpilleur céramique | 38. Arsenal d’Aubagne et des collines | `ceramicScattergun` |
| Fusil des Restanques | 38. Arsenal d’Aubagne et des collines | `restanqueRifle` |
| Fusil en olivier | 38. Arsenal d’Aubagne et des collines | `olivewoodRifle` |
| Arc du Garlaban | 38. Arsenal d’Aubagne et des collines | `garlabanBow` |
| Marteau de carrière | 38. Arsenal d’Aubagne et des collines | `quarryHammer` |
| Fusil-pompe de l’Huveaune | 38. Arsenal d’Aubagne et des collines | `huveaunePumpGun` |
| Canon du Débit | 38. Arsenal d’Aubagne et des collines | `flowCannon` |
| Harpon de l’Aqueduc | 38. Arsenal d’Aubagne et des collines | `aqueductHarpoon` |
| Canon à grêle | 38. Arsenal d’Aubagne et des collines | Aucune — concept à traiter |
| Débroussailleuse de combat | 38. Arsenal d’Aubagne et des collines | Aucune — concept à traiter |
| Fourche voltaïque | 38. Arsenal d’Aubagne et des collines | Aucune — concept à traiter |
| P.-M. des Arcades | 39. Arsenal de Marseille | `marseilleSMG` |
| Pistolet de la Rumeur | 39. Arsenal de Marseille | `rumorPistol` |
| Répétiteur du Transit | 39. Arsenal de Marseille | `transitRepeater` |
| Carabine des Seuils | 39. Arsenal de Marseille | `thresholdCarbine` |
| Revolver des Héritiers | 39. Arsenal de Marseille | `heirsRevolver` |
| Aiguille CONCORDE | 39. Arsenal de Marseille | `concordeNeedler` |
| Laser de Mémoire | 39. Arsenal de Marseille | `memoryLaser` |
| Lance-fusées civique | 39. Arsenal de Marseille | `civicFlareGun` |
| Fusil de la Vue | 39. Arsenal de Marseille | `viewpointRifle` |
| Agrafeuse pneumatique | 39. Arsenal de Marseille | Aucune — concept à traiter |
| Massicot de préfecture | 39. Arsenal de Marseille | Aucune — concept à traiter |
| Fusil-riveteur des Mains | 40. Arsenal du littoral | `handsRivetRifle` |
| Canon-bobine de La Ciotat | 40. Arsenal du littoral | `ciotatCoilgun` |
| Tesla maritime | 40. Arsenal du littoral | `maritimeTesla` |
| Canon des Marées | 40. Arsenal du littoral | `tideGun` |
| Fusil du Mistral | 40. Arsenal du littoral | `mistralShotgun` |
| Railgun des Calanques | 40. Arsenal du littoral | `calanqueRailgun` |
| Émetteur de la Sirène | 40. Arsenal du littoral | `sirenEmitter` |
| Pistolet des Balises | 40. Arsenal du littoral | `beaconPistol` |
| Scie du Mistral | 40. Arsenal du littoral | `mistralSaw` |
| Plasma salin | 40. Arsenal du littoral | `saltPlasma` |
| Mousquet voltaïque de l’An 220 | 41. Armes révolutionnaires | Aucune — concept à traiter |
| Pique de la République | 41. Armes révolutionnaires | Aucune — concept à traiter |
| Sabre-briquet du Fédéré | 41. Armes révolutionnaires | Aucune — concept à traiter |
| Carabine de Valmy | 41. Armes révolutionnaires | Aucune — concept à traiter |
| Pistolet du Citoyen | 41. Armes révolutionnaires | Aucune — concept à traiter |
| Grenade tricolore | 41. Armes révolutionnaires | Aucune — concept à traiter |
| Bombe de barricade | 41. Armes révolutionnaires | Aucune — concept à traiter |
| Pavé du peuple | 41. Armes révolutionnaires | Aucune — concept à traiter |
| Tambour de rupture | 41. Armes révolutionnaires | Aucune — concept à traiter |
| Couperet civique | 41. Armes révolutionnaires | Aucune — concept à traiter |
| Boule n°13 | 42. Armes de pétanque | Aucune — concept à traiter |
| Boule magnétique | 42. Armes de pétanque | Aucune — concept à traiter |
| Boule répulsive | 42. Armes de pétanque | Aucune — concept à traiter |
| Boule creuse | 42. Armes de pétanque | Aucune — concept à traiter |
| Cochonnet chercheur | 42. Armes de pétanque | Aucune — concept à traiter |
| Maillet de mesure | 42. Armes de pétanque | Aucune — concept à traiter |

Une absence de correspondance exacte ne prouve pas une absence de tout équivalent fonctionnel. Elle interdit simplement de fusionner deux armes distinctes sur la base de leur nom.

## Désignations de créatures et automates

| Nom | Source narrative | Données / représentation | État et limite |
|---|---|---|
| Cigale de cendre | 29. Cigales irradiées | — | concept-ou-temoignage  |
| Nymphe foreuse | 29. Cigales irradiées | — | concept-ou-temoignage  |
| Crisseuse | 29. Cigales irradiées | — | concept-ou-temoignage  |
| Cymbalier | 29. Cigales irradiées | — | concept-ou-temoignage  |
| Porteuse de chaux | 29. Cigales irradiées | — | concept-ou-temoignage  |
| Cigale de câble | 29. Cigales irradiées | — | concept-ou-temoignage  |
| Biset de plomb | 30. Faune urbaine | — | concept-ou-temoignage  |
| Pigeon-paratonnerre | 30. Faune urbaine | — | concept-ou-temoignage  |
| Gabian bombardier | 30. Faune urbaine | rig:gabianBombardier | representation-regionale  |
| Général Biset | 30. Faune urbaine | — | concept-ou-temoignage  |
| Rat des caves | 30. Faune urbaine | — | concept-ou-temoignage  |
| Rat-câble | 30. Faune urbaine | rig:ratCable | representation-regionale  |
| Rat-couronné | 30. Faune urbaine | rig:ratCrowned | representation-regionale · agrégat non représenté |
| Roi des Égouts | 30. Faune urbaine | — | concept-ou-temoignage  |
| Sanglier cuirassé | 31. Faune terrestre | sanglier | archetype-declare  |
| Traqueur de poussière | 31. Faune terrestre | dustStalker | archetype-declare  |
| Radcerf des collines | 31. Faune terrestre | — | concept-ou-temoignage  |
| Molosse mutant | 31. Faune terrestre | mutantHound | archetype-declare  |
| Chèvre des falaises | 31. Faune terrestre | — | concept-ou-temoignage  |
| Mante des restanques | 31. Faune terrestre | — | concept-ou-temoignage  |
| Radscorpion de garrigue | 31. Faune terrestre | — | concept-ou-temoignage  |
| Fourmi de ciment | 31. Faune terrestre | — | concept-ou-temoignage  |
| Frelon de péage | 31. Faune terrestre | — | concept-ou-temoignage  |
| Processionnaire radieuse | 31. Faune terrestre | — | concept-ou-temoignage  |
| Moustique-tigre rouge | 31. Faune terrestre | — | concept-ou-temoignage  |
| Chien de rond-point | 31. Faune terrestre | — | concept-ou-temoignage  |
| Crabe-fer | 32. Faune maritime | crab | archetype-declare  |
| Fangeux de saumure | 32. Faune maritime | brineMirelurk | archetype-declare  |
| Chasseur de saumure | 32. Faune maritime | — | concept-ou-temoignage  |
| Reine de saumure | 32. Faune maritime | — | concept-ou-temoignage  |
| Poulpe de cale | 32. Faune maritime | dockOctopus | archetype-declare  |
| Sangsue de quai | 32. Faune maritime | quayLeech | archetype-declare  |
| Murène-câble | 32. Faune maritime | — | concept-ou-temoignage  |
| Méduse de batterie | 32. Faune maritime | — | concept-ou-temoignage  |
| Oursin-grenade | 32. Faune maritime | — | concept-ou-temoignage  |
| Bernard-citerne | 32. Faune maritime | — | concept-ou-temoignage  |
| Moule mordeuse | 32. Faune maritime | — | concept-ou-temoignage  |
| Sardine-lame | 32. Faune maritime | — | concept-ou-temoignage  |
| Rascasse rouge | 32. Faune maritime | — | concept-ou-temoignage  |
| Dauphin de sonar | 32. Faune maritime | — | concept-ou-temoignage  |
| Porte-racines | 33. Végétaux et champignons | rootCarrier | archetype-declare  |
| Porte-spores | 33. Végétaux et champignons | sporeCarrier | archetype-declare  |
| Plante à spores | 33. Végétaux et champignons | sporePlant | archetype-declare  |
| Laurier rouge | 33. Végétaux et champignons | — | concept-ou-temoignage  |
| Platane hurleur | 33. Végétaux et champignons | — | concept-ou-temoignage  |
| Canne étrangleuse | 33. Végétaux et champignons | — | concept-ou-temoignage  |
| Figuière vorace | 33. Végétaux et champignons | — | concept-ou-temoignage  |
| Lavande narcotique | 33. Végétaux et champignons | — | concept-ou-temoignage  |
| Mousse alcaline | 33. Végétaux et champignons | — | concept-ou-temoignage  |
| Levain-Mère | 33. Végétaux et champignons | — | concept-ou-temoignage  |
| Vigne sanguine | 33. Végétaux et champignons | — | concept-ou-temoignage  |
| Olivier de verre | 33. Végétaux et champignons | — | concept-ou-temoignage  |
| Herbe de sirène | 33. Végétaux et champignons | — | concept-ou-temoignage  |
| Goule saline | 34. Goules régionales | saltGhoul | archetype-declare  |
| Porte-cendres | 34. Goules régionales | cinderBearer | archetype-declare  |
| Piquet Mort | 34. Goules régionales | — | concept-ou-temoignage  |
| Gilet Fumé | 34. Goules régionales | — | concept-ou-temoignage  |
| Vacancier éternel | 34. Goules régionales | — | concept-ou-temoignage  |
| Usager | 34. Goules régionales | — | concept-ou-temoignage  |
| Agent d’accueil | 34. Goules régionales | — | concept-ou-temoignage  |
| Supporter cendré | 34. Goules régionales | — | concept-ou-temoignage  |
| CERFA‑77 | 36. Robots civils | rig:cerfa77 | representation-regionale  |
| CRS‑77 | 36. Robots civils | — | concept-ou-temoignage  |
| Percepteur 3000 | 36. Robots civils | — | concept-ou-temoignage  |
| Contrôleur du Réseau | 36. Robots civils | — | concept-ou-temoignage  |
| Mairie-Adjoint | 36. Robots civils | — | concept-ou-temoignage  |
| Radar automatique | 36. Robots civils | — | concept-ou-temoignage  |
| Fourrière mobile | 36. Robots civils | — | concept-ou-temoignage  |
| Balayeuse municipale | 36. Robots civils | — | concept-ou-temoignage  |
| Facteur Autopostal | 36. Robots civils | — | concept-ou-temoignage  |
| Agent d’accueil 24/24 | 36. Robots civils | — | concept-ou-temoignage  |
| Cantinier scolaire | 36. Robots civils | — | concept-ou-temoignage  |
| Inspecteur du Travail | 36. Robots civils | — | concept-ou-temoignage  |
| Drone archiviste | 36. Robots civils | archiveDrone | archetype-declare  |
| Huissier d’abri | 36. Robots civils | vaultBailiff | archetype-declare  |
| Sirène du Mistral | 36. Robots civils | mistralSiren | archetype-declare  |
| Soudeur autonome | 36. Robots civils | welder | archetype-declare  |
| Marche-grue | 36. Robots civils | craneWalker | archetype-declare  |
| Midi-Zéro | 29. Prose et sous-titres | — | concept-ou-temoignage  |
| Blattes de cité | 30. Prose et sous-titres | — | concept-ou-temoignage  |
| Punaises de foyer | 30. Prose et sous-titres | — | concept-ou-temoignage  |
| Taupes de métro | 30. Prose et sous-titres | — | concept-ou-temoignage  |
| Fouines de compteur | 30. Prose et sous-titres | — | concept-ou-temoignage  |
| Mites d’archive | 30. Prose et sous-titres | — | concept-ou-temoignage  |
| Termites de béton | 30. Prose et sous-titres | — | concept-ou-temoignage  |
| Écorcheur calcaire | 31. Prose et sous-titres | — | concept-ou-temoignage  |
| La Sardine | 32. Prose et sous-titres | — | concept-ou-temoignage  |
| Hommes-lourds | 35. Prose et sous-titres | — | concept-ou-temoignage  |
| Agrégats ATLAS | 35. Prose et sous-titres | — | concept-ou-temoignage  |
| César ATLAS | 35. Prose et sous-titres | — | concept-ou-temoignage  |
| Roi-Couronne | Catalogue de témoins v0.46 | — | concept-ou-temoignage  |
| Coq d’alarme | Catalogue de témoins v0.46 | — | concept-ou-temoignage  |
| Blatte de cité | Catalogue de témoins v0.46 | — | concept-ou-temoignage  |
| Escargot de béton | Catalogue de témoins v0.46 | — | concept-ou-temoignage  |
| Limace alcaline | Catalogue de témoins v0.46 | — | concept-ou-temoignage  |
| Chien du rond-point | Catalogue de témoins v0.46 | — | concept-ou-temoignage  |
| Cigale du Mistral | Catalogue de témoins v0.46 | mistralCicada, rig:mistralCicada | representation-regionale  |
| Contrôleur RNF | Catalogue de témoins v0.46 | — | concept-ou-temoignage  |

Les désignations proches ou au singulier/pluriel restent séparées tant qu’un alias n’est pas attesté : le total n’est pas un décompte d’espèces uniques. Les cinq formes régionales du module 13 ne sont pas les vingt-cinq noms du catalogue des témoins. Les quatre figures Fallout récurrentes du même module conservent leurs identités. Les variantes de cigales, les créatures marines et les robots seulement nommés restent des concepts tant que leur boucle n’est pas réalisée.

## Manques maintenus ouverts

- Profils génériques restants : harpons, charges de saumure, bobines et combustibles ne sont pas des alimentations uniques achevées.
- Pique de la République et Mousquet voltaïque de l’An 220 ne sont pas assimilés à une lance ou un mousquet laser existant.
- Pigeons postaux neutres distincts du Biset de plomb, du Pigeon-paratonnerre et du Général Biset.
- Roi des Égouts et Roi-Couronne : rapprochement éditorial à résoudre, aucun boss déclaré livré.
- Inventaire des armures, acquisition de chaque arme, équilibrage et campagne humaine encore à examiner.
- COCHONNET PR 17 demeure séparé.

## Reproduire la vérification

`python tools/audit_regional_content.py --check`

Le générateur examine les sources locales ; il ne contacte aucun service et n’édite aucune sauvegarde. Le contrôle échoue si les données documentées ne correspondent plus aux sources.
