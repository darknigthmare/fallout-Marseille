from qa029_support import Game
import json
G=Game('V030_STORY');c=G.c;ck=G.check;p=G.p
p.on('dialog',lambda d:d.accept())
def st():return c('v030State')
def actual(dest,label):
 out=c('v021ActualWalk',dest);ck(out['ok'],label,out);return out
try:
 G.memory();c('v030Start');c('v021MuteEnemies');c('v022Time',10)
 ck(G.s()['player']['zone']=='mooring_station' and 'mistralRig'not in G.s()['equipment']['ownedArmors'],'Départ au poste sans châssis gratuit')
 ck(st()['core']is None and not st()['spares'] and G.s()['ammo'].get('fusionCore',0)==0,'Aucun cœur plein ou entamé distribué au départ')
 ck(len(c('v020Stats')['rooms'])==11,'Dix espaces conservés et baie d’assistance ajoutée')
 ck(not c('v030StoryAction','servo')and not c('v030Resolve','rescue'),'Ni prélèvement distant ni conclusion prématurée')
 actual([5.2,0,36.5],'Alba atteinte par déplacement au contrôleur');c('v030Talk');G.speak('rapport');ck(st()['quest']['accepted'],'Acceptation par réplique cliquée');G.dismiss()
 G.load('transit_depot');c('v020SetPlayer',{'pos':[9.5,1.65,-18.5]});ck(not c('v030StoryAction','servo'),'Actionneur à l’étage non récupérable à travers le plancher')
 c('v020SetPlayer',{'pos':[0,1.65,18]});walk=actual([9.5,3.2,-17],'Escaliers réellement gravis jusqu’à l’actionneur');ck(walk.get('maxY',0)>4.7,'Le porteur atteint le vrai niveau haut');ck(c('v030StoryAction','servo'),'Actionneur pris physiquement après la montée');ck(not c('v030StoryAction','servo'),'Actionneur unique non duplicable')
 actual([0,0,18],'Retour au niveau bas par les escaliers');G.load('relay_brake');actual([-6,0,9.7],'Cahier du palan atteint au contrôleur');ck(c('v030StoryAction','plan'),'Plan lu au poste existant');G.dismiss()
 G.load('mooring_station');before=G.s();actual([10,0,34.2],'Châssis approché sans traverser son volume');ck(not c('v030StoryAction','restore'),'Pas de réparation avant consignation')
 actual([14,0,33.6],'Sectionneur rejoint à pied');before=G.s();ck(c('v030StoryAction','isolate'),'Baie isolée physiquement');ck(G.s()['v021']==before['v021'] and G.s()['v029']==before['v029'],'Consignation distincte du canal six et des contrôleurs existants')
 actual([10,0,34.2],'Retour au châssis pour devis');c('v020Seed',{'scrap':0,'circuitry':0});c('v030StoryAction','restore');inv=G.s()['inventory'];G.speak('Confirmer');ck(not st()['quest']['restored'] and G.s()['inventory']==inv,'Travaux sans matériaux : refus sans débit partiel');G.dismiss()
 c('v020Seed',{'scrap':10,'circuitry':5});c('v030StoryAction','restore');before=G.s();G.speak('Pas encore');ck(not st()['quest']['restored'] and G.s()['inventory']==before['inventory'],'Devis réversible');G.dismiss();c('v030StoryAction','restore');before=G.s();G.speak('Confirmer');after=G.s()
 ck(st()['quest']['restored']and 'mistralRig'in after['equipment']['ownedArmors'],'Attribution réelle du M-45');ck(all(n==85 for n in st()['rigs']['mistralRig']['parts'].values()),'Six plaques à 85 % et pas neuves')
 ck(after['player']['hp']==before['player']['hp']and after['v028']['limbs']==before['v028']['limbs'],'Travaux ne soignent pas le personnage');before=after['inventory'];ck(not c('v030StoryAction','restore')and G.s()['inventory']==before,'Aucune seconde attribution ni consommation')
 ck(next(x for x in c('v030Colliders')if x['id']=='v030:parked-frame')['disabled'],'Le châssis réclamé libère son emplacement')
 actual([15.7,0,32.65],'Casier du cœur approché au contrôleur');ck(c('v030StoryAction','battery')and st()['spares']==[65],'Cœur d’essai effectivement récupéré à 65 %');ck(not c('v030StoryAction','battery')and st()['spares']==[65],'Pas de cœur infini')
 saved=G.s();actual([21,0,35],'Portillon atteint à pied');before=G.s();ck(c('v030Trial'),'Ouverture du choix moteur/manivelle');ck(p.locator('#dialogueChoices button').first.get_attribute('aria-disabled')=='true','Voie motorisée affichée indisponible sans assistance');G.speak('manivelle');ck(st()['quest']['trial']=='manual' and st()['spares']==[65]and st()['core']is None,'Manivelle valide l’essai sans exiger ni consommer de cœur')
 ck(next(x for x in c('v030Colliders')if x['id']=='v030:gate')['disabled'],'Le portillon est physiquement ouvert');actual([21,0,30.8],'Passer au travers du portillon ouvert avec le contrôleur');actual([5.2,0,36.5],'Rejoindre Alba après essai manuel')
 c('v030Talk');G.speak('usage');c('v030Preview','rescue');before=G.s();G.speak('Revenir');ck(st()['quest']['ending']is None and G.s()['inventory']==before['inventory'],'Prévisualisation d’accord réversible');c('v030Preview','rescue');before=G.s();G.speak('Confirmer');after=G.s()
 ck(st()['quest']['ending']=='rescue'and after['player']['caps']==before['player']['caps']+70,'Conclusion secours validée une fois et capsules réelles');ck(after['inventory'].get('traumaKit',0)==before['inventory'].get('traumaKit',0)+1 and after['inventory'].get('fieldSplint',0)==before['inventory'].get('fieldSplint',0)+2,'Une trousse et deux attelles attribuées')
 texts=[]
 for _ in range(3):texts.append(p.locator('#dialogueLine').inner_text());p.locator('#dialogueChoices button').first.click()
 ck(len(set(texts))==3 and min(map(len,texts))>180,'Trois scènes d’épilogue secours originales')
 caps=G.s()['player']['caps'];c('v030Epilogue',0);G.dismiss();ck(G.s()['player']['caps']==caps and not c('v030Resolve','independent'),'Relecture sans récompense et issue non remplaçable')
 ck(after['v021']==before['v021']and after['v028']['quest']==before['v028']['quest']and after['v029']==before['v029'],'Aucun accord antérieur ni circuit voisin réécrit')
 snapshot=G.s();G.load('mooring_station');ck(next(x for x in c('v030Colliders')if x['id']=='v030:gate')['disabled'],'Portillon reste ouvert au retour');ck(st()['quest']['ending']=='rescue','Accord persisté après rechargement du lieu')
 # Replay from a real reached checkpoint for motorised branch and other ending.
 ck(c('v018ImportRaw',json.dumps(saved)),'Reprise du point de contrôle avant essai');G.dismiss();G.load('mooring_station');G.near('v030:station');c('v030Show');c('v030Dispatch','p30:equip','mistralRig');c('v030Dispatch','p30:used','0');c('v030Dispatch','p30:power');G.dismiss();actual([21,0,35],'Armure portée : trajet réel jusqu’au portillon');before=st()['core'];c('v030Trial');G.speak('Tenir la charge');ck(st()['quest']['trial']=='powered'and abs(before-st()['core']-2)<1e-8,'Essai motorisé : exactement 2 % en plus du déplacement')
 actual([5.2,0,36.5],'Retour vers Alba avec assistance active');c('v030Talk');G.speak('usage');c('v030Preview','independent');before=G.s();G.speak('Confirmer');after=G.s()
 ck(st()['quest']['ending']=='independent'and after['inventory']['weaponParts']==before['inventory']['weaponParts']+4 and after['inventory']['circuitry']==before['inventory']['circuitry']+2 and after['inventory']['scrap']==before['inventory']['scrap']+3,'Issue autonomie : quatre pièces, deux circuits, trois ferrailles')
 texts2=[]
 for _ in range(3):texts2.append(p.locator('#dialogueLine').inner_text());p.locator('#dialogueChoices button').first.click()
 ck(len(set(texts+texts2))==6 and min(map(len,texts2))>180,'Six scènes distinctes sur les deux accords')
 G.near('v030:tape');ck(c('v030Tape')and G.s()['lore']['holotapes']['v030_rig'],'Bande d’Alba acquise physiquement');G.dismiss();c('v027Open','radio','tapes');ck('Pas une seconde peau'in p.locator('#pipboy').inner_text(),'Bande consultable depuis RADIO sans faux fichier audio')
 # Geometry supports, actual access for station at local bay and stale confirmation.
 G.dismiss();G.near('v030:station');c('v030Switch');c('v030Show');ck(c('v030NearService'),'Établi approchable avec l’armure et lieu sans menace')
 c('v030Quote','repair','head');G.load('transit_depot');c('v030Show');inv=G.s()['inventory'];ck(not c('v030Quote','repair','head',True)and G.s()['inventory']==inv,'Changement de scène invalide le devis de maintenance')
 # Stat panel in actual touch context is tested separately.
 G.dismiss();G.load('mooring_station');c('v030Show');ck(p.locator('.p30-slots button').count()==6,'Six contrôles natifs de pièce dans le Pip-Boy');ck('CŒUR À FUSION'in p.locator('#pipboy').inner_text(),'Charge installée et cœurs entamés présentés séparément')
except Exception:G.fail()
G.output()
