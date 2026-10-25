# Continuité des factions et des relais

Ce prolongement ajoute quatre dossiers jouables aux factions françaises déjà présentes dans [le lore v0.46](LORE_RECONSTRUIT_V046.md). Les neuf factions, les huit dossiers historiques et les vingt-cinq noms du bestiaire des témoins sont conservés. Les noms et positions des lieux du catalogue v0.42 restent inchangés.

Le canon utilisé ici est celui conservé dans [04_lore.js](../src/v046/04_lore.js) : Convention des Cendres, Gilets de Cendre, Syndicat Perpétuel, CONCORDE, Communes du Mistral, Sans-Dossier, COCHONNET, Vigies et Insulaires. Les quatre histoires et leurs issues ci-dessous sont des **extensions nouvelles de ce canon**. Elles ne sont pas présentées comme une récupération des scripts, retags ou armes de la v0.44, ni comme une transcription supplémentaire d’une conversation ChatGPT.

## Les quatre nouveaux dossiers

| Dossier | Faction et contact dans le catalogue existant | Progression | Décisions |
|---|---|---|---|
| Le droit d’être compté | Convention des Cendres ; `v042-marseille-caravan-01`, Halte caravanière · Vieux-Port | Recueillir les témoignages d’habitants de deux relais marseillais distincts, puis revenir au contact | Protéger les identités ; ou déposer un registre contradictoire auprès des assemblées |
| Le formulaire impossible | CONCORDE ; `v042-marseille-caravan-02`, Relais marchand · Saint-Charles | Intelligence 5 et un circuit pour analyser la copie CERFA-77 ; **ou** deux témoignages distincts | Obtenir une rectification avec reçu pour les habitants ; ou publier les contradictions |
| Les signaux des crêtes | Vigies ; `v042-garlaban-caravan-01`, Halte caravanière · Font de Mai | Examiner sur place les trois repères `v042-garlaban-landmark-01`, `-02` et `-03`, puis revenir au relais | Alerte publique assortie de ses incertitudes ; ou transmission préalable aux relais locaux |
| L’autre rive | Insulaires ; `v042-frioul-caravan-01`, Halte caravanière · Ratonneau | Revenir avec les fournitures de l’issue choisie | Réserve de soin : deux eaux et un antibiotique ; ou passage accompagné : deux eaux et deux vivres |

Les contacts sont hébergés dans des relais fictifs existants du catalogue du jeu. Ce rattachement ne remplace pas leurs coordonnées et n’identifie pas ces points comme des relevés du bâtiment des Baumettes ou du Lazaret réel. Il ne crée pas de nouveau trajet de bateau ni de simulation de quarantaine.

Les dossiers sont disponibles dans **Pip-Boy → DATA → RELAIS ET DOSSIERS**. La rubrique **FRANCE EN CENDRES** conserve ses anciens dossiers et propose un accès à ces engagements. Les habitants concernés peuvent également ouvrir les nouveaux dialogues ; le choix « Parler du secteur et commercer » donne toujours accès aux échanges historiques.

## Présence, preuves et coûts

L’ouverture, les témoignages, l’analyse et la conclusion vérifient la présence d’un habitant vivant du bon relais, à moins de huit mètres, à une hauteur compatible et avec une ligne de vue libre. Un contact découvert doit être présent dans la scène active. Les callbacks recontrôlent ces conditions au moment de l’action, après l’affichage du dialogue. Un chargement, un combat proche, le banc synthétique ou une scène intérieure ne permettent pas de payer ni de recevoir une récompense de ces dossiers.

Un même relais ne peut pas fournir deux témoignages au même dossier. Pour les Vigies, une lecture distante de l’archive ne valide pas de repère : l’interaction d’examen doit être présente, à portée et visible dans la scène. Le suivi indique le prochain lieu utile ; il ne complète aucune preuve, ne déplace pas le personnage et n’accorde aucune récompense.

Chaque dossier possède deux issues exclusives et une récompense unique. Les fournitures sont retirées de l’inventaire normal. Les capsules, l’expérience et les réputations sont appliquées dans la même transaction que la décision. Une écriture refusée ou une exception de stockage rétablit les ressources, les réputations et l’état du dossier ; l’autre sauvegarde n’hérite pas de ces progrès.

## Réactivité et radios

Les décisions modifient la réputation narrative de la faction et les réputations du jeu déjà utilisées par les commerces et options sociales : Ligue, Continuité, Réseau des Vigies, Veilleurs ou Francs du Large selon l’issue. Les habitants du contact rappellent la décision conservée après un retour ou une reprise.

Trois stations textuelles complètent les radios existantes :

- **Canal 13 — Ronds-Points Libres** rend compte des identités protégées, des contradictions CERFA-77 et des observations des crêtes réellement conclues.
- **Ligue des Cent Trêves** réutilise les mènes et victoires COCHONNET déjà sauvegardées et réagit aux deux dossiers historiques concernés.
- **Lazaret — l’autre rive** distingue le besoin initial, la réserve de soin livrée et le passage approvisionné.

Ces bulletins sont des transcriptions, dans le lecteur de radio existant. Aucun enregistrement vocal, flux audio, musique commerciale ou bande v0.44 retrouvée n’est annoncé.

## Sauvegarde et vérification

Le registre `v053Lore` conserve les quatre engagements, leurs preuves bornées, l’analyse éventuelle et leur issue. Il ne remplace pas `v046.lore`. La migration rejette les identifiants étrangers au catalogue, les faux noms d’issue et les doublons ; une nouvelle partie commence avec un registre vide.

[lore_continuity.cjs](../tests/expansion/lore_continuity.cjs) vérifie les liaisons sur le véritable catalogue, les conditions de contact, les preuves distinctes, les coûts, les récompenses uniques, le rollback, la reprise, le changement de sauvegarde, les bulletins et la conservation des boutons historiques. Ses scènes, positions de PNJ et stockage sont des bancs contrôlés explicitement déclarés ; ils ne constituent pas un parcours humain complet des quatre dossiers.
