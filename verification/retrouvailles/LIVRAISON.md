# De main en main — livraison et vérification

La consigne du Vieux-Port accueille désormais Éloi, Mina et Rachid. Le joueur peut leur rendre personnellement la clef, la bague et le sifflet, ou conserver le dépôt chez Nora. Chaque souvenir, reçu et remise est suivi séparément. Les parties déjà terminées conservent leur conclusion et leurs 45 capsules déjà reçues ; les retrouvailles restent possibles sans seconde récompense. Le registre des gabians passe au schéma 2 sans inventer de rencontre antérieure.

Base : `9849cb57512b93379e27070f8145c23180005cd4`. Sources et quatre sorties canoniques publiées dans `6dbefa271e9eb01ad6ab6ace461ea2280fc7df6f`.

Le run 42904811029, job 130140120573, a terminé avec succès : 625 tests de logique, quatre régressions territoriales, compilation complète et contrôle déterministe, 837 contrôles dans quinze parcours, 65 contrôles de six reprises à froid des oiseaux et 26 contrôles historiques de reprise des rats. Aucune exception JavaScript dans ces parcours.

Les artefacts 13805840204 et 13805805324 ont été téléchargés et inspectés. Les quatre sorties et les sources de jeu modifiées correspondent octet pour octet à la version locale corrigée. Le paquet reprend les sorties canoniques téléchargées. `QA.json` contient leurs empreintes exactes ; les anciens rapports restent historiques.

Les reprises à froid emploient un profil Chromium sur disque, une fermeture complète puis le programme de production inchangé et son bouton Continuer. Elles couvrent un pigeon en vol, les deux conclusions postales, un projectile et un gabian blessé, un panier suspendu et des restitutions partielles. Ce n’est pas une certification contre les coupures de courant, de tous les navigateurs ou d’une campagne humaine complète.

La publication demeure dans la PR 18, sans fusion sur main ni intégration de COCHONNET (PR 17). L’import provisoire est retiré ; le workflow permanent reprend les nouveaux tests. Ses contrôles sont distincts du run canonique terminé ci-dessus.

Le ZIP est une mise à jour cumulative : il ne remplace pas les grandes archives géographiques, tous les modules source ni les lanceurs. Exporter la sauvegarde, conserver les packs IGN et ne pas écraser une installation binaire de COCHONNET. Les animations détaillées de remise, le doublage et les trajets maritimes restent ouverts.
