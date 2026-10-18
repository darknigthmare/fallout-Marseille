#!/usr/bin/env python3
"""Install or verify the complete Fallout: Mistral v0.41 local territory pack.

The service groups the 5,884 vector coordinates into 24 authenticated ZIP
archives. Every chunk is validated before atomic extraction. Officially empty
cadastre coordinates remain zero-byte .pbf files with explicit proof markers.
Local bundles may supply a .zip.gz transport instead of its .zip: only the
original ZIP's pinned byte count and SHA-256 authorize the decoded content.
"""
from __future__ import annotations
import argparse, concurrent.futures, gzip, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time, zipfile, zlib
from pathlib import Path, PurePosixPath
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from mvt_audit_v036 import parse_tile
from install_real_map_v038 import validate as validate_tile

ROOT=Path(__file__).resolve().parents[1]
BUNDLED_CHUNKS=ROOT/'data/map_pack/archives'
BUNDLED_MANIFEST=BUNDLED_CHUNKS/'manifest.json'
DEFAULT_MANIFEST=BUNDLED_MANIFEST if BUNDLED_MANIFEST.is_file() else ROOT/'data/map_pack/local_pack_v041_manifest.json'
VECTOR_MANIFEST=ROOT/'data/map_pack/manifest_v038.json'
DEFAULT_OUTPUT=ROOT/'data/map_pack'
MAX_CHUNK_BYTES=40_000_000
MAX_MEMBER_BYTES=8_100_000
MAX_EXPANDED_BYTES=128_000_000
MAX_PROOF_BYTES=64_000
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

def coordinate(path:str,source:str):
    match=re.fullmatch(r'(france-vector|cadastre)/(\d+)/(\d+)/(\d+)\.pbf',path)
    if match is None:raise PackError(f'invalid tile path: {path!r}')
    dataset,z,x,y=match.groups();z,x,y=int(z),int(x),int(y)
    if (dataset,z)!={'base':('france-vector',14),'cadastre':('cadastre',16)}.get(source):raise PackError('tile source or zoom differs from chunk')
    if not (0<=x<2**z and 0<=y<2**z):raise PackError('tile coordinate is out of bounds')
    return {'source':source,'z':z,'x':x,'y':y}

def check_empty_proof(raw:bytes,row:dict):
    if not raw or len(raw)>MAX_PROOF_BYTES:raise PackError('invalid empty proof size')
    proof=json.loads(raw)
    if not isinstance(proof,dict) or proof.get('officialEmpty') is not True:raise PackError('invalid empty proof')
    if any(type(proof.get(k)) is not type(v) or proof.get(k)!=v for k,v in row.items()):raise PackError('empty proof belongs to another coordinate')
    if proof.get('sha256')!=EMPTY_SHA:raise PackError('invalid empty proof SHA-256')
    return proof

def validate_archive_bytes(raw:bytes,chunk:dict):
    if not raw or len(raw)>MAX_CHUNK_BYTES or raw[:2]!=b'PK':raise PackError('invalid ZIP size or signature')
    expected=chunk.get('sha256')
    if expected is not None:
        if not isinstance(expected,str) or not re.fullmatch('[0-9a-fA-F]{64}',expected):raise PackError('invalid pinned ZIP SHA-256')
        if sha(raw)!=expected.lower():raise PackError(f"{chunk['name']}: pinned ZIP SHA-256 mismatch")
    size=chunk.get('archiveBytes')
    if size is not None and (type(size) is not int or size!=len(raw)):raise PackError(f"{chunk['name']}: ZIP byte count mismatch")
    return raw

def read_gzip_chunk(path:Path,chunk:dict):
    """Decode a local transport with a strict cap, preserving the original ZIP."""
    limit=chunk.get('archiveBytes');expected=chunk.get('sha256')
    if type(limit) is not int or not 0<limit<=MAX_CHUNK_BYTES:raise PackError('gzip transport requires a bounded pinned ZIP byte count')
    if not isinstance(expected,str) or not re.fullmatch('[0-9a-fA-F]{64}',expected):raise PackError('gzip transport requires the original ZIP SHA-256')
    if not 0<path.stat().st_size<=MAX_CHUNK_BYTES:raise PackError('gzip transport exceeds compressed size limit')
    try:
        with gzip.open(path,'rb') as stream:
            # The extra byte distinguishes an oversized expansion without ever
            # materializing the rest of it. Reading to EOF also checks gzip CRC.
            raw=stream.read(limit+1)
    except (OSError,EOFError,zlib.error) as error:raise PackError(f'invalid gzip transport: {error}') from error
    if len(raw)>limit:raise PackError('gzip expansion exceeds the pinned ZIP byte count')
    return validate_archive_bytes(raw,chunk)

def request_chunk(chunk:dict,manifest:dict,cache:Path,timeout:int,retries:int,chunk_dir:Path|None):
    name=chunk['name'];dest=cache/name
    if not isinstance(name,str) or not name.endswith('.zip') or Path(name).name!=name or '\\' in name or ':' in name:raise PackError('invalid ZIP archive name')
    if dest.exists() and 0<dest.stat().st_size<=MAX_CHUNK_BYTES:
        try:validate_archive_bytes(dest.read_bytes(),chunk);return dest
        except PackError:pass
    if chunk_dir:
        src=chunk_dir/name
        if src.is_file():
            if src.stat().st_size>MAX_CHUNK_BYTES:raise PackError(f'local ZIP exceeds size limit: {src}')
            raw=validate_archive_bytes(src.read_bytes(),chunk)
        else:
            compressed=src.with_name(src.name+'.gz')
            if not compressed.is_file():raise PackError(f'local ZIP and gzip transport missing (no network fallback): {src}')
            raw=read_gzip_chunk(compressed,chunk);src=compressed
        if src.resolve()!=dest.resolve():atomic_bytes(dest,raw)
        return dest
    url=manifest['endpoint'].replace('{name}',name)
    headers={'apikey':manifest['publicKey'],'Accept':'application/zip','User-Agent':'Fallout-Mistral-Local-Pack/0.41'};last=None
    for attempt in range(retries):
        try:
            with urlopen(Request(url,headers=headers),timeout=timeout) as r:
                status=getattr(r,'status',r.getcode());raw=r.read(MAX_CHUNK_BYTES+1)
                if status!=200:raise PackError(f'HTTP {status}')
                validate_archive_bytes(raw,chunk)
                atomic_bytes(dest,raw);return dest
        except Exception as e:
            last=e;time.sleep(min(8,1.7**attempt))
    raise PackError(f'{name}: {last!r}')

def inspect_chunk(path:Path,expected:dict):
    if path.stat().st_size>MAX_CHUNK_BYTES:raise PackError('ZIP exceeds size limit')
    validate_archive_bytes(path.read_bytes(),expected)
    with zipfile.ZipFile(path) as z:
        infos=z.infolist();names={i.filename for i in infos}
        if len(names)!=len(infos):raise PackError(f'{path.name}: duplicate ZIP members')
        if len(infos)>expected['rows']*3+1:raise PackError(f'{path.name}: too many ZIP members')
        # Inspect metadata before any decompression. ZipFile.read validates CRC
        # for each declared member below; testzip() first would bypass our caps.
        if sum(i.file_size for i in infos)>MAX_EXPANDED_BYTES:raise PackError('ZIP expanded size exceeds limit')
        for info in infos:
            safe_member(info.filename)
            if info.is_dir():continue
            if info.file_size>MAX_MEMBER_BYTES:raise PackError(f'{path.name}: oversized {info.filename}')
            if info.filename.endswith('.empty.json') and info.file_size>MAX_PROOF_BYTES:raise PackError('empty proof exceeds size limit')
            if (info.external_attr>>16)&0o170000==0o120000:raise PackError('ZIP symlink is not a tile')
        if 'chunk_manifest.json' not in names:raise PackError(f'{path.name}: chunk_manifest.json missing')
        meta=json.loads(z.read('chunk_manifest.json'))
        if not isinstance(meta,dict):raise PackError('invalid chunk manifest')
        for key in ('source','cursor','limit'):
            exp={'source':expected['source'],'cursor':expected['cursor'],'limit':expected['rows']}[key]
            if meta.get(key)!=exp:raise PackError(f'{path.name}: {key} {meta.get(key)!r} != {exp!r}')
        rows=meta.get('files')
        if not isinstance(rows,list):raise PackError('invalid chunk rows')
        if len(rows)!=expected['rows']:raise PackError(f'{path.name}: rows {len(rows)}/{expected["rows"]}')
        checked=[];declared={'chunk_manifest.json'}
        for row in rows:
            if not isinstance(row,dict):raise PackError('invalid chunk row')
            rel=row['path'];safe_member(rel)
            coord=coordinate(rel,expected['source'])
            if rel in declared:raise PackError('duplicate tile in chunk manifest')
            declared.add(rel)
            if rel not in names:raise PackError(f'{path.name}: missing {rel}')
            if type(row.get('empty')) is not bool:raise PackError('empty flag must be a boolean')
            raw=z.read(rel);empty=row['empty']
            if type(row.get('bytes')) is not int or len(raw)!=row['bytes']:raise PackError(f'{path.name}: byte mismatch {rel}')
            if not isinstance(row.get('sha256'),str) or sha(raw)!=row['sha256'].lower():raise PackError(f'{path.name}: sha mismatch {rel}')
            if empty:
                marker=rel+'.empty.json'
                if raw or marker not in names:raise PackError(f'{path.name}: empty proof missing for {rel}')
                check_empty_proof(z.read(marker),coord);declared.add(marker)
            else:
                if not raw:raise PackError(f'{path.name}: unexpected empty {rel}')
                parse_tile(raw)
            checked.append({'path':rel,'bytes':len(raw),'empty':empty,'sha256':sha(raw)})
        if {i.filename for i in infos if not i.is_dir()}!=declared:raise PackError('ZIP contains undeclared files')
        return meta,checked

def extract_chunk(path:Path,expected:dict,output:Path):
    meta,checked=inspect_chunk(path,expected)
    with zipfile.ZipFile(path) as z:
        for row in checked:
            rel=Path(*PurePosixPath(row['path']).parts);dest=output/rel
            raw=z.read(row['path'])
            marker=row['path']+'.empty.json'
            if row['empty']:
                # The coordinate proof is ready before the zero-byte tile.
                atomic_bytes(output/Path(*PurePosixPath(marker).parts),z.read(marker))
                atomic_bytes(dest,raw)
            else:
                atomic_bytes(dest,raw)
                (output/Path(*PurePosixPath(marker).parts)).unlink(missing_ok=True)
    return {'name':path.name,'source':expected['source'],'cursor':expected['cursor'],'rows':len(checked),'empty':sum(x['empty'] for x in checked),'bytes':sum(x['bytes'] for x in checked),'chunkSha256':sha(path.read_bytes())}

def validate_local(output:Path,vector_manifest:Path):
    m=json.loads(vector_manifest.read_text());missing=[];invalid=[];empty=objects=bytes_total=0;started=time.perf_counter()
    for row in m['tiles']:
        dest=output/row['local'].replace('data/map_pack/','');marker=dest.with_suffix(dest.suffix+'.empty.json')
        if not dest.exists():missing.append(row['key']);continue
        try:
            valid,meta=validate_tile(dest,row.get('sha256'),row)
            if not valid:raise PackError(meta['error'])
            if meta['empty']:
                empty+=1
            else:
                objects+=1;bytes_total+=meta['bytes']
        except Exception as e:invalid.append({'key':row['key'],'error':str(e)})
    return {'coordinates':len(m['tiles']),'objects':objects,'officialEmpty':empty,'missing':len(missing),'invalid':len(invalid),'bytes':bytes_total,'seconds':round(time.perf_counter()-started,3),'missingSample':missing[:20],'invalidSample':invalid[:20],'ok':not missing and not invalid and objects+empty==len(m['tiles'])}

def copy_bundled_terrain(output:Path):
    """Install already supplied terrain into a separate --output, offline."""
    from install_terrain_v039 import validate_bytes, DEFAULT_MANIFEST, DEFAULT_OUTPUT as bundled
    if output.resolve()==bundled.resolve():return []
    manifest=json.loads(DEFAULT_MANIFEST.read_text(encoding='utf-8'));copied=[]
    for region in manifest['regions']:
        dest=output/f"{region['macro']}.json"
        if dest.is_file():
            try:validate_bytes(dest.read_bytes(),region,manifest);continue
            except (OSError,ValueError,RuntimeError,TypeError,AttributeError):pass
        source=bundled/dest.name
        if not source.is_file():continue
        raw=source.read_bytes();clean,meta=validate_bytes(raw,region,manifest)
        proof_path=source.with_suffix('.proof.json')
        proof=json.loads(proof_path.read_text()) if proof_path.is_file() else {}
        if not isinstance(proof,dict):raise PackError('invalid bundled terrain proof')
        if proof.get('sha256') and proof['sha256']!=sha(raw):raise PackError('bundled terrain SHA-256 mismatch')
        atomic_bytes(dest,clean)
        atomic_json(dest.with_suffix('.proof.json'),{**proof,**meta,'verification':'copied from validated bundled terrain'})
        copied.append(region['macro'])
    return copied

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',type=Path,default=DEFAULT_MANIFEST);ap.add_argument('--vector-manifest',type=Path,default=VECTOR_MANIFEST);ap.add_argument('--output',type=Path,default=DEFAULT_OUTPUT)
    ap.add_argument('--source',choices=['all','base','cadastre'],default='all');ap.add_argument('--workers',type=int,default=3);ap.add_argument('--timeout',type=int,default=120);ap.add_argument('--retries',type=int,default=4);ap.add_argument('--verify-only',action='store_true');ap.add_argument('--keep-chunks',action='store_true');ap.add_argument('--skip-terrain',action='store_true');ap.add_argument('--chunk-dir',type=Path);ap.add_argument('--limit-chunks',type=int,default=0)
    ap.add_argument('--offline',action='store_true',help='Use only validated local ZIPs and terrain; never contact a remote service')
    a=ap.parse_args();a.output=a.output.resolve()
    if a.timeout<=0 or a.retries<1:ap.error('--timeout and --retries must be positive')
    if a.chunk_dir is None and (a.offline or a.manifest.resolve()==BUNDLED_MANIFEST.resolve()):a.chunk_dir=BUNDLED_CHUNKS
    manifest=json.loads(a.manifest.read_text());chunks=[c for c in manifest['chunks'] if a.source=='all' or c['source']==a.source]
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
        if a.offline and not a.verify_only:
            try:
                copied=copy_bundled_terrain(a.output/'terrain')
                if copied:print(f"Reliefs fournis copiés : {len(copied)}",flush=True)
            except Exception as e:errors.append({'terrain':'bundled','error':repr(e)})
        cmd=[sys.executable,str(ROOT/'tools/install_terrain_v039.py'),'--output',str(a.output/'terrain'),'--timeout',str(a.timeout),'--retries',str(a.retries)]
        if a.offline:cmd.append('--offline')
        if a.verify_only:cmd.append('--verify-only')
        else:cmd += ['--workers',str(max(1,min(a.workers,8)))]
        rc=subprocess.run(cmd,cwd=ROOT)
        terrain={'returncode':rc.returncode,'ok':rc.returncode==0}
    status={'version':'0.41.0','generated':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source':a.source,'chunksExpected':len(chunks),'chunksInstalled':len(reports) if not a.verify_only else None,'chunkErrors':errors,'vector':audit,'terrain':terrain,'seconds':round(time.time()-started,2),'complete':not errors and audit['ok'] and (terrain is None or terrain['ok'])}
    atomic_json(a.output/'local_pack_v041_status.json',status)
    if not a.keep_chunks and not errors and not a.verify_only:shutil.rmtree(cache,ignore_errors=True)
    print(json.dumps(status,ensure_ascii=False,indent=2));return 0 if status['complete'] else 1
if __name__=='__main__':raise SystemExit(main())
