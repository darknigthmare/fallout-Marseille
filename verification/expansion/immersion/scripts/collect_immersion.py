"""Assemble exact current evidence. Older attempts remain outside the count."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,os
from urllib.parse import urlsplit
ROOT=Path('/workspace/fallout-Marseille')
BASE=Path('/workspace/.cloud-setup/fallout-marseille/fps-expansion')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def field(value,key):
 if isinstance(key,list):
  for part in key:value=value[part]
  return value
 if key in value:return value[key]
 for part in key.split('.'):value=value[part]
 return value
def observed_total(log):
 rows=re.findall(r'Ran (\d+) tests|ℹ tests (\d+)|^# tests (\d+)|"passed"\s*:\s*(\d+)',log,re.M)
 assert len(rows)==1,'A single reported count is required in each model log'
 return int(next(v for v in rows[0]if v))

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--publish',action='store_true');a=p.parse_args()
 collector_hash=sha(Path(__file__));config_hash=sha(a.config)
 config=read(a.config);html=sha(ROOT/'index.html');frozen=read(BASE/'FROZEN_INPUTS.json')
 qa=read(BASE/'QA_ONLY_ADAPTATIONS.json');qa_changes={r['path']:r for r in qa['nonRuntimeQaOnlyChanges']}
 assert set(qa_changes)=={'tools/check_v050.py'} and qa['html_sha256']==html and qa['gameBytesUnchanged']
 assert sha(ROOT/'tools/check_v050.py')==qa_changes['tools/check_v050.py']['afterSha256']
 assert sha(BASE/'qa-adaptation/check_v050_before.py')==qa_changes['tools/check_v050.py']['beforeSha256']
 original_native_inputs=read(BASE/'RUNTIME_VALIDATION_INPUTS.json')
 assert set(original_native_inputs)==set(frozen)
 for name,h in original_native_inputs.items():
  if h!=frozen[name]:assert name in qa_changes and h==qa_changes[name]['beforeSha256']and frozen[name]==qa_changes[name]['afterSha256']
 assert html==config['html_sha256']==frozen['index.html']
 assert all((ROOT/name).is_file() and sha(ROOT/name)==h for name,h in frozen.items())
 methods=[];copies=[];captures=[]
 ids=[r['id']for r in config['native_methods']];reports=[(BASE/r['report']).resolve()for r in config['native_methods']]
 reserved={'models','rebuild','closure','runtime-closure','legacy','scripts','supplementary'}
 assert len(ids)==len(set(ids))and not reserved.intersection(ids)and all(re.fullmatch('[a-z][a-z0-9_-]*',i)for i in ids)
 assert len(reports)==len(set(reports))and all(q.is_relative_to(BASE)and q.is_file()for q in reports)
 units=read(BASE/'models/UNITS.json')
 assert units['stage']=='complete' and units['html_sha256']==html and units['failedProcesses']==0 and units['skipped']==0 and not units['changedInputs']
 assert len(units['suites'])==39 and units['total']==sum(row['total']for row in units['suites'])
 for name,h in {**units['sourceHashes'],**units['testScriptHashes']}.items():assert sha(ROOT/name)==h,name
 for row in units['suites']:
  assert row['exitCode']==0 and row['skipped']==0 and row['total']>0
  assert sha(BASE/'models'/row['log'])==row['logSha256']
  assert observed_total((BASE/'models'/row['log']).read_text())==row['total']
 methods.append({'id':'models','label':'Modèles et outils, fixtures contrôlées','passed':units['total'],'report':'models/UNITS.json','reportSha256':sha(BASE/'models/UNITS.json')})
 copies.append((BASE/'models','models'))
 rebuild=read(BASE/'REPRODUCIBLE_BUILD.json');assert rebuild['exitCode']==0 and len(rebuild['files'])==3 and {r['path']for r in rebuild['files']}=={'index.html','JOUER_FALLOUT_MISTRAL_v0.50.html','src/game.js'}and all(r['same']and r['sourceSha256']==r['rebuiltSha256']==sha(ROOT/r['path'])for r in rebuild['files'])
 methods.append({'id':'rebuild','label':'Reconstruction indépendante, comparaisons d’octets','passed':3,'report':'REPRODUCIBLE_BUILD.json','reportSha256':sha(BASE/'REPRODUCIBLE_BUILD.json')})
 copies.append((BASE/'REPRODUCIBLE_BUILD.json','REPRODUCIBLE_BUILD.json'))
 closure=read(BASE/'runtime-closure/RUNTIME_CLOSURE.json');assert closure['stage']=='complete' and closure['exitCode']==0 and closure['failed']==0 and closure['passed']==3 and closure['html_sha256']==html
 methods.append({'id':'closure','label':'HTTP isolé, dépendances Python standard','passed':3,'report':'runtime-closure/RUNTIME_CLOSURE.json','reportSha256':sha(BASE/'runtime-closure/RUNTIME_CLOSURE.json')});copies.append((BASE/'runtime-closure','runtime-closure'))
 legacy=read(BASE/'legacy-final/QA_LEGACY_RUN.json');audit=read(BASE/'legacy-final/RUN_AUDIT.json')
 assert audit['passed'] and audit['checker_exit_code']==0 and all(audit['checks'].values())
 assert legacy['passed']==434 and legacy['failed']==0 and legacy['total']==434 and legacy['html_sha256']==html and legacy['allHtmlMatch'] and not legacy['javascriptErrors']
 assert len(legacy['processes'])==15 and all(r['exitCode']==0 for r in legacy['processes'])
 methods.append({'id':'legacy','label':'Contrats hérités, géométries et réseau contrôlés','passed':434,'report':'legacy/QA_LEGACY_RUN.json','reportSha256':sha(BASE/'legacy-final/QA_LEGACY_RUN.json')});copies.append((BASE/'legacy-final','legacy'))
 copies.append((BASE/'legacy-game/verification/v050/legacy','legacy/outputs'))
 for row in config['native_methods']:
  assert all(row.get(k)for k in ('exit_key','receipt_report_hash_key','receipt_script_hash_key','receipt_log_hash_key'))
  path=BASE/row['report'];report=read(path);receipt_path=BASE/row['receipt'];receipt=read(receipt_path)
  actual_html=report.get('html_sha256') or report.get('pinned_inputs',{}).get('index.html')
  if isinstance(actual_html,dict):actual_html=actual_html.get('sha256')
  assert actual_html==html,(row['id'],'wrong HTML',actual_html)
  checks=report['checks'];assert checks and all(c['ok']is True for c in checks) and report['failed']==0 and report['passed']==len(checks)
  if row.get('category')=='simulated_gamepad':assert report.get('stage')is None and 'Gamepad API simulated'in report['scope']and not report.get('errors')
  else:assert report.get('stage')in('complete','completed')
  assert not report.get('page_errors') and not report.get('javascript_console_errors')
  console=report.get('console_errors',[])
  # Resource failures are kept raw below; any other console.error is fatal.
  assert all(t=='Failed to load resource: net::ERR_TUNNEL_CONNECTION_FAILED'for t in console),(row['id'],'application or unclassified console error',console)
  assert not report.get('html_injected') and not report.get('network_mocked') and not report.get('storage_mocked')
  assert not report.get('local_http_errors') and not report.get('http_errors')
  assert field(receipt,row['exit_key'])==0
  if row.get('receipt_report_hash_key'):assert field(receipt,row['receipt_report_hash_key'])==sha(path)
  if row.get('receipt_script_hash_key'):
   script_hash=field(receipt,row['receipt_script_hash_key']);assert any(sha(q)==script_hash for q in path.parent.glob('*.py')),(row['id'],'receipt executed script missing')
  for name,h in {**receipt.get('inputHashes',{}),**receipt.get('sourceHashes',{})}.items():
   assert(ROOT/name).is_file(),(row['id'],'receipt dependency absent',name)
   actual=sha(ROOT/name)
   if actual!=h:assert name in qa_changes and h==qa_changes[name]['beforeSha256']and actual==qa_changes[name]['afterSha256'],(row['id'],'receipt dependency changed',name)
  for name,h in report.get('pinned_inputs',{}).items():
   if isinstance(h,dict):h=h.get('sha256')
   assert isinstance(h,str)and re.fullmatch('[a-f0-9]{64}',h)and(ROOT/name).is_file(),(row['id'],'pinned dependency absent or invalid',name)
   assert sha(ROOT/name)==h,(row['id'],name)
  if report.get('script_sha256'):
   assert any(sha(q)==report['script_sha256']for q in path.parent.glob('*.py')),(row['id'],'missing exact executed script')
  log=BASE/row['log'];text=log.read_text()
  if row.get('receipt_log_hash_key'):assert field(receipt,row['receipt_log_hash_key'])==sha(log)
  command=receipt.get('argv')
  if row.get('command_file'):
   command_record=read(BASE/row['command_file']);command=command_record['command'];assert command_record['executedScriptSha256']==field(receipt,row['receipt_script_hash_key'])
  assert isinstance(command,list)and command
  flag=next((f for f in ('--expect-html-sha','--expected-html-sha256')if f in command),None)
  assert flag and command[command.index(flag)+1]==html,(row['id'],'command HTML identity differs')
  script_path=Path(command[1]);script_path=script_path if script_path.is_absolute()else ROOT/script_path
  assert script_path.is_file()and any(sha(q)==sha(script_path)for q in path.parent.glob('*.py')),(row['id'],'argv script is not archived exactly')
  failures=[]
  for key in ('request_failures','local_request_failures','local_geographic_request_failures','external_request_failures'):
   for failure in report.get(key,[]):
    if failure not in failures:failures.append(failure)
  local=[];external=[]
  for failure in failures:
   url=failure.get('url','');u=urlsplit(url)
   if u.hostname in ('localhost','127.0.0.1','::1'):
    detail=str(failure.get('failure',failure.get('error',failure.get('errorText',''))))
    assert u.path=='/__mistral/local-data'and'ERR_ABORTED'in detail,(row['id'],'unexpected local source request failure',failure)
    local.append(failure)
   else:
    assert u.hostname and u.hostname.endswith('.supabase.co'),(row['id'],'unclassified external request failure',failure)
    external.append(failure)
  if console:assert external,(row['id'],'resource console diagnostics have no corresponding external requests')
  observed=[m.group(1)for m in re.finditer(r'^OK (.*)$',text,re.M)]
  assert observed==[c['name']for c in checks],(row['id'],'stdout/check sequence differs',len(observed),len(checks))
  for shot in report.get('shots',[]):
   q=path.parent/shot['file'];assert q.is_file()and q.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')and sha(q)==shot['sha256']
   captures.append({'method':row['id'],'file':row['id']+'/'+shot['file'],'sha256':sha(q)})
  methods.append({'id':row['id'],'label':row['label'],'passed':len(checks),'report':row['id']+'/'+path.name,'reportSha256':sha(path),'scope':report.get('scope'),'rawConsoleErrors':console,'metadataCancellations':local,'externalRequestFailures':external,'networkObservationPresent':any(k in report for k in ('request_failures','local_request_failures','external_request_failures'))})
  copies.append((path.parent,row['id']))
  if receipt_path.parent!=path.parent:copies.append((receipt_path,row['id']+'/EXECUTION_STATUS.json'))
  if log.parent!=path.parent:copies.append((log,str(Path(row['id'])/os.path.relpath(log,path.parent))))
 result={'version':'0.50.0','html_sha256':html,'baseCommit':'f4a733755c7cf20e99284dfb90ca0465fca0c607','passed':sum(m['passed']for m in methods),'failed':0,'methods':methods,'captureCount':len(captures),'captures':captures,'productionInputCount':len(frozen),'productionHashes':frozen,'methodCaveat':'Methods overlap; sums are not equivalent playthroughs. Geographic placements, freezes, resource/rig preparation and simulated controller inputs are explicitly declared in each report. Raw metadata cancellations and external probe failures remain in their reports.','limitations':['Full Marseille facade/interior 1:1 fidelity remains uncertified.','MNS measures observed upper surfaces, not architectural roof semantics or room plans.','Southern terrain is resampled to requested 1m nodes; the central 0.50m native lattice remains separate.','First-person meshes are original stylized family models, with partial hand cropping in some frames.','Physical mobile/gamepad hardware and exhaustive human playthroughs are not certified.'],'collectorSha256':sha(Path(__file__))}
 result['qaOnlyAdaptationsAfterNativeValidation']=qa
 assert len(captures)==len({r['file']for r in captures})
 assert collector_hash==sha(Path(__file__))and config_hash==sha(a.config)
 write(BASE/'IMMERSION_INTEGRATION.json',result)
 if a.publish:
  target=ROOT/'verification/expansion/immersion';assert not target.exists()
  stage=BASE/'publication';assert not stage.exists();stage.mkdir()
  destinations=set()
  for source,destination in copies:
   dest=(stage/destination).resolve();assert dest.is_relative_to(stage.resolve())
   if source.is_dir():members=[(q,dest/q.relative_to(source))for q in source.rglob('*')if q.is_file()and'__pycache__'not in q.parts]
   else:members=[(source,dest)]
   for q,target_path in members:
    assert not q.is_symlink()and target_path not in destinations,('Conflicting evidence destination',target_path)
    destinations.add(target_path)
   
   if source.is_dir():shutil.copytree(source,dest,ignore=shutil.ignore_patterns('__pycache__'),dirs_exist_ok=True)
   else:dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
  shutil.copy2(BASE/'IMMERSION_INTEGRATION.json',stage/'IMMERSION_INTEGRATION.json')
  shutil.copy2(a.config,stage/'METHODS_CONFIG.json')
  scripts=stage/'scripts';scripts.mkdir()
  for file in ['collect_immersion.py','prepare_validation.py','check_runtime_closure.py']:shutil.copy2(BASE/file,scripts/file)
  shutil.copytree(ROOT/'tests/expansion',scripts/'tests',ignore=shutil.ignore_patterns('__pycache__'))
  shutil.copy2(ROOT/'tools/check_expansion.py',scripts/'check_expansion.py')
  shutil.copy2(ROOT/'tools/check_v050.py',scripts/'check_v050.py')
  shutil.copytree(BASE/'qa-adaptation',stage/'supplementary/qa-adaptation')
  for row in config.get('supplements',[]):
   source=BASE/row['source'];dest=(stage/'supplementary'/row['destination']).resolve();assert dest.is_relative_to((stage/'supplementary').resolve())and not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
   if source.is_dir():shutil.copytree(source,dest,ignore=shutil.ignore_patterns('__pycache__','*.tif','*.tiff','*.f32','*.zip','candidate-*'))
   else:shutil.copy2(source,dest)
  table='\n'.join('| '+m['label']+' | '+str(m['passed'])+' |'for m in methods)
  (stage/'README.md').write_text('# Validation FPS et poursuite de Marseille\n\nHTML `'+html+'`.\n\n'+str(result['passed'])+' contrôles descriptifs, '+str(len(captures))+' événements de capture native. Les méthodes se chevauchent et ne sont pas des parties équivalentes.\n\n| Méthode | Contrôles |\n| --- | ---: |\n'+table+'\n\nLes aides, préparations, entrées simulées, cadrages limités et événements réseau restent explicités dans les rapports. Les scripts archivés servent à vérifier leur identité ; lancer les tests maintenus depuis la racine du projet. Les TIFF et les archives géographiques ne sont pas dupliqués ici. Les essais antérieurs ou interrompus restent hors de cette somme. Marseille intégralement 1:1 et le matériel physique restent non certifiés.\n')
  assert collector_hash==sha(Path(__file__))and config_hash==sha(a.config)
  write(stage/'MANIFEST.json',{'files':[{'file':str(q.relative_to(stage)),'bytes':q.stat().st_size,'sha256':sha(q)}for q in sorted(stage.rglob('*'))if q.is_file()]})
  shutil.move(stage,target)
 print(json.dumps({'passed':result['passed'],'methods':len(methods),'captures':len(captures),'html':html,'published':a.publish}))
if __name__=='__main__':main()
