from pathlib import Path
from qa_support import chromium_path
import json,hashlib,traceback
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];H=(R/'JOUER_FALLOUT_MISTRAL_v0.30.html').read_text();out=[];err=[]
def ck(ok,name,details=None):out.append(dict(ok=bool(ok),name=name,detail=details));print('OK' if ok else 'FAIL',name,details or '',flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1280,'height':900});p.on('pageerror',lambda e:err.append(str(e)));p.set_content(H,wait_until='load');p.locator('#btnV023').wait_for(timeout=30000)
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def s():return c('getState')
 def reset():c('v020ModalDismiss');c('v020Reset');c('v020Fixture',False)
 try:
  c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True)
  reset();c('v020GrantWeapon','maritimeSMG');c('v020Equip','maritimeSMG');c('v020SetPlayer',{'ammoClip':4,'ap':200,'maxAp':200});c('v020Tick',1);c('v020Vats');c('v023Select',0,'body');c('v023Queue');c('v023Queue');ck([q['rounds'] for q in c('v023QueueInfo')]==[3,1],'Rafale : réserver trois puis une munition')
  c('v023EditQueue',1,-1);c('v020VatsExecute');c('v020RandomTick',.1,.5);ck(s()['player']['ammoClip']==3,'Rafale partielle remontée : une seule munition consommée');c('v020RandomTick',.8,.5);ck(s()['player']['ammoClip']==0 and s()['player']['ap']==150,'Rafale entière suivante : trois munitions, total 50 PA');ck(s()['v023']['critical']==38,'Jauge : deux actions touchées, pas quatre projectiles');c('v020VatsCancel')
  reset();c('v023Crit',80);c('v020RandomFire',.5);ck(s()['v023']['critical']==80,'Un tir libre ne remplit pas la réserve critique')
  reset();c('v020SetPlayer',{'ap':25});ck(c('v020Vats')=='VATS','Ouverture à exactement 25 PA');c('v023Select',0,'body');ck(c('v023Queue') and not c('v023Queue'),'Réservation AP ne peut dépasser la réserve');c('v020VatsCancel')
  reset();c('v023Crit',100);c('v020Vats');c('v023Select',0,'body');c('v023Queue',True);c('v020EnemyPatch',{'alive':False,'health':0});ap=s()['player']['ap'];ammo=s()['player']['ammoClip'];c('v020VatsExecute');c('v020RandomTick',.1,.5);ck(s()['player']['ap']==ap and s()['player']['ammoClip']==ammo and s()['v023']['critical']==100,'Cible neutralisée avant le tir : aucune perte critique ou ressource');c('v020VatsCancel')
  reset();c('v023Crit',100);c('v020Vats');c('v023Select',0,'body');c('v023Queue',True);c('v020VatsExecute');c('v020Load','transit_depot');c('v021MuteEnemies');c('v020Tick',1);ck(c('v020Combat')['execution'] is None and s()['v023']['critical']==100,'Transition annule la file, pas la jauge')
  c('v022ResetRuntime');c('v020Approach','v023:goat');c('v023OpenGoat');c('v023Draft',['repair','medicine','speech']);c('v020ModalDismiss');ck(not c('v023Answer',0) and not c('v023ConfirmGoat'),'Réponse ou validation après fermeture du questionnaire refusée')
  c('v023SetQuest',{'accepted':True,'ending':'network','deliveries':{'transit_depot':True,'traverse_archives':True,'mooring_station':False}});c('v023Set',{'consequences':[{'id':'deliveries','text':'Trois réserves','observed':False}]});c('v020Load','mooring_station');c('v021MuteEnemies');c('v022ResetRuntime');c('v020Approach','v023:delivery');ck(c('v023Delivery'),'Dernière livraison effectivement récupérée');ck(next(e for e in s()['v023']['consequences'] if e['id']=='deliveries')['observed'],'Bilan passe de disponible à reçu après les trois caisses')
  # Separate migration invariants, no adapter installed: refusal remains explicit.
  raw=s();raw['v023']['history']=[dict(speaker='X',text='Texte '+str(i),choice=False,role='',zone='transit_depot') for i in range(180)];m=c('v018Migrate',raw);ck(len(m['v023']['history'])==120 and m['v023']['history'][0]['text']=='Texte 60','Historique borné aux 120 derniers échanges')
  c('v023SetQuest',{'accepted':True,'ending':None,'tracked':True});c('v020Tick',.1);ck(not p.locator('#v020QuestHint').is_hidden(),'Objectif du dossier suivi visible pendant l’enquête');c('v023SetQuest',{'ending':'network','tracked':False});c('v020Tick',.1);ck(p.locator('#v020QuestHint').is_hidden() or 'Le droit de choisir' not in p.locator('#v020QuestHint').inner_text(),'Objectif ancien retiré du HUD après conclusion')
  ck(not err,'Aucune exception JavaScript supplémentaire',err)
 except Exception:ck(False,'Exception',traceback.format_exc())
 finally:
  result=dict(version='0.23.0',html_sha256=hashlib.sha256(H.encode()).hexdigest(),total=len(out),passed=sum(x['ok'] for x in out),failed=sum(not x['ok'] for x in out),errors=err,scope='Exact HTML set_content; synthetic combat fixture explicitly used; software Chromium; no geographical import; narrow targeted guards.',results=out);(R/'verification/QA_V023_EXTRA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));b.close();print('RESULT',result['passed'],result['failed'])
raise SystemExit(result['failed']>0)
