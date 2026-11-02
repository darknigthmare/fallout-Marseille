from qa029_support import Game
import math,json
G=Game('V029_PERCEPTION_MOBILE');c=G.c;ck=G.check;p=G.p

def arena(wall=False,dist=10,yaw=math.pi):
 G.reset();c('v020Fixture',wall,'raider',dist);c('v020EnemyPatch',{'damage':10,'speed':1.5,'range':2,'detect':20,'yaw':yaw,'alerted':False,'attackCooldown':100,'state':'idle','v029Sense':{'awareness':0,'heard':None,'time':0}});c('v028Set',{'lamp':False});c('v020SetPlayer',{'crouched':False});return c('v029Stealth')['enemies'][0]
try:
 G.memory();arena();x=c('v029Observe',.1);ck(not x['acquired'] and 0<x['awareness']<1,'Une fraction de seconde en vue produit du soupçon, pas une attaque instantanée')
 ck(c('v029Stealth')['meter']['label']=='SOUPÇON','HUD de soupçon correspond à la perception réelle')
 for _ in range(15):x=c('v029Observe',.1)
 ck(x['alerted'] and x['awareness']==1 and c('v029Stealth')['meter']['label']=='DANGER','Regard soutenu déclenche réellement alerte et danger')
 arena(yaw=0)
 for _ in range(30):x=c('v029Observe',.1)
 ck(not x['alerted']and x['awareness']==0,'Adversaire de dos à dix mètres ne voit pas à travers son propre dos')
 arena(dist=2,yaw=0)
 for _ in range(10):x=c('v029Observe',.1)
 ck(x['alerted'],'Très proche derrière un adversaire : détection de proximité')
 arena(True)
 for _ in range(30):x=c('v029Observe',.1)
 ck(not x['alerted']and x['awareness']==0,'Mur entre joueur et adversaire : aucune acquisition visuelle')
 arena(dist=15);x=c('v029Observe',.2);ck(x['awareness']>0,'Debout à quinze mètres dans le cône : soupçon')
 c('v020EnemyPatch',{'v029Sense':{'awareness':0,'heard':None,'time':0}});c('v020SetPlayer',{'crouched':True});x=c('v029Observe',1);ck(x['awareness']==0,'Accroupi : portée de détection réduite par la règle existante')
 arena();c('v029Observe',.4);a=c('v029Stealth')['enemies'][0]['sense']['awareness'];c('v020EnemyPatch',{'yaw':0});x=c('v029Observe',.5);ck(x['awareness']<a,'Soupçon décroît quand le contact visuel est perdu')
 # Same behavior goes through real updateEnemies, not only isolated perception helper.
 arena();c('v029AI',.1);ck(not c('v029Stealth')['enemies'][0]['alerted'],'Boucle réelle des ennemis ne court-circuite pas le délai de regard')
 for _ in range(22):c('v029AI',.1)
 ck(c('v029Stealth')['enemies'][0]['alerted'],'Boucle réelle termine l’acquisition après observation prolongée')
 arena(True);before=c('v029Stealth')['enemies'][0];heard=c('v029Noise',[5,0,-2],21,'test carillon')
 after=c('v029Stealth')['enemies'][0];ck(heard==1 and after['sense']['heard']==[5,0,-2]and not after['alerted'],'Un son transmet une position à inspecter, pas la position du joueur')
 ck(after['pos']==before['pos'] and c('v029Stealth')['meter']['label']=='PRUDENCE','Aucune téléportation au bruit ; état de recherche affiché')
 for _ in range(10):c('v029AI',.1)
 new=c('v029Stealth')['enemies'][0];ck(0<math.dist(new['pos'],after['pos'])<2,'Enquête sonore : déplacement limité par la vitesse',{'before':after['pos'],'after':new['pos']})
 ck(not new['alerted'],'Le son derrière le mur ne donne pas une vision traversante du joueur')
 for _ in range(75):c('v029AI',.1)
 ck(c('v029Stealth')['enemies'][0]['sense']['heard']is None,'Fin du délai de recherche : point sonore abandonné')
 arena(True);ck(c('v029Noise',[0,0,8],10,'son atténué')==0,'Une cloison réduit la portée auditive au lieu de propager uniformément')
 ck(c('v029Noise',[0,0,8],30,'son fort')==1,'Un son assez fort reste audible derrière le même obstacle')
 ck(c('v029Noise',[0,0,8],-2,'invalide')==0 and c('v029Noise',[None,0,0],20,'invalide')==0,'Rayons et coordonnées invalides ignorés')
 arena();c('v020EnemyPatch',{'alerted':True});ck(c('v029Noise',[5,0,0],30,'leurre')==0 and c('v029Stealth')['enemies'][0]['alerted'],'Un ennemi déjà en combat ne vous oublie pas avec un leurre')
 arena();c('v020EnemyPatch',{'v029Standby':True});ck(c('v029Noise',[0,0,0],30,'leurre')==0,'Un automate en veille ne part pas enquêter')
 c('v029AI',1);ck(not c('v029Stealth')['enemies'][0]['alerted'],'Veille ne déclenche ni acquisition ni attaque')
 arena(True);c('v029Noise',[5,0,-2],20,'test');before=c('v029Stealth')['enemies'][0];c('v027Open','status','health');c('v029AI',5);after=c('v029Stealth')['enemies'][0]
 ck(after['pos']==before['pos']and after['sense']==before['sense'],'Menu Pip-Boy : les investigations sont suspendues')
 # Lamp rule from v028 remains an explicit detection tradeoff.
 G.dismiss();arena(dist=8,yaw=0);c('v028Set',{'lamp':True});c('v029AI',.05);ck(c('v029Stealth')['enemies'][0]['alerted'],'Lampe à huit mètres visible : règle de révélation précédente conservée')
 c('v028Set',{'lamp':False});c('v029AI',.05);ck(c('v029Stealth')['enemies'][0]['alerted'],'Éteindre la lampe n’efface pas la dernière alerte')
 # Physical footsteps via real keys and the real player update.
 arena(dist=9,yaw=0);p.locator('#gameCanvas').focus();p.keyboard.down('Shift');p.keyboard.down('w')
 for _ in range(4):c('v029Advance',.08)
 p.keyboard.up('w');p.keyboard.up('Shift');info=c('v029Stealth');ck(info['lastNoise']['kind']=='pas' and info['lastNoise']['heard']>=1,'Course au clavier : bruit réellement propagé',info['lastNoise'])
 arena(dist=9,yaw=0);c('v020SetPlayer',{'crouched':True});c('v020EnemyPatch',{'damage':10});p.locator('#gameCanvas').focus();p.keyboard.down('w')
 for _ in range(4):c('v029Advance',.08)
 p.keyboard.up('w');ck(c('v029Stealth')['enemies'][0]['sense']['heard']is None,'Déplacement accroupi : pas de bruit de pas artificiel')
 # Remote chime session remains local; cooldown does not run in menus.
 G.reset();G.solve('depot');G.click('command','signal');elapsed=G.st()['elapsed'];signal=G.st()['terminals']['depot']['lastSignal'];ck(signal==elapsed,'Carillon activé réellement depuis le contrôleur')
 ck(c('v029Command','signal')is False,'Carillon non répétable avant douze secondes actives')
 c('v029Advance',60);ck(c('v029Command','signal')is False,'Attendre dans le terminal ne réarme pas le carillon')
 G.dismiss()
 for _ in range(125):c('v029Advance',.1)
 G.open('depot');ck(c('v029Command','signal')is True,'Délai de jeu actif écoulé : nouvel essai possible')
 # Compact interface with actual touch input in a separate browser context.
 G.dismiss();G.reset();G.open('depot');p.set_viewport_size({'width':390,'height':844});G.click('hack')
 bounds=p.locator('#terminal29').bounding_box();ck(bounds['x']>=0 and bounds['x']+bounds['width']<=391,'Boîtier ne déborde pas la largeur 390 px',bounds)
 ck(p.locator('#terminal29').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'),'Aucun débordement horizontal du terminal')
 for selector in ['[data-t29="word"]','[data-t29="bracket"]']:
  bb=p.locator('#terminal29 '+selector).first.bounding_box();ck(bb['height']>=40,'Cible tactile suffisamment haute : '+selector,bb)
 p.locator('#terminal29').evaluate('(e)=>e.scrollTop=e.scrollHeight');ck(p.locator('[data-t29="main"]').count()==1,'Menu et journal restent accessibles par défilement')
 p.keyboard.press('Escape');ck(c('getMode')=='PLAYING','Échap fonctionne après défilement mobile')
except Exception:G.fail()
err=G.output()
T=Game('V029_TOUCH',{'width':390,'height':844},True)
try:
 T.memory();T.reset();T.open('depot');T.p.locator('[data-t29="hack"]').tap();deck=T.c('v029Deck','depot');wrong=next(i for i in range(12)if i!=deck['answer']);T.p.locator('[data-t29="word"][data-arg="'+str(wrong)+'"]').tap();T.check(T.st()['terminals']['depot']['attempts']==3,'Tap tactile sur un candidat : véritable tentative')
 T.p.locator('[data-t29="bracket"][data-arg="1"]').tap();T.check(T.st()['terminals']['depot']['attempts']==4,'Tap tactile sur les crochets : aide réellement exécutée')
 T.p.locator('[data-t29="close"]').tap();T.check(T.c('getMode')=='PLAYING','Tap QUITTER : retour au personnage')
except Exception:T.fail()
raise SystemExit(T.output()or err)
