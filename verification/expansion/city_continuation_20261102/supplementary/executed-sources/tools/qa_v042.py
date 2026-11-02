#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib, json, sys, traceback
from qa_support import chromium_path
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parents[1]
O=R/'verification';O.mkdir(exist_ok=True)
H=R/'JOUER_FALLOUT_MISTRAL_v0.42.html'
checks=[];errors=[]
def ck(name,cond,detail=None):
    checks.append({'name':name,'ok':bool(cond),'detail':detail})
    print(('OK ' if cond else 'FAIL ')+name,flush=True)

def setup_storage(p):
    p.evaluate("""() => {
      const store={};
      Object.defineProperty(window,'localStorage',{configurable:true,value:{
        getItem:k=>store[k]??null,
        setItem:(k,v)=>{store[k]=String(v)},
        removeItem:k=>{delete store[k]},
        clear:()=>{for(const k of Object.keys(store)) delete store[k]}
      }});
      Object.defineProperty(navigator,'storage',{configurable:true,value:{estimate:async()=>({usage:0,quota:536870912})}});
    }""")


with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage'])
    p=b.new_page(viewport={'width':1440,'height':960});p.set_default_timeout(10000)
    p.on('pageerror',lambda e:errors.append(str(e)))
    p.route('https://hykklcvvwjwhcvukbzts.supabase.co/**',lambda r:r.abort())
    p.set_content(H.read_text(encoding='utf-8'),wait_until='load');setup_storage(p);p.wait_for_timeout(600)
    def c(name,*args):return p.evaluate('(a)=>__MISTRAL_DEBUG.'+name+'(...a)',list(args))
    try:
        ck('titre exact v0.42','v0.42' in p.title(),p.title())
        ck('surface debug v0.42',p.evaluate("typeof __MISTRAL_DEBUG.v042Info")=='function')
        info=c('v042Info');meta=info['meta']
        ck('248 sites territoriaux',meta['siteCount']==248,meta)
        ck('8 macro-régions',meta['macroCount']==8,meta)
        ck('répartition fonctionnelle exacte',meta['counts']=={'shelter':16,'settlement':24,'outpost':24,'interior':48,'nest':64,'elite':24,'boss':8,'landmark':24,'caravan':16},meta['counts'])
        ck('64 lieux visitables',meta['visitable']==64,meta['visitable'])
        ck('96 zones hostiles',meta['hostileSites']==96,meta['hostileSites'])
        ck('200 postes PNJ potentiels',meta['npcSlots']==200,meta['npcSlots'])
        ck('720 postes ennemis potentiels',meta['enemySlots']==720,meta['enemySlots'])
        ck('31 sites par macro-région',all(v==31 for v in meta['macroCounts'].values()),meta['macroCounts'])
        catalog=c('v042Catalog');known=set(p.evaluate('Object.keys(__MISTRAL_DEBUG.enemyCatalog())'))
        used={t for s in catalog for t in [*(s.get('enemyTypes') or []),s.get('eliteType'),s.get('bossType')] if t}
        ck('bestiaire référencé entièrement existant',used.issubset(known),sorted(used-known))
        # Macro settlement and NPC streaming.
        c('setRenderPaused',True);c('v022Freeze',True);c('v018NoNetwork',True);c('v020Reset')
        huveaune=c('v042Macro','geo_huveaune')
        settlement=next(s for s in huveaune if s['kind']=='settlement')
        c('v017LoadMacro','geo_huveaune');c('v017SetPlayerLatLon',settlement['lat'],settlement['lon']);c('v042Update',.8)
        runtime=c('v042Runtime');world=c('v042World')
        ck('colonie instanciée près du joueur',settlement['id'] in runtime['active'],runtime)
        pn=[n for n in world['npcs'] if n['site']==settlement['id']]
        ck('quatre PNJ locaux instanciés',len(pn)==settlement['npcSlots'],pn)
        ck('site découvert par proximité',c('v042Info')['discovered']>=1,c('v042Info'))
        ck('budget de streaming respecté',len(runtime['active'])<=7,runtime)
        # NPC dialogue and contract.
        ck('dialogue PNJ territorial',c('v042Talk',pn[0]['id']) is True,pn[0])
        dialog=' '.join(p.locator('#dialogue').inner_text().split())
        ck('dialogue contextualisé',settlement['name'] in dialog and 'Avez-vous du travail' in dialog,dialog[:900])
        c('v020ModalDismiss');ck('contrat territorial assignable',c('v042Contract',settlement['id']) is True)
        target=c('v042Site',c('v042Info')['tracked']);ck('contrat cible un site hostile',target['kind'] in ['nest','elite','boss'],target)
        # Map layer after discovering a macro.
        c('v042DiscoverMacro','geo_huveaune');c('v042Map');p.wait_for_timeout(100)
        text=' '.join(p.locator('#pipContent').inner_text().split())
        ck('onglet Pip-Boy couche Fallout','COUCHE FALLOUT TERRITORIALE' in text and '248' in text and 'PROGRESSION RÉGIONALE' in text,text[:1500])
        ck('marqueurs SVG produits',p.locator('#pipContent .v42-marker').count()>=31,p.locator('#pipContent .v42-marker').count())
        c('closePip')
        # Elite site streaming and rank.
        elite=next(s for s in huveaune if s['kind']=='elite')
        c('v017LoadMacro','geo_huveaune');c('v017SetPlayerLatLon',elite['lat'],elite['lon']);c('v042Update',.8)
        ew=c('v042World');ee=[e for e in ew['enemies'] if e['site']==elite['id']]
        ck('repaire élite instancié',len(ee)==elite['enemySlots'],ee)
        ck('ennemi élite distinct',sum(e['rank']=='elite' for e in ee)==1,ee)
        defeat=c('v042Defeat',elite['id']);ck('combat élite sécurise le site',defeat['count']==elite['enemySlots'] and defeat['cleared'],defeat)
        ck('progression élite persistante',bool(c('v020State')['v042']['eliteKills'].get(elite['id'])),c('v020State')['v042']['eliteKills'])
        # Regional boss.
        boss=next(s for s in huveaune if s['kind']=='boss')
        c('v017LoadMacro','geo_huveaune');c('v017SetPlayerLatLon',boss['lat'],boss['lon']);c('v042Update',.8)
        bw=c('v042World');be=[e for e in bw['enemies'] if e['site']==boss['id']]
        ck('boss régional et escorte instanciés',len(be)==boss['enemySlots'] and any(e['rank']=='boss' for e in be),be)
        bd=c('v042Defeat',boss['id']);ck('boss régional vaincu',bd['cleared'],bd)
        ck('région mémorise le boss',c('v020State')['v042']['regional']['geo_huveaune']['boss'] is True,c('v020State')['v042']['regional']['geo_huveaune'])
        # Visitable shelter exterior and interior.
        shelter=next(s for s in huveaune if s['kind']=='shelter')
        c('v017LoadMacro','geo_huveaune');c('v017SetPlayerLatLon',shelter['lat'],shelter['lon']);c('v042Update',.8)
        ck('entrée d’abri instanciée',any(i['id']==f"v042-enter-{shelter['id']}" for i in c('v020Stats')['interactables']))
        ck('entrée dans l’abri',c('v042Enter',shelter['id']) is True)
        p.wait_for_timeout(120);inside=c('v042World')
        ck('instance visitable chargée',inside['id']=='v042_expedition',inside)
        ie=[e for e in inside['enemies'] if e['site']==shelter['id']]
        ck('menaces intérieures conservées',len(ie)==shelter['enemySlots'],ie)
        ck('six sous-zones intérieures',len(inside['allSubzones'])==6,inside['allSubzones'])
        idf=c('v042Defeat',shelter['id']);ck('ennemis intérieurs neutralisés',idf['count']==shelter['enemySlots'],idf)
        ck('noyau récupérable',c('v042Claim',shelter['id']) is True)
        ck('abri sécurisé et visité',bool(c('v020State')['v042']['cleared'].get(shelter['id'])) and bool(c('v020State')['v042']['visited'].get(shelter['id'])),c('v020State')['v042'])
        c('v020ModalDismiss')
        # Persistence round-trip using project snapshot helpers.
        snapshot=c('v023SnapshotState');clears_before=c('v042Info')['cleared'];tracked_before=c('v042Info')['tracked']
        c('v020Reset');ck('reset efface la progression active',c('v042Info')['cleared']==0,c('v042Info'))
        c('v023Restore',snapshot);ck('restauration conserve sécurisations',c('v042Info')['cleared']==clears_before,c('v042Info'))
        ck('restauration conserve le repère',c('v042Info')['tracked']==tracked_before,c('v042Info'))
        # Mobile map layout.
        c('v020Load','transit_depot');p.set_viewport_size({'width':390,'height':844});c('v042Map');p.wait_for_timeout(100)
        ck('carte mobile défilable',p.locator('#pipContent .v42-layer').count()==1 and p.locator('#pipContent .v42-summary').count()==1)
        ck('aucune exception JavaScript',not errors,errors)
    except Exception as exc:
        ck('scénario navigateur v0.42',False,traceback.format_exc())
    b.close()
rep={'version':'0.42.0','html_sha256':hashlib.sha256(H.read_bytes()).hexdigest(),'passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'total':len(checks),'errors':errors,'checks':checks,'scope':'Exact v0.42 HTML in Chromium software. Remote map services deliberately blocked. Deterministic catalog, proximity streaming, settlements, NPCs, contracts, elite/boss sites, visitable shelter, persistence and mobile map are exercised.'}
(O/'QA_V042.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':rep['passed'],'failed':rep['failed'],'total':rep['total'],'errors':errors},ensure_ascii=False))
raise SystemExit(bool(rep['failed'] or errors))
