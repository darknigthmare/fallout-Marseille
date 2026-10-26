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

HTML='ed6e4103b23a45c413fef182862a93accb72ec25c6e1d8b101251822bfd5c670'

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
 for key in ['errors','page_errors','javascriptErrors','javascript_console_errors','local_http_errors','http_errors']:
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
 r=c.obj(c.evidence/'FINAL_BUILD.json');need(r.get('htmlSha256')==HTML and len(r.get('hashes',{}))==405,'Expected coordinated FINAL_BUILD405');c.hashes(r['hashes'],'freeze405')
 need(r['hashes'].get('index.html')==HTML,'Frozen HTML mismatch');c.add(c.evidence/'FINAL_BUILD.json','FINAL_BUILD.json');return r

def units(c):
 folder=c.evidence/'units';r=c.obj(folder/'UNITS.json');need(r.get('stage')=='complete' and r.get('html_sha256')==HTML and r.get('failedProcesses')==0 and not r.get('changedInputs'),'Units incomplete/stale')
 rows=r.get('suites');need(isinstance(rows,list) and len(rows)==34 and len({x['suite'] for x in rows})==34,'Expected34 unit suites');total=sum(x['total'] for x in rows);need(type(r.get('total')) is int and total==r['total'] and total>0,'Unit recomputed sum mismatch')
 c.hashes(r['sourceHashes'],'unit production');c.hashes(r['testScriptHashes'],'unit executed scripts')
 for x in rows:
  need(type(x.get('exitCode')) is int and x['exitCode']==0,'Unit process failure '+x['suite']);raw=c.add(folder/relative(x['log']),'units/'+x['log']);need(sha(raw)==x['logSha256'],'Unit log changed '+x['suite'])
  matches=re.findall(r'Ran (\d+) tests|ℹ tests (\d+)|"passed"\s*:\s*(\d+)',raw.decode());values=[int(next(v for v in group if v)) for group in matches];need(values==[x['total']],'Unit stdout count mismatch '+x['suite'])
  need(not re.search(r'ℹ fail [1-9]|"failed"\s*:\s*[1-9]|FAILED\s*\(',raw.decode()),'Unit stdout failure '+x['suite'])
 if r.get('rerunEvidence'):
  rerun=r['rerunEvidence'];previous=c.obj(c.evidence/relative(rerun['priorDirectory'])/'UNITS.json')
  need(sha(c.read(c.evidence/relative(rerun['priorDirectory'])/'UNITS.json'))==rerun['priorReportSha256'],'Original units report changed')
  need(previous['sourceHashes']==r['sourceHashes'] and previous['testScriptHashes']==r['testScriptHashes'] and not previous['changedInputs'],'Rerun inputs differ')
  oldrows={x['suite']:x for x in previous['suites']};attempts={x['suite']:x for x in rerun['attempts']}
  need(set(attempts)=={'source_tools','architecture_sources.cjs'},'Unexpected unit reruns')
  for row in rows:
   if row['suite'] in attempts:
    a=attempts[row['suite']];need(a['previous']==oldrows[row['suite']] and a['previous']['exitCode']==1 and a['successful']==row,'Rerun receipts differ')
   else:need(row==oldrows[row['suite']] and row['exitCode']==0,'Previously passing unit process replaced')
  raw=c.add(c.evidence/'rerun_failed_units.py','scripts/rerun_failed_units.py');need(sha(raw)==rerun['runnerSha256'],'Actual unit rerun wrapper changed')
  c.add(c.evidence/'UNITS_RERUN_EXECUTION.log','units/UNITS_RERUN_EXECUTION.log')
 for name in r['testScriptHashes']:c.add(c.root/relative(name),'scripts/units/'+name)
 runner=c.add(c.root/'tools/check_expansion.py','scripts/check_expansion.py');need(sha(runner)==r['runner_sha256'],'Unit runner changed');c.add(folder/'UNITS.json','units/UNITS.json');return {'total':total,'passed':total,'failed':0,'processes':34,'method':r['scope']}

def rebuild(c,freeze):
 r=c.obj(c.evidence/'REPRODUCIBLE_BUILD.json');need(r.get('ok') is True and type(r.get('exitCode')) is int and r['exitCode']==0 and len(r.get('files',[]))==3 and not r.get('stderr'),'Rebuild incomplete or process exit missing')
 need({x['path'] for x in r['files']}=={'index.html','JOUER_FALLOUT_MISTRAL_v0.50.html','src/game.js'},'Rebuild outputs missing')
 for x in r['files']:need(x['same'] is True and x['sourceSha256']==x['rebuiltSha256']==freeze['hashes'][x['path']],'Rebuilt bytes differ')
 c.add(c.evidence/'REPRODUCIBLE_BUILD.json','REPRODUCIBLE_BUILD.json');return {'total':3,'passed':3,'failed':0,'method':r['scope'],'unit':'byte-identical output comparisons'}

def closure(c):
 p=c.evidence/'runtime-closure/RUNTIME_CLOSURE.json';r=c.obj(p);out=checked(r,'runtime closure');need(r.get('stage')=='complete' and r.get('html_sha256')==HTML and r.get('exitCode')==0 and out['total']==3,'Runtime closure stale/incomplete');c.hashes(r['sourceHashes'],'closure production')
 runner=c.add(c.evidence/'check_runtime_closure.py','scripts/check_runtime_closure.py');need(sha(runner)==r['runnerSha256'],'Closure runner changed');c.tree(p.parent,'runtime-closure');return {**out,'method':r['scope'],'processes':1}


def command_receipt(value,label,script_sha=None):
 if isinstance(value,dict):
  declared=value.get('executedScriptSha256',value.get('script_sha256'))
  if declared and script_sha:need(declared==script_sha,label+': command/script mismatch')
  args=value.get('argv',value.get('command'))
 else:args=value
 need(isinstance(args,list) and args and all(isinstance(x,str) for x in args),label+': exact argv missing')
 flag='--expected-html-sha256' if label=='controller' else '--expect-html-sha'
 need(flag in args and args.index(flag)+1<len(args) and args[args.index(flag)+1]==HTML,label+': command HTML stale/missing')
 return args

def qualify_network(r,label):
 origins=set()
 if r.get('url'):origins.add(urllib.parse.urlsplit(r['url']).netloc)
 for item in r.get('responses',r.get('http_responses',[])):
  u=urllib.parse.urlsplit(item.get('url',''))
  if u.path=='/index.html' and item.get('status')==200:origins.add(u.netloc)
 fields=['local_request_failures','local_geographic_request_failures','request_failures','external_request_failures']
 local={};external={}
 for field in fields:
  for item in r.get(field,[]):
   need(isinstance(item,dict) and isinstance(item.get('url'),str),label+': unsupported network record')
   u=urllib.parse.urlsplit(item['url']);key=json.dumps(item,sort_keys=True)
   is_local=field.startswith('local_') or u.hostname in ['127.0.0.1','localhost','::1'] or u.netloc in origins
   (local if is_local else external)[key]=item
 declared=r.get('expected_local_cancellations',[])
 for item in declared:need(json.dumps(item,sort_keys=True) in local,label+': declared cancellation not observed')
 for item in r.get('local_diagnostic_cancellations',[]):need(json.dumps(item,sort_keys=True) in local,label+': diagnostic cancellation not observed')
 declared_keys={json.dumps(x,sort_keys=True) for x in declared};allowed=[];unknown=[]
 for identity,item in local.items():
  u=urllib.parse.urlsplit(item['url']);same=u.netloc in origins and u.hostname in ['127.0.0.1','localhost','::1'];aborted=item.get('failure')=='net::ERR_ABORTED'
  metadata=same and aborted and u.path=='/__mistral/local-data'
  source_cancel=label=='terrain' and same and aborted and item.get('stage')=='cancel_source_load' and identity in declared_keys and u.path.startswith('/data/map_pack/') and u.path.endswith('.pbf')
  if metadata or source_cancel:allowed.append({'record':item,'kind':'metadata-only cancellation' if metadata else 'declared source-load cancellation','phaseCaptured':bool(item.get('stage'))})
  else:unknown.append(item)
 need(not unknown,label+': unqualified local request failures '+json.dumps(unknown))
 return {'localDiagnosticCancellations':[x['record'] for x in allowed],'qualifiedLocalCancellations':allowed,'unqualifiedLocalRequestFailures':len(unknown),'externalFailureCount':len(external),'qualification':'Actual raw schemas are merged without dropping local records. Only same-origin metadata ERR_ABORTED or a declared PBF cancel_source_load cancellation is qualified. Missing event phases remain explicitly unrecorded.'}


def exit_proof(c,folder,r,label):
 candidates=[]
 for name in ['process.exit','execution.exit','EXECUTION.exit','exit_code.txt','exit-code.txt','process.exitcode','EXIT_CODE.txt']:
  p=folder/name
  if p.exists():
   code=int(c.read(p).decode().strip());need(code==0,label+': nonzero process exit');c.add(p,label+'/'+name);candidates.append({'file':name,'exitCode':code,'method':'Real process exit recorded by execution wrapper'})
 for name in ['EXECUTION_STATUS.json','execution-status.json','PROCESS_STATUS.json','PROCESS_EXIT.json','EXECUTION_IDENTITY.json','EXECUTION_ATTESTATION.json']:
  p=folder/name
  if p.exists():
   status=c.obj(p);code=status.get('exitCode',status.get('exit_code',status.get('returncode',status.get('actual_process_exit_code',status.get('process',{}).get('observedExitCode')))));need(type(code) is int and code==0,label+': process status not zero');need(status.get('processFinished',True) is True,label+': process unfinished');
   if status.get('htmlSha256') or status.get('html_sha256'):need(status.get('htmlSha256',status.get('html_sha256'))==HTML,label+': status HTML stale')
   declared_script=status.get('scriptSha256',status.get('script_sha256'))
   if declared_script and r.get('script_sha256'):need(declared_script==r['script_sha256'],label+': status script differs')
   if status.get('command') or status.get('argv'):command_receipt(status,label,r.get('script_sha256'))
   declared_log=status.get('logSha256',status.get('log_sha256',status.get('executionLogSha256')))
   if declared_log:need(any(sha(c.read(p))==declared_log for p in folder.glob('*.log')),label+': status log SHA differs')
   for link in status.get('linkedFiles',[]):
    linked=c.read(folder/relative(link['file']));need(sha(linked)==link['sha256'] and len(linked)==link['bytes'],label+': status linked file changed')
   c.add(p,label+'/'+name);candidates.append({'file':name,'exitCode':code,'method':status.get('method','Process status written by the execution wrapper'),'scope':status.get('scope')})
 if type(r.get('exitCode')) is int:need(r['exitCode']==0,label+': report exit notzero');candidates.append({'file':'runtime-report','exitCode':r['exitCode']})
 need(candidates,label+': actual process exit evidence absent');return candidates

def browser(c,key,rel):
 path=c.evidence/relative(rel);folder=path.parent;r=c.obj(path);out=checked(r,key);need(key=='controller' or r.get('stage')=='complete',key+': unfinished stage')
 network=qualify_network(r,key);allowed=network['localDiagnosticCancellations']
 pinned=r.get('pinned_inputs',r.get('source_snapshot',{}));html=r.get('html_sha256') or pinned.get('index.html');need(html==HTML,key+': HTML stale/unbound')
 if isinstance(pinned,dict) and pinned:
  need(all(isinstance(h,str) for h in pinned.values()),key+': unsupported source binding');c.hashes(pinned,key+' pinned sources')
 if key!='controller':
  for field in ['html_injected','network_mocked','storage_mocked']:need(r.get(field) is False,key+': method missing/altered '+field)
  method='Assisted native HTTP/canvas/UI/storage pilot; diagnostic navigation/camera/freeze/stepped physics remain declared.'
 else:method='DOM/keyboard/storage browser pilot with SIMULATED Gamepad API and synthetic touch PointerEvent; not physical gamepad hardware validation.'
 identity=c.obj(folder/'EXECUTION_IDENTITY.json') if key=='controller' else None
 if identity and identity.get('sourceHashes'):c.hashes(identity['sourceHashes'],'controller exact inputs')
 if key!='controller':need(isinstance(r.get('assistance'),list) and r['assistance'],key+': missing declared assistance')
 else:need(identity.get('capturedAfterExecution') is True and identity.get('reportSha256')==sha(c.read(path)),key+': controller post-exit identity missing/stale')
 all_scripts=sorted(set(folder.glob('EXECUTED*.py'))|set(folder.glob('*.executed.py'))|set(folder.glob('executed_*.py')));expected_script=r.get('script_sha256',r.get('executed_script_sha256'));scripts=[p for p in all_scripts if not expected_script or sha(c.read(p))==expected_script];need(len(scripts)==1,key+': expected one exact executed primary script')
 script=c.add(scripts[0],key+'/'+scripts[0].name)
 command_path=folder/'COMMAND.json'
 if command_path.exists():
  command=json.loads(c.read(command_path));command_receipt(command,key,sha(script))
 expected=(identity.get('scriptSha256') if identity else None) or r.get('script_sha256',r.get('executed_script_sha256'));need(expected and sha(script)==expected,key+': script identity stale/missing')
 if key=='interiors':
  helpers=r.get('imported_geometry_helpers');need(isinstance(helpers,dict) and len(helpers.get('definitionsSha256',{}))==4,'Interior imported helper identities absent')
  for helper_path in [folder/'architecture_native_browser.imported.py',c.root/relative(helpers['sourcePath'])]:
   tree=ast.parse(c.read(helper_path).decode());actual={n.name:sha(ast.dump(n,include_attributes=False).encode()) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in helpers['definitionsSha256']};need(actual==helpers['definitionsSha256'],'Imported pure helper definitions differ')
 exits=exit_proof(c,folder,r,key);logs=[p for p in folder.iterdir() if p.is_file() and p.suffix=='.log'];need(logs,key+': execution log absent')
 for p in logs:
  log=c.add(p,key+'/'+p.name)
  if identity:need(sha(log)==identity.get('logSha256',identity.get('executionLogSha256')),key+': controller log identity mismatch')
 printed=['OK '+x['name'] for x in r.get('checks',r.get('tests',[]))];need(any([line for line in c.read(p).decode().splitlines() if line.startswith('OK ')]==printed for p in logs),key+': actual stdout check sequence differs')
 shots=r.get('shots',r.get('screenshots',[]));need(isinstance(shots,list) and (key=='controller' or shots),key+': capture list absent')
 for x in shots:
  name=x.get('file',x.get('path'));p=relative(name);need(p.suffix.lower()=='.png',key+': nonPNG capture');raw=c.add(folder/p,key+'/'+str(p));need(raw.startswith(b'\x89PNG\r\n\x1a\n') and sha(raw)==x['sha256'],key+': capture SHA/PNG differs');c.captures.append({'path':key+'/'+str(p),'sha256':sha(raw),'html_sha256':HTML,'label':x.get('label'),'method':method})
 c.tree(folder,key)
 return {**out,'method':method,'assistance':r.get('assistance', [r['scope']]),'scriptIdentityCapturedAfterExecution':key=='controller','actualProcessExits':exits,'captures':len(shots),'sourceReport':key+'/'+path.name,'localDiagnosticCancellations':allowed,'unqualifiedLocalRequestFailures':network['unqualifiedLocalRequestFailures'],'networkQualification':network,'networkObservations':{name:r.get(name,[]) for name in ['external_request_failures','request_failures','resource_console_diagnostics']}}

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



REPORTS={
 'terrain':'world/native/PRECISE_TERRAIN_NATIVE.json',
 'architecture':'facades/native/ARCHITECTURE_NATIVE.json',
 'interiors':'interiors/native/INTERIOR_PROGRAMS_NATIVE.json',
 'bestiary':'bestiary/native/BESTIARY_NATIVE.json',
 'factions':'lore/native/FACTION_DOSSIERS_NATIVE.json',
 'ordnance':'ordnance/native/ORDNANCE_NATIVE.json',
 'continuation':'continuation-native/CONTINUATION_NATIVE.json',
 'chems':'chems-native/CHEMS_NATIVE.json',
 'controller':'controller/browser/CONTROLLER_BROWSER.json',
}

def prior_attempts(c):
 output=[]
 roots=[c.evidence]+[c.evidence/n for n in ['world','facades','interiors','bestiary','lore','ordnance','controller']]
 for parent in roots:
  if not parent.is_dir():continue
  for folder in sorted(parent.iterdir()):
   if not folder.is_dir() or not any(s in folder.name for s in ['attempt','interrupted','superseded','bdf82']):continue
   target='historical/'+str(folder.relative_to(c.evidence)).replace('/','__')
   reports=[]
   for path in folder.rglob('*.json'):
    if any(x in path.parts for x in ['data','src','__pycache__']):continue
    try:r=c.obj(path)
    except (ValueError,json.JSONDecodeError):continue
    if 'checks' in r or 'failed' in r:reports.append({'file':str(path.relative_to(folder)),'stage':r.get('stage'),'passed':r.get('passed'),'failed':r.get('failed'),'html_sha256':r.get('html_sha256')})
   c.tree(folder,target)
   output.append({'directory':target,'reports':reports,'countedInAssertionSum':False,'capturesArchivedAsFinal':False})
 return output

def main():
 p=argparse.ArgumentParser(description='Validate exact current continuation evidence; publication only with --publish.')
 p.add_argument('--repo',type=Path,default=Path('/workspace/fallout-Marseille'))
 p.add_argument('--evidence',type=Path,default=Path(__file__).parent)
 p.add_argument('--output',type=Path)
 modes=p.add_mutually_exclusive_group();modes.add_argument('--partial',action='store_true');modes.add_argument('--publish',action='store_true')
 a=p.parse_args();c=Collection(a.repo.resolve(),a.evidence.resolve());statuses={};results={};freeze=None
 tasks=[('frozen405',lambda:frozen(c)),('units',lambda:units(c)),('rebuild',lambda:rebuild(c,freeze)),('runtimeClosure',lambda:closure(c)),('legacy',lambda:legacy(c,'legacy-final/QA_LEGACY_RUN.json'))]+[(key,lambda k=key,rel=rel:browser(c,k,rel)) for key,rel in REPORTS.items()]
 for key,fn in tasks:
  try:
   result=fn();statuses[key]={'status':'validated','result':result}
   if key=='frozen405':freeze=result
   else:results[key]=result
  except (OSError,ValueError,TypeError,KeyError,AssertionError) as error:statuses[key]={'status':'pending-or-invalid','reason':str(error)}
 pending={k:v for k,v in statuses.items() if v['status']!='validated'}
 summary={'status':'partial' if pending else 'validated','published':False,'html_sha256':HTML,'reports':statuses,'pending':pending,'filesPrepared':len(c.files),'captureCount':len(c.captures)}
 if a.partial:
  (c.evidence/'PARTIAL_VALIDATION.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='reports'},ensure_ascii=False));return 0
 need(not pending,'Incomplete evidence: '+json.dumps(pending,ensure_ascii=False));c.unchanged()
 attempts=prior_attempts(c);c.add(Path(__file__),'scripts/collect_next.py')
 for name in ['UNIT_EXECUTION_STATUS.json','UNITS_EXECUTION.log','run_existing_native.py','RUNTIME_CLOSURE_EXECUTION_STATUS.json']:
  if (c.evidence/name).exists():c.add(c.evidence/name,name)
 # Independent source snapshots and bounded CPU probes are measurements, not
 # additional gameplay assertions, and remain outside the arithmetic sum.
 measurements=[]
 for owner,name in [('world','ROAD_CPU_PROBE.json'),('world','ORDNANCE_GEOMETRY_REVIEW.json'),('interiors','DOCUMENTARY_LEGACY_COMPARISON.json'),('bestiary','NATIVE_ATTEMPTS_COMPARISON.json'),('bestiary','MARGIN_DIAGNOSTIC_BEFORE.json'),('bestiary','MARGIN_DIAGNOSTIC_AFTER.json'),('lore/scout','SOURCE_WATER_PROBE.json')]:
  path=c.evidence/owner/name
  if path.exists():c.add(path,'measurements/'+owner+'/'+name);measurements.append('measurements/'+owner+'/'+name)
 now=datetime.now(timezone.utc).isoformat()
 integration={'schemaVersion':1,'createdAt':now,'stage':'complete','ok':True,'html_sha256':HTML,'allHtmlMatch':True,'completeGameOrOneToOneWorldClaimed':False,'scope':'Current frozen program: distinct model, historical-contract, byte/HTTP, assisted native and simulated input methods. Arithmetic sum does not represent equivalent gameplay sessions.','checksByMethod':results,'reportedAssertionSum':sum(r['total'] for r in results.values()),'assertionSumIsNotEquivalentPlaythroughCount':True,'frozenProduction':freeze,'captures':c.captures,'measurementsExcludedFromAssertionSum':measurements,'historicalReportsExcludedFromAssertionSum':attempts,'previous2324AssertionsIncluded':False,'previous288SourceCellComparisonsIncluded':False,'correctedIntegrationDefects':['Grenade identity bound to actual building/floor or expedition site, with persistence.','Eight-button HUD now fits desktop and small viewport.','No-world/empty-grenade queries remain safe at menu.','Grenade collisions use actual measured roof/deck geometry and active interior ceiling instead of an empty or broad envelope.','The new Syndicat host is an existing physically verified land relay; catalogue coordinates and the two actual landmarks remain unchanged.','Known bestiary bodies retain full collision radius and four source-ground/water/height checks; extra creation clearance is not reapplied during restoration or walking.'],'limits':['All-Marseille surveyed visual/interior1:1 is not certified; unsupported architectural details and interior doors remain invented.','Native0.5m LiDAR covers12km² central Marseille, no new source extent acquired in this iteration.','Road refinement uses finite probes, a1m minimum edge and declared budgets; no continuous4cm guarantee.','Native browser pilots use declared scene selection, camera placement and controlled stepping; not human unassisted citywide playthroughs.','Gamepad API is simulated; no physical hardware certification.','Grenades preserve the historical invulnerability of civilian NPCs/companions and the historical last-alive-save death rule.','Older-build, failed and interrupted attempts remain separate, excluded from current sums and final captures.'],'inputHashes':{str(p):h for p,h in c.inputs.items()}}
 c.generated('WASTELAND_INTEGRATION.json',integration)
 lines=['# Marseille et systèmes du Wasteland — preuves du 26 octobre 2026','',f'HTML courant : `{HTML}`. Rapports, journaux et scripts exécutés copiés sans retouche.','']
 for key,r in results.items():lines.append(f'- {key} : **{r["total"]} contrôles**. {r["method"]}')
 lines+=['',f'Somme descriptive : **{integration["reportedAssertionSum"]} contrôles**, **{len(c.captures)} captures finales**, **{len(freeze["hashes"])} empreintes de production**. Les méthodes se chevauchent et ne représentent pas autant de parties.','',*integration['limits'],'','Les 2 324 contrôles et 288 comparaisons de cellules de la livraison 3d94e4c restent historiques. Les tentatives visant un ancien HTML, interrompues ou échouées ne participent pas au total. Le manifeste exclut seulement son propre fichier.']
 c.files['README.md']=('\n'.join(lines)+'\n').encode();c.unchanged()
 if not a.publish:print(json.dumps({'status':'validated without publication','methods':{k:v['total'] for k,v in results.items()},'sum':integration['reportedAssertionSum'],'captures':len(c.captures),'files':len(c.files)},ensure_ascii=False));return 0
 destination=(a.output or c.root/'verification/expansion/wasteland').resolve();need(not destination.exists(),'Destination already exists; do not overwrite historical proof');need(destination.is_relative_to(c.root/'verification/expansion'),'Unsafe publication destination')
 destination.parent.mkdir(parents=True,exist_ok=True);staging=Path(tempfile.mkdtemp(prefix='.wasteland-stage-',dir=destination.parent))
 try:
  for name,raw in c.files.items():
   target=staging/relative(name);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);need(sha(target.read_bytes())==sha(raw),'Staging mismatch')
  manifest={'schemaVersion':1,'createdAt':now,'html_sha256':HTML,'selfExcluded':True,'files':{name:{'sha256':sha(raw),'bytes':len(raw)} for name,raw in sorted(c.files.items())}}
  (staging/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');c.unchanged();os.replace(staging,destination)
 finally:
  if staging.exists():shutil.rmtree(staging)
 print(json.dumps({'status':'published','path':str(destination),'files':len(c.files)+1,'sum':integration['reportedAssertionSum'],'captures':len(c.captures)},ensure_ascii=False));return 0

if __name__=='__main__':
 try:raise SystemExit(main())
 except (OSError,ValueError,KeyError,TypeError) as error:raise SystemExit('Evidence not published: '+str(error))
