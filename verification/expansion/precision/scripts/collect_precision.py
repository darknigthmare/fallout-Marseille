#!/usr/bin/env python3
"""Recount frozen QA evidence; no tests/build/browser. Default validates only.

--partial writes a pending inventory outside the repository. --publish is the
coordinator's explicit final step, after every required report validates.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import ast
import hashlib
import json
import os
import re
import runpy
import shutil
import tempfile
import urllib.parse

HTML='120e04972fb08a6f59b929d8a0952010712cf3849b8e512c383ff3a8ae87d636'
REPORTS={
 'terrain':'terrain-native/PRECISE_TERRAIN_NATIVE.json',
 'architecture':'architecture-native/ARCHITECTURE_NATIVE.json',
 'interiors':'interiors-native/INTERIOR_PROGRAMS_NATIVE.json',
 'bestiary':'bestiary-native/BESTIARY_NATIVE.json',
 'chems':'chems-native/CHEMS_NATIVE.json',
 'controller':'controller/browser/CONTROLLER_BROWSER.json',
 'legacy':'legacy-final/QA_LEGACY_RUN.json',
 'continuation':'continuation-native/CONTINUATION_NATIVE.json',
}

def need(ok,message):
 if not ok: raise ValueError(message)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def relative(value):
 need(isinstance(value,str) and value and '\\' not in value,'Invalid relative path')
 p=Path(value);need(not p.is_absolute() and '..' not in p.parts,'Unsafe path: '+value);return p

def checked(r,label):
 rows=r.get('checks',r.get('tests'));need(isinstance(rows,list) and rows,label+': missing checks')
 good=sum(x.get('ok') is True for x in rows);bad=len(rows)-good
 need(good==r.get('passed') and bad==r.get('failed') and r.get('total',len(rows))==len(rows),label+': totals do not match actual check rows')
 need(bad==0,label+': failed checks')
 need(not any(r.get(k) for k in ['error','exception','traceback']),label+': error/exception present')
 for key in ['errors','page_errors','javascriptErrors','javascript_console_errors','local_http_errors']:
  need(not r.get(key),label+': '+key)
 return {'passed':good,'failed':0,'total':len(rows)}

class Collection:
 def __init__(self,root,evidence):self.root,self.evidence=root,evidence;self.inputs={};self.files={};self.captures=[]
 def read(self,path):
  p=Path(path);need(p.is_file() and not p.is_symlink(),'Missing/unsafe file: '+str(p));raw=p.read_bytes();h=sha(raw);need(p not in self.inputs or self.inputs[p]==h,'Input changed: '+str(p));self.inputs[p]=h;return raw
 def obj(self,path):
  r=json.loads(self.read(path),parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON '+x)));need(isinstance(r,dict),'Expected object: '+str(path));return r
 def add(self,path,target):
  target=str(relative(target));need(Path(target).suffix.lower() not in ['.tif','.tiff','.f32','.zip'],'Raw raster/archive must not be duplicated: '+target)
  raw=self.read(path);need(target not in self.files or self.files[target]==raw,'Conflicting evidence path: '+target);self.files[target]=raw;return raw
 def generated(self,target,r):self.files[str(relative(target))]=(json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
 def hashes(self,mapping,label):
  need(isinstance(mapping,dict) and mapping,label+': hashes missing')
  for name,h in mapping.items():need(sha(self.read(self.root/relative(name)))==h,label+': changed '+name)
 def unchanged(self):
  for p,h in self.inputs.items():need(p.is_file() and not p.is_symlink() and sha(p.read_bytes())==h,'Input changed during collection: '+str(p))
 def tree(self,folder,target):
  for p in sorted(folder.rglob('*')):
   if p.is_file() and '__pycache__' not in p.parts and p.suffix.lower() not in ['.png','.zip','.tif','.tiff','.f32']:
    self.add(p,target+'/'+str(p.relative_to(folder)))


def frozen(c):
 r=c.obj(c.evidence/'FINAL_BUILD.json');need(r.get('htmlSha256')==HTML and len(r.get('hashes',{}))==403,'Expected coordinated FINAL_BUILD403');c.hashes(r['hashes'],'freeze403')
 need(r['hashes'].get('index.html')==HTML,'Frozen HTML mismatch');c.add(c.evidence/'FINAL_BUILD.json','FINAL_BUILD.json');return r

def units(c):
 folder=c.evidence/'units';r=c.obj(folder/'UNITS.json');need(r.get('stage')=='complete' and r.get('html_sha256')==HTML and r.get('failedProcesses')==0 and not r.get('changedInputs'),'Units incomplete/stale')
 rows=r.get('suites');need(isinstance(rows,list) and len(rows)==30 and len({x['suite'] for x in rows})==30,'Expected30 unit suites');total=sum(x['total'] for x in rows);need(type(r.get('total')) is int and total==r['total'] and total>0,'Unit recomputed sum mismatch')
 c.hashes(r['sourceHashes'],'unit production');c.hashes(r['testScriptHashes'],'unit executed scripts')
 for x in rows:
  need(type(x.get('exitCode')) is int and x['exitCode']==0,'Unit process failure '+x['suite']);raw=c.add(folder/relative(x['log']),'units/'+x['log']);need(sha(raw)==x['logSha256'],'Unit log changed '+x['suite'])
  matches=re.findall(r'Ran (\d+) tests|ℹ tests (\d+)|"passed"\s*:\s*(\d+)',raw.decode());values=[int(next(v for v in group if v)) for group in matches];need(values==[x['total']],'Unit stdout count mismatch '+x['suite'])
  need(not re.search(r'ℹ fail [1-9]|"failed"\s*:\s*[1-9]|FAILED\s*\(',raw.decode()),'Unit stdout failure '+x['suite'])
 for name in r['testScriptHashes']:c.add(c.root/relative(name),'scripts/units/'+name)
 runner=c.add(c.evidence/'verify_units.py','scripts/verify_units.py');need(sha(runner)==r['runner_sha256'],'Unit runner changed');c.add(folder/'UNITS.json','units/UNITS.json');return {'total':total,'passed':total,'failed':0,'processes':30,'method':r['scope']}

def rebuild(c,freeze):
 r=c.obj(c.evidence/'REPRODUCIBLE_BUILD.json');need(r.get('ok') is True and type(r.get('exitCode')) is int and r['exitCode']==0 and len(r.get('files',[]))==3 and not r.get('stderr'),'Rebuild incomplete or process exit missing')
 need({x['path'] for x in r['files']}=={'index.html','JOUER_FALLOUT_MISTRAL_v0.50.html','src/game.js'},'Rebuild outputs missing')
 for x in r['files']:need(x['same'] is True and x['sourceSha256']==x['rebuiltSha256']==freeze['hashes'][x['path']],'Rebuilt bytes differ')
 c.add(c.evidence/'REPRODUCIBLE_BUILD.json','REPRODUCIBLE_BUILD.json');return {'total':3,'passed':3,'failed':0,'method':r['scope'],'unit':'byte-identical output comparisons'}

def closure(c):
 p=c.evidence/'runtime-closure/RUNTIME_CLOSURE.json';r=c.obj(p);out=checked(r,'runtime closure');need(r.get('stage')=='complete' and r.get('html_sha256')==HTML and r.get('exitCode')==0 and out['total']==3,'Runtime closure stale/incomplete');c.hashes(r['sourceHashes'],'closure production')
 runner=c.add(c.evidence/'check_runtime_closure.py','scripts/check_runtime_closure.py');need(sha(runner)==r['runnerSha256'],'Closure runner changed');c.tree(p.parent,'runtime-closure');return {**out,'method':r['scope'],'processes':1}

def independent(c):
 folder=c.evidence/'terrain-independent';r=c.obj(folder/'TERRAIN_INDEPENDENT.json');points=r.get('points');need(isinstance(points,list) and len(points)==r.get('passed')==r.get('expectedPoints')==288 and r.get('failed')==0 and not r.get('failures'),'Independent source comparisons incomplete')
 need(r.get('sourceCount')==12 and len(r.get('sources',[]))==12 and r.get('chunkCount')==48 and len(r.get('chunks',[]))==48,'Independent source/chunk coverage differs')
 for x in points:need(x.get('equal') is True and x['runtimeValue']==x['sourceValue'] and x['runtimeCentre']==x['sourceCentre'],'Independent unequal point')
 for filename,key in [('index.json','indexSha256'),('ACQUISITION.json','acquisitionSha256')]:need(sha(c.read(c.root/'data/map_pack/precise'/filename))==r[key],'Independent '+filename+' changed')
 for x in r['sources']+r['chunks']:
  raw=c.read(x['file']);need(sha(raw)==x['sha256'] and len(raw)==x['bytes'],'Independent source/runtime file changed')
 # The original review predates the final boundary correction; keep it verbatim
 # without presenting its old source-code citation as the final module hash.
 stale=[]
 for x in r.get('rendererSourceReview',[]):
  actual=sha(c.read(c.root/relative(x['file'])))
  if actual!=x['sha256']:stale.append({'file':x['file'],'reviewedSha256':x['sha256'],'finalSha256':actual})
 c.tree(folder,'terrain-independent');return {'countedInAssertionSum':False,'pointComparisons':288,'sourceGeoTIFFs':12,'runtimeChunks':48,'scope':r['scope'],'exhaustiveCellComparison':False,'rawGeoTIFFsIncluded':False,'runtimeRasterDataDuplicated':False,'olderCodeReviewCitations':stale,'olderCodeReviewIsFinalBuildValidation':False}

def exit_proof(c,folder,r,label):
 candidates=[]
 for name in ['process.exit','execution.exit','EXECUTION.exit','exit_code.txt','exit-code.txt','process.exitcode','EXIT_CODE.txt']:
  p=folder/name
  if p.exists():
   code=int(c.read(p).decode().strip());need(code==0,label+': nonzero process exit');c.add(p,label+'/'+name);candidates.append({'file':name,'exitCode':code,'method':'Real process exit recorded by execution wrapper'})
 for name in ['EXECUTION_STATUS.json','execution-status.json','PROCESS_STATUS.json','PROCESS_EXIT.json','EXECUTION_IDENTITY.json','EXECUTION_ATTESTATION.json']:
  p=folder/name
  if p.exists():
   status=c.obj(p);code=status.get('exitCode',status.get('returncode',status.get('process',{}).get('observedExitCode')));need(type(code) is int and code==0,label+': process status not zero');need(status.get('processFinished',True) is True,label+': process unfinished');
   if status.get('htmlSha256'):need(status['htmlSha256']==HTML,label+': status HTML stale')
   for link in status.get('linkedFiles',[]):
    linked=c.read(folder/relative(link['file']));need(sha(linked)==link['sha256'] and len(linked)==link['bytes'],label+': status linked file changed')
   c.add(p,label+'/'+name);candidates.append({'file':name,'exitCode':code,'method':status.get('method','Process status written by the execution wrapper'),'scope':status.get('scope')})
 if type(r.get('exitCode')) is int:need(r['exitCode']==0,label+': report exit notzero');candidates.append({'file':'runtime-report','exitCode':r['exitCode']})
 need(candidates,label+': actual process exit evidence absent');return candidates

def browser(c,key,rel):
 path=c.evidence/relative(rel);folder=path.parent;r=c.obj(path);out=checked(r,key);need(key=='controller' or r.get('stage')=='complete',key+': unfinished stage')
 local_failures=r.get('local_request_failures',[]);allowed=r.get('local_diagnostic_cancellations',[]) if key=='continuation' else []
 if allowed:
  need(local_failures==allowed and all(x.get('failure')=='net::ERR_ABORTED' and x.get('stage')=='native_continue_reload' and urllib.parse.urlsplit(x.get('url','')).path=='/__mistral/local-data' and urllib.parse.urlsplit(x['url']).netloc==urllib.parse.urlsplit(r['url']).netloc for x in allowed),'Unqualified continuation local failure')
 else:need(not local_failures,key+': local request failure')
 pinned=r.get('pinned_inputs',r.get('source_snapshot',{}));html=r.get('html_sha256') or pinned.get('index.html');need(html==HTML,key+': HTML stale/unbound')
 if isinstance(pinned,dict) and pinned:
  need(all(isinstance(h,str) for h in pinned.values()),key+': unsupported source binding');c.hashes(pinned,key+' pinned sources')
 if key!='controller':
  for field in ['html_injected','network_mocked','storage_mocked']:need(r.get(field) is False,key+': method missing/altered '+field)
  method='Assisted native HTTP/canvas/UI/storage pilot; diagnostic navigation/camera/freeze/stepped physics remain declared.'
 else:method='DOM/keyboard/storage browser pilot with SIMULATED Gamepad API and synthetic touch PointerEvent; not physical gamepad hardware validation.'
 identity=c.obj(folder/'EXECUTION_IDENTITY.json') if key=='controller' else None
 if key!='controller':need(isinstance(r.get('assistance'),list) and r['assistance'],key+': missing declared assistance')
 else:need(identity.get('capturedAfterExecution') is True and identity.get('reportSha256')==sha(c.read(path)),key+': controller post-exit identity missing/stale')
 scripts=sorted(folder.glob('EXECUTED*.py')) or sorted(folder.glob('*.executed.py'));need(len(scripts)==1,key+': expected one exact executed script')
 script=c.add(scripts[0],key+'/'+scripts[0].name)
 command_path=folder/'COMMAND.json'
 if command_path.exists():
  command=c.obj(command_path);need(not command.get('executedScriptSha256') or command['executedScriptSha256']==sha(script),key+': command/script mismatch')
 expected=(identity.get('scriptSha256') if identity else None) or r.get('script_sha256',r.get('executed_script_sha256'));need(expected and sha(script)==expected,key+': script identity stale/missing')
 if key=='interiors':
  helpers=r.get('imported_geometry_helpers');need(isinstance(helpers,dict) and len(helpers.get('definitionsSha256',{}))==4,'Interior imported helper identities absent')
  for helper_path in [folder/'architecture_native_browser.imported.py',c.root/relative(helpers['sourcePath'])]:
   tree=ast.parse(c.read(helper_path).decode());actual={n.name:sha(ast.dump(n,include_attributes=False).encode()) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in helpers['definitionsSha256']};need(actual==helpers['definitionsSha256'],'Imported pure helper definitions differ')
 exits=exit_proof(c,folder,r,key);logs=[p for p in folder.iterdir() if p.is_file() and p.suffix=='.log'];need(logs,key+': execution log absent')
 for p in logs:
  log=c.add(p,key+'/'+p.name)
  if identity:need(sha(log)==identity.get('logSha256',identity.get('executionLogSha256')),key+': controller log identity mismatch')
 shots=r.get('shots',r.get('screenshots',[]));need(isinstance(shots,list) and (key=='controller' or shots),key+': capture list absent')
 for x in shots:
  name=x.get('file',x.get('path'));p=relative(name);need(p.suffix.lower()=='.png',key+': nonPNG capture');raw=c.add(folder/p,key+'/'+str(p));need(raw.startswith(b'\x89PNG\r\n\x1a\n') and sha(raw)==x['sha256'],key+': capture SHA/PNG differs');c.captures.append({'path':key+'/'+str(p),'sha256':sha(raw),'html_sha256':HTML,'label':x.get('label'),'method':method})
 c.tree(folder,key)
 return {**out,'method':method,'assistance':r.get('assistance', [r['scope']]),'scriptIdentityCapturedAfterExecution':key=='controller','actualProcessExits':exits,'captures':len(shots),'sourceReport':key+'/'+path.name,'localDiagnosticCancellations':allowed,'unqualifiedLocalRequestFailures':0,'networkObservations':{name:r.get(name,[]) for name in ['external_request_failures','request_failures','resource_console_diagnostics']}}

def legacy(c,rel):
 path=c.evidence/relative(rel);r=c.obj(path);detail_folder=c.evidence/'legacy-game/verification/v050/legacy';audit=c.obj(path.parent/'RUN_AUDIT.json');need(audit.get('passed') is True and audit.get('checker_exit_code')==0 and all(v is True for v in audit.get('checks',{}).values()),'Legacy execution audit failed');need(r.get('html_sha256')==HTML and r.get('allHtmlMatch') is True,'Legacy HTML stale');suites,processes=r.get('suites'),r.get('processes');need(isinstance(suites,list) and len(suites)==15 and len(processes)==15,'Legacy15 processes incomplete');need(len({x['test'] for x in suites})==15 and {x['test'] for x in suites}=={x['test'] for x in processes},'Legacy identities mismatch')
 need(all(type(x.get('exitCode')) is int and x['exitCode']==0 for x in processes),'Legacy failed processes');need(sum(x['total'] for x in suites)==r.get('total')==r.get('passed')==434 and r.get('failed')==0,'Legacy totals mismatch');need(not r.get('javascriptErrors'),'LegacyJSerrors')
 adapter=runpy.run_path(str(c.root/'tools/check_v050.py'));adaptations={x['test']:x for x in r['adaptations']};need(len(adaptations)==15,'Legacy adaptation bindings missing')
 for x in suites:
  detail=c.obj(detail_folder/relative(x['file']));totals=checked(detail,'legacy/'+x['test']);need(totals['total']==x['total'] and x.get('sameHtml') is True,'Legacy detail mismatch')
  source=c.read(c.root/'tests/v049'/relative(x['test']));executed=adapter['adapt'](x['test'],source.decode()).encode();binding=adaptations[x['test']];need(sha(source)==binding['sourceSha256'] and sha(executed)==binding['executedSha256'],'Legacy executed script mismatch');c.files['legacy/source-scripts/'+x['test']]=source;c.files['legacy/executed-scripts/'+x['test']]=executed
 for source,spec in audit['sources_after'].items():
  raw=c.read(source);need(sha(raw)==spec['sha256'] and len(raw)==spec['bytes'],'Legacy audited source changed')
 need(len(audit['outputs'])==31,'Legacy expected31 fresh output files')
 for source,spec in audit['outputs'].items():
  raw=c.read(source);need(sha(raw)==spec['sha256'] and len(raw)==spec['bytes'] and audit['started_ns']<=spec['mtime_ns']<=audit['finished_ns'],'Legacy output changed/not fresh')
 c.tree(path.parent,'legacy/run');c.tree(detail_folder,'legacy/reports');c.add(c.root/'tools/check_v050.py','scripts/check_v050.py');c.add(c.root/'tools/check_v049.py','scripts/check_v049.py');return {'passed':434,'failed':0,'total':434,'processes':15,'method':r['scope'],'adaptedExecutedBytesRecreatedAndMatched':True}

def histories(c,final_dirs):
 out=[]
 history_dirs=list(c.evidence.iterdir())
 for parent in ['controller','legacy-final']:
  if (c.evidence/parent).is_dir():history_dirs+=list((c.evidence/parent).iterdir())
 for folder in sorted(history_dirs):
  if not folder.is_dir() or folder in final_dirs or not any(x in folder.name for x in ['attempt','first-run','second-run','third-run','failed','aborted','5e6895ac']):continue
  history_name=str(folder.relative_to(c.evidence)).replace('/','__')
  reports=[]
  for p in folder.glob('*.json'):
   try:r=c.obj(p)
   except (ValueError,json.JSONDecodeError):continue
   if 'checks' in r or 'failed' in r:reports.append({'report':p.name,'stage':r.get('stage'),'passed':r.get('passed'),'failed':r.get('failed'),'exception':r.get('exception')})
  if '5e6895ac' in folder.name:
   # Keep obsolete build trees outside current proof publication. Archive only
   # their shallow execution receipts, never their old source/data tree.
   for item in folder.iterdir():
    if item.is_file() and item.suffix in ['.json','.log','.py','.exit','.txt']:c.add(item,'historical/'+history_name+'/'+item.name)
  else:c.tree(folder,'historical/'+history_name)
  out.append({'directory':'historical/'+history_name,'reports':reports,'countedInAssertionSum':False,'failedImagesUsedAsFinalEvidence':False,'capturesArchived':False})
 return out


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,default=Path('/workspace/fallout-Marseille'));p.add_argument('--evidence',type=Path,default=Path(__file__).parent);p.add_argument('--output',type=Path);p.add_argument('--report',action='append',default=[],help='Override final report: key=relative/path.json');mode=p.add_mutually_exclusive_group();mode.add_argument('--partial',action='store_true');mode.add_argument('--publish',action='store_true');p.add_argument('--replace',action='store_true');a=p.parse_args();c=Collection(a.repo.resolve(),a.evidence.resolve());reports=REPORTS.copy()
 for value in a.report:key,name=value.split('=',1);need(key in REPORTS or key=='continuation','Unknown report key');reports[key]=str(relative(name))
 statuses={};results={};frozen_build=None
 tasks=[('frozen403',lambda:frozen(c)),('units',lambda:units(c)),('rebuild',lambda:rebuild(c,frozen_build)),('runtimeClosure',lambda:closure(c)),('independentTerrain',lambda:independent(c))]+[(key,(lambda k=key,r=rel:legacy(c,r) if k=='legacy' else browser(c,k,r))) for key,rel in reports.items()]
 for key,fn in tasks:
  try:
   result=fn();statuses[key]={'status':'validated','result':result}
   if key=='frozen403':frozen_build=result
   else:results[key]=result
  except (OSError,ValueError,TypeError,KeyError,AssertionError) as error:statuses[key]={'status':'pending-or-invalid','reason':str(error)}
 pending={k:v for k,v in statuses.items() if v['status']!='validated'};summary={'status':'partial' if pending else 'validated','published':False,'html_sha256':HTML,'reports':statuses,'pending':list(pending),'filesPrepared':len(c.files),'captureCount':len(c.captures)}
 if a.partial:
  (c.evidence/'PARTIAL_VALIDATION.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='reports'},ensure_ascii=False));return 0
 need(not pending,'Incomplete evidence: '+json.dumps(pending,ensure_ascii=False));c.unchanged()
 histories_result=histories(c,{(c.evidence/rel).parent for rel in reports.values()});c.add(Path(__file__).resolve(),'scripts/collect_precision.py')
 now=datetime.now(timezone.utc).isoformat();counted={k:v for k,v in results.items() if k!='independentTerrain'}
 integration={'schemaVersion':1,'createdAt':now,'stage':'complete','ok':True,'html_sha256':HTML,'allHtmlMatch':True,'completeGameOrOneToOneWorldClaimed':False,'scope':'Distinct assertion methods and assisted pilots; their arithmetic sum is not an equivalent number of gameplay sessions.','checksByMethod':counted,'reportedAssertionSum':sum(x['total'] for x in counted.values()),'assertionSumIsNotEquivalentPlaythroughCount':True,'sourceComparisonsExcludedFromAssertionSum':results['independentTerrain'],'historicalReportsExcludedFromAssertionSum':histories_result,'correctedProductionDefects':[{'module':'14_precise_terrain','problem':'Native patch at coverage borders removed coarse terrain outside supported fine cells; corrected by bounding native coverage before cutout.','currentEvidence':['units/precise_terrain.cjs.log','terrain/PRECISE_TERRAIN_NATIVE.json']},{'module':'13_regional_bestiary','problem':'Airborne admission incorrectly applied a walking elevation test above sloping terrain; corrected airborne free-volume admission.','currentEvidence':['units/regional_bestiary.cjs.log','bestiary/BESTIARY_NATIVE.json']}],'supersededHarnessAndPreparationFailures':['Theoretical camera/portal candidates and canonical-offset pilot selection','Whole-helper-file pinning while another pilot main changed, with unchanged imported pure definitions','Gameplay input attempted before the real equipment cooldown ended','QA data symlinks/copy destinations rejected by the precise-data containment helper','Unsafe unattended town wait and a Playwright cleanup after its event loop stopped'],'older1847HistoricalAssertionsIncluded':False,'frozenProduction':frozen_build,'captures':c.captures,'limits':['Native LiDAR coverage is 12 km² at a 0.5 m source grid, not all Marseille.','Façades and coherent generated interiors remain invented unless a particular document is explicitly attributed.','Gamepad API and touch pilot are simulated input tests; no hardware test is claimed.','Raw GeoTIFFs remain in the external acquisition cache; no raw TIFF, raster chunk or existing 150MB data ZIP is duplicated in this evidence tree.','Failed attempts are preserved as scripts/reports/logs, excluded from sums; their images are not final evidence.'],'inputHashes':{str(p):h for p,h in c.inputs.items()}}
 c.generated('PRECISION_INTEGRATION.json',integration)
 lines=['# Précision Marseille : preuves de validation','',f'HTML de production : `{HTML}`. Rapports et scripts exécutés copiés exactement.','']
 for key,r in counted.items():lines.append(f'- {key} : **{r["total"]} contrôles**, méthode : {r["method"]}')
 lines+=['',f'Somme descriptive recomptée : **{integration["reportedAssertionSum"]} contrôles**, avec **{len(c.captures)} captures finales**. Cette somme ne mesure pas un nombre de parties.', '', 'Les défauts de production corrigés sont distincts des échecs de pilotage : le découpage du terrain aux bords de couverture (14) et l’admission des acteurs volants au-dessus des pentes (13) sont attestés par les tests et pilotes finaux. Les anciens problèmes de cibles caméra, de liaison de helpers, de délai après équipement et de copie des données QA restent décrits dans les rapports historiques. Aucune capture d’une tentative échouée ne figure dans les captures finales.', '', 'Les 288 comparaisons de cellules indépendantes, les anciennes 1847 assertions et les tentatives échouées sont exclues de cette somme. Les totaux distinguent modèles contrôlés, contrats hérités, octets, HTTP et parcours assistés ; ils ne comptent pas des parties équivalentes.','',*integration['limits'],'','Le manifeste SHA-256 exclut seulement son propre fichier. Les captures finales PNG sont liées par SHA au rapport et au HTML. `scripts/collect_precision.py` ne lance aucun jeu, navigateur, acquisition ou build. La publication exige `--publish` après validation complète.']
 c.files['README.md']=('\n'.join(lines)+'\n').encode();c.unchanged()
 if not a.publish:print(json.dumps({'status':'validated without publication','files':len(c.files),'sum':integration['reportedAssertionSum'],'methods':{k:r['total'] for k,r in counted.items()}},ensure_ascii=False));return 0
 destination=(a.output or c.root/'verification/expansion/precision').resolve();need(destination!=c.root and not destination.is_relative_to(c.evidence),'Unsafe destination');need(not destination.exists() or a.replace,'Destination exists; --replace required');destination.parent.mkdir(parents=True,exist_ok=True);staging=Path(tempfile.mkdtemp(prefix='.precision-stage-',dir=destination.parent));backup=None
 try:
  for name,raw in c.files.items():target=staging/relative(name);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);need(sha(target.read_bytes())==sha(raw),'Staging mismatch')
  manifest={'schemaVersion':1,'createdAt':now,'html_sha256':HTML,'selfExcluded':True,'files':{name:{'sha256':sha(raw),'bytes':len(raw)} for name,raw in sorted(c.files.items())}};(staging/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');c.unchanged()
  if destination.exists():backup=Path(tempfile.mkdtemp(prefix='.precision-old-',dir=destination.parent));backup.rmdir();os.replace(destination,backup)
  os.replace(staging,destination)
  if backup:shutil.rmtree(backup)
 except Exception:
  if backup and backup.exists() and not destination.exists():os.replace(backup,destination)
  raise
 finally:
  if staging.exists():shutil.rmtree(staging)
 print(json.dumps({'status':'published','path':str(destination),'files':len(c.files)+1,'sum':integration['reportedAssertionSum']},ensure_ascii=False));return 0

if __name__=='__main__':
 try:raise SystemExit(main())
 except (OSError,ValueError,KeyError,TypeError) as error:raise SystemExit('Precision evidence not published: '+str(error))
