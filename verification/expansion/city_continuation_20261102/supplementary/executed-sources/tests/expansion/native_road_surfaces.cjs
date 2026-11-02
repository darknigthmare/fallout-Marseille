#!/usr/bin/env node
'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const ROOT=path.resolve(__dirname,'../..'),M=require('../../src/v050/14_precise_terrain.js'),I=require('../../src/v046/00_integrity.js');
const vertices=[[0,.085,0],[12,.085,0],[0,.085,6],[12,.085,6]],faces=[[0,2,1],[1,2,3]];
const native=height=>({height,sourceResource:M.resource,sources:['synthetic-native'],verticalDatum:'NGF-IGN69',resolutionMeters:[.5,.5]});
const area=(v,f)=>f.reduce((sum,ids)=>{const[a,b,c]=ids.map(i=>v[i]);return sum+Math.abs((b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0]))/2;},0);
function error(mesh,read){return Math.max(0,...mesh.faces.map(f=>{const p=f.map(i=>mesh.vertices[i]),x=p.reduce((n,v)=>n+v[0],0)/3,z=p.reduce((n,v)=>n+v[2],0)/3;return Math.abs(read(x,z).height+.085-p.reduce((n,v)=>n+v[1],0)/3);}));}
test('Native road refinement preserves the original XY footprint, winding and immutable inputs',()=>{
 const before=JSON.stringify({vertices,faces}),r=M.roadSurface(vertices,faces,(x,z)=>native(.4*Math.sin(x/3)+.05*z*z));
 assert.equal(JSON.stringify({vertices,faces}),before);assert.ok(r.faces.length>faces.length);assert.ok(Math.abs(area(r.vertices,r.faces)-area(vertices,faces))<1e-9);
 for(const f of r.faces){const[a,b,c]=f.map(i=>r.vertices[i]);assert.ok((b[0]-a[0])*(c[2]-a[2])-(b[2]-a[2])*(c[0]-a[0])<0);}
 for(const v of r.vertices)assert.ok(v[0]>=0&&v[0]<=12&&v[2]>=0&&v[2]<=6);
});
test('Each published native road vertex uses the current terrain source plus its declared visual offset',()=>{
 const read=(x,z)=>native(.4*Math.sin(x/3)+.05*z*z),r=M.roadSurface(vertices,faces,read);
 for(const v of r.vertices)assert.ok(Math.abs(v[1]-read(v[0],v[2]).height-.085)<1e-10);
 assert.equal(r.stats.visualOffsetMeters,.085);assert.equal(r.sources[0].verticalDatum,'NGF-IGN69');
});
test('Ground bumps absent from sparse edge elevations cause actual additional geometry',()=>{
 const read=(x,z)=>native(Math.sin(Math.PI*x/12)*Math.sin(Math.PI*z/6)),r=M.roadSurface(vertices,faces,read);
 assert.ok(r.stats.splits>0);assert.ok(r.vertices.some(v=>v[1]>.8));assert.ok(error(r,read)<error({vertices,faces},read)/4);
});
test('Coarse-only representation is not relabeled as a native road surface',()=>{
 const r=M.roadSurface(vertices,faces,()=>({height:0,sourceResource:'old-coarse'}));assert.equal(r.stats.nativeSamples,0);assert.equal(r.stats.splits,0);assert.equal(r.faces.length,2);
});
test('Adaptive shared-edge partitions are propagated without T joins or vertical cracks',()=>{
 const r=M.roadSurface(vertices,faces,(x,z)=>native(x<7?Math.sin(x*1.3)*.4:0));assert.ok(r.stats.conformitySplits>0);
 const heights=new Map();for(const p of r.vertices){const k=p[0]+':'+p[2];if(heights.has(k))assert.equal(p[1],heights.get(k));heights.set(k,p[1]);}
 for(const f of r.faces)for(let j=0;j<3;j++){const a=r.vertices[f[j]],b=r.vertices[f[(j+1)%3]],dx=b[0]-a[0],dz=b[2]-a[2],length=dx*dx+dz*dz;for(const p of r.vertices){const t=((p[0]-a[0])*dx+(p[2]-a[2])*dz)/length;if(t>1e-7&&t<1-1e-7)assert.ok(Math.abs((p[0]-a[0])*dz-(p[2]-a[2])*dx)>1e-7,'No published vertex remains inside an unsplit shared edge');}}
});
test('Native NoData inside an initially valid sparse triangle is omitted after bounded subdivision',()=>{
 const r=M.roadSurface(vertices,faces,(x,z)=>native(x>4&&x<8&&z>2&&z<4?null:1));assert.ok(r.stats.omittedNoDataFaces>0);assert.ok(r.stats.noDataSamples>0);assert.ok(area(r.vertices,r.faces)<area(vertices,faces));
 for(const p of r.vertices)assert.equal(p[1],1.085);
 for(const f of r.faces){const points=f.map(i=>r.vertices[i]),x=points.reduce((n,p)=>n+p[0],0)/3,z=points.reduce((n,p)=>n+p[2],0)/3;assert.ok(!(x>4&&x<8&&z>2&&z<4));}
});
test('The entire road is absent when native support is unavailable instead of using zero altitude',()=>{
 const r=M.roadSurface(vertices,faces,()=>native(null));assert.equal(r.faces.length,0);assert.equal(r.vertices.length,0);assert.ok(r.stats.omittedNoDataFaces>0);
});
test('A strict adaptive split budget is explicit and retains valid unresolved geometry',()=>{
 const r=M.roadSurface(vertices,faces,(x,z)=>native(Math.sin(x*3)+Math.cos(z*2)),{maxSplits:2});assert.equal(r.stats.splits,2);assert.ok(r.stats.budgetLimitedFaces>0);assert.equal(area(r.vertices,r.faces),72);assert.ok(r.faces.length<=faces.length+6);
});
test('The minimum edge limit honestly reports residual detail instead of claiming the tolerance was met',()=>{
 const r=M.roadSurface(vertices,faces,(x,z)=>native(Math.sin(x*3)+Math.cos(z*2)));assert.ok(r.stats.resolutionLimitedFaces>0);assert.ok(r.stats.maxAdaptiveLeafProbeErrorMeters>r.stats.toleranceMeters);assert.ok(r.stats.splits<=r.stats.maximumSplits);
});
test('Malformed faces, vertices or budgets fail before publishing geometry',()=>{
 for(const f of [[[0,1,99]],[[0,1,NaN]],[[0,1]]])assert.throws(()=>M.roadSurface(vertices,f,()=>native(0)));
 assert.throws(()=>M.roadSurface([[0,0],vertices[1],vertices[2]],[[0,1,2]],()=>native(0)));
 for(const o of [{tolerance:0},{minEdge:0},{maxEdge:.5},{maxSplits:-1},{maxSplits:9000}])assert.throws(()=>M.roadSurface(vertices,faces,()=>native(0),o));
});
function wrapper(base,bank){
 const context=vm.createContext({M,sourceBase:base,V046:{terrain:bank},v015GeoUnproject:(_id,x,z)=>[x,z]});
 vm.runInContext('let v046SourceRoad=sourceBase;',context);
 const code=fs.readFileSync(path.join(ROOT,'src/v050/14_precise_terrain.js'),'utf8');vm.runInContext(code.slice(code.indexOf(' const sourceRoad='),code.indexOf(' async function ready()')),context);
 return context;
}
test('Production wrapper excludes measured decks, tunnels and ordinary unrefined source roads',()=>{
 for(const profile of [{bridge:true},{tunnel:true},{surfaceDerived:false}]){const d={vertices,faces,sourceProfile:profile},w={id:'real-sector',staticDraws:[d]},c=wrapper(()=>d,{grids:new Map([['native',{v054Native:true}]])});c.w=w;assert.equal(vm.runInContext('v046SourceRoad(w,[],{},[],"tile","transportation")',c),d);assert.equal(d.vertices,vertices);}
});
test('Production staging wrapper publishes a refined draw and preserves the exact source axis and receipt',()=>{
 const axis=[[0,0,8],[12,0,9]],d={vertices,faces,roadPath:axis,sourceGeometry:{type:'LineString',coordinates:axis},sourceProfile:{surfaceDerived:true,sourceXYZPreserved:true}},bank={grids:new Map([['native',{v054Native:true}]]),read:(x,z)=>native(Math.sin(x/2))},w={id:'real-sector',v047TerrainBank:bank,staticDraws:[d]},c=wrapper(()=>d,bank);c.w=w;
 assert.equal(vm.runInContext('v046SourceRoad(w,[],{},[],"tile","transportation")',c),d);assert.equal(w.staticDraws.length,1);assert.equal(d.roadPath,axis);assert.equal(d.sourceGeometry.coordinates,axis);assert.equal(d.sourceProfile.sourceXYZPreserved,true);assert.ok(d.sourceProfile.surfaceNativeRefinement.outputFaces>2);
});
test('A staged road with entirely missing native terrain is removed without touching the live scene',()=>{
 const d={vertices,faces,sourceProfile:{surfaceDerived:true}},bank={grids:new Map([['native',{v054Native:true}]]),read:()=>native(null)},w={id:'stage',staticDraws:[d]},live={staticDraws:['keep']},c=wrapper(()=>d,bank);c.w=w;
 assert.equal(vm.runInContext('v046SourceRoad(w,[],{},[],"tile","transportation")',c),null);assert.equal(w.staticDraws.length,0);assert.deepEqual(live.staticDraws,['keep']);
});
test('The actual static GPU packer splits refined road geometry below the WebGL Uint16 limit',()=>{
 const r=M.roadSurface(vertices,faces,(x,z)=>native(Math.sin(x/2))),source=fs.readFileSync(path.join(ROOT,'src/core-v017.js'),'utf8'),context=vm.createContext({});vm.runInContext(source.slice(source.indexOf('class GLStaticGeometryBatches'),source.indexOf('// END GL_STATIC_GEOMETRY_BATCHES'))+'\nglobalThis.P=GLStaticGeometryBatches;',context);
 const draw={vertices:r.vertices,faces:r.faces,color:[.5,.5,.5]},sources=Array.from({length:2000},()=>draw),pack=new context.P(d=>[{positions:d.vertices.flat(),normals:d.vertices.flatMap(()=>[0,1,0]),indices:d.faces.flat()}],()=>{},()=>{}),chunks=pack.pack(sources,sources.map(d=>pack.stamp(d)));
 assert.ok(chunks.length>1);assert.equal(chunks.reduce((n,c)=>n+c.indices.length,0),2000*r.faces.length*3);for(const c of chunks){assert.ok(c.positions.length/3<=54000);assert.ok(c.indices.every(i=>i<54000));assert.deepEqual(Array.from(new Uint16Array(c.indices)),Array.from(c.indices));}
});
test('The actual retained Vieux-Port source route follows the real installed native LiDAR without changing its geometry',()=>{
 const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures/vieux_port_road_ground.json'))),feature=fixture.feature,before=JSON.stringify(feature),context=vm.createContext({rad:n=>n*Math.PI/180}),patch=fs.readFileSync(path.join(ROOT,'src/patches/01_geometry.js'),'utf8');vm.runInContext(patch.slice(patch.indexOf('function v018Lambert93'),patch.indexOf('const V018_OLD_SCALES')),context);
 const axis=feature.geometry.coordinates.map(p=>{const v=context.v018Lambert93(p[1],p[0]);return[v[0],-v[1]];}),atlas=JSON.parse(fs.readFileSync(path.join(ROOT,'data/map_pack/precise/index.json'))),grids=[];
 for(const d of atlas.tiles)if(axis.some(p=>p[0]>=d.nativeBounds[0]-30&&p[0]<=d.nativeBounds[2]+30&&-p[1]>=d.nativeBounds[1]-30&&-p[1]<=d.nativeBounds[3]+30)){const b=fs.readFileSync(path.join(ROOT,d.path));grids.push(M.decode(b.buffer.slice(b.byteOffset,b.byteOffset+b.length),d,atlas.provenance));}
 const read=(x,z)=>{for(const g of grids){const r=M.sample(g,x,-z);if(r.inside)return{height:r.height,sourceResource:M.resource,sources:[g.id],resolutionMeters:[.5,.5],verticalDatum:'NGF-IGN69'};}return{};},mesh=I.roadMesh(axis,feature.properties,(x,z)=>read(x,z).height),r=M.roadSurface(mesh.vertices,mesh.faces,read);
 assert.equal(JSON.stringify(feature),before);assert.equal(feature.id,'troncon_de_route.6003809');assert.equal(mesh.faces.length,14);assert.ok(r.faces.length>mesh.faces.length);assert.equal(r.stats.noDataSamples,0);assert.equal(r.stats.budgetLimitedFaces,0);assert.ok(error(mesh,read)>.2);assert.ok(error(r,read)<.06);assert.ok(error(r,read)<error(mesh,read)/3);assert.ok(Math.abs(area(r.vertices,r.faces)-area(mesh.vertices,mesh.faces))<1e-5);
 for(const p of r.vertices)assert.ok(Math.abs(p[1]-read(p[0],p[2]).height-.085)<1e-10);
});
