# Continuité des factions et des relais

Ce prolongement ajoute huit dossiers jouables aux factions françaises déjà présentes dans [le lore v0.46](LORE_RECONSTRUIT_V046.md). Les neuf factions, les huit dossiers historiques et les vingt-cinq noms du bestiaire des témoins sont conservés. Les noms et positions des lieux du catalogue v0.42 restent inchangés.

Le canon utilisé ici est celui conservé dans [04_lore.js](../src/v046/04_lore.js) : Convention des Cendres, Gilets de Cendre, Syndicat Perpétuel, CONCORDE, Communes du Mistral, Sans-Dossier, COCHONNET, Vigies et Insulaires. Les huit histoires et leurs issues ci-dessous sont des **extensions nouvelles de ce canon**. Elles ne sont pas présentées comme une récupération des scripts, retags ou armes de la v0.44, ni comme une transcription supplémentaire d’une conversation ChatGPT.

## Les dossiers des relais

| Dossier | Faction et contact dans le catalogue existant | Progression | Décisions |
|---|---|---|---|
| Le droit d’être compté | Convention des Cendres ; `v042-marseille-caravan-01`, Halte caravanière · Vieux-Port | Recueillir les témoignages d’habitants de deux relais marseillais distincts, puis revenir au contact | Protéger les identités ; ou déposer un registre contradictoire auprès des assemblées |
| Le formulaire impossible | CONCORDE ; `v042-marseille-caravan-02`, Relais marchand · Saint-Charles | Intelligence 5 et un circuit pour analyser la copie CERFA-77 ; **ou** deux témoignages distincts | Obtenir une rectification avec reçu pour les habitants ; ou publier les contradictions |
| Les signaux des crêtes | Vigies ; `v042-garlaban-caravan-01`, Halte caravanière · Font de Mai | Examiner sur place les trois repères `v042-garlaban-landmark-01`, `-02` et `-03`, puis revenir au relais | Alerte publique assortie de ses incertitudes ; ou transmission préalable aux relais locaux |
| L’autre rive | Insulaires ; `v042-frioul-caravan-01`, Halte caravanière · Ratonneau | Revenir avec les fournitures de l’issue choisie | Réserve de soin : deux eaux et un antibiotique ; ou passage accompagné : deux eaux et deux vivres |
| Les mains avant la cadence | Syndicat Perpétuel ; `v042-laciotat-caravan-01`, Halte caravanière · La Ciotat | Examiner le Mémorial · Fontsainte et l’Épave · Mugel sur place, puis revenir au contact | Atelier sous contrôle des équipes : trois ferrailles et un circuit ; ou halte des blessés : deux tissus et deux eaux |
| Ceux qu’on attend | Sans-Dossier ; `v042-marseille-caravan-02`, Relais marchand · Saint-Charles | Recueillir deux engagements de relais marseillais distincts, puis revenir au contact | Garder les lieux d’attente sans publier les familles ; ou les approvisionner avec deux vivres et deux eaux |
| L’eau à hauteur de table | Communes du Mistral ; `v042-marseille-caravan-01`, Halte caravanière · Vieux-Port | Obtenir précisément les engagements du Vieux-Port et de Saint-Charles, puis revenir au Vieux-Port | Réserve finie des tables d’accueil : trois eaux et un tissu ; ou matériel confié aux équipes de récipients : trois ferrailles et un circuit |
| Le passage ne se vend pas | Gilets de Cendre ; `v042-huveaune-caravan-02`, Relais marchand · Aubagne Haute | Obtenir précisément les engagements de la Halte caravanière · Vallée de l’Huveaune et du relais d’Aubagne Haute, puis revenir à Aubagne Haute | Cantine sans péage : trois vivres et deux eaux ; ou fournitures de repères : deux ferrailles et deux tissus |

Les dossiers du Syndicat et des Sans-Dossier sont ajoutés après `3d94e4c`. Les quatre précédents gardent leurs identifiants, contacts, coûts, preuves et décisions. Le dossier du Syndicat est lié explicitement à la Halte caravanière · La Ciotat, visitée auprès d’un habitant réellement présent. La Cale sèche, dont le placement source est refusé dans le bassin, ne sert pas de contact. Il s’appuie sur deux repères nommés du catalogue : s’il en manque un dans un autre pack, il reste indisponible ; un autre lieu ne le remplace pas. Si la halte explicite manque au catalogue, aucun autre relais ne lui est substitué. Les pièces et fournitures sont remises aux représentants : aucune machine du monde n’est annoncée comme physiquement réparée ou animée. Le dossier des Sans-Dossier ne prétend ni rétablir un train ni créer une traversée.

Les contacts sont hébergés dans des relais fictifs existants du catalogue du jeu. Ce rattachement ne remplace pas leurs coordonnées et n’identifie pas ces points comme des relevés du bâtiment des Baumettes ou du Lazaret réel. Il ne crée pas de nouveau trajet de bateau ni de simulation de quarantaine.

Les dossiers sont disponibles dans **Pip-Boy → DATA → RELAIS ET DOSSIERS**. La rubrique **FRANCE EN CENDRES** conserve ses anciens dossiers et propose un accès à ces engagements. Les habitants concernés peuvent également ouvrir les nouveaux dialogues ; le choix « Parler du secteur et commercer » donne toujours accès aux échanges historiques.

## Présence, preuves et coûts

L’ouverture, les témoignages, l’analyse et la conclusion vérifient la présence d’un habitant vivant du bon relais, à moins de huit mètres, à une hauteur compatible et avec une ligne de vue libre. Un contact découvert doit être présent dans la scène active. Les callbacks recontrôlent ces conditions au moment de l’action, après l’affichage du dialogue. Un chargement, un combat proche, le banc synthétique ou une scène intérieure ne permettent pas de payer ni de recevoir une récompense de ces dossiers.

Un même relais ne peut pas fournir deux témoignages au même dossier. Pour les Vigies et le Syndicat, une lecture distante de l’archive ne valide pas de repère : l’interaction d’examen doit être présente, à portée et visible dans la scène. Le suivi indique le prochain lieu utile ; il ne complète aucune preuve, ne déplace pas le personnage et n’accorde aucune récompense.

Chaque dossier possède deux issues exclusives et une récompense unique. Les fournitures sont retirées de l’inventaire normal. Les capsules, l’expérience et les réputations sont appliquées dans la même transaction que la décision. Une écriture refusée ou une exception de stockage rétablit les ressources, les réputations et l’état du dossier ; l’autre sauvegarde n’hérite pas de ces progrès.

## Réactivité et radios

Les décisions modifient la réputation narrative de la faction et les réputations du jeu déjà utilisées par les commerces et options sociales : Ligue, Continuité, Réseau des Vigies, Veilleurs ou Francs du Large selon l’issue. Les habitants du contact rappellent la décision conservée après un retour ou une reprise.

Trois stations textuelles complètent les radios existantes :

- **Canal 13 — Ronds-Points Libres** rend compte des identités protégées, des contradictions CERFA-77, des observations des crêtes, des priorités des équipes des chantiers et des lieux d’attente réellement conclus.
- **Ligue des Cent Trêves** réutilise les mènes et victoires COCHONNET déjà sauvegardées et réagit aux deux dossiers historiques concernés.
- **Lazaret — l’autre rive** distingue le besoin initial, la réserve de soin livrée et le passage approvisionné.

Les Communes et les Gilets rendent aussi compte des quantités remises et des engagements conservés, sans annoncer une eau illimitée, une pompe animée, un barrage levé ou un convoi autonome. Ces bulletins sont des transcriptions, dans le lecteur de radio existant. Aucun enregistrement vocal, flux audio, musique commerciale ou bande v0.44 retrouvée n’est annoncé.

## Sauvegarde et vérification

Le registre `v053Lore` conserve les huit engagements, leurs preuves bornées, l’analyse éventuelle et leur issue. Il ne remplace pas `v046.lore`. La migration rejette les identifiants étrangers au catalogue, les faux noms d’issue et les doublons ; une nouvelle partie commence avec un registre vide.

[lore_continuity.cjs](../tests/expansion/lore_continuity.cjs) vérifie les liaisons sur le véritable catalogue, les conditions de contact, les preuves distinctes, les coûts, les récompenses uniques, le rollback, la reprise, le changement de sauvegarde, les bulletins et la conservation des boutons historiques. Ses scènes, positions de PNJ et stockage sont des bancs contrôlés explicitement déclarés ; ils ne constituent pas un parcours humain complet des huit dossiers.


## Source du lore et accès au projet ChatGPT

Le projet ChatGPT correspondant a été retrouvé et consulté ; les éléments accessibles ne contiennent pas de lore supplémentaire exploitable. Les archives ne sont pas accessibles depuis cet environnement cloud. Les neuf factions, huit dossiers historiques et vingt-cinq noms déjà conservés dans le dépôt restent la source du canon ; les nouvelles histoires sont des prolongements écrits du jeu.

Lors de la livraison `f4a7337`, la migration d’une campagne à quatre dossiers conservait ses preuves, décisions et journal, et ajoutait `cadences` et `attente` vierges. La suite de contrats couvre aussi les nouveaux coûts, les deux décisions de chaque dossier, les refus à distance, l’observation physique sans croisement des dossiers, le rollback de stockage, les bulletins et les dialogues de retour. Le [pilote natif complémentaire](../tests/expansion/faction_dossiers_native.py) a réussi **213/213 contrôles**, avec cinq captures, sur le HTML `ed6e4103b23a45c413fef182862a93accb72ec25c6e1d8b101251822bfd5c670`. Il accomplit les deux nouvelles décisions par les commandes visibles, deux contacts marseillais distincts et les deux examens réels de La Ciotat, paie exactement les fournitures, puis conserve les preuves, issues, coûts et réputations par sauvegarde et Continuer. Les quatre anciens dossiers restent vierges dans cette nouvelle partie. Les aides de sélection de secteur, placement sur le terrain source, gel et fournitures de paiement sont déclarées ; aucun PNJ, relief, témoignage ni résultat de quête n’est injecté. Les 18 XP accordés lors de la première découverte effective de la zone au chargement sont vérifiés séparément des 85 et 95 XP des dossiers. Les tentatives précédentes échouées restent exclues de ce résultat.


## Communes et Gilets après `f4a7337`

`partage` et `passage_libre` complètent les engagements de relais pour les deux factions jusque-là sans dossier de continuité ; COCHONNET conserve ses deux dossiers historiques et ses mènes. Les six définitions et liaisons livrées dans `f4a7337` restent identiques, vérifiées par deux empreintes de régression. Une campagne existante conserve exactement ses six dossiers et son journal ; seuls les deux nouveaux registres sont ajoutés vierges.

Chaque nouveau dossier exige les **deux relais nommés**, et pas deux habitants d’un même relais ni deux lieux quelconques du secteur. Le contact et les témoins doivent exister dans le catalogue compatible : l’absence d’un lieu nommé rend le dossier indisponible, sans substituer un autre hôte. Les conditions de présence, hauteur, vie, sol stable, ligne de vue et hors combat restent celles des transactions communes. Les fournitures et récompenses sont finies, exclusives et sauvegardées ensemble, avec restauration complète si l’écriture échoue.

Ces histoires sont des prolongements originaux du canon du dépôt. Les tables, équipes et convois évoqués sont des engagements narratifs des contacts existants : ce lot n’ajoute pas de canalisation, de pompe fonctionnelle, de bâtiment mesuré, de taxation automatique ni de convoi mobile. Les Communes confient soit une réserve d’accueil réellement débitée, soit des pièces aux équipes ; les Gilets ravitaillent soit la cantine, soit les équipes de repères. Les différentes réputations influencent les systèmes existants, tandis que le journal, Canal 13 et le dialogue du contact rappellent la décision conservée.

Les **58 contrats contrôlés** de [lore_continuity.cjs](../tests/expansion/lore_continuity.cjs) réussissent sur les huit définitions, dont la conservation des six précédentes, les deux témoins explicites, les deux choix de chaque nouveau dossier, les coûts incomplets, les récompenses uniques, les migrations et les refus/échecs de stockage. Ils ne remplacent pas une visite native. Le [pilote natif des Communes et des Gilets](../tests/expansion/community_dossiers_native.py) a réussi **327/327 contrôles**, avec **six captures réelles**, sur le HTML `844376c014575111f268f292c8307bb3f47ac33629604406f5e0da00104c5a34`. Il ouvre les dossiers par E et les dialogues réels, recueille les deux engagements nommés de chaque histoire, paie les fournitures normales, vérifie les 40/45 capsules et les 90/95 XP des décisions, les réputations, Canal 13 et le retour aux contacts, puis conserve exactement les preuves, issues et journal par sauvegarde, rechargement et Continuer. Les six dossiers précédents restent vierges dans cette nouvelle partie. Les deux cartes conclues sont cadrées séparément après Continuer. Les 18 XP de première découverte de la zone au chargement sont vérifiés séparément des récompenses de quête.

Le résultat **213/213 sur `ed6e4103…`** du paragraphe précédent appartient à la livraison `f4a7337` : il valide alors les dossiers du Syndicat et des Sans-Dossier. Il reste historique et ne certifie pas le nouveau programme ni les nouveaux contacts des Gilets.

Les cartes des engagements conclus affichent leur texte de décision une seule fois ; les dossiers actifs conservent leur progression distincte. La régression du panneau couvre les huit cartes conclues, après avoir reproduit le doublon dans le rendu précédent.

Le parcours natif est assisté : sélection des secteurs installés, placement de la caméra sur des points libres du terrain source, gel de simulation et dotation initiale destinée aux coûts réels. Les actions des dossiers passent par les PNJ, commandes et boutons de production ; la géographie, les acteurs, les preuves et le stockage du navigateur restent ceux du jeu servi par HTTP. Les branches alternatives et les échecs de sauvegarde relèvent des contrats contrôlés. La session Chromium de bureau ne certifie pas un parcours humain exhaustif ni un appareil mobile ou une manette physique. Une sonde de métadonnées locale annulée à la reprise et 18 échecs de sondes externes historiques sont conservés dans le rapport brut ; les fichiers et requêtes de sources locales restent sans erreur HTTP. Les essais préparatoires et échoués sont distincts du résultat courant.

## Les reçus reviennent aux relais

Après les décisions des Communes et des Gilets, deux suites donnent un usage à la copie du reçu. **Le reçu revient à table** demande de porter la copie du Vieux-Port à Saint-Charles, puis de revenir au Vieux-Port. **La copie n’est pas un laissez-passer** suit le même principe entre Aubagne Haute et la Halte de la vallée. Le second relais accuse réception par son dialogue habituel, ouvert avec **E** ; le contact initial remet ensuite un contre-don unique.

| Dossier et décision déjà conservée | Contre-don au retour |
| --- | --- |
| Communes · Réserve des tables d’accueil | Un Stimpak de la trousse commune |
| Communes · Matériel des équipes de récipients | Une pièce d’arme du stock d’atelier |
| Gilets · Cantine des personnes en attente | Une ration mise de côté par l’équipe |
| Gilets · Fournitures des repères | Une ferraille et un tissu du stock du relais |

Ces objets rejoignent l’inventaire ordinaire et son poids. Les huit décisions précédentes, leurs preuves, les fournitures déjà payées, les capsules, l’expérience et les réputations restent conservées exactement ; le retour n’accorde pas une deuxième récompense de dossier. Chaque don correspond au choix effectué, puis son action disparaît. Une autre scène, un rechargement ou un retour au même PNJ ne reconstitue pas ce stock.

Le suivi du reçu choisit d’abord le second relais nommé, puis le contact initial. Le journal expose ces deux étapes et le registre des décisions garde le compte rendu final. Les dialogues de retour et Canal 13 distinguent la copie encore attendue, l’accusé de réception et le don déjà remis. Le commerce historique demeure accessible.

Ces suites sont des prolongements originaux du canon conservé dans le dépôt. Elles s’appuient sur les habitants existants sans déplacer les relais, modifier les relevés géographiques ni ajouter un convoi mobile. Les copies sont des engagements narratifs sauvegardés, sans objet de papier supplémentaire dans le sac. Les dons sont des lots finis remis au personnage ; ils ne produisent pas de ressources à intervalles réguliers.

Le registre `v053Lore.returns` conserve deux paires de drapeaux bornés, et `returnJournal` garde au plus quatre événements. La migration d’une campagne antérieure conserve tous ses dossiers et son journal, puis ajoute les retours vierges. Elle rejette un don marqué reçu sans accusé de réception, une issue inconnue et les événements incohérents ou répétés. Si un catalogue personnalisé retire temporairement un relais nommé, les échanges restent indisponibles mais les dons déjà remis restent conservés ; restaurer ce catalogue ne les rend pas à nouveau disponibles. Les interactions recontrôlent contact vivant, découverte, distance, hauteur, ligne de vue, sol, chargement et absence de combat au moment du clic. Le suivi de dossier et celui des reçus utilisent la même restauration complète si leur sauvegarde échoue. Les nouveaux callbacks de dialogue refusent également une sauvegarde ou un monde qui a remplacé celui de leur ouverture. Une écriture refusée ou une exception restaure la totalité de la campagne en gardant sa référence, notamment le registre, les deux journaux, les fournitures et les instantanés d’acteurs que la sauvegarde ordinaire peut avoir préparés.

Les **90 contrats contrôlés** de [lore_continuity.cjs](../tests/expansion/lore_continuity.cjs) couvrent les 58 contrats antérieurs et 32 contrôles complémentaires : quatre lots selon les issues, remise et retour, absence de seconde récompense, rejets physiques, callbacks périmés, limites du sac, migrations avec retrait/restauration de catalogue, rollback composé avec la vraie enveloppe de sauvegarde v0.49 et séparation des campagnes. Les empreintes des huit définitions et des huit liaisons sont comparées aux valeurs de `29df190` ; aucun ancien dossier n’est réécrit. Le [pilote natif](../tests/expansion/community_dossiers_native.py) accepte `--with-returns` pour visiter les deux seconds relais, remettre les copies par E, recevoir les dons par les boutons de dialogue, inspecter journal/radio puis reprendre par Continuer. Ses résultats seront rattachés au HTML effectivement exécuté dans le bilan de cette nouvelle livraison ; les 327 contrôles sur `844376c…` du paragraphe précédent restent historiques.

La campagne du 1er novembre avant intégration conserve les deux chaînes complètes avec leurs retours : **472 contrôles natifs et 10 captures**, sur le HTML `98a78a1c…`, avec écritures et Continuer réels. Ce [rapport historique](../verification/expansion/continuation_20261101/lore/COMMUNITY_DOSSIERS_NATIVE.json) décrit les déplacements et ressources préparés. Le [bilan courant intégré](../verification/expansion/continuation_20261101_integrated/CONTINUATION_INTEGRATION.json) rattache les nouvelles vérifications au HTML `c0f13de3…` ; les preuves du HTML précédent ne lui sont pas réattribuées. Les 327 contrôles et six captures du HTML `844376c0…` demeurent historiques.
