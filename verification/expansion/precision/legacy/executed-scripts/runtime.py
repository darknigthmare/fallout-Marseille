from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
import json,hashlib,traceback
R=Path(__file__).resolve().parents[2];O=R/'verification/v050/legacy';O.mkdir(exist_ok=True);H=(R/'JOUER_FALLOUT_MISTRAL_v0.50.html').read_text();tests=[];errors=[]
def ck(n,ok,d=None):tests.append({'name':n,'ok':bool(ok),'detail':d});print(('OK ' if ok else 'FAIL ')+n,flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1440,'height':900});p.set_default_timeout(25000);p.on('pageerror',lambda e:errors.append(str(e)));p.route('https://**/*',lambda r:r.abort());p.set_content(H,wait_until='load');p.wait_for_timeout(3100)
 p.evaluate("window.__store=new Map();Object.defineProperty(window,'localStorage',{configurable:true,value:{get length(){return __store.size},getItem:k=>__store.get(String(k))||null,setItem:(k,v)=>__store.set(String(k),String(v)),removeItem:k=>__store.delete(String(k)),key:i=>[...__store.keys()][i]||null}})")
 def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
 def actor(id):return next(a for a in c('v049Actors') if a['id']==id)
 def state():return json.loads(c('v023SnapshotState'))
 try:
  ck('Build v0.49 exécutée',c('v049Info')['version']=='0.49.0');ck('Banc identifié chargé',c('v046Lab') is True);c('setRenderPaused',True);c('v022Freeze',True);c('v047Control',{'auto':False})
  sites=c('v042Catalog');nest=next(s for s in sites if s['kind']=='nest');safe=next(s for s in sites if s['kind']=='settlement');shelter=next(s for s in sites if s['kind']=='shelter');other=next(s for s in sites if s['kind']=='shelter' and s['id']!=shelter['id']);boss=next(s for s in sites if s['kind']=='boss')
  ck('Rencontre territoriale instanciée',c('v049ProbeSpawn',nest['id'],[12,0]));en=next(a for a in c('v049Actors') if a['site']==nest['id']);eid=en['id'];geometry=c('v049SiteGeometry',nest['id'])
  pos=[en['pos'][0]+.7,en['pos'][1],en['pos'][2]+.9];c('v049ProbePose',eid,pos,.75);c('v049Damage',eid,18,'leg_l');hurt=actor(eid);c('v049ProbeState',eid,{'attackCooldown':1.2,'searchTimer':7});c('v049Checkpoint')
  ck('Santé effectivement réduite',0<hurt['hp']<en['hp'],hurt)
  ck('Jambe gauche enregistrée',hurt['limbs'].get('leg_l',0)>0,hurt['limbs'])
  c('v042Unload',nest['id']);ck('Acteurs réellement retirés de la scène',not any(a['site']==nest['id'] for a in c('v049Actors')))
  ck('Journal conservé sans acteur visible',c('v049Info')['wounded']==1,c('v049Info'))
  c('v049ProbeSpawn',nest['id'],[12,0]);back=actor(eid)
  ck('Pas de soin au rechargement',back['hp']==hurt['hp'],{'before':hurt['hp'],'after':back['hp']})
  ck('Position et orientation retrouvées',back['pos']==pos and back['yaw']==.75,back)
  ck('Membre blessé retrouvé',back['limbs']==hurt['limbs'])
  ck('Décor du site déterministe',c('v049SiteGeometry',nest['id'])==geometry)
  before=back['limbs']['leg_l'];c('v049Damage',eid,5,'leg_l');ck('Nouvelle blessure cumulative après retour',actor(eid)['limbs']['leg_l']>before,actor(eid)['limbs'])
  c('v049RegionLabel','geo_huveaune');ck('Blessure indépendante du nom de macro-région',actor(eid)['limbs']['leg_l']>before)
  # Native JSON serialization / loading guard: a stale active scene must not be checkpointed into another save.
  raw=state();remember=raw['v049']['actors'][eid]['health'];raw['v049']['actors'][eid]['health']=21;raw['v022']['encounters']={};c('v049ReloadState',json.dumps(raw));c('v049Checkpoint');ck('Ancienne scène ne pollue pas une sauvegarde restaurée',state()['v049']['actors'][eid]['health']==21)
  c('v042Unload',nest['id']);c('v049ProbeSpawn',nest['id'],[12,0]);ck('Santé chargée depuis le JSON',actor(eid)['hp']==21,actor(eid))
  # Dead body finite inventory, binding across the macro label and re-streaming.
  c('v049Damage',eid,99999);body=next(x for x in c('v049Bodies') if x['id']=='remains:'+eid);ck('Clé de dépouille canonique',body['key'].startswith('territory|'),body['key'])
  ck('Mort inscrite au journal et flags',state()['v049']['actors'][eid]['alive'] is False and state()['flags']['enemyDead'][eid])
  count=len(c('v049Bodies'));caps=body['items']['caps'];q=body['pos'];c('v046CameraAt',[q[0],q[1]+1.65,q[2]+1.6],0,0)
  ck('Dépouille fouillable physiquement',c('v026OpenContainer',body['key']) is True)
  wallet=state()['player']['caps'];ck('Prélèvement réel du butin',c('v026Take','caps',3) is True);c('v026Close');ck('Capsules réellement reçues',state()['player']['caps']==wallet+3)
  c('v049RegionLabel','geo_marseille');c('v042Unload',nest['id']);c('v049ProbeSpawn',nest['id'],[12,0]);b2=next(x for x in c('v049Bodies') if x['id']==body['id'])
  ck('Mort non ressuscité au retour',not any(a['id']==eid and a['alive'] for a in c('v049Actors')))
  ck('Butin partiellement pris non recréé',b2['items']['caps']==caps-3 and len(c('v049Bodies'))==count,b2)
  ck('Dépouille liée à la région actuellement affichée',b2['zone']=='geo_marseille',b2['zone'])
  ck('Interaction de dépouille réattachée',any(i['id']=='v026:'+body['key'] for i in c('v026Scene')['interactions']))
  ck('Le corps reste rendu',body['id'] in c('v049BodyDraws'))
  c('v049Damage',eid,99999) if any(a['id']==eid for a in c('v049Actors')) else None
  ck('Un seul inventaire de dépouille',len(c('v049Bodies'))==count)
  # Citizens remember location, rather than randomizing their pose every visit.
  c('v049ProbeSpawn',safe['id'],[-14,0]);n=next(a for a in c('v049Actors') if a['kind']=='npc');npos=[n['pos'][0]+.2,n['pos'][1],n['pos'][2]+.3];c('v049ProbePose',n['id'],npos,1.12);c('v042Unload',safe['id']);c('v049ProbeSpawn',safe['id'],[-14,0]);nn=actor(n['id']);ck('Habitant conserve sa position et son orientation',nn['pos']==npos and nn['yaw']==1.12,nn)
  # Interior scope and world reconstruction (not a retained interior).
  c('v042Enter',shelter['id']);p.wait_for_timeout(150);ins=next(a for a in c('v049Actors') if a['kind']=='enemy');c('v049Damage',ins['id'],17,'arm_r');ip=[-19,0,24];c('v049ProbePose',ins['id'],ip,.22);ih=actor(ins['id']);c('v049RebuildInstance');p.wait_for_timeout(200);ir=actor(ins['id'])
  ck('Intérieur reconstruit conserve santé et pose',ir['hp']==ih['hp'] and ir['pos']==ip and ir['yaw']==.22,ir)
  ck('Blessure intérieure conservée',ir['limbs']==ih['limbs'])
  c('v049Damage',ins['id'],99999);ib=next(x for x in c('v049Bodies') if x['id']=='remains:'+ins['id']);c('v049RebuildInstance');p.wait_for_timeout(120)
  ck('Dépouille intérieure rattachée après reconstruction',any(i['id']=='v026:'+ib['key'] for i in c('v026Scene')['interactions']))
  ck('Aucun adversaire mort recréé dans l’intérieur',not any(a['id']==ins['id'] and a['alive'] for a in c('v049Actors')))
  c('v042Exit');p.wait_for_function('__MISTRAL_DEBUG.v042World().geo && !__MISTRAL_DEBUG.v046Info().busy');c('v042Enter',other['id']);p.wait_for_timeout(150)
  ck('Dépouille du premier intérieur absente du second',not any(i['id']=='v026:'+ib['key'] for i in c('v026Scene')['interactions']))
  ck('Inventaire intérieur caché sans être perdu',next(x for x in c('v049Bodies') if x['id']==ib['id'])['zone']=='v049_inactive')
  ck('Deux sites intérieurs utilisent des identités distinctes',all(a['site']==other['id'] for a in c('v049Actors')))
  c('v042Exit');p.wait_for_function('__MISTRAL_DEBUG.v042World().geo && !__MISTRAL_DEBUG.v046Info().busy')
  # Duplication migration: never refill a previously looted corpse.
  s=state();orig=s['v026']['containers'][body['key']];dup=json.loads(json.dumps(orig));dup['items']['caps']=1;s['v026']['containers']['geo_huveaune|'+body['id']]=dup;c('v049ReloadState',json.dumps(s));merged=[x for x in c('v049Bodies') if x['id']==body['id']]
  ck('Migration fusionne les anciens doublons',len(merged)==1 and merged[0]['items']['caps']==1,merged)
  # Normal respawn delay retires old corpses + damage, unique sites never reset.
  c('v042Unload',nest['id']);c('v049ProbeSpawn',nest['id'],[12,0]);c('v042Defeat',nest['id']);ck('Site ordinaire sécurisable',bool(state()['v042']['cleared'].get(nest['id'])))
  c('v042Unload',nest['id']);t0=state()['playTime'];c('v049ProbeTime',t0+nest['respawnHours']*3600-1);ck('Pas de respawn avant le délai',c('v049Respawn',nest['id']) is False)
  c('v049ProbeTime',t0+nest['respawnHours']*3600+1);ck('Respawn autorisé après le délai',c('v049Respawn',nest['id']) is True)
  ck('Anciennes blessures retirées pour le nouveau cycle',not any(a['site']==nest['id'] for a in state()['v049']['actors'].values()))
  ck('Anciennes dépouilles retirées au nouveau cycle',not any(':'+nest['id']+':' in x['id'] for x in c('v049Bodies')))
  c('v049ProbeSpawn',nest['id'],[12,0]);ck('Nouveau cycle à santé normale',all(a['hp']==a['max'] and a['alive'] for a in c('v049Actors') if a['site']==nest['id']))
  c('v042Clear',boss['id']);c('v049ProbeTime',t0+1e8);ck('Boss unique jamais réinitialisé',c('v049Respawn',boss['id']) is False and bool(state()['v042']['cleared'].get(boss['id'])))
  ck('Journal de taille bornée',c('v049Info')['bytes']<c('v049Info')['budget'],c('v049Info')['bytes'])
  c('v027Open','map','integrity');txt=p.locator('#pipContent').inner_text();ck('Diagnostic de persistance dans le Pip-Boy','LE QUARTIER SE SOUVIENT' in txt);c('closePip')
  # Lab exit/new lab does not carry encounters into another playthrough.
  c('v046Campaign');p.wait_for_timeout(100);ck('Banc ne contamine pas le journal campagne',c('v049Info')['entries']==0,c('v049Info'))
  ck('Nouvelle session de banc réinitialise les rencontres',c('v046Lab') and c('v049Info')['entries']==0)
  ck('Aucune exception JavaScript',not errors,errors)
 except Exception:ck('Scénario v0.49',False,traceback.format_exc())
 b.close()
rep={'version':'0.49.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'passed':sum(t['ok'] for t in tests),'failed':sum(not t['ok'] for t in tests),'total':len(tests),'errors':errors,'tests':tests,'scope':'HTML final, vrais acteurs des sites placés explicitement dans le banc synthétique. Déchargement/rechargement, dégâts, inventaire de dépouille, instances, migration et respawn utilisent les fonctions de production. Pas de pack géographique réel installé.'};(O/'QA_ENCOUNTERS.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:rep[k] for k in ['passed','failed','total','errors']}));raise SystemExit(bool(rep['failed'] or errors))
