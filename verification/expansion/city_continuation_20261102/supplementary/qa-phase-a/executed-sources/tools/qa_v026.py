#!/usr/bin/env python3
"""New loot and inventory transaction tests. Physical authored levels + explicit
synthetic combat, plus native clicks. File navigation is blocked; exact HTML via
set_content. Native save rejection tested first, then a declared memory adapter."""
from pathlib import Path
import json,hashlib,traceback,math
from playwright.sync_api import sync_playwright
from qa_support import chromium_path
R=Path(__file__).resolve().parents[1];H=(R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_text();O=R/'verification';rows=[];errors=[]
def ck(ok,name,detail=None):
 rows.append(dict(ok=bool(ok),name=name,detail=detail));print('OK' if ok else 'FAIL',name,str(detail)[:240] if detail is not None else '',flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':960});p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(H,wait_until='load');p.locator('#btnV026').wait_for(timeout=30000);p.set_default_timeout(8000)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def s():return c('getState')
 def d():c('v020ModalDismiss')
 def reset():d();c('v020Reset');c('v022ResetRuntime')
 def load(z,mute=True):d();c('v020Load',z);c('v022ResetRuntime');c('v022Time',10);c('v021MuteEnemies') if mute else None
 def near(id):return c('v020Approach',id)
 def chest(z,id):load(z);ck(near('v026:'+z+'|'+id) is not None,'Accès physique au conteneur '+z+'/'+id);return c('v026OpenContainer',z+'|'+id)
 def dialog(text):p.locator('#dialogueChoices button').filter(has_text=text).first.click()
 def salome():load('transit_depot');near('v022:salome:talk');return c('v026QuestTalk')
 def prime():salome();dialog('comparer les bordereaux');d()
 def inspect_all():
  for z in ['transit_depot','traverse_archives','mooring_station']:
   chest(z,'consignment');p.locator('[data-v26="inspect"]').click();d()
 try:
  c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True);reset();load('transit_depot')
  ck(c('v026Info')['version']=='0.30.0','Le HTML final annonce 0.27.0')
  ck(c('save') is False,'Écriture native sur origine opaque refusée, sans faux succès')
  p.evaluate("window.__store={};Object.defineProperty(window,'localStorage',{configurable:true,value:{getItem:k=>__store[k]??null,setItem:(k,v)=>__store[k]=String(v),removeItem:k=>delete __store[k]}})")
  ck(c('save') is True,'Écriture de test avec adaptateur mémoire explicitement déclaré')
  ck(c('v018Keys')['campaign']=='fallout_mistral_save_v030' and c('v018Keys')['sandbox']=='fallout_mistral_sandbox_v030','Campagne et exploration v0.26 séparées')
  # Coverage and real controller routes, not checks on decorative object counts.
  for z in ['transit_depot','traverse_archives','mooring_station','relay_vent','relay_cold','relay_brake']:
   load(z);cc=c('v026Containers');ck(len(cc)==(3 if z in ['transit_depot','traverse_archives','mooring_station'] else 1),z+' : conteneurs attendus réellement attachés',len(cc))
   for box in cc:
    if box['id']=='workcase':
     target=[box['pos'][0],3.2,box['pos'][2]+1.6];walk=c('v021ActualWalk',target);ck(walk['ok'] and walk['maxY']>4.7,z+' : monter au coffret via le contrôleur',walk)
    ck(near('v026:'+box['key']) is not None,z+' : interaction atteignable '+box['id'])
  reset();chest('transit_depot','free');before=s()['inventory'].get('enamelCup',0);p.locator('[data-v26="select|enamelCup"]').click();p.locator('[data-v26="take|enamelCup|1"]').click();ck(s()['inventory']['enamelCup']==before+1,'Clic natif : prendre un objet, pas toute la pile');ck(c('v026State')['containers']['transit_depot|free']['items']['enamelCup']==1,'La quantité restante est finie')
  ck(not c('v026Take','enamelCup',-1) and not c('v026Take','enamelCup',999) and not c('v026Take','enamelCup',1.5),'Transferts négatifs, excessifs et fractionnaires refusés')
  snapshot=c('v026State')['containers']['transit_depot|free']['items'];d();load('traverse_archives');load('transit_depot');ck(c('v026State')['containers']['transit_depot|free']['items']==snapshot,'Quantité partielle conservée après aller-retour entre scènes')
  near('v026:transit_depot|free');c('v026OpenContainer','transit_depot|free');p.locator('[data-v26="all"]').click();ck(all(n==0 for n in c('v026State')['containers']['transit_depot|free']['items'].values()),'Tout prendre vide le conteneur sans le régénérer');bag=s()['inventory'].copy();ck(not c('v026TakeAll') and s()['inventory']==bag,'Reprendre une caisse vide ne duplique rien')
  # Actual locks, repeated failures consume one pin every third failed attempt.
  chest('transit_depot','workcase');key='transit_depot|workcase';pins=s()['inventory']['bobbyPin'];target=c('v026LockTarget',key);wrong=0 if target>90 else 180
  ck(not c('v026Take','weaponParts',1),'Serrure fermée empêche de prendre du matériel')
  for i in range(3):p.locator('#v026Pin').fill(str(wrong)) if False else c('v026LockSet',wrong);p.locator('[data-v26="turn"]').click()
  ck(s()['inventory']['bobbyPin']==pins-1,'Trois tentatives ratées cassent une épingle, pas trois');xp=s()['player'].get('xp',s().get('xp'))
  c('v026LockSet',target);p.locator('[data-v26="turn"]').click();ck(c('v026State')['containers'][key]['unlocked'],'Le réglage correct ouvre le vrai coffre');ck(s()['player'].get('xp',s().get('xp'))==xp,'Aucune boucle d’XP au crochetage')
  ck(c('v026Take','pipeCarbine',1),'L’arme usée du coffret peut être prise');ck(s()['equipment']['weaponCondition']['pipeCarbine']==48,'État du coffre conservé à la récupération')
  d();load('traverse_archives');chest('transit_depot','workcase');ck(c('v026State')['containers'][key]['unlocked'],'Serrure reste ouverte après retour')
  # Owned loot confirmation, witness and restitution.
  reset();prime();chest('transit_depot','consignment');stock=s()['inventory']['water'];crime=dict(s()['crime']);ck(not c('v026Take','water',1),'Inspecter une réserve ne donne pas le droit de la vider')
  p.locator('[data-v26="owned"]').click();ck(c('v026Take','water',1),'Prélèvement volontaire après avertissement');ck(s()['inventory']['water']==stock+1,'Un seul objet a quitté la réserve')
  ck(sum(s()['crime'].values())>sum(crime.values()),'Témoin proche : un avis local est enregistré',s()['crime']);crime=dict(s()['crime']);c('v026Take','water',1);ck(s()['crime']==crime,'Le même lot ne cumule pas un avis par article')
  ck(c('v026Missing')['water']==2,'Deux eaux manquent au lot dans le bilan');ck(c('v026ReturnItem','water',1) and c('v026Missing')['water']==1,'Remise physique diminue le manque et le sac');ck(not c('v026ReturnItem','water',999),'Rendre au-delà du contenu initial est refusé')
  # Premature and distant resolutions fail, no stale scene effects.
  d();ck(not c('v026Resolve','return'),'Conclure avant les trois bordereaux est refusé');inspect_all();salome();before=s()['player']['caps'];c('v020Seed',{'water':0});c('v026Options');c('v026Preview','return');ck(not c('v026Resolve','return') and s()['player']['caps']==before,'Une restitution sans ses ressources est bloquée, sans paiement partiel');d();c('v020Seed',{'water':5});salome();c('v026Preview','return');dialog('Confirmer');ck(c('v026State')['quest']['ending']=='return','Restitution conclue par vraie confirmation');ck(s()['player']['caps']==before+60,'Prime unique de restitution attribuée')
  c('v026Epilogue',2);dialog('Revenir');ck(not c('v026Resolve','return'),'Rejouer une conclusion ne verse pas de seconde prime');ck(all(n==0 for n in c('v026State')['containers']['transit_depot|consignment']['items'].values()),'Les réserves restituées ne restent pas à disposition du joueur');ck(any(not d['hidden'] for d in c('v026Scene')['after']),'Fournitures de l’accord réellement visibles')
  for outcome in ['share','claim']:
   reset();prime();inspect_all();salome();c('v026Options');c('v026Preview',outcome);dialog('Confirmer');ck(c('v026State')['quest']['ending']==outcome,'Chemin complet : '+outcome)
   caps=s()['player']['caps'];c('v026Epilogue',2);dialog('Revenir');c('v026Epilogue',2);dialog('Revenir');ck(s()['player']['caps']==caps,'Épilogue '+outcome+' relisible sans gain')
   chest('transit_depot','consignment');content=c('v026State')['containers']['transit_depot|consignment'];ck(content['permission'] and sum(content['items'].values())==(1 if outcome=='share' else 10),outcome+' : partage limité ou récupération des restes, pas un double don')
   if outcome=='claim':ck(s()['rep']['ligue']<0,'Récupération personnelle affecte la réputation locale')
  # Global combat loot: no immediate resource pickup; corpse persists and is bounded.
  reset();c('v020Fixture',False,'protectron',5);c('v020EnemyPatch',{'health':10,'loot':{'ammo':6,'caps':9,'scrap':3}});pre=s();c('v026Kill',0);after=s();ck(after['player']['caps']==pre['player']['caps'] and after['ammo']==pre['ammo'] and after['inventory'].get('scrap')==pre['inventory'].get('scrap'),'Neutraliser ne transfère plus les ressources à distance');cc=c('v026Containers');ck(len(cc)==1 and cc[0]['kind']=='remains','Un conteneur de dépouille est créé au lieu du décès');dr=c('v026CorpseDraws');ck(len(dr)>10 and all(all(math.isfinite(v) for v in x['pos']) for x in dr),'Restes visuels issus du modèle, coordonnées finies');ck(not c('v026OpenContainer',cc[0]['key']),'Impossible de fouiller un corps distant');near('v026:'+cc[0]['key']);ck(c('v026OpenContainer',cc[0]['key']),'Fouille à proximité du vrai corps');ck(c('v026TakeAll'),'Récupération du butin après fouille');ck(s()['player']['caps']==pre['player']['caps']+9,'Capsules du décès transférées une fois');c('v026Close');c('v026Kill',0);ck(len(c('v026Containers'))==1,'Appel répété sur mort ignoré')
  # Corpse reload in an authored zone, with old death key preserved.
  reset();load('transit_depot',False);e=c('v020Stats')['enemy'][0];c('v026Kill',0);key='transit_depot|remains:'+e['id'];load('traverse_archives');load('transit_depot');ck(any(x['key']==key for x in c('v026Containers')) and len(c('v026CorpseDraws'))>10,'Restes et butin persistent dans une scène réelle rechargée')
  # Inventory, recycling, optional weight.
  reset();load('aubagne');c('v020SetPlayer',{'pos':[70,1.65,70]});c('v026Give','radioTube',2);c('v026Open');before=s()['inventory'].get('circuitry',0);ck(not c('v026Recycle','radioTube',1),'Démontage à distance refusé');d();station=c('v020Stats')['station'];near(station['id']);c('v026Open');ck(c('v026Recycle','radioTube',1),'Démontage au véritable établi');ck(s()['inventory'].get('circuitry',0)==before+1 and s()['inventory']['radioTube']==1,'Consommation et résultat de récupération exacts')
  ck(not c('v026Recycle','shipKey',1),'Les objets de quête ne sont pas démontables');c('v020SetPlayer',{'hp':10});c('v020Seed',{'stimpak':2});ck(c('v026Use','stimpak') and s()['inventory']['stimpak']==1,'Soin depuis le sac consomme un Stimpak');d();c('v026Open');p.locator('#v026Query').fill('Tube radio');ck(p.locator('.v26-row').count()==1,'Recherche réelle sur le contenu possédé');p.keyboard.press('Escape');ck(c('getMode')=='PLAYING','Échap depuis recherche rend la commande au jeu')
  reset();c('v020Fixture',False,'raider',20);c('v020Seed',{'scrap':9999});c('v026Carry',False);pos=s()['player']['pos'];c('v026Move',1,0);normal=s()['player']['pos'][0]-pos[0];c('v026Carry',True);pos=s()['player']['pos'];c('v026Move',1,0);slow=s()['player']['pos'][0]-pos[0];ck(abs(slow/normal-.65)<.001,'Encombrement facultatif ralentit de 35 %, pas d’effacement d’objets')
  # Equipment sales unload once, preserve mods and condition, no duplicate purchases.
  reset();load('aubagne');c('v020Seed',{'caps':10000});c('v020GrantWeapon','pipeCarbine');c('v026Condition','pipeCarbine',40);ammo=s()['ammo']['ammo10'];loaded=s()['equipment']['loadedAmmo']['pipeCarbine'];c('v026Trade','aubagne');ck(c('v026Sell','pipeCarbine'),'Vendre une arme non équipée');ck(s()['ammo']['ammo10']==ammo+loaded,'Chargeur revendu vidé dans la réserve une seule fois');ck(not c('v026Sell','pipeCarbine'),'Vente répétée d’un objet absent refusée');ck(c('v026TradeState','aubagne')['stock']['pipeCarbine']>0,'Objet revendu disponible au comptoir');ck(c('v026Buy','pipeCarbine'),'Rachat de l’arme');ck(s()['equipment']['weaponCondition']['pipeCarbine']==40 and s()['equipment']['loadedAmmo']['pipeCarbine']==0,'Rachat conserve la condition et ne remplit pas le chargeur');caps=s()['player']['caps'];ck(not c('v026Buy','pipeCarbine') and s()['player']['caps']==caps,'Achat d’un modèle déjà possédé bloqué sans débiter');ck(not c('v026Sell','pistol10'),'Arme active protégée');ck(not c('v026Buy','miniNukes'),'Un produit absent du stock ne peut pas être acheté');c('v026CloseTrade');ck(not c('v026Buy','water') and not c('v026Sell','water'),'Transactions refusées après fermeture du comptoir')
  # Save migration retains new finite ledger, malformed keys bounded.
  reset();chest('transit_depot','free');c('v026Take','radioTube',1);d();snap=s();old=json.loads(json.dumps(snap));old.pop('v026');old['version']='0.25.0';old['future_field']={'preserve':True};m=c('v018Migrate',old);ck(m['future_field']['preserve'] and m['v025']==old['v025'] and not m['v026']['carry'],'Migration v0.25 conserve VATS, champs inconnus, encombrement inactif');m=c('v018Migrate',snap);ck(all(m['v026']['containers'][k]['items']=={id:n for id,n in v['items'].items() if n>0} and m['v026']['containers'][k]['unlocked']==v['unlocked'] for k,v in snap['v026']['containers'].items()),'État des conteneurs conservé dans la migration');c('v023SnapshotState');raw=c('v023SnapshotState');c('v023Restore',raw);ck(c('v026State')['containers']['transit_depot|free']['items'].get('radioTube',0)==0,'Export/import de test conserve l’objet déjà pris')
  snap=s();snap['v026']['containers']['bad']={'zone':'transit_depot','pos':[0,0,0],'items':{'water':-3,'ghost':500,'scrap':2.5}};m=c('v018Migrate',snap);ck(m['v026']['containers']['bad']['items']=={},'Quantités invalides et objets inconnus éliminés du nouveau registre')
  # Actual responsive clicks and scene-change invalidation.
  d();chest('transit_depot','free');p.set_viewport_size({'width':390,'height':844});ck(p.locator('#v026Panel').is_visible(),'Panneau de fouille visible à 390×844');ck(p.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Pas de débordement horizontal en mode étroit');p.locator('[data-v26="close"]').click();p.keyboard.press('i');ck(p.locator('#pipboy').is_visible(),'I ouvre le nouvel inventaire Pip-Boy avec une vraie touche');p.keyboard.press('Escape');ck(c('getMode')=='PLAYING','Échap ferme le sac étroit');chest('transit_depot','consignment');load('mooring_station');ck(not c('v026Take','water',1),'Un ancien transfert est invalidé lors du changement de scène');ck(not p.locator('#v026Panel').is_visible(),'Panneau invalidé et masqué au changement de scène')
 except Exception as e:
  ck(False,'Exception suite v0.26',str(e));traceback.print_exc()
 ck(not errors,'Aucune exception JavaScript',errors);b.close()
out=dict(version='0.30.0',html_sha256=hashlib.sha256(H.encode()).hexdigest(),total=len(rows),passed=sum(r['ok']for r in rows),failed=sum(not r['ok']for r in rows),errors=errors,scope='Exact HTML / software Chromium / authored level routes, real UI clicks, explicit synthetic combat, memory save adapter',results=rows)
(O/'QA_V026.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('RESULT',out['total'],out['failed'],flush=True);raise SystemExit(bool(out['failed']))
