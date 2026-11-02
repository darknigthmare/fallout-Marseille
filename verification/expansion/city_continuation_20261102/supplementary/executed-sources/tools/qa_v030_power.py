"""Powered armour mechanics; explicit synthetic arena where needed. Real UI
clicks and exact build; no official geography or GPU certification."""
from qa029_support import Game
import json, math
G=Game('V030_POWER'); c=G.c; ck=G.check; p=G.p
SLOTS=['head','torso','leftArm','rightArm','leftLeg','rightLeg']
def st():return c('v030State')
def reset(zone='mooring_station'):
 G.reset(zone);c('v028Set',{'limbs':{k:100 for k in SLOTS}})
def rig(parts=None,core=None,active=False):
 c('v030Set',{'rig':'mistralRig','parts':parts or {k:100 for k in SLOTS},'core':core,'active':active})
def click(a,arg=None):
 s='[data-p27="p30:'+a+'"]'+('' if arg is None else '[data-arg="'+str(arg)+'"]');p.locator(s).filter(visible=True).last.click()
try:
 c('v020Load','mooring_station');ck(c('save')is False,'Stockage natif opaque refusé avant adaptateur');G.memory();ck(c('save')is True,'Adaptateur mémoire explicite permet les scénarios de conservation');reset()
 ck(c('v030Info')['slots']==6 and c('v030Info')['mods']==3 and c('v030Info')['suits']>=10,'Six plaques, trois modifications et familles assistées existantes reconnues')
 ck(p.title().endswith('Relève complète'),'Titre courant exact');keys=c('v018Keys');ck(keys['campaign'].endswith('v035')and keys['sandbox'].endswith('v035'),'Nouvelles clés de campagne et exploration distinctes')
 old=G.s();old.pop('v030',None);old['unknown_save_field']={'keep':1};old['equipment']['ownedArmors']=['vaultSuit','t51Armor'];old['equipment']['armorCondition']['t51Armor']=37
 mig=c('v018Migrate',old);ck(mig['v030']['rigs']['t51Armor']['parts']=={k:37 for k in SLOTS},'Ancienne T-51 à 37 % : six plaques à 37 %, pas de réparation gratuite')
 ck(not mig['v030']['active']and mig['v030']['core']is None and not mig['v030']['spares'],'Migration sans moteur activé ni cœur offert');ck(mig['unknown_save_field']=={'keep':1} and mig['v029']==old['v029'],'Anciennes données et champs inconnus conservés')
 old['v030']={'core':101,'spares':[-1,0,45,'bad',None,200]*20,'active':True,'rigs':{'t51Armor':{'parts':{'head':-5,'torso':300,'leftArm':'bad'},'mod':'inventé'},'inventé':{'parts':{}}},'quest':{'ending':'inventée'},'history':['x'*600]*60};old['player']['armorId']='t51Armor';mig=c('v018Migrate',old)
 ck(mig['v030']['core']==100 and len(mig['v030']['spares'])==40 and all(0<x<=100 for x in mig['v030']['spares']),'Charges invalides rejetées ou bornées et quarante cœurs entamés maximum')
 ck(mig['v030']['rigs']['t51Armor']['parts']['head']==0 and mig['v030']['rigs']['t51Armor']['parts']['torso']==100,'Pièces importées bornées à 0–100')
 ck(mig['v030']['rigs']['t51Armor']['mod']is None and 'inventé'not in mig['v030']['rigs'] and mig['v030']['quest']['ending']is None,'Modèle, réglage et issue inconnus non inventés');ck(len(mig['v030']['history'])==40 and len(mig['v030']['history'][0])==240,'Historique borné sans grossissement de sauvegarde')
 # Charge conservation, actual buttons.
 reset();rig();c('v020Seed',{'fusionCore':2});c('v030Show');before=G.s();click('insert','new');ck(st()['core']==100 and G.s()['ammo']['fusionCore']==1,'Insérer retire exactement un cœur neuf pour une charge de 100 %')
 ck(not c('v030Insert','new')and G.s()['ammo']['fusionCore']==1,'Un emplacement occupé ne consomme pas de second cœur');click('power');ck(st()['active'],'Moteurs activés depuis le Pip-Boy')
 ck(not c('v030Eject')and not c('v030Insert','new'),'Manipulations refusées pendant l’assistance');before=st()['core'];c('v020Tick',3,True);ck(st()['core']==before,'Aucune charge perdue en menus')
 click('power');click('eject');ck(st()['core']is None and st()['spares']==[100]and G.s()['ammo']['fusionCore']==1,'Éjection en réserve entamée, sans recréer de cœur neuf');click('used','0');ck(st()['core']==100 and not st()['spares'],'Insertion exacte du cœur rangé')
 click('power');G.dismiss();c('v030Spend',28.375);ck(abs(st()['core']-71.625)<1e-9,'Charge réellement débitée');c('v030Switch');c('v030Eject');c('v030Insert','used',0);ck(abs(st()['core']-71.625)<1e-9,'Retirer puis réinsérer conserve les fractions de charge')
 ck(not c('v030Insert','used',-1)and abs(st()['core']-71.625)<1e-9,'Index négatif et emplacement occupé non exploitables')
 c('v030Set',{'spares':[3]*40});ck(c('v030Eject')is False and abs(st()['core']-71.625)<1e-9,'Réserve pleine : le cœur reste installé')
 # Drain only real movement. Fixture is explicitly synthetic.
 reset();c('v020Fixture',False);rig(core=10,active=True);cap=c('v030Health')['capacity'];before=st()['core'];moved=c('v030Move',1,0);ck(abs(moved-.92)<1e-7,'Marche assistée intacte : 92 % du déplacement de référence');ck(abs(before-st()['core']-moved*.014)<1e-9,'Charge proportionnelle au déplacement réellement parcouru')
 c('v030Switch');cap2=c('v030Health')['capacity'];before=st()['core'];moved=c('v030Move',1,0);ck(abs(moved-.58)<1e-7 and st()['core']==before,'Coque hors tension : marche lourde sans charge débitée');ck(cap-cap2==60,'Assistance apporte 60 de portage, retirés hors tension')
 c('v030Set',{'core':10,'active':True,'mod':'servos'});cap3=c('v030Health')['capacity'];before=st()['core'];moved=c('v030Move',1,0);ck(abs(moved-.98)<1e-7 and cap3-cap2==85,'Servos actifs : 98 % de marche et +85 de capacité totale');ck(abs(before-st()['core']-moved*.014*1.25)<1e-9,'Servos paient leur dépense accrue')
 c('v020AddWall');c('v020SetPlayer',{'pos':[0,1.65,3.6]});before=st()['core'];moved=c('v030Move',0,-.3);ck(moved<.0001 and st()['core']==before,'Buter contre une collision ne consomme pas de mouvement',{'moved':moved,'core':st()['core']})
 c('v030Set',{'core':.001,'active':True});c('v030Spend',5);ck(st()['core']is None and not st()['active'],'Cœur épuisé : arrêt automatique, pas de valeur négative')
 c('v030Show');c('v030Dispatch','p30:equip','vaultSuit');ck(G.s()['player']['armorId']=='vaultSuit','Châssis vidé retirable : aucune partie immobilisée')
 # Damage & body not confused. No drain for invalid action, single valid action.
 reset();c('v020Fixture',False);rig(core=10,active=True);hp=G.s()['player']['hp'];c('v030Hurt',30,'leftArm');health=c('v030Health');ck(health['hp']<hp and health['slots']['leftArm']<100,'Impact traverse le calcul de protection puis use le bras gauche');ck(all(health['slots'][k]==100 for k in SLOTS if k!='leftArm'),'Cinq plaques non frappées conservent leur intégrité');ck(G.s()['v028']['limbs']['leftArm']<100,'Le porteur peut rester blessé sous la plaque')
 c('v030Set',{'parts':{'torso':.1},'active':True});c('v030Hurt',30,'torso');ck(st()['rigs']['mistralRig']['parts']['torso']==0 and not st()['active'],'Circuit du plastron cassé coupe les moteurs')
 c('v030Set',{'parts':{k:100 for k in SLOTS},'core':10,'active':True});melee=c('v020Damage','machete');ball=c('v020Damage','pistol10');c('v030Switch');ck(abs(melee/c('v020Damage','machete')-1.2)<1e-8,'Force assistée augmente réellement les dégâts de mêlée de 20 %');ck(ball==c('v020Damage','pistol10'),'Armure ne multiplie pas les dégâts de balle')
 c('v030Switch');before=st()['core'];c('v020Vats');c('v020VatsAdd');c('v020AddWall');c('v020VatsExecute');c('v020Tick',2);ck(st()['core']==before,'Action V.A.T.S. masquée avant émission : aucune charge dépensée')
 G.dismiss();c('v020Fixture',False);c('v020Equip','pistol10');c('v020Tick',1);c('v020SetPlayer',{'ammoClip':8,'ap':150,'maxAp':150});rig(core=10,active=True);c('v020Vats');c('v020VatsAdd');c('v020VatsExecute');c('v020Tick',2);ck(abs(st()['core']-9.65)<1e-7,'Une action V.A.T.S. émise dépense 0,35 % une seule fois',st()['core'])
 G.dismiss();c('v020Fixture',False);rig(core=10,active=True);c('v028Set',{'limbs':{k:100 for k in SLOTS}});jump=c('v028Jump');ck(jump['jumpVelocity']>0 and st()['core']==9.75,'Saut réussi : débit de 0,25 %');before=st()['core'];c('v028Jump');ck(st()['core']==before,'Saut déjà en l’air : pas de second débit')
 # Workshop repair isolation and transactions.
 reset();rig({'head':20,'torso':40,'leftArm':0,'rightArm':70,'leftLeg':40,'rightLeg':80},core=20);c('v028Set',{'limbs':{'leftArm':15}});c('v020SetPlayer',{'hp':60});G.near('v030:station');c('v020Seed',{'scrap':30,'weaponParts':15,'circuitry':15,'cloth':20,'chemicals':20,'clay':20,'steelPlate':20});c('v030Show')
 ck(c('v030NearService'),'Nouvel établi vraiment à portée');click('slot','leftArm');before=G.s();click('repair','leftArm');ck(G.s()['inventory']==before['inventory'],'Devis de plaque sans prélèvement');click('confirm');after=G.s();ck(after['v030']['rigs']['mistralRig']['parts']['leftArm']==100 and after['v030']['rigs']['mistralRig']['parts']['rightArm']==70,'Réparer gauche ne répare pas droite');ck(after['player']['hp']==60 and after['v028']['limbs']['leftArm']==15,'Réparer une plaque ne soigne ni PV ni traumatisme');ck(after['inventory']['scrap']==before['inventory']['scrap']-5 and after['inventory']['weaponParts']==before['inventory']['weaponParts']-3,'Coût exact pour une plaque détruite');ck(after['player']['xp']==before['player']['xp'],'Aucun XP de réparation répétable')
 before=G.s()['inventory'];ck(not c('v030Quote','repair','leftArm')and G.s()['inventory']==before,'Plaque intacte : aucun service superflu')
 c('v030Quote','repair','head');c('v030Set',{'parts':{'head':15}});before=G.s()['inventory'];ck(not c('v030Quote','repair','head',True)and before==G.s()['inventory'],'Dommage modifié invalide le devis')
 c('v030Quote','repair','head');p.keyboard.press('Tab');c('v030Show');ck(not c('v030Quote','repair','head',True),'Ranger l’appareil invalide le devis')
 c('v020Seed',{'weaponParts':0});c('v030Quote','repair','head');before=G.s()['inventory'];ck(not c('v030Quote','repair','head',True)and G.s()['inventory']==before,'Ressources insuffisantes : pas de paiement partiel')
 c('v020Seed',{'weaponParts':15});c('v030Quote','mod','servos');before=G.s();click('confirm');after=G.s();ck(st()['rigs']['mistralRig']['mod']=='servos'and after['inventory']['circuitry']==before['inventory']['circuitry']-3,'Modification installée depuis le devis, ressources exactes');before=after['inventory'];ck(not c('v030Quote','mod','servos')and G.s()['inventory']==before,'Modification identique ne se facture pas deux fois')
 c('v030Quote','mod','ceramic');click('confirm');ck(st()['rigs']['mistralRig']['mod']=='ceramic','Une nouvelle configuration remplace la précédente, sans empilement');c('v030Switch');ck(not c('v030Quote','repair','head'),'Moteurs actifs : atelier refuse les travaux')
 G.dismiss();c('v030Show');c('v030Dispatch','p30:equip','vaultSuit');ck(G.s()['player']['armorId']=='mistralRig','Tenue active ne se retire pas pendant l’assistance');c('v030Switch');c('v030Dispatch','p30:equip','vaultSuit');ck(G.s()['player']['armorId']=='vaultSuit','Moteurs coupés : changement de tenue autorisé')
 # Persistence with the real import/export path on a valid scene.
 c('v030Set',{'rig':'mistralRig','core':31.275,'spares':[9.25,43.125],'parts':{'head':12,'leftLeg':24},'active':True});snap=json.loads(c('v030Export'));G.load('transit_depot');ck(c('v018ImportRaw',json.dumps(snap))is True,'Sauvegarde de châssis acceptée à l’import');ck(abs(st()['core']-31.275)<1e-8 and st()['spares']==[9.25,43.125],'Charges exactes conservées dans l’export/import');ck(st()['rigs']['mistralRig']['parts']['head']==12 and st()['rigs']['mistralRig']['parts']['leftLeg']==24,'Pièces individuelles conservées')
 old=json.loads(json.dumps(snap));old.pop('v030');old['version']='0.29.0';p.evaluate('(x)=>localStorage.setItem("fallout_mistral_sandbox_v029",x)',json.dumps(old));p.evaluate('localStorage.removeItem("fallout_mistral_sandbox_v030")');ck(c('v030Resume'),'Reprise de l’exploration v029');ck(p.evaluate('localStorage.getItem("fallout_mistral_sandbox_v029")')==json.dumps(old),'Sauvegarde v029 non écrasée par la reprise')
 # Geometry tests for original procedural rig, not source IP models.
 reset();rig();whole=c('v030RigDraw');c('v030Set',{'parts':{'leftArm':0}});broken=c('v030RigDraw');ck(len(broken)<len(whole),'Plaque détruite retire ses éléments visuels et garde la structure')
 ck(all(all(isinstance(x,(int,float))and math.isfinite(x)for x in d['pos']+d['scale']+d['color'])for d in whole+broken),'Maillages d’armure : positions, dimensions et couleurs finies')
 # Mobile real buttons, not only dispatched functions.
 p.set_viewport_size({'width':390,'height':844});G.near('v030:station');c('v030Show');click('slot','rightArm');ck(p.locator('.p30-slots button[data-arg="rightArm"]').get_attribute('aria-pressed')=='true','Sélection du bras droit au clic en fenêtre mobile')
 ck(p.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Pip-Boy mobile sans débordement horizontal de page');ck(c('getMode')=='PIP','La sélection ne ferme pas le Pip-Boy')
except Exception:G.fail()
G.output()
