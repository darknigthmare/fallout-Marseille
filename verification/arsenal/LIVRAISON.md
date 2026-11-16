# Le carnet des ateliers — livraison du 11 novembre 2026

Base exacte : `580f432e32369a950bb7761f9441da9f063f521e` (cour et bible consolidée).
Sources et programme validés publiés dans `01d1ed8c484182c8974a0282cdaff722fc857717`.

## Jeu et bible

55 identifiants régionaux déjà déclarés reçoivent un contrat visuel stable, indépendant de leur nom et conservé par les copies modifiées. Ils ne sont pas 55 armes nouvelles ni 55 modèles propres. Trois présentations supplémentaires : aiguilles pneumatiques (deux armes), scie céramique et charge courte de 40 mm du mortier. L’Arc salin, le Juge civique et le Pistolet CONCORDE retrouvent leur famille visuelle. Les statistiques, alimentations, stocks, récompenses et anciens registres ne sont pas modifiés.

DATA → ATELIERS · ARMES donne accès à un carnet de 55 fiches, avec recherche, pagination, filtre de possession, valeurs de référence et lien vers l’inventaire pour les armes possédées. La consultation ne fournit ni arme, ni munition, ni équipement automatique.

La bible documentaire 1.3 conserve les parties précédentes et ajoute la section 69, l’annexe `LORE_ARSENAL_REGIONAL.md` et l’inventaire généré Markdown/JSON. Celui-ci distingue 55 IDs régionaux, 49 noms d’armes de conception et 98 désignations de créatures/automates. Ces désignations incluent des variantes de nom et ne sont pas 98 espèces distinctes. Les neuf assemblages du bestiaire existaient avant ce lot. Correspondance exacte normalisée, sans alias supposé.

## Validation effectuée

Run GitHub **43082206647**, job **130737353474**, entrée `89c5b6bf47465ae55ddf5ef75d11b6795118ca47` : terminé avec succès, publication comprise.

- 795 tests de logique de lore, dont 68 nouveaux ;
- 19 tests de registre narratif et 20 tests du nouvel inventaire ;
- 45 contrôles du modèle FPS conservé et 102 du bestiaire conservé ;
- compilation complète et contrôle déterministe, inventaire à jour, quatre commandes territoriales ;
- 975 contrôles dans 18 parcours navigateur, dont 48 pour le nouveau carnet et ses armes, sans exception JavaScript ;
- 40 contrôles des reprises de cour, 65 des oiseaux et 26 des rats, exécutés sur le nouveau programme.

Les artefacts **13885342291** (programme et sources) et **13885477010** (preuves) ont été téléchargés, leurs SHA-256 vérifiés, les treize sources modifiées comparées et les deux inventaires générés comparés au travail local. Les quatre sorties sont identiques octet pour octet au programme final testé localement.

HTML SHA-256 : `f3aa677ba40dcd4325bc09c8cd54208775b5e7632e070291606aa009bcc5b0a5`.
Rapport courant : `verification/arsenal/QA.json`. Les anciennes preuves ne sont pas réattribuées à ce programme. Les répétitions locales et distantes ne sont pas comptées comme des tests distincts.

Le workflow temporaire est retiré. Le workflow permanent refuse une sortie compilée ou un inventaire périmés avant de reconstruire, puis vérifie le nouveau carnet et les anciens parcours. Il n’écrit plus de fichiers avec le compte automatique : les corrections doivent être livrées avec leurs sources et leurs sorties.

## Limites

Le tir et le rechargement sont natifs, mais les armes d’inspection, positions et départs sont préparés, avec stockage mémoire isolé et rendu logiciel. Pas de preuve d’acquisition naturelle des 55 armes, d’équilibrage global, de toutes les manettes ou d’une campagne humaine sur toute la carte IGN.

Les reprises après fermeture concernent les checkpoints existants cour/oiseaux/rats sur ce programme, avec un profil Chromium sur disque et une fermeture normale. Elles ne sont pas une nouvelle reprise disque spécifique au carnet, ni une certification contre coupure électrique. La navigation persistante locale était bloquée par politique administrateur ; les résultats à froid proviennent de GitHub, sans contournement de cette politique.

Les alimentations et familles restent partagées pour plusieurs autres armes. Pas de son propre ajouté, pas de nouvelle créature hostile, pas de réseau postal régional ni de ferry. La PR 17 COCHONNET reste séparée et intacte.

Le ZIP est une mise à jour sans les grandes archives géographiques. Exporter la sauvegarde, conserver les packs IGN, les lanceurs et la même origine de lancement. Ne pas écraser une installation binaire de COCHONNET ou une branche plus récente. La fusion et le déploiement restent des faits distincts de ce run validé ; consulter la PR pour leur statut.
