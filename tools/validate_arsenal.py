#!/usr/bin/env python3
"""Run bounded, reproducible arsenal and retained game regressions; record actual evidence.
A full report is emitted only after all requested commands succeeded. Existing historical
QA files are not rewritten. Cold restart tests are optional locally but required in CI.
"""
from pathlib import Path
import argparse, concurrent.futures, hashlib, json, os, re, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[1]
SUITES='arsenal consigne_vie gestes retrouvailles pigeons gabians rats cigales secours parts lys compagnons voisins notaires mutuelle radieuse poste pharmacie'.split()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'verification/arsenal/ci');p.add_argument('--cold',action='store_true');p.add_argument('--jobs',type=int,default=2);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);started=time.monotonic();stages=[]
 def run(name,cmd):
  log=out/(name+'.log');t=time.monotonic()
  with log.open('w',encoding='utf-8') as f:z=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=240)
  status={'name':name,'command':cmd,'returncode':z.returncode,'seconds':round(time.monotonic()-t,2)};print(json.dumps(status,ensure_ascii=False),flush=True)
  if z.returncode:raise RuntimeError(name+' failed: '+str(log))
  return status
 def stage(name,cmd):stages.append(run(name,cmd))
 try:
  stage('build',['python','tools/build_single.py']);stage('build-check',['python','tools/build_single.py','--check']);stage('syntax',['node','--check','src/game.js'])
  stage('inventory',['python','tools/audit_regional_content.py','--check'])
  stage('registry',['python','tools/verify_lore_registry.py','--bundle','src/game.js','--output',str(out/'REGISTRY.json')])
  lore=sorted(str(x.relative_to(ROOT)) for x in (ROOT/'tests/expansion').glob('lore_*.cjs'))
  stage('lore',['node','--test',*lore]);stage('first-person',['node','tests/expansion/first_person.cjs']);stage('bestiary',['node','tests/expansion/regional_bestiary.cjs'])
  for key in ['lore_registry','regional_inventory']:stage(key,['python','-m','unittest','discover','-s','tests/expansion','-p','test_'+key+'.py','-v'])
  for key in ['city_streaming.cjs','city_wait_cancel.test.cjs','city_partition_seams.test.cjs','city_geometry_identity.test.cjs']:stage(key,['node','tests/expansion/'+key])
  def browser(s):return run(s,['python','tests/expansion/'+s+'_browser_smoke.py','--html','index.html','--output',str(out/s)])
  with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(3,a.jobs))) as ex:
   for z in ex.map(browser,SUITES):stages.append(z)
  cold={'cour-cold':'consigne_vie','birds-cold':'birds','rats-cold':'rats'} if a.cold else {}
  for name,s in cold.items():stage(name,['python','tests/expansion/'+s+'_cold_save_smoke.py','--html','index.html','--output',str(out/name)])
  h=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
  outputs={x:h(x) for x in ['index.html','JOUER_FALLOUT_MISTRAL_v0.50.html','src/game.js','sw.js']};html=outputs['index.html'];assert html==outputs['JOUER_FALLOUT_MISTRAL_v0.50.html']
  reports={}
  for name in SUITES+list(cold):
   candidates=[]
   for p in (out/name).glob('*.json'):
    v=json.loads(p.read_text())
    if isinstance(v,dict) and 'passed' in v and 'html_sha256' in v:candidates.append((p,v))
   assert len(candidates)==1,(name,len(candidates));p,v=candidates[0]
   assert v['html_sha256']==html and v['passed']>0 and not v.get('errors') and v.get('complete',True),name
   reports[name]={'passed':v['passed'],'errors':v.get('errors',[]),'report':p.relative_to(ROOT).as_posix(),'scope':v.get('scope'),'browser':v.get('browser')}
  text=(out/'lore.log').read_text();lore_count=int(re.search(r'^# pass (\d+)$',text,re.M)[1]);assert re.search(r'^# fail 0$',text,re.M)
  python_counts={}
  for name in ['lore_registry','regional_inventory']:
   text=(out/(name+'.log')).read_text();assert '\nOK\n' in text;python_counts[name]=int(re.search(r'Ran (\d+) tests',text)[1])
  checks={}
  for name in ['first-person','bestiary']:
   v=json.loads((out/(name+'.log')).read_text().strip().splitlines()[-1]);assert v.get('failed',0)==0;checks[name]=v['passed']
  data=json.loads((ROOT/'docs/INVENTAIRE_ARSENAL_BESTIAIRE.json').read_text())
  qa={'baseline':'580f432e32369a950bb7761f9441da9f063f521e','validation_input':os.getenv('GITHUB_SHA','local working tree'),'workflow_run':os.getenv('GITHUB_RUN_ID'),'lore_passed':lore_count,'python_tests':python_counts,'retained_model_checks':checks,'canonical_outputs':outputs,'inventory_counts':data['counts'],'browser_suites':{k:reports[k] for k in SUITES},'browser_checks':sum(reports[k]['passed'] for k in SUITES),'cold_suites':{k:reports[k] for k in cold},'cold_requested':a.cold,'territory_commands':4,'stages':stages,'seconds':round(time.monotonic()-started,2),'limits':['55 existing regional IDs, not 55 new or unique models; three additional shared presentation profiles.','49 weapon concepts and 98 creature/automaton designations are documentary records, not completed content; exact-name matching does not infer aliases.','Numeric weapon data, ammunition ownership and rewards unchanged; no new save schema.','Browser suites use scripted origins/positions and isolated MemoryStorage with software rendering; no full human campaign or exhaustive IGN traversal.','When requested, cold suites cover existing courtyard/birds/rats with orderly Chromium restart, not power loss or every browser. No new arsenal-specific disk restart scenario.','COCHONNET PR17 not incorporated.'],'publication_note':'Validated working tree. Source publication, PR checks, merge and deployment remain separate facts.'}
  (ROOT/'verification/arsenal/QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n');(out/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n')
  print(json.dumps({'ok':True,'lore':lore_count,'browser':qa['browser_checks'],'cold':{k:reports[k]['passed'] for k in cold},'html':html}),flush=True)
 except Exception as e:
  (out/'FAILED.json').write_text(json.dumps({'error':str(e),'completed_stages':stages},ensure_ascii=False,indent=2));raise
if __name__=='__main__':main()
