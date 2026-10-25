#!/usr/bin/env python3
"""Validate and publish only the final continuation evidence; stdlib, no tests run."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ast, hashlib, json, os, re, runpy, shutil, struct, tempfile, urllib.parse, xml.etree.ElementTree as ET

INDICES={'index.json':'3a83c7f821a2f3bd824240d7f065568df7ae786b1f5719c8c57f004dbd817d61','terrain-index.json':'53887ce8a6707dafee45ef9993e545f9c23b7c8d926f61696aa6117f21c359cd','water-index.json':'f46745db1df594a2ea8a4d60f5ef53ce6fa3ca82bb4e16ab686d62ef2102d927'}
def need(ok,msg):
    if not ok: raise ValueError(msg)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def rel(s):
    p=Path(s);need(isinstance(s,str) and s and not p.is_absolute() and '..' not in p.parts and '\\' not in s,'Unsafe relative path: '+str(s));return p
class Archive:
    def __init__(self,root,base): self.root,self.base,self.inputs,self.files,self.shots=root,base,{}, {},[]
    def read(self,p):
        p=Path(p);need(p.is_file() and not p.is_symlink(),'Missing/unsafe file: '+str(p));raw=p.read_bytes();need(raw,'Empty file: '+str(p));h=sha(raw);need(p not in self.inputs or self.inputs[p]==h,'Input changed: '+str(p));self.inputs[p]=h;return raw
    def obj(self,p):
        d=json.loads(self.read(p),parse_constant=lambda n:(_ for _ in ()).throw(ValueError('Nonfinite JSON')));need(isinstance(d,dict),'Expected JSON object: '+str(p));return d
    def verify(self,p,h): need(re.fullmatch('[a-f0-9]{64}',h) and sha(self.read(p))==h,'Hash mismatch: '+str(p))
    def add(self,p,name):
        name=str(rel(name));raw=self.read(p);need(name not in self.files or self.files[name]==raw,'Conflicting output: '+name);self.files[name]=raw;return raw
    def generated(self,name,d): self.files[str(rel(name))]=(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
    def unchanged(self):
        for p,h in self.inputs.items(): need(p.is_file() and not p.is_symlink() and sha(p.read_bytes())==h,'Input changed during collection: '+str(p))
def counted(d,label,expected=None):
    p,f=d.get('passed'),d.get('failed');t=d.get('total',p+f if type(p)is int and type(f)is int else None)
    need(type(p)is int and p>0 and f==0 and type(f)is int and t==p,label+': incomplete/failed counts');need(expected is None or t==expected,label+': unexpected count')
    for k in ['error','exception','traceback','page_errors','javascriptErrors','javascript_console_errors','local_http_errors','cleanup_errors']: need(not d.get(k),label+': '+k)
    if 'checks' in d: need(len(d['checks'])==t and all(x.get('ok') is True for x in d['checks']),label+': checks do not recount')
    return {'passed':p,'failed':0,'total':t}
def frozen(a):
    d=a.obj(a.base/'FINAL_BUILD.json');need(isinstance(d.get('hashes'),dict) and len(d['hashes'])==315,'Expected 315 frozen production hashes')
    for n,h in d['hashes'].items(): a.verify(a.root/rel(n),h)
    html=d['htmlSha256'];need(d['hashes']['index.html']==d['hashes']['JOUER_FALLOUT_MISTRAL_v0.50.html']==html,'Frozen HTML aliases differ')
    for n,h in INDICES.items(): a.verify(a.root/'data/map_pack/city'/n,h)
    a.add(a.base/'FINAL_BUILD.json','FINAL_BUILD.json');return d,html
def units(a,html):
    d=a.obj(a.base/'units/UNITS.json');need(d.get('stage')=='complete' and d.get('html_sha256')==html and d.get('failedProcesses')==0 and d.get('changedInputs')==[],'Units unfinished/stale/failed')
    need(len(d['suites'])==27 and len({x['suite'] for x in d['suites']})==27 and sum(x['total'] for x in d['suites'])==d['total']==1080,'Units must recount to 1080/27')
    a.verify(a.base/'verify_units.py',d['runner_sha256']);a.add(a.base/'verify_units.py','scripts/verify_units.py')
    for n,h in d['sourceHashes'].items(): a.verify(a.root/rel(n),h)
    for n,h in d['testScriptHashes'].items(): a.verify(a.root/rel(n),h);a.add(a.root/n,'scripts/units/'+n)
    for s in d['suites']:
        need(s['exitCode']==0 and not s.get('error'),'Unit process failed: '+s['suite']);raw=a.add(a.base/'units'/rel(s['log']),'units/'+s['log']);need(sha(raw)==s['logSha256'],'Unit log hash differs')
        values=[int(next(v for v in row if v)) for row in re.findall(r'Ran (\d+) tests|ℹ tests (\d+)|^# tests (\d+)|"passed"\s*:\s*(\d+)',raw.decode(),re.M)];need(values==[s['total']],'Unit log count differs: '+s['suite']);need(not re.search(r'FAILED\s*\(|ℹ fail [1-9]|^# fail [1-9]|skipped=[1-9]|ℹ skipped [1-9]|^# skipped [1-9]',raw.decode(),re.M),'Unit log contains failure/skip')
    a.add(a.base/'units/UNITS.json','UNITS.json');return {'passed':1080,'failed':0,'total':1080,'suites':27,'method':d['scope']}
def rebuild(a,f):
    d=a.obj(a.base/'REPRODUCIBLE_BUILD.json');need(d.get('ok') is True and not d.get('stderr') and len(d['files'])==3,'Independent rebuild failed')
    need({x['path'] for x in d['files']}=={'index.html','JOUER_FALLOUT_MISTRAL_v0.50.html','src/game.js'},'Rebuild outputs incomplete')
    for x in d['files']: need(x['same'] is True and x['sourceSha256']==x['rebuiltSha256']==f['hashes'][x['path']],'Rebuild bytes differ')
    a.add(a.base/'REPRODUCIBLE_BUILD.json','REPRODUCIBLE_BUILD.json');return {'passed':3,'failed':0,'total':3,'method':d['scope']}
def manifested(a,folder,target):
    d=a.obj(folder/'MANIFEST.json');need(d.get('files'),'Empty manifest')
    for n,s in d['files'].items(): raw=a.add(folder/rel(n),target+'/'+n);need(len(raw)==s['bytes'] and sha(raw)==s['sha256'],'Manifest mismatch: '+n)
    a.add(folder/'MANIFEST.json',target+'/MANIFEST.json')
def targeted(a,f):
    manifested(a,a.base/'facades','facades');d=a.obj(a.base/'facades/FACADES_CONTINUATION.json');need(d['stage']=='complete' and d['tests']=={'passed':108,'failed':0,'suites':d['tests']['suites']},'Facade tests failed')
    need(d['modules']['currentFacade']==f['hashes']['src/v050/07_facades.js'] and d['modules']['currentInterior']==f['hashes']['src/v050/08_city_interiors.js'],'Facade freeze differs')
    c=d['targetedGeometryComparisonsNotCountedAsUnitAssertions'];need(c['population']==191 and c['currentUsableEntrances']==c['currentRenderedDoors']==191 and c['currentSpanFailures']==0 and c['sourceGeometryUnchanged'] and c['allPaginationConsistent'],'Facade source comparison failed')
    for n,h in d['sourceIndices'].items(): need(INDICES.get(n)==h,'Facade source index differs')
    w=a.obj(a.base/'world/WORLD_CONTINUATION.json');need(w['passed']==129 and w['failed']==0 and sum(s['passed'] for s in w['suites'])==129,'World suite counts failed')
    for n,h in w['files'].items(): a.verify(a.root/rel(n),h)
    for s in w['suites']:
        need(s['exitCode']==0 and s['failed']==0,'World process failed');a.verify(a.root/s['command'][-1],s['scriptSha256']);raw=a.add(a.base/'world'/rel(s['log']),'world/'+s['log']);need(sha(raw)==s['logSha256'],'World log differs')
    need(w['frozenSourceIndices']==INDICES,'World source indices differ');a.add(a.base/'world/WORLD_CONTINUATION.json','world/WORLD_CONTINUATION.json')
    replay=w['baselineReplay'];a.add(a.base/'world'/rel(replay['script']),'world/'+replay['script'])
    for n,h in replay['productionSnapshots'].items(): a.verify(a.base/'world'/rel(n),h);a.add(a.base/'world'/n,'world/'+n)
    for n in replay['expectedFailedSuites']:
        raw=a.add(a.base/'world'/rel(n),'world/baseline-expected-failures/'+n);need(re.search(rb'AssertionError|ERR_ASSERTION|FAIL',raw),'Expected baseline regression failure absent')
    return {'facades':{'countedInAssertionSum':False,'reason':'Facade 89+19 suites already occur in UNITS.json; coverage populations are not assertions.','comparison':c},'world':{'countedInAssertionSum':False,'reason':'These 129 checks already occur in the unit campaign; expected failed replays are clearly baseline only.','checks':129,'baselineCommit':w['baselineCommit'],'limits':w['limits']}}
def png(raw):
    need(raw[:8]==b'\x89PNG\r\n\x1a\n' and raw[12:16]==b'IHDR' and len(raw)>32 and raw[-12:-8]==b'\x00\x00\x00\x00' and raw[-8:-4]==b'IEND','Invalid PNG structure')
    width,height=struct.unpack('>II',raw[16:24]);need(0<width<=16384 and 0<height<=16384,'Invalid screenshot dimensions');return width,height
def browser(a,kind,folder,report_name,script_name,expected,last,html):
    d=a.obj(a.base/folder/report_name);counts=counted(d,kind,expected);need(d.get('stage')=='complete' and d.get('html_sha256')==html,kind+': unfinished/stale')
    for k in ['html_injected','network_mocked','storage_mocked','synthetic_geography']: need(d.get(k) is False,kind+': nonnative '+k)
    need(d.get('native_navigation') is True and d.get('service_workers_disabled') is True and d.get('contexts_created')==1 and d.get('assistance'),kind+': native method missing')
    need(d['checks'][-1]['name']==last,kind+': terminal integrity check missing')
    pins=d.get('pinned_inputs',d.get('source_snapshot'));need(isinstance(pins,dict) and pins,kind+': source pins absent')
    for n,h in pins.items(): a.verify(a.root/rel(n),h)
    if kind=='native':
        cancellations=[r for r in d.get('local_request_failures',[]) if urllib.parse.urlsplit(r['url']).path=='/__mistral/local-data' and urllib.parse.urlsplit(r['url']).hostname in ['127.0.0.1','localhost','::1'] and r.get('failure')=='net::ERR_ABORTED'];need(d.get('local_request_failures',[])==cancellations and d.get('local_diagnostic_cancellations',[])==cancellations,'Unexpected local native failure')
    else: need(not d.get('local_request_failures') and not d.get('local_geographic_request_failures'),'Local source request failure')
    script=a.add(a.base/folder/script_name,kind+'/'+script_name);need(sha(script)==d['script_sha256'],kind+': executed script differs')
    repository_script={'native':'continuation_native.py','architecture':'architecture_native_browser.py','bestiary':'regional_bestiary_native.py'}[kind];a.verify(a.root/'tests/expansion'/repository_script,d['script_sha256'])
    if kind=='architecture':
        status=a.obj(a.base/folder/'EXECUTION_STATUS.json');need(status['exitCode']==0 and status['reportSha256']==sha(a.read(a.base/folder/report_name)) and status['scriptSha256']==d['script_sha256'] and status['stdoutCaptured'] is False,'Architecture execution attestation differs');a.add(a.base/folder/'EXECUTION_STATUS.json',kind+'/EXECUTION_STATUS.json')
    else:
        logfile='EXECUTION.log' if kind=='native' else 'execution.log';log=a.add(a.base/folder/logfile,kind+'/'+logfile);need(b'STAGE complete' in log,kind+': incomplete execution log')
        if kind=='native': need(b'Process exit code: 0' in log,'Native process exit not zero')
    need(d.get('shots'),kind+': no native screenshots')
    for shot in d['shots']:
        n=str(rel(shot['file']));need(Path(n).name==n and n.endswith('.png') and not n.upper().startswith(('FAILED','FAILURE')),kind+': invalid final screenshot path');raw=a.add(a.base/folder/n,kind+'/'+n);need(sha(raw)==shot['sha256'],kind+': screenshot SHA differs');width,height=png(raw);a.shots.append({'path':kind+'/'+n,'sha256':shot['sha256'],'width':width,'height':height,'label':shot.get('label'),'method':shot.get('method','Actual native WebGL capture; assistance declared in original report')})
    if kind=='architecture':
        artifacts=d['layout_artifacts'];j=rel(artifacts['json']);s=rel(artifacts['svg']);layout=a.obj(a.base/folder/j);need(layout['nativeReportSha256']==sha(a.read(a.base/folder/report_name)) and layout['htmlSha256']==html and layout['actualLayout']==d['interior']['layout'],'Architecture layout receipt differs');raw=a.add(a.base/folder/j,kind+'/'+str(j));svg=a.add(a.base/folder/s,kind+'/'+str(s));meta=ET.fromstring(svg).find('{http://www.w3.org/2000/svg}metadata');need(meta is not None,'SVG provenance absent');binding=json.loads(meta.text);need(binding['layoutJsonSha256']==sha(raw) and binding['nativeReportSha256']==layout['nativeReportSha256'] and binding['htmlSha256']==html,'SVG SHA chain differs')
    a.add(a.base/folder/report_name,kind+'/'+report_name)
    return {**counts,'method':d['scope'],'assistance':d['assistance'],'limitations':d.get('limitations',[]),'remoteRequestFailuresPreserved':len(d.get('external_request_failures',[])),'cancelledLocalDiagnosticProbesPreserved':len(d.get('local_diagnostic_cancellations',[]))}
def legacy(a,html):
    folder=a.base/'legacy-game/verification/v050';d=a.obj(folder/'QA_LEGACY.json');counts=counted(d,'legacy',434);need(d.get('html_sha256')==html and d.get('allHtmlMatch') is True,'Legacy HTML stale');need(len(d['suites'])==len(d['processes'])==len(d['adaptations'])==15 and all(x['exitCode']==0 for x in d['processes']),'Legacy processes incomplete')
    audit=a.obj(a.base/'legacy-final/RUN_AUDIT.json');need(audit['passed'] is True and audit['checker_exit_code']==0 and all(v is True for v in audit['checks'].values()),'Legacy audit failed');need(a.obj(a.base/'legacy-final/QA_LEGACY_RUN.json')==d,'Audited legacy report differs')
    adapter=runpy.run_path(str(a.root/'tools/check_v050.py'));specs=adapter['specifications']();need({x[0] for x in specs}=={x['test'] for x in d['suites']} and sum(x['total'] for x in d['suites'])==434,'Legacy specs/counts differ');bindings={x['test']:x for x in d['adaptations']}
    for s in d['suites']:
        counted(s,'legacy/'+s['test']);need(s['sameHtml'] is True,'Legacy suite HTML differs');source=a.read(a.root/'tests/v049'/rel(s['test']));executed=adapter['adapt'](s['test'],source.decode()).encode();need(sha(source)==bindings[s['test']]['sourceSha256'] and sha(executed)==bindings[s['test']]['executedSha256'],'Legacy adaptation mismatch');a.files['legacy/source-scripts/'+s['test']]=source;a.files['legacy/executed-scripts/'+s['test']]=executed
        detail=a.obj(folder/'legacy'/rel(s['file']));counted(detail,'legacy detail/'+s['test'],s['total']);need(not detail.get('html_sha256') or detail['html_sha256']==html,'Legacy detail stale');a.add(folder/'legacy'/s['file'],'legacy/reports/'+s['file']);a.add(folder/'legacy'/(s['test']+'.log'),'legacy/logs/'+s['test']+'.log')
    for name in ['RUN_AUDIT.json','QA_LEGACY_RUN.json','SOURCE_BEFORE.json','run.log','run_legacy_audit.py']: a.add(a.base/'legacy-final'/name,'legacy/audit/'+name)
    for name in ['check_v050.py','check_v049.py']: a.add(a.root/'tools'/name,'scripts/'+name)
    a.add(folder/'QA_LEGACY.json','legacy/QA_LEGACY.json');return {**counts,'processes':15,'method':d['scope'],'adaptedExecutedBytesRecreatedAndVerified':True}
def preflights(a):
    entries=[]
    specs=[('private-helper','preflight-native/CONTINUATION_NATIVE.json','Native helper called a private lexical function (groundHeightAt), unavailable from page.evaluate; test corrected to public diagnostics. No production regression inferred.'),('layout-expectation','preflight-architecture-layout2-expectation/ARCHITECTURE_NATIVE.json','Pilot still expected layout version 2 after the version-3 room programme; corrected QA expectation, without production mutation.'),('missing-venv','units-system-python-attempt/UNITS.json','The system interpreter lacked rasterio: first source-tools attempt had 9 errors and 12 skips; the complete venv rerun passed all 154 source-tool tests without skips.'),('diagnostic-abort','preflight-native-attempt2/CONTINUATION_NATIVE.json','Only the exact local-data metadata diagnostic was cancelled (ERR_ABORTED); source-file requests were not the reported failure. Final pilot preserves that exact cancellation separately while requiring all production files to succeed.')]
    best=a.base/'bestiary-native/first-run-cleanup-error';candidates=list(best.glob('*NATIVE.json'))
    if candidates: specs.append(('bestiary-cleanup',str(candidates[0].relative_to(a.base)),'All 23 actor checks passed, but the initial Playwright cleanup helper raised after leaving the context manager and returned code 1. The corrected pilot reran on unchanged production and exited 0.'))
    for key,note_path,reason in specs:
        p=a.base/rel(note_path);d=a.obj(p);entries.append({'id':key,'sourceReport':note_path,'sourceReportSha256':sha(a.read(p)),'stage':d.get('stage'),'reportedPassed':d.get('passed'),'reportedFailed':d.get('failed'),'reportedTotal':d.get('total'),'failedProcesses':d.get('failedProcesses'),'explanation':reason,'countedInFinalAssertions':False,'originalReportAndImagesCopied':False})
    a.generated('PREFLIGHT_SUMMARY.json',{'scope':'Superseded QA setup/harness outcomes, not final validation and not automatically production defects. Original failed images and private ChatGPT data are not copied.','entries':entries});return entries

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path('/workspace/fallout-Marseille'));p.add_argument('--evidence',type=Path,default=Path(__file__).parent);p.add_argument('--publish',action='store_true');p.add_argument('--check-only',action='store_true');args=p.parse_args();need(not(args.publish and args.check_only),'Choose publish or check-only')
    root,base=args.repo.resolve(),args.evidence.resolve();destination=root/'verification/expansion/continuation';need(destination!=root/'verification/expansion/architecture','Historical destination forbidden');a=Archive(root,base)
    f,html=frozen(a);u=units(a,html);r=rebuild(a,f);t=targeted(a,f);print('VALID frozen315, units1080, rebuild3, targeted geometry',flush=True)
    n=browser(a,'native','native-final','CONTINUATION_NATIVE.json','EXECUTED_CONTINUATION_NATIVE.py',206,'Local HTTP responses are served natively without a service worker',html)
    arch=browser(a,'architecture','architecture-native-final','ARCHITECTURE_NATIVE.json','EXECUTED_ARCHITECTURE_NATIVE.py',101,'Frozen HTML, sources, atlas, selected geographic chunks and city indices remain unchanged',html)
    b=browser(a,'bestiary','bestiary-native','BESTIARY_NATIVE.json','EXECUTED_REGIONAL_BESTIARY_NATIVE.py',23,'Actual local source requests succeed without service-worker substitution',html);print('VALID three native pilots, 330 checks',flush=True)
    le=legacy(a,html);pre=preflights(a);methods={'isolatedUnits':u,'inheritedControlledContracts':le,'independentRebuildOutputs':r,'assistedContinuationBrowser':n,'assistedArchitectureBrowser':arch,'assistedBestiaryBrowser':b};total=sum(x['total'] for x in methods.values());need(total==1847 and len(a.shots)==23,'Final assertion/capture sum differs')
    a.add(base/'FINAL_BUILD.json','FINAL_BUILD.json');a.add(Path(__file__),'scripts/collect_continuation.py')
    report={'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),'stage':'complete','ok':True,'html_sha256':html,'frozenProductionHashCount':315,'checksByMethod':methods,'reportedAssertionSum':total,'assertionSumIsNotEquivalentPlaythroughCount':True,'nativePilotCount':3,'captures':a.shots,'sourceIndices':INDICES,'targetedEvidenceExcludedFromAssertionSum':t,'preflightSummary':'PREFLIGHT_SUMMARY.json','historicalDelivery':{'path':'../architecture/ARCHITECTURE_INTEGRATION.json','reportedAssertions':1492,'countedInCurrentSum':False},'scope':'Separate production-unit, controlled legacy, byte-rebuild and assisted native evidence. Targeted facade/world checks already covered in units and baseline/preflight failures are excluded from the assertion sum.','limits':['Metric source footprints do not certify surveyed 1:1 facades/interiors or a complete game. Unrecorded architecture and regional game content are authored fiction.','Native pilots use declared placement, freeze, simulation steps and seeded payment materials; they are not human or citywide playthroughs.','Private ChatGPT conversations are not archived here; only allowlisted QA artifacts are copied.','Raw external network failures and exact cancelled local metadata probes remain visible in original final reports.']}
    a.generated('CONTINUATION_INTEGRATION.json',report)
    a.files['README.md']=(f'# Marseille : prolongement parallèle\n\nHTML gelé : `{html}` ; **315 hashes** revérifiés.\n\n**1 847 contrôles** : 1 080 unités, 434 contrats hérités, 3 sorties de reconstruction identiques, 206 contrôles natifs de lore/armure/collectes, 101 contrôles architecturaux et 23 contrôles du bestiaire. Les méthodes et aides sont séparées dans `CONTINUATION_INTEGRATION.json`. Les 23 captures sont de vrais rendus WebGL, identifiés par SHA et signature PNG.\n\nLes rapports originaux restent intacts. `architecture/ACTUAL_LAYOUT_AUDIT.svg` est un plan dérivé du vrai layout, lié par SHA au JSON et au rapport natif. `facades/` et `world/` conservent leurs preuves ciblées, sans les compter une deuxième fois ; les rejouements en échec sont clairement rangés comme baseline. Les 1 492 contrôles précédents restent historiques dans le dossier voisin `architecture`.\n\n`PREFLIGHT_SUMMARY.json` explique les erreurs de préparation/pilote : helper privé, attente layout2, interpréteur sans dépendance raster, diagnostic annulé et cleanup Playwright. Aucun préflight ni image ratée ne compte comme validation finale ou bug de production établi. Aucun contenu de conversation ChatGPT privé n’est copié.\n\nL’architecture sans relevé reste inventée. Les parcours natifs sont assistés ; ils ne certifient pas toutes les branches, créatures, rues ou pièces de Marseille. Les observations de réseau sont conservées. L’architecture dispose d’une attestation de processus exit0 ; son stdout avait été diffusé par l’outil et les checks/stages restent dans le rapport.\n\nLe collecteur ne lance ni build, navigateur ni test : `python scripts/collect_continuation.py --repo CHEMIN --evidence DOSSIER_QA --check-only`. `--publish` écrit uniquement `verification/expansion/continuation/` après validation. Les hashes de tous les fichiers publiés figurent dans `MANIFEST.json`, hors lui-même.\n').encode()
    a.unchanged()
    if not args.publish: print(json.dumps({'status':'validated without publication','files':len(a.files),'assertions':total,'captures':len(a.shots)}));return 0
    need(not destination.exists(),'Continuation archive already exists; historical proofs are never replaced automatically');destination.parent.mkdir(parents=True,exist_ok=True);staging=Path(tempfile.mkdtemp(prefix='.continuation-stage-',dir=destination.parent))
    try:
        for n,raw in a.files.items():
            q=staging/rel(n);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw);need(sha(q.read_bytes())==sha(raw),'Staging copy differs: '+n)
        manifest={'schemaVersion':1,'html_sha256':html,'selfExcluded':True,'files':{n:{'sha256':sha(raw),'bytes':len(raw)}for n,raw in sorted(a.files.items())}};(staging/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');a.unchanged();os.replace(staging,destination)
    finally:
        if staging.exists():shutil.rmtree(staging)
    for n,s in manifest['files'].items():need(sha((destination/n).read_bytes())==s['sha256'],'Published hash differs: '+n)
    print(json.dumps({'status':'published verified continuation evidence','destination':str(destination),'files':len(a.files)+1,'assertions':total,'captures':len(a.shots),'manifestVerified':True}));return 0
if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,OSError,KeyError,TypeError,ET.ParseError)as e:raise SystemExit('Continuation evidence not published: '+str(e))
