#!/usr/bin/env python3
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'fixtures'; OUT.mkdir(parents=True,exist_ok=True)

def vi(n:int)->bytes:
    n=int(n); b=bytearray()
    while True:
        x=n&0x7f; n >>= 7
        if n: b.append(x|0x80)
        else: b.append(x); return bytes(b)

def field_var(n,v): return vi((n<<3)|0)+vi(v)
def field_len(n,b): return vi((n<<3)|2)+vi(len(b))+b
def zig(n): return (n<<1)^(n>>31)

def value(v):
    if isinstance(v,str): return field_len(1,v.encode())
    if isinstance(v,bool): return field_var(7,int(v))
    if isinstance(v,int): return field_var(4,v)
    if isinstance(v,float): return vi((3<<3)|1)+struct.pack('<d',v)
    raise TypeError(v)

def geom_line(points):
    out=[]; x=y=0
    out.append((1<<3)|1)
    nx,ny=points[0]; out += [zig(nx-x),zig(ny-y)]; x,y=nx,ny
    out.append(((len(points)-1)<<3)|2)
    for nx,ny in points[1:]: out += [zig(nx-x),zig(ny-y)]; x,y=nx,ny
    return out

def geom_polygon(rings):
    out=[]; x=y=0
    for ring in rings:
        pts=ring[:-1] if ring[0]==ring[-1] else ring
        out.append((1<<3)|1)
        nx,ny=pts[0]; out += [zig(nx-x),zig(ny-y)]; x,y=nx,ny
        out.append(((len(pts)-1)<<3)|2)
        for nx,ny in pts[1:]: out += [zig(nx-x),zig(ny-y)]; x,y=nx,ny
        out.append((1<<3)|7)
    return out

def packed(nums): return b''.join(vi(n) for n in nums)

def layer(name,features,extent=4096):
    keys=[]; vals=[]; key_index={}; val_index={}; fmsgs=[]
    for fid,ftype,props,geom in features:
        tags=[]
        for k,v in props.items():
            if k not in key_index: key_index[k]=len(keys); keys.append(k)
            vk=(type(v).__name__,v)
            if vk not in val_index: val_index[vk]=len(vals); vals.append(v)
            tags += [key_index[k],val_index[vk]]
        fm=field_var(1,fid)+field_len(2,packed(tags))+field_var(3,ftype)+field_len(4,packed(geom))
        fmsgs.append(fm)
    body=field_len(1,name.encode())
    for fm in fmsgs: body += field_len(2,fm)
    for k in keys: body += field_len(3,k.encode())
    for v in vals: body += field_len(4,value(v))
    body += field_var(5,extent)+field_var(15,2)
    return body

def tile(layers):
    return b''.join(field_len(3,l) for l in layers)

# z14 base fixture: two continuous roads, rail, park, water and one coarse building
transport=[
 (1,2,{'class':'primary','name':'Axe cadastral QA'},geom_line([(120,2100),(1000,2050),(2050,1980),(3200,1850),(4000,1800)])),
 (2,2,{'class':'residential','name':'Rue irrégulière QA'},geom_line([(900,400),(1050,1200),(1000,2050),(1250,3100),(1600,4000)])),
 (3,2,{'class':'rail','subclass':'rail'},geom_line([(250,2600),(1250,2500),(2400,2450),(3900,2550)])),
]
park_ring=[(300,300),(1700,260),(1850,1000),(1250,1500),(380,1330),(300,300)]
water_ring=[(2650,2900),(4090,2850),(4090,4090),(2400,4090),(2480,3400),(2650,2900)]
land_ring=[(2100,200),(4050,200),(3980,1250),(3300,1150),(2700,1450),(2100,200)]
bld_ring=[(2050,1600),(2450,1500),(2600,1900),(2200,2070),(2050,1600)]
base=tile([
 layer('transportation',transport),
 layer('park',[(10,3,{'class':'park'},geom_polygon([park_ring]))]),
 layer('water',[(11,3,{'class':'lake'},geom_polygon([water_ring]))]),
 layer('landuse',[(12,3,{'class':'residential'},geom_polygon([land_ring]))]),
 layer('building',[(13,3,{'render_height':12.0},geom_polygon([bld_ring]))]),
])
(OUT/'france-vector-z14-8437-6001.pbf').write_bytes(base)

# z16 cadastre fixture: 18 irregular and L-shaped building footprints
features=[]
for i in range(18):
    col=i%6; row=i//6; ox=350+col*560; oy=500+row*1000
    if i%3==0:
        r=[(ox,oy),(ox+390,oy+20),(ox+380,oy+260),(ox+220,oy+250),(ox+220,oy+440),(ox,oy+430),(ox,oy)]
    elif i%3==1:
        r=[(ox,oy),(ox+430,oy+40),(ox+400,oy+360),(ox+120,oy+410),(ox-20,oy+220),(ox,oy)]
    else:
        r=[(ox,oy),(ox+360,oy),(ox+430,oy+190),(ox+300,oy+420),(ox+30,oy+390),(ox-40,oy+160),(ox,oy)]
    features.append((100+i,3,{'id':f'QA-{i:02d}'},geom_polygon([r])))
cad=tile([layer('batiments',features)])
(OUT/'cadastre-z16-33750-24006.pbf').write_bytes(cad)
print(OUT)
print('base',len(base),'cadastre',len(cad))
