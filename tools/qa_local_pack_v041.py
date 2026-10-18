#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[1]
BASE=(ROOT/'data/fixtures/france-vector-z14-8437-6001.pbf').read_bytes()
CAD=(ROOT/'data/fixtures/cadastre-z16-33750-24006.pbf').read_bytes()
checks=[]
def ck(name,ok,detail=None):checks.append({'name':name,'ok':bool(ok),'detail':detail});print(('OK ' if ok else 'FAIL ')+name,flush=True)
def chunk(path,source,cursor,rows,files):
    meta={'version':'0.41.0','source':source,'cursor':cursor,'limit':rows,'next':None,'files':[]}
    with zipfile.ZipFile(path,'w',zipfile.ZIP_STORED) as z:
        for rel,raw,empty in files:
            z.writestr(rel,raw)
            row={'path':rel,'empty':empty,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
            meta['files'].append(row)
            if empty:z.writestr(rel+'.empty.json',json.dumps({'version':'0.41.0','officialEmpty':True,'source':source,'sha256':hashlib.sha256(b'').hexdigest()}))
        z.writestr('chunk_manifest.json',json.dumps(meta))
with tempfile.TemporaryDirectory() as td:
    td=Path(td);chunks=td/'chunks';out=td/'pack';chunks.mkdir();
    chunk(chunks/'base_00000_1.zip','base',0,1,[('france-vector/14/8437/6001.pbf',BASE,False)])
    chunk(chunks/'cadastre_00000_2.zip','cadastre',0,2,[('cadastre/16/33750/24006.pbf',CAD,False),('cadastre/16/33751/24006.pbf',b'',True)])
    manifest={'version':'0.41.0','endpoint':'unused/{name}','publicKey':'fixture','chunks':[{'name':'base_00000_1.zip','source':'base','cursor':0,'rows':1,'base64Bytes':0},{'name':'cadastre_00000_2.zip','source':'cadastre','cursor':0,'rows':2,'base64Bytes':0}]}
    (td/'manifest.json').write_text(json.dumps(manifest))
    vector={'tiles':[{'key':'14/8437/6001','local':'data/map_pack/france-vector/14/8437/6001.pbf'},{'key':'16/33750/24006','local':'data/map_pack/cadastre/16/33750/24006.pbf'},{'key':'16/33751/24006','local':'data/map_pack/cadastre/16/33751/24006.pbf'}]}
    (td/'vector.json').write_text(json.dumps(vector))
    cmd=[sys.executable,str(ROOT/'tools/install_local_pack_v041.py'),'--manifest',str(td/'manifest.json'),'--vector-manifest',str(td/'vector.json'),'--output',str(out),'--chunk-dir',str(chunks),'--skip-terrain','--keep-chunks']
    r=subprocess.run(cmd,capture_output=True,text=True);ck('installation fixture réussie',r.returncode==0,r.stderr+r.stdout[-1200:])
    status=json.loads((out/'local_pack_v041_status.json').read_text());ck('trois coordonnées vérifiées',status['vector']['coordinates']==3,status);ck('deux PBF et une vide',status['vector']['objects']==2 and status['vector']['officialEmpty']==1,status['vector']);ck('aucun manque',status['vector']['ok'] is True,status['vector'])
    r2=subprocess.run([sys.executable,str(ROOT/'tools/install_local_pack_v041.py'),'--manifest',str(td/'manifest.json'),'--vector-manifest',str(td/'vector.json'),'--output',str(out),'--source','all','--verify-only','--skip-terrain'],capture_output=True,text=True);ck('vérification seule réussie',r2.returncode==0,r2.stderr+r2.stdout[-1000:])
    r3=subprocess.run([sys.executable,str(ROOT/'tools/benchmark_map_v041.py'),'--root',str(out),'--workers','2'],capture_output=True,text=True);ck('benchmark fixture réussi',r3.returncode==0,r3.stderr);bench=json.loads((out/'benchmark_v041.json').read_text());ck('benchmark décode deux PBF',bench['sampledPbf']==2,bench);ck('débit mesuré',bench['throughputMiBps']>=0,bench['throughputMiBps'])
    # Path traversal must be rejected before extraction.
    bad=chunks/'base_00001_1.zip'
    with zipfile.ZipFile(bad,'w') as z:z.writestr('../escape.pbf',BASE);z.writestr('chunk_manifest.json',json.dumps({'source':'base','cursor':1,'limit':1,'files':[{'path':'../escape.pbf','empty':False,'bytes':len(BASE),'sha256':hashlib.sha256(BASE).hexdigest()}]}))
    bad_manifest={'version':'0.41.0','endpoint':'unused/{name}','publicKey':'fixture','chunks':[{'name':bad.name,'source':'base','cursor':1,'rows':1,'base64Bytes':0}]};(td/'bad.json').write_text(json.dumps(bad_manifest))
    rb=subprocess.run([sys.executable,str(ROOT/'tools/install_local_pack_v041.py'),'--manifest',str(td/'bad.json'),'--vector-manifest',str(td/'vector.json'),'--output',str(td/'badout'),'--chunk-dir',str(chunks),'--skip-terrain'],capture_output=True,text=True);ck('traversée ZIP refusée',rb.returncode!=0,rb.stdout[-1000:])
# Production manifest continuity.
m=json.loads((ROOT/'data/map_pack/local_pack_v041_manifest.json').read_text());ck('24 lots de production',len(m['chunks'])==24);ck('5884 coordonnées déclarées',sum(x['rows'] for x in m['chunks'])==5884);ck('367 générales',sum(x['rows'] for x in m['chunks'] if x['source']=='base')==367);ck('5517 cadastrales',sum(x['rows'] for x in m['chunks'] if x['source']=='cadastre')==5517);ck('taille Base64 cohérente',sum(x['base64Bytes'] for x in m['chunks'])==m['totalBase64Bytes']==119130028)
report={'version':'0.41.0','passed':sum(x['ok'] for x in checks),'failed':sum(not x['ok'] for x in checks),'total':len(checks),'checks':checks};(ROOT/'verification/QA_LOCAL_PACK_V041.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('passed','failed','total')},indent=2));raise SystemExit(1 if report['failed'] else 0)
