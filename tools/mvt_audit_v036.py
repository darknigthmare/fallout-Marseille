#!/usr/bin/env python3
"""Minimal, dependency-free Mapbox Vector Tile reader used by the v0.36 installer.

It validates protobuf structure, lists layers/features and decodes geometry commands
well enough to audit road/building seams. It intentionally does not interpret every
attribute or render the data.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
import hashlib, json

class MVTError(ValueError): pass

def read_varint(data:bytes,pos:int)->tuple[int,int]:
 value=0;shift=0
 for _ in range(10):
  if pos>=len(data):raise MVTError('truncated varint')
  b=data[pos];pos+=1;value|=(b&0x7f)<<shift
  if not b&0x80:return value,pos
  shift+=7
 raise MVTError('varint too long')

def fields(data:bytes)->Iterable[tuple[int,int,object]]:
 pos=0
 while pos<len(data):
  key,pos=read_varint(data,pos);number=key>>3;wire=key&7
  if not number:raise MVTError('field number zero')
  if wire==0:
   value,pos=read_varint(data,pos);yield number,wire,value
  elif wire==1:
   if pos+8>len(data):raise MVTError('truncated fixed64')
   yield number,wire,data[pos:pos+8];pos+=8
  elif wire==2:
   size,pos=read_varint(data,pos)
   if size<0 or pos+size>len(data):raise MVTError('truncated bytes')
   yield number,wire,data[pos:pos+size];pos+=size
  elif wire==5:
   if pos+4>len(data):raise MVTError('truncated fixed32')
   yield number,wire,data[pos:pos+4];pos+=4
  else:raise MVTError(f'unsupported wire type {wire}')

def zigzag(n:int)->int:return (n>>1)^(-(n&1))

@dataclass
class Feature:
 fid:int|None=None
 tags:list[int]=field(default_factory=list)
 geom_type:int=0
 geometry:list[int]=field(default_factory=list)

@dataclass
class Layer:
 name:str=''
 version:int=1
 extent:int=4096
 keys:list[str]=field(default_factory=list)
 values:list[object]=field(default_factory=list)
 features:list[Feature]=field(default_factory=list)

def parse_value(raw:bytes):
 for n,w,v in fields(raw):
  if n==1 and w==2:return v.decode('utf-8','replace')
  if n in (4,5,6) and w==0:return int(v)
  if n==7 and w==0:return bool(v)
 return None

def parse_feature(raw:bytes)->Feature:
 f=Feature()
 for n,w,v in fields(raw):
  if n==1 and w==0:f.fid=int(v)
  elif n==2 and w==2:
   p=0
   while p<len(v):x,p=read_varint(v,p);f.tags.append(x)
  elif n==3 and w==0:f.geom_type=int(v)
  elif n==4 and w==2:
   p=0
   while p<len(v):x,p=read_varint(v,p);f.geometry.append(x)
 if len(f.tags)%2:raise MVTError('odd feature tags')
 if f.geom_type not in (0,1,2,3):raise MVTError('invalid geometry type')
 return f

def parse_layer(raw:bytes)->Layer:
 l=Layer()
 for n,w,v in fields(raw):
  if n==1 and w==2:l.name=v.decode('utf-8','replace')
  elif n==2 and w==2:l.features.append(parse_feature(v))
  elif n==3 and w==2:l.keys.append(v.decode('utf-8','replace'))
  elif n==4 and w==2:l.values.append(parse_value(v))
  elif n==5 and w==0:l.extent=int(v)
  elif n==15 and w==0:l.version=int(v)
 if not l.name:raise MVTError('layer without name')
 if not 1<=l.extent<=65536:raise MVTError('invalid extent')
 return l

def parse_tile(data:bytes)->dict[str,Layer]:
 if len(data)<2:raise MVTError('empty tile')
 head=data[:64].lstrip().lower()
 if head.startswith(b'<') or head.startswith(b'{'):raise MVTError('HTML/JSON instead of PBF')
 out={}
 for n,w,v in fields(data):
  if n==3 and w==2:
   layer=parse_layer(v)
   if layer.name in out:raise MVTError(f'duplicate layer {layer.name}')
   out[layer.name]=layer
 if not out:raise MVTError('no layers')
 return out

def attributes(layer:Layer,feature:Feature)->dict:
 out={}
 for i in range(0,len(feature.tags),2):
  k,v=feature.tags[i:i+2]
  if k<len(layer.keys) and v<len(layer.values):out[layer.keys[k]]=layer.values[v]
 return out

def decode_geometry(feature:Feature)->list[list[tuple[int,int]]]:
 g=feature.geometry;i=0;x=y=0;paths=[];path=[]
 while i<len(g):
  command=g[i];i+=1;cmd=command&7;count=command>>3
  if count<=0 or count>1_000_000:raise MVTError('invalid geometry command count')
  if cmd in (1,2):
   if i+count*2>len(g):raise MVTError('truncated geometry')
   for _ in range(count):
    dx=zigzag(g[i]);dy=zigzag(g[i+1]);i+=2;x+=dx;y+=dy
    if cmd==1:
     if path:paths.append(path)
     path=[(x,y)]
    else:
     if not path:raise MVTError('LineTo without MoveTo')
     path.append((x,y))
  elif cmd==7:
   if path and path[-1]!=path[0]:path.append(path[0])
  else:raise MVTError(f'unsupported geometry command {cmd}')
 if path:paths.append(path)
 return paths

def tile_summary(path:Path,decode=False)->dict:
 data=path.read_bytes();layers=parse_tile(data);rows={};
 for name,l in layers.items():
  row={'features':len(l.features),'points':0,'lines':0,'polygons':0,'extent':l.extent}
  for f in l.features:
   if f.geom_type==1:row['points']+=1
   elif f.geom_type==2:row['lines']+=1
   elif f.geom_type==3:row['polygons']+=1
   if decode:decode_geometry(f)
  rows[name]=row
 return {'file':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'layers':rows,'featureCount':sum(x['features'] for x in rows.values())}

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('files',nargs='+',type=Path);p.add_argument('--decode',action='store_true');p.add_argument('--json',type=Path)
 a=p.parse_args();result=[];errors=[]
 for f in a.files:
  try:result.append(tile_summary(f,a.decode))
  except Exception as e:errors.append({'file':str(f),'error':repr(e)})
 out={'tiles':result,'errors':errors}
 text=json.dumps(out,ensure_ascii=False,indent=2)
 if a.json:a.json.write_text(text,encoding='utf-8')
 else:print(text)
 raise SystemExit(bool(errors))
if __name__=='__main__':main()
