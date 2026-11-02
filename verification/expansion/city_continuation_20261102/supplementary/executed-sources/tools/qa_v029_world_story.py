from qa029_support import Game
import json,math
G=Game('V029_WORLD_STORY');c=G.c;ck=G.check;p=G.p
try:
 G.memory();G.reset();defs=c('v029Defs')
 for id in ['depot','archives','amarres']:
  d=defs[id];G.reset(d['zone'],False);x,z=d['room'];inside=[x,0,z-.65];out=[x,0,z-4]
  stats=c('v020Stats');ck(len(stats['rooms'])==(11 if id=='amarres' else 10),id+' : neuf espaces précédents et un local de service',stats['rooms'])
  ck(c('v020Route',inside) is None or not c('v020Route',inside),id+' : local fermé vraiment inaccessible depuis la scène')
  ck(c('v029ManualExit',id)is False,id+' : poignée de secours non actionnable depuis dehors')
  G.solve(id);before=G.s();alive=c('v021EnemyInfo');G.click('command','standby');ck(not G.st()['terminals'][id]['standby'],id+' : veille seulement après confirmation')
  G.click('confirm','standby');enemy=next(e for e in c('v029Stealth')['enemies']if e['id']==d['robot']);ck(enemy['standby']and enemy['alive'],id+' : un automate vivant en veille')
  others=[e['id']for e in c('v029Stealth')['enemies']if e['standby']];ck(others==[d['robot']],id+' : aucun autre ennemi neutralisé')
  ck(G.s()['flags']['enemyDead']==before['flags']['enemyDead'] and G.s()['inventory']==before['inventory'],id+' : veille sans mort ni attribution de butin')
  G.click('command','door');G.click('confirm','door');G.dismiss();walk=c('v021ActualWalk',inside);ck(walk['ok'],id+' : entrer par le contrôleur de déplacement réel',walk)
  if id=='depot':
   ck(c('v029Contact')and G.st()['quest']['contact'],'Contact mécanique collecté depuis l’intérieur, après marche')
   inv=G.s()['inventory'];ck(c('v029Contact')is False and G.s()['inventory']==inv,'Contact non duplicable');G.dismiss()
  else:
   ck(c('v020Interact','v029:roomnote:'+id)is not False,id+' : note intérieure accessible après parcours');G.dismiss()
  back=c('v021ActualWalk',out);ck(back['ok'],id+' : ressortir sans chargement ni téléportation',back)
  saved=G.s();G.load(d['zone'],False);ck(any(q['id']=='v029:door:'+id and q['disabled']for q in c('v029RoomInfo')),id+' : volet ouvert conservé au retour')
  enemy=next(e for e in c('v029Stealth')['enemies']if e['id']==d['robot']);ck(enemy['standby']and enemy['alive'],id+' : veille conservée après rechargement')
  G.load(d['zone'],False);hp=G.s()['player']['hp'];c('v029AI',.2);enemy=next(e for e in c('v029Stealth')['enemies']if e['id']==d['robot']);ck(not enemy['alerted']and enemy['state']=='standby',id+' : aucun cycle offensif d’un automate en veille')
  # Deliberately prepare player inside a closed room to test failsafe (not a traversal claim).
  G.reset(d['zone']);c('v020SetPlayer',{'pos':[x,1.65,z-.8]});ck(c('v029ManualExit',id)is True,id+' : ouverture mécanique depuis l’intérieur sans mot de passe')
  ck(not G.st()['terminals'][id]['unlocked'],id+' : sortie de secours n’authentifie pas le contrôleur')
  ck(c('v021ActualWalk',out)['ok'],id+' : évacuation réelle après ouverture intérieure')
 # Prior power-cut and scripted-death semantics may not be undone.
 G.reset();G.near('transit_depot:power');c('v021Action','transit_depot','power');G.dismiss();G.solve('depot');G.click('command','standby');G.click('confirm','standby');G.dismiss()
 e=next(e for e in c('v029Stealth')['enemies']if e['id']==defs['depot']['robot']);ck(not e['alive'],'Une coupure historique ayant neutralisé le robot n’est pas annulée par la nouvelle veille')
 # Alternative quest progression by credentials: no G.O.A.T. or Science grind.
 G.reset();G.near('v029:adrien');ck(c('v029Talk'),'Adrien abordé sur place');G.speak('suivre le refus');ck(G.st()['quest']['accepted'],'Acceptation par clic réel dans le dialogue');G.dismiss()
 ck(c('v029Resolve','local')is False,'Conclusion impossible sans journaux et contact')
 G.near('v029:badge:d4');ck(c('v029Credential','d4'),'Fiche D-4 recueillie à la cantine');G.dismiss();G.open('depot');G.click('badge');ck(G.st()['terminals']['depot']['method']=='badge','D-4 accessible sans jouer au piratage')
 G.click('read',1);G.click('main');G.click('command','door');G.click('confirm','door');G.dismiss();x,z=defs['depot']['room'];walk=c('v021ActualWalk',[x,0,z-.65]);ck(walk['ok'],'Contact atteint par trajet réel dans l’alcôve ouverte');ck(c('v029Contact'),'Contact emporté dans le dossier');G.dismiss()
 G.load('traverse_archives');before=G.s();c('v020SetPlayer',{'pos':[10,1.65,-16]});ck(c('v029Credential','a2')is False,'Fiche A-2 interdite à travers son étage')
 c('v020SetPlayer',{'pos':[0,1.65,18]});walk=c('v021ActualWalk',[10,3.2,-15]);ck(walk['ok'] and walk['maxY']>4.7,'Habilitation A-2 atteinte par escaliers existants',walk)
 ck(c('v029Credential','a2'),'Habilitation A-2 lue physiquement');G.dismiss();G.open('archives');G.click('badge');G.click('read',1);ck(G.st()['quest']['proof']['filter'],'Journal A-2 conservé par accès habilité malgré Science basse');G.dismiss()
 G.load();G.near('v029:adrien');c('v029Talk');G.speak('habilitation Q-8');ck(G.st()['credentials']['q8'],'Autorisation Q-8 délivrée seulement avec deux journaux');G.dismiss()
 G.load('mooring_station');G.open('amarres');G.click('badge');G.click('read',1);ck(all(G.st()['quest']['proof'].values())and not G.s()['v023']['goat']['completed'],'Trois preuves sans G.O.A.T., sans points de Science ajoutés');G.dismiss();G.load();G.near('v029:adrien')
 c('v029Options');ck(p.locator('#dialogueChoices button').count()==3,'Deux issues et possibilité de différer')
 c('v029Preview','supervised');before=G.s();G.speak('Revenir');ck(G.s()['inventory']==before['inventory'] and G.st()['quest']['ending']is None,'Prévisualisation réversible sans dépense')
 # Seed only amounts for the insufficient-resources test; completion data came from prior UI actions.
 c('v020Seed',{'scrap':0,'circuitry':0});before=G.s();ck(c('v029Resolve','supervised')is False and G.s()['inventory']==before['inventory'],'Matériaux manquants : pas de paiement partiel')
 before=G.s();c('v029Preview','local');G.speak('Confirmer');after=G.s();ck(G.st()['quest']['ending']=='local'and after['player']['caps']==before['player']['caps']+75,'Issue locale signée une fois : 75 capsules')
 ck(after['inventory'].get('fieldSplint',0)==before['inventory'].get('fieldSplint',0)+2,'Issue locale : deux attelles, pas un bonus fictif')
 texts=[]
 for _ in range(3):texts.append(p.locator('#dialogueLine').inner_text());p.locator('#dialogueChoices button').first.click()
 ck(len(set(texts))==3 and all(len(t)>180 for t in texts),'Trois scènes textuelles distinctes de l’accord local')
 caps=G.s()['player']['caps'];c('v029Epilogue',0);G.dismiss();ck(G.s()['player']['caps']==caps and c('v029Resolve','supervised')is False,'Relecture sans récompense et conclusion non remplaçable')
 for id in ['depot','archives','amarres']:
  G.load(defs[id]['zone']);ck(G.st()['terminals'][id]['door']and G.st()['terminals'][id]['standby'],id+' : accord appliqué lors du rechargement')
 ck(G.s()['v021']==before['v021']and G.s()['v023']['quest']==before['v023']['quest']and G.s()['v028']['quest']==before['v028']['quest'],'Canal six, dossier d’aptitudes et pharmacie non réécrits par cet accord')
 G.reset();c('v028Render',[0,1.65,39],0,0);ck('Les portes ont des oreilles' not in p.locator('#v020QuestHint').inner_text() or not p.locator('#v020QuestHint').is_visible(),'Le suivi de la quête ne reste pas affiché après une nouvelle partie')
 # Second ending, preconditions prepared (not described as full playthrough).
 G.reset();c('v029Set',{'quest':{'accepted':True,'proof':{'route':True,'filter':True,'clause':True},'contact':True}});G.near('v029:adrien');c('v020Seed',{'scrap':4,'circuitry':3});before=G.s();c('v029Preview','supervised');G.speak('Confirmer');after=G.s()
 ck(after['inventory']['scrap']==before['inventory']['scrap']-2 and after['inventory']['circuitry']==before['inventory']['circuitry']-1,'Issue surveillée : deux ferrailles et un circuit exactement')
 ck(after['inventory'].get('traumaKit',0)==before['inventory'].get('traumaKit',0)+1 and after['player']['caps']==before['player']['caps']+75,'Issue surveillée : trousse et capsules effectives')
 texts2=[]
 for _ in range(3):texts2.append(p.locator('#dialogueLine').inner_text());p.locator('#dialogueChoices button').first.click()
 ck(len(set(texts+texts2))==6 and all(len(t)>180 for t in texts2),'Six scènes d’épilogue réellement distinctes entre les deux issues')
 c('save');snap=G.s();G.load('mooring_station');ck(c('v018ImportRaw',json.dumps(snap))is True,'État d’accord sauvegardé puis réimporté')
 ck(G.st()['quest']['ending']=='supervised'and all(G.st()['terminals'][k]['door']for k in ['depot','archives','amarres']),'Décision et portes persistent dans l’import')
 G.load();G.near('v029:tape');ck(c('v029PickupTape')and G.s()['lore']['holotapes']['v029_door'],'Bande trouvée sur place inscrite à la bibliothèque');G.dismiss();c('v027Open','radio','tapes');ck('La main sous la porte' in p.locator('#pipboy').inner_text(),'Bande d’Adrien consultable depuis le lecteur existant');G.dismiss()
 # Existing campaign terminal replay must not rewind quest or award repeated benefits.
 G.reset('aubagne');c('setQuest',{'main':3});G.load('aubagne');G.solve('relay');G.click('command','legacy');G.click('confirm','legacy');ck(G.s()['quest']['main']>=4 and G.st()['terminals']['relay']['legacyDone'],'Ancien relais résolu par nouvelle authentification puis commande explicite')
 G.dismiss();stage=G.s()['quest']['main'];money=G.s()['player']['caps'];G.open('relay');ck(c('v029Command','legacy',True)is False and G.s()['quest']['main']==stage and G.s()['player']['caps']==money,'Revisiter le relais ne recule pas la campagne et ne répète pas sa récompense')
 G.reset('laciotat');c('setQuest',{'main':9});G.load('laciotat');G.solve('ship');G.click('command','legacy');G.click('confirm','legacy');ck(G.s()['flags']['shipBypassed']and G.st()['terminals']['ship']['legacyDone'],'Ancien mandat du chantier : contournement réel du système historique')
 G.dismiss();G.open('ship');reps=G.s()['rep'];ck(c('v029Command','legacy',True)is False and G.s()['rep']==reps,'Pas de réputation répétable sur le mandat réécrit')
except Exception:G.fail()
raise SystemExit(G.output())
