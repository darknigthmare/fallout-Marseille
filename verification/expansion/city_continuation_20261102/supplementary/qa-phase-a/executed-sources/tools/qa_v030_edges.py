from qa029_support import Game
import json, math
G=Game('V030_EDGES');c=G.c;ck=G.check;p=G.p
parts={'head':20,'torso':45,'leftArm':12,'rightArm':87,'leftLeg':61,'rightLeg':39}
def st():return c('v030State')
def equip(id):
 G.dismiss();c('v030Show');c('v030Dispatch','p30:equip',id);G.dismiss()
try:
 G.memory();G.reset('aubagne');c('v020Seed',{'caps':50000});c('v030Set',{'rig':'mistralRig','parts':parts,'mod':'ceramic','core':43.75,'spares':[22.25],'active':False});equip('vaultSuit')
 c('v026Trade','aubagne');ck(not c('v026Sell','mistralRig'),'Marchand sans budget suffisant refuse le châssis sans le prendre')
 for _ in range(30):c('v026Buy','ammo10')
 before=G.s();ck(c('v026Sell','mistralRig'),'Châssis usé vendu depuis le vrai système de comptoir');vendor=st()['vendorRigs']['aubagne']['mistralRig'][0];ck(vendor['parts']==parts and vendor['mod']=='ceramic','Six plaques et modification préservées dans le stock marchand')
 ck(st()['core']==43.75 and st()['spares']==[22.25]and G.s()['ammo'].get('fusionCore',0)==before['ammo'].get('fusionCore',0),'Vente n’emporte ni ne recharge le cœur conservé par le porteur')
 ck('mistralRig'not in st()['rigs'] and 'mistralRig'not in G.s()['equipment']['ownedArmors'],'Châssis vendu retiré du sac et de ses métadonnées personnelles')
 raw=G.s();mig=c('v018Migrate',raw);ck(mig['v030']['vendorRigs']['aubagne']['mistralRig'][0]['parts']==parts,'L’état marchand survit à la migration')
 ck(c('v026Buy','mistralRig'),'Rachat possible du châssis vendu');ck(st()['rigs']['mistralRig']['parts']==parts and st()['rigs']['mistralRig']['mod']=='ceramic','Rachat sans remise à neuf et configuration intacte')
 ck(st()['core']==43.75 and st()['spares']==[22.25],'Rachat ne recrée pas de batterie');c('v026CloseTrade')
 # Two used copies at merchant; controlled addition of second specimen for test.
 G.load('aubagne');c('v026Trade','aubagne');ck(c('v026Sell','mistralRig'),'Nouvelle vente du même châssis hors tension');c('v026Give','mistralRig',1,{'condition':58});c('v030Set',{'rig':'mistralRig','parts':{k:58 for k in parts},'mod':'seal'});c('v026CloseTrade');equip('vaultSuit');c('v026Trade','aubagne');ck(c('v026Sell','mistralRig'),'Second exemplaire synthétique usé enregistré au comptoir')
 ck(len(st()['vendorRigs']['aubagne']['mistralRig'])==2,'Deux fiches de six pièces conservées, pas une moyenne écrasée');ck(c('v026Buy','mistralRig'),'Rachat du dernier exemplaire vendu');ck(st()['rigs']['mistralRig']['parts']=={k:58 for k in parts} and st()['rigs']['mistralRig']['mod']=='seal','Dernier exemplaire retrouve ses six états et joints');ck(st()['vendorRigs']['aubagne']['mistralRig'][0]['parts']==parts,'Le stock restant conserve l’ancien exemplaire');c('v026CloseTrade')
 # Mod deltas pass through live armour data; script adds no perma stats.
 G.reset();c('v030Set',{'rig':'mistralRig','parts':{k:100 for k in parts},'mod':'servos','core':20,'active':True});c('v030Show');before=st()['core'];c('v020Tick',20,True);ck(st()['core']==before,'Longue consultation en Pip-Boy sans décharge ni marche')
 G.dismiss();c('v020Fixture',False);c('v030Set',{'rig':'mistralRig','core':20,'active':True});p.keyboard.down('Shift');c('v030Move',1,0);p.keyboard.up('Shift');m=st()['travelDistance'];ck(abs(20-st()['core']-m*.014*1.25*1.55)<1e-7,'Course paie le multiplicateur prévu en plus des servos')
 # Old global adjustments (including companion maintenance) must not flatten six distinct plates.
 c('v030Set',{'parts':{'head':25,'torso':100,'leftArm':100,'rightArm':100,'leftLeg':100,'rightLeg':100}});avg=c('v030Health')['condition'];c('v026Condition','mistralRig',avg+2);ck(abs(st()['rigs']['mistralRig']['parts']['head']-27)<1e-8 and st()['rigs']['mistralRig']['parts']['torso']==100,'Ancien entretien global ajoute un delta borné, sans niveler ni réparer toutes les plaques')
 # Declared danger refusal and depletion guard. No fixture confused with actual location.
 c('v030Switch');c('v020EnemyPatch',{'alive':True,'alerted':True,'health':100,'damage':5});before=G.s();ck(not c('v030Eject')and not c('v030Insert','new')and st()['core']==before['v030']['core'],'Charge non manipulable à côté d’une menace engagée')
 c('v030Set',{'active':True});q=st()['core'];ck(c('v030Spend',-1)==0 and st()['core']==q,'Débit négatif ne recharge pas le cœur')
 # Equip from the historical salvage bag while active must also be protected.
 c('v030Set',{'active':True});c('v026Open');before=G.s()['player']['armorId'];c('v026Equip','vaultSuit');ck(G.s()['player']['armorId']==before,'Changement de tenue par ancien sac interdit lorsque moteurs actifs');G.dismiss()
 # Repair quote is invalidated by actual JSON import.
 G.reset();c('v030Set',{'rig':'mistralRig','parts':parts});G.near('v030:station');c('v030Show');c('v030Quote','repair','head');raw=json.loads(c('v030Export'));ck(c('v018ImportRaw',json.dumps(raw))is True,'Import de l’état d’entretien valide');G.near('v030:station');c('v030Show');inv=G.s()['inventory'];ck(not c('v030Quote','repair','head',True)and inv==G.s()['inventory'],'Le devis antérieur à un import est annulé')
 # Body contrast, original assembly and keyboard action.
 G.dismiss();p.keyboard.press('u');ck(c('getMode')=='PIP'and p.locator('.p30-slots button').count()==6,'U ouvre réellement la rubrique des six pièces');p.locator('.p30-slots button[data-arg="leftLeg"]').click();style=p.locator('.p30-slots button.active').evaluate('(e)=>({b:getComputedStyle(e).backgroundColor,c:getComputedStyle(e).color})');ck(style['b']!=style['c'],'Pièce choisie contrastée hors simple couleur de survol')
 c('v030Set',{'core':22.125,'spares':[12.875],'active':False});c('save');saved=json.loads(p.evaluate('(k)=>localStorage.getItem(k)',c('v018SaveKey')));ck(saved['v030']['core']==22.125 and saved['v030']['spares']==[12.875],'Données de charge réellement écrites au stockage de test')
except Exception:G.fail()
G.output()
