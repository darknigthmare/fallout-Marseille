"""Actual authored-scene captures from the exact runnable HTML. Cameras and some
inventory/quest states prepared for visibility; controller routes tested separately.
No image generation or real geographic sources used."""
from qa029_support import Game,R,H
import json,hashlib,math
G=Game('CAPTURES_V030');c=G.c;p=G.p;images=[];camera={};p.on('dialog',lambda d:d.accept())
def draw(pos,yaw=0,pitch=0,third=False):
 camera.update(zone=G.s()['player']['zone'],pos=pos,yaw=yaw,pitch=pitch,third=third);return c('v030Render',pos,yaw,pitch,third,2)
def shot(file,title,note):
 p.evaluate("document.getElementById('toastStack').innerHTML=''");p.wait_for_timeout(100);p.screenshot(path=str(R/'verification'/file));images.append({'file':file,'title':title,'note':note,'camera':dict(camera),'renderer':'Chromium logiciel','html_sha256':hashlib.sha256(H.encode()).hexdigest()});print('CAPTURE',file,flush=True)
def near(id):
 a=G.near(id);s=G.s()['player'];draw(s['pos'],s['yaw'],s['pitch']);return a
try:
 G.memory();p.wait_for_timeout(3000);shot('01_menu.png','Sous la cuirasse','Menu du HTML exact. Le nouveau départ séparé demande une confirmation et n’attribue aucune armure assistée.')
 c('v030Start');c('v021MuteEnemies');c('v022Time',10);c('v028Settings',{'quality':'high'});draw([11,2,38],0,-.045)
 shot('02_baie_assistance.png','Une baie dans la cour des amarres','Gantry, établi, châssis, casier et portillon ajoutés au lieu fictif existant. Ce n’est pas une reconstruction cadastrale.')
 draw([10,1.75,35.5],0,-.12);shot('03_chassis_stationne.png','Le M-45 avant sa remise en service','Assemblage 3D original de primitives : plaques, hydraulique, cage et logement de cœur. Les modèles historiques partagent cette base visuelle, pas des modèles extraits de Fallout.')
 near('v030:alba');c('v030Talk');shot('04_alba_dialogue.png','Alba refuse un simple voyant vert','Dialogue original. L’intervention doit distinguer le porteur, les plaques et l’assistance ; l’essai est réalisable sans cellule neuve.')
 G.speak('rapport');G.dismiss();G.load('transit_depot');near('v030:servo');s=G.s()['player'];draw(s['pos'],s['yaw'],-.18);shot('05_actionneur_etage.png','Un actionneur à rapporter','Objet dans la galerie haute du dépôt. Caméra préparée ; montée et descente sont parcourues séparément avec le contrôleur dans la suite narrative.')
 c('v030StoryAction','servo');G.load('relay_brake');near('v030:plan');c('v030StoryAction','plan');shot('06_cahier_palan.png','Le cahier du levage porté','Note originale posée sur une table dans le Poste du palan 12. La consignation ancienne du palan garde ses propres commandes.')
 G.dismiss();G.load('mooring_station');near('v030:isolate');c('v030StoryAction','isolate');near('v030:frame');c('v030StoryAction','restore');shot('07_devis_restauration.png','Des travaux avant de prendre le châssis','Bilan avant validation. Coût dépendant de Réparation ; aucune guérison, aucun châssis attribué avant la confirmation.')
 G.speak('Confirmer');near('v030:battery');c('v030StoryAction','battery');near('v030:station');c('v030Show');c('v030Dispatch','p30:equip','mistralRig');c('v030Dispatch','p30:used','0');shot('08_pip_coeur.png','Charge installée et six plaques','La batterie d’essai réellement récupérée commence à 65 %. Chaque plaque restaurée commence à 85 %, indépendamment des blessures du personnage.')
 c('v030Dispatch','p30:power');G.dismiss();draw([10,1.65,36.3],math.pi,.03,True);shot('09_armure_portee.png','Le châssis porté en troisième personne','Le vrai personnage porte l’assemblage dans la cour. Pose et caméra préparées ; les déplacements et la consommation sont testés indépendamment. Pas d’animation d’entrée dans une armure physique.')
 c('v030Switch');c('v030Set',{'core':37.625});near('v030:station');c('v030Show');c('v030Dispatch','p30:eject');shot('10_coeur_entame.png','Une charge qui ne se réinitialise pas','État de charge préparé à 37,625 % pour illustrer l’éjection exacte. Elle devient un cœur entamé, pas une nouvelle cellule à 100 %. La conservation est testée numériquement.')
 c('v030Set',{'parts':{'head':35,'torso':80,'leftArm':0,'rightArm':85,'leftLeg':52,'rightLeg':85}});c('v030Dispatch','p30:slot','leftArm');shot('11_plaque_detruite.png','Bras gauche détruit, bras droit encore intact','Pièces endommagées préparées pour la démonstration. Le diagramme représente les plaques, pas les membres blessés du porteur.')
 c('v030Dispatch','p30:repair','leftArm');p.locator('.p30-quote').scroll_into_view_if_needed();shot('12_devis_plaque.png','Réparation d’une seule pièce','Prix réel généré à partir de la pièce choisie, avant confirmation. L’établi, la sécurité, le stock et le devis sont revérifiés au clic.')
 c('v020Seed',{'scrap':30,'weaponParts':15,'circuitry':15,'clay':20,'steelPlate':10});c('v030Dispatch','p30:confirm');p.locator('.p30-suit').scroll_into_view_if_needed();shot('13_plaque_reparee.png','Le bras est réparé, pas le corps entier','La confirmation réelle restaure seulement le bras gauche. Les autres plaques et les blessures du joueur ne sont pas réparées.')
 c('v030Dispatch','p30:mod','ceramic');p.locator('.p30-quote').scroll_into_view_if_needed();shot('14_configuration_atelier.png','Une configuration, pas des bonus empilés','Trois réglages possibles. Le remplacement consomme son coût sans rembourser le précédent ; pas d’XP de fabrication répétable.')
 c('v030Dispatch','p30:confirm');c('v030Dispatch','p30:used','0');c('v030Dispatch','p30:power');G.dismiss();draw([10,1.65,36.3],math.pi,.03,True);shot('15_ecrans_refractaires.png','Les écrans réfractaires sont visibles','Plaques claires sur les épaules de l’assemblage. Le modèle reste procédural ; cette modification a aussi une masse et une résistance au feu dépendant de l’usure.')
 near('v030:trial');draw([21,1.75,37.3],0,-.02);shot('16_portillon_ferme.png','Avant l’essai : le portillon est fermé','Même caméra que la capture suivante. Le volet possède sa collision, et une manivelle permet de finir même sans charge.')
 c('v030Trial');G.speak('Tenir la charge');draw([21,1.75,37.3],0,-.02);shot('17_portillon_ouvert.png','Après l’essai : passage effectif','L’essai assisté a débité 2 % et ouvert le passage. Sa traversée est aussi testée au contrôleur ; il ne s’agit pas d’un montage après coup.')
 near('v030:alba');c('v030Preview','rescue');shot('18_bilan_accord.png','Choisir ce que prépare l’atelier','Bilan de l’une des deux conclusions. Les deux gardent le châssis au joueur ; aucune réécriture des anciens circuits, réserves ou dossiers.')
 G.speak('Confirmer');shot('19_epilogue.png','L’essai à vide','Première des trois scènes textuelles de cette conclusion. Six scènes distinctes sur les deux accords, aucun doublage.')
 for _ in range(3):p.locator('#dialogueChoices button').first.click()
 G.dismiss();near('v030:tape');c('v030Tape');G.dismiss();c('v027Open','radio','tapes');shot('20_bande_alba.png','Pas une seconde peau','Bande originale à trouver physiquement, puis à relire dans RADIO. Cinq segments, pas de fichier audio enregistré.')
 G.dismiss();near('v030:station');c('v030Show');p.set_viewport_size({'width':390,'height':844});p.locator('.p30-slots button[data-arg="head"]').click();shot('21_mobile_pieces.png','Six plaques sur un écran étroit','Fenêtre 390 × 844, pas un iPhone réel. Des boutons natifs permettent la sélection indépendamment du schéma.')
 p.locator('[data-p27="p30:power"]').scroll_into_view_if_needed();shot('22_mobile_charge.png','Commandes de charge accessibles','La page défile jusqu’aux commandes. Les gestes tactiles et la conservation de charge sont testés séparément.')
except Exception:G.fail()
(R/'verification/CAPTURES_V030.json').write_text(json.dumps({'html_sha256':hashlib.sha256(H.encode()).hexdigest(),'images':images,'errors':G.errors,'checks':G.checks,'scope':'Exact runtime, software Chromium. Prepared cameras and selected damaged/equipment states. Existing fictional scenes, zero official cartography. Controller routes tested separately.'},ensure_ascii=False,indent=2))
print('CAPTURES',len(images),'ERRORS',G.errors,flush=True);G.b.close();G.pw.stop()
raise SystemExit(bool(G.errors or G.checks))
