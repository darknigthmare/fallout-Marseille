#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'verification';O.mkdir(exist_ok=True);H=R/'JOUER_FALLOUT_MISTRAL_v0.41.html';checks=[];errors=[]
def ck(n,c,d=None):
    checks.append({'name':n,'ok':bool(c),'detail':d});print(('OK ' if c else 'FAIL ')+n,flush=True)
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage'])
    p=b.new_page(viewport={'width':1440,'height':900});p.on('pageerror',lambda e:errors.append(str(e)))
    p.evaluate(r'''() => {
      const databases=new Map();function open(name,version=1){const req={result:null,error:null};setTimeout(()=>{let state=databases.get(name);if(!state){state={version:0,stores:new Map(),options:new Map()};databases.set(name,state)}const db={get objectStoreNames(){return{contains:n=>state.stores.has(n)}},createObjectStore(n,opt={}){if(!state.stores.has(n)){state.stores.set(n,new Map());state.options.set(n,opt)}return{}},transaction(names,mode){names=Array.isArray(names)?names:[names];const tx={oncomplete:null,onerror:null,onabort:null};let pending=0,done=false;const end=()=>setTimeout(()=>{if(!pending&&!done){done=true;tx.oncomplete?.()}},0);tx.objectStore=n=>{if(!state.stores.has(n))throw new Error('missing '+n);const store=state.stores.get(n),opts=state.options.get(n)||{};const request=fn=>{const q={result:null,error:null,onsuccess:null,onerror:null};pending++;setTimeout(()=>{try{q.result=fn();q.onsuccess?.()}catch(e){q.error=e;q.onerror?.();tx.onerror?.()}finally{pending--;end()}},0);return q};return{get:k=>request(()=>store.get(k)),getAll:()=>request(()=>[...store.values()]),put:(v,k)=>request(()=>{const key=k??(opts.keyPath?v[opts.keyPath]:undefined);store.set(key,v);return key}),delete:k=>request(()=>store.delete(k)),clear:()=>request(()=>store.clear())}};end();return tx},close(){}};req.result=db;if(version>state.version){req.oldVersion=state.version;state.version=version;req.onupgradeneeded?.()}req.onsuccess?.()},0);return req}Object.defineProperty(window,'indexedDB',{configurable:true,value:{open}});Object.defineProperty(navigator,'storage',{configurable:true,value:{estimate:async()=>({usage:0,quota:512*1024*1024})}});
    }''')
    p.route('https://hykklcvvwjwhcvukbzts.supabase.co/**',lambda r:r.abort())
    p.set_content(H.read_text(encoding='utf-8'),wait_until='load');p.wait_for_timeout(700)
    def c(n,*a):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+n+'(...a)',list(a))
    try:
        ck('titre v0.41','v0.41' in p.title(),p.title());ck('surface debug v0.40',p.evaluate("typeof __MISTRAL_DEBUG.v040Info")=='function')
        info=c('v040Info');rows=info['corridors']['rows'];ck('deux preuves hors ligne',len(rows)==2,rows)
        mar=next(x for x in rows if x['id']=='aubagne_marseille');cio=next(x for x in rows if x['id']=='aubagne_laciotat')
        ck('Aubagne–Marseille certifié',mar['status']=='certified' and mar['distanceM']==23701 and mar['pathPoints']==72,mar)
        ck('Aubagne–La Ciotat certifié',cio['status']=='certified' and cio['distanceM']==22740 and cio['pathPoints']==109,cio)
        ck('macro séquences réelles',mar['macroSequence']==['geo_huveaune','geo_marseille'] and cio['macroSequence']==['geo_huveaune','geo_laciotat'])
        base_tiles=c('v040Tiles','aubagne_marseille','base');cad_tiles=c('v040Tiles','aubagne_marseille','cadastre')
        ck('préchargement corridor calculé',len(base_tiles)>20 and len(cad_tiles)>40,{'base':len(base_tiles),'cadastre':len(cad_tiles)})
        seam=c('v040SeamFixture',2);ck('raccord terrain aligné',seam['status']=='aligned' and seam['samples']==81 and abs(seam['mean']-2)<.001,seam)
        c('v018LoadMacro','geo_huveaune');p.wait_for_timeout(300)
        fixture=c('v040StitchFixture');ck('bâtiment de frontière recousu',fixture['fixtureMerged'] and fixture['mergedDelta']==1 and fixture['hidden']==[True,True],fixture)
        ck('frontières exactes détectées',fixture['touchA']==['E'] and fixture['touchB']==['W'] and fixture['boundaryError']<.001,fixture)
        async_result=p.evaluate(r'''async () => {
          const meters=(a,b)=>{const R=6378137,lat=(a[0]+b[0])*.5*Math.PI/180,dx=(a[1]-b[1])*Math.PI/180*R*Math.cos(lat),dy=(a[0]-b[0])*Math.PI/180*R;return Math.hypot(dx,dy)};
          const run=async id=>{const proof=await __MISTRAL_DEBUG.v040Proof(id);await __MISTRAL_DEBUG.v040Start(id);__MISTRAL_DEBUG.v040SetPlayer(proof.path[0][0],proof.path[0][1]);__MISTRAL_DEBUG.v040Tick(.31);for(let i=0;i<proof.path.length-1;i++){const a=proof.path[i],b=proof.path[i+1],steps=Math.max(1,Math.ceil(meters(a,b)/280));for(let k=1;k<=steps;k++){const t=k/steps;__MISTRAL_DEBUG.v040SetPlayer(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t);__MISTRAL_DEBUG.v040Tick(.31)}}return __MISTRAL_DEBUG.v040Info().corridors.completed[id]};
          return{laciotat:await run('aubagne_laciotat'),marseille:await run('aubagne_marseille'),active:__MISTRAL_DEBUG.v040Active()};
        }''')
        ck('traversée La Ciotat jouée sans rupture',async_result['laciotat']['status']=='continuous' and async_result['laciotat']['breaks']==0,async_result['laciotat'])
        ck('traversée Marseille jouée sans rupture',async_result['marseille']['status']=='continuous' and async_result['marseille']['breaks']==0,async_result['marseille'])
        ck('roadbook se termine proprement',async_result['active'] is None,async_result)
        c('v027Open','map','corridors');txt=' '.join(p.locator('#pipContent').inner_text().split());ck('Pip-Boy roadbook','TRAVERSÉES CONTINUES' in txt and 'MARSEILLE' in txt and 'LA CIOTAT' in txt,txt[:1400]);c('closePip')
        c('v041OpenStatus');st=' '.join(p.locator('#v018StatusScreen').inner_text().split());ck('statut cartographique v0.41','PACK LOCAL' in st and '5 884' in st,st[:1600])
        ck('aucune exception JavaScript',not errors,errors)
    except Exception as e:ck('scénario navigateur v0.40',False,repr(e))
    b.close()
rep={'version':'0.41.0','html_sha256':hashlib.sha256(H.read_bytes()).hexdigest(),'passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'total':len(checks),'errors':errors,'checks':checks,'scope':'Exact v0.40 HTML. Corridor relay deliberately blocked to verify embedded certified snapshots. Traversals are simulated through every proof segment at <=280 m increments; geometric stitch and terrain seam fixtures exercise production code.'}
(O/'QA_REGRESSION_V040_ON_V041.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'passed':rep['passed'],'failed':rep['failed'],'total':rep['total'],'errors':errors},ensure_ascii=False));raise SystemExit(bool(rep['failed'] or errors))
