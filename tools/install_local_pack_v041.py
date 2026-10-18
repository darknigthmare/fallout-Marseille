#!/usr/bin/env python3
"""Install or verify the complete Fallout: Mistral v0.41 local territory pack.

The service groups the 5,884 vector coordinates into 24 authenticated ZIP
archives. Every chunk is validated before atomic extraction. Officially empty
cadastre coordinates remain zero-byte .pbf files with explicit proof markers.
"""
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, os, shutil, subprocess, sys, tempfile, time, zipfile
from pathlib import Path, PurePosixPath
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from mvt_audit_v036 import parse_tile

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST=ROOT/'data/map_pack/local_pack_v041_manifest.json'
VECTOR_MANIFEST=ROOT/'data/map_pack/manifest_v038.json'
DEFAULT_OUTPUT=ROOT/'data/map_pack'
MAX_CHUNK_BYTES=40_000_000
MAX_MEMBER_BYTES=8_100_000
EMPTY_SHA=hashlib.sha256(b'').hexdigest()

class PackError(RuntimeError): pass

def atomic_bytes(path:Path,data:bytes):
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.part');tmp.write_bytes(data);os.replace(tmp,path)
def atomic_json(path:Path,obj):atomic_bytes(path,(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode())
def safe_member(name:str)->Path:
    p=PurePosixPath(name)
    if '\\' in name or ':' in name or '\x00' in name or p.is_absolute() or '..' in p.parts or not p.parts or any(part in ('','.','..') for part in p.parts):raise PackError(f'unsafe ZIP member: {name!r}')
    if p.parts[0] not in ('france-vector','cadastre','chunk_manifest.json'):
        raise PackError(f'unexpected ZIP root: {name!r}')
    return Path(*p.parts)
def sha(raw:bytes)->str:return hashlib.sha256(raw).hexdigest()

def request_chunk(chunk:dict,manifest:dict,cache:Path,timeout:int,retries:int,chunk_dir:Path|None):
    name=chunk['name'];dest=cache/name
    if dest.exists() and 0<dest.stat().st_size<=MAX_CHUNK_BYTES:return dest
    if chunk_dir:
        src=chunk_dir/name
        if not src.exists():raise PackError(f'fixture chunk missing: {src}')
        atomic_bytes(dest,src.read_bytes());return dest
    url=manifest['endpoint'].replace('{name}',name)
    headers={'apikey':manifest['publicKey'],'Accept':'application/zip','User-Agent':'Fallout-Mistral-Local-Pack/0.41'};last=None
    for attempt in range(retries):
        try:
            with urlopen(Request(url,headers=headers),timeout=timeout) as r:
                status=getattr(r,'status',r.getcode());raw=r.read(MAX_CHUNK_BYTES+1)
                if status!=200:raise PackError(f'HTTP {status}')
                if len(raw)>MAX_CHUNK_BYTES:raise PackError('chunk exceeds 40 MB')
                if raw[:2]!=b'PK':raise PackError('response is not ZIP')
                atomic_bytes(dest,raw);return dest
        except Exception as e:
            last=e;time.sleep(min(8,1.7**attempt))
    raise PackError(f'{name}: {last!r}')

def inspect_chunk(path:Path,expected:dict):
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:raise PackError(f'{path.name}: bad CRC')
        infos=z.infolist();names={i.filename for i in infos}
        if 'chunk_manifest.json' not in names:raise PackError(f'{path.name}: chunk_manifest.json missing')
        meta=json.loads(z.read('chunk_manifest.json'))
        for key in ('source','cursor','limit'):
            exp={'source':expected['source'],'cursor':expected['cursor'],'limit':expected['rows']}[key]
            if meta.get(key)!=exp:raise PackError(f'{path.name}: {key} {meta.get(key)!r} != {exp!r}')
        rows=meta.get('files') or []
        if len(rows)!=expected['rows']:raise PackError(f'{path.name}: rows {len(rows)}/{expected["rows"]}')
        checked=[]
        for info in infos:
            if info.is_dir():continue
            safe_member(info.filename)
            if info.file_size>MAX_MEMBER_BYTES and info.filename!='chunk_manifest.json':raise PackError(f'{path.name}: oversized {info.filename}')
        for row in rows:
            rel=row['path'];safe_member(rel)
            if rel not in names:raise PackError(f'{path.name}: missing {rel}')
            raw=z.read(rel);empty=bool(row.get('empty'))
            if empty:
                marker=rel+'.empty.json'
                if raw or marker not in names:raise PackError(f'{path.name}: empty proof missing for {rel}')
                proof=json.loads(z.read(marker))
                if proof.get('officialEmpty') is not True:raise PackError(f'{path.name}: invalid empty proof {marker}')
            else:
                if not raw:raise PackError(f'{path.name}: unexpected empty {rel}')
                if row.get('bytes') is not None and len(raw)!=int(row['bytes']):raise PackError(f'{path.name}: byte mismatch {rel}')
                if row.get('sha256') and sha(raw)!=row['sha256']:raise PackError(f'{path.name}: sha mismatch {rel}')
                parse_tile(raw)
            checked.append({'path':rel,'bytes':len(raw),'empty':empty,'sha256':sha(raw)})
        return meta,checked

def extract_chunk(path:Path,expected:dict,output:Path):
    meta,checked=inspect_chunk(path,expected)
    with zipfile.ZipFile(path) as z:
        for row in checked:
            rel=Path(*PurePosixPath(row['path']).parts);dest=output/rel
            raw=z.read(row['path']);atomic_bytes(dest,raw)
            marker=row['path']+'.empty.json'
            if row['empty']:atomic_bytes(output/Path(*PurePosixPath(marker).parts),z.read(marker))
            else:(output/Path(*PurePosixPath(marker).parts)).unlink(missing_ok=True)
    return {'name':path.name,'source':expected['source'],'cursor':expected['cursor'],'rows':len(checked),'empty':sum(x['empty'] for x in checked),'bytes':sum(x['bytes'] for x in checked),'chunkSha256':sha(path.read_bytes())}

def validate_local(output:Path,vector_manifest:Path):
    m=json.loads(vector_manifest.read_text());missing=[];invalid=[];empty=objects=bytes_total=0;started=time.perf_counter()
    for row in m['tiles']:
        dest=output/row['local'].replace('data/map_pack/','');marker=dest.with_suffix(dest.suffix+'.empty.json')
        if not dest.exists():missing.append(row['key']);continue
        try:
            raw=dest.read_bytes()
            if not raw:
                proof=json.loads(marker.read_text()) if marker.exists() else {}
                if proof.get('officialEmpty') is not True:raise PackError('empty marker missing')
                empty+=1
            else:
                parse_tile(raw);objects+=1;bytes_total+=len(raw)
        except Exception as e:invalid.append({'key':row['key'],'error':str(e)})
    return {'coordinates':len(m['tiles']),'objects':objects,'officialEmpty':empty,'missing':len(missing),'invalid':len(invalid),'bytes':bytes_total,'seconds':round(time.perf_counter()-started,3),'missingSample':missing[:20],'invalidSample':invalid[:20],'ok':not missing and not invalid and objects+empty==len(m['tiles'])}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',type=Path,default=DEFAULT_MANIFEST);ap.add_argument('--vector-manifest',type=Path,default=VECTOR_MANIFEST);ap.add_argument('--output',type=Path,default=DEFAULT_OUTPUT)
    ap.add_argument('--source',choices=['all','base','cadastre'],default='all');ap.add_argument('--workers',type=int,default=3);ap.add_argument('--timeout',type=int,default=120);ap.add_argument('--retries',type=int,default=4);ap.add_argument('--verify-only',action='store_true');ap.add_argument('--keep-chunks',action='store_true');ap.add_argument('--skip-terrain',action='store_true');ap.add_argument('--chunk-dir',type=Path);ap.add_argument('--limit-chunks',type=int,default=0)
    a=ap.parse_args();manifest=json.loads(a.manifest.read_text());chunks=[c for c in manifest['chunks'] if a.source=='all' or c['source']==a.source]
    if a.limit_chunks:chunks=chunks[:a.limit_chunks]
    cache=a.output/'.chunks_v041';cache.mkdir(parents=True,exist_ok=True);started=time.time();reports=[];errors=[]
    if not a.verify_only:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(a.workers,6))) as ex:
            jobs={ex.submit(request_chunk,c,manifest,cache,a.timeout,a.retries,a.chunk_dir):c for c in chunks}
            paths={}
            for fut in concurrent.futures.as_completed(jobs):
                c=jobs[fut]
                try:paths[c['name']]=fut.result();print(f"Téléchargé {c['name']}",flush=True)
                except Exception as e:errors.append({'chunk':c['name'],'error':repr(e)})
        if errors:
            print(json.dumps(errors,ensure_ascii=False,indent=2));return 1
        for i,c in enumerate(chunks,1):
            try:reports.append(extract_chunk(paths[c['name']],c,a.output));print(f"Extrait {i}/{len(chunks)} · {c['name']}",flush=True)
            except Exception as e:errors.append({'chunk':c['name'],'error':repr(e)})
    audit=validate_local(a.output,a.vector_manifest)
    terrain=None
    if not a.skip_terrain and a.source=='all' and not a.limit_chunks:
        cmd=[sys.executable,str(ROOT/'tools/install_terrain_v039.py')]
        if a.verify_only:cmd.append('--verify-only')
        else:cmd += ['--workers',str(max(1,min(a.workers,8)))]
        rc=subprocess.run(cmd,cwd=ROOT)
        terrain={'returncode':rc.returncode,'ok':rc.returncode==0}
    status={'version':'0.41.0','generated':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source':a.source,'chunksExpected':len(chunks),'chunksInstalled':len(reports) if not a.verify_only else None,'chunkErrors':errors,'vector':audit,'terrain':terrain,'seconds':round(time.time()-started,2),'complete':audit['ok'] and (terrain is None or terrain['ok'])}
    atomic_json(a.output/'local_pack_v041_status.json',status)
    if not a.keep_chunks and not errors and not a.verify_only:shutil.rmtree(cache,ignore_errors=True)
    print(json.dumps(status,ensure_ascii=False,indent=2));return 0 if status['complete'] else 1
if __name__=='__main__':raise SystemExit(main())
