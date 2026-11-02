#!/usr/bin/env node
'use strict';
// Execute production batching, tessellation and renderer code with a recording
// GL interface. Native browser coverage separately verifies the actual driver.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'../..');
const core=fs.readFileSync(path.join(root,'src/core-v017.js'),'utf8');
const geometry=fs.readFileSync(path.join(root,'src/patches/01_geometry.js'),'utf8');
const context=vm.createContext({console,TAU:Math.PI*2,COLORS:{white:[1,1,1]},world:{v046:true,geoMacro:true,id:'geo_huveaune'},rad:n=>n*Math.PI/180});
vm.runInContext(core.slice(core.indexOf('function v3('),core.indexOf('class SoftwareRenderer')),context);
for(const name of ['v017SignedArea','v017PointInPoly'])vm.runInContext(core.split('\n').find(line=>line.startsWith('function '+name+'(')),context);
vm.runInContext(geometry.slice(0,geometry.indexOf('/* The software fallback')),context);
vm.runInContext(fs.readFileSync(path.join(__dirname,'renderer_terrain_fixture.js'),'utf8'),context);
vm.runInContext('globalThis.Batch=GLStaticGeometryBatches;globalThis.Renderer=GLRenderer;globalThis.meshData=v018MeshData;globalThis.renderInfo=()=>({...V018.render});',context);
const plain=x=>JSON.parse(JSON.stringify(x));
let checks=0;
function test(name,fn){fn();checks++;console.log('OK '+name);}
function prism(id,color=[.6,.5,.4]){
  return {mesh:'prism',v046Tile:'cadastre:16:33700:24000',pos:[20+id*12,2,20],baseY:0,height:4,
    rings:[[[id*12,0],[id*12+10,0],[id*12+10,10],[id*12,10],[id*12,0]],
      [[id*12+3,3],[id*12+3,7],[id*12+7,7],[id*12+7,3],[id*12+3,3]]],color};
}
function recorder(geometryFn=context.meshData){
  const uploaded=[],deleted=[];
  const cache=new context.Batch(geometryFn,data=>{const m={id:uploaded.length,data,count:data.indices.length};uploaded.push(m);return m;},m=>deleted.push(m));
  return {cache,uploaded,deleted};
}
const candidate=d=>!!d.v046Tile&&!d.hidden&&(d.alpha??1)===1;
function stream(data,color){
  const out=[];
  for(const part of data)for(const index of part.indices)out.push([
    ...part.positions.slice(index*3,index*3+3),...part.normals.slice(index*3,index*3+3),
    ...(part.colors?part.colors.slice(index*3,index*3+3):color)]);
  return plain(out);
}
const a=prism(0),b=prism(1,[.713,.292,.419]);
const first=recorder();
let plan=first.cache.prepare([a,b],candidate);
test('Different building colors share one GPU upload',()=>assert.equal(first.uploaded.length,1));
test('Batch retains both source features',()=>assert.deepEqual(plain(first.cache.stats),{groups:1,sources:2,uploads:1,builds:1,hits:0}));
test('Every source triangle, normal and exact RGB is retained in order',()=>assert.deepEqual(stream([first.uploaded[0].data]),[...stream(context.meshData(a),a.color),...stream(context.meshData(b),b.color)]));
test('Source rings and source material arrays remain unchanged',()=>{assert.equal(a.rings[0].length,5);assert.deepEqual(a.color,[.6,.5,.4]);assert.equal(a.mesh,'prism');});
test('A source courtyard remains open after batching',()=>{
  const data=first.uploaded[0].data;let area=0;
  for(let i=0;i<data.positions.length;i+=9){
    const p=data.positions.slice(i,i+9);
    if(p[1]===4&&p[4]===4&&p[7]===4)area+=Math.abs((p[3]-p[0])*(p[8]-p[2])-(p[6]-p[0])*(p[5]-p[2]))/2;
  }
  assert.equal(area,2*(100-16));
});
test('An unchanged scene reuses buffers without uploading',()=>{first.cache.prepare([a,b],candidate);assert.equal(first.uploaded.length,1);assert.equal(first.cache.stats.hits,1);});
test('A height revision refreshes the GPU batch',()=>{b.height=9;first.cache.prepare([a,b],candidate);assert.equal(first.uploaded.length,2);assert.equal(first.deleted.length,1);assert.ok(first.uploaded[1].data.positions.includes(9));});
test('Replacing geometry references invalidates without stale triangles',()=>{b.rings=b.rings.map(r=>r.map(([x,z])=>[x+1,z]));first.cache.prepare([a,b],candidate);assert.equal(first.uploaded.length,3);assert.equal(first.deleted.length,2);});
test('In-place source edits are honored when revision advances',()=>{b.rings[0][0][0]+=.25;b.revision=1;first.cache.prepare([a,b],candidate);assert.equal(first.uploaded.length,4);});
test('In-place color changes refresh per-vertex materials',()=>{a.color[0]=.234;first.cache.prepare([a,b],candidate);assert.equal(first.uploaded.length,5);assert.equal(first.uploaded[4].data.colors[0],.234);});
const transparent={...prism(2),alpha:.5};
test('Transparent geometry breaks batches and retains its render position',()=>{
  const r=recorder(),p=r.cache.prepare([a,b,transparent,prism(3),prism(4)],candidate);
  assert.equal(p.length,3);assert.equal(p[1],transparent);assert.equal(r.uploaded.length,2);
});
test('Tile ownership remains separate for streaming invalidation',()=>{
  const r=recorder(),c=prism(3),d=prism(4);c.v046Tile=d.v046Tile='cadastre:16:33701:24000';
  r.cache.prepare([a,b,c,d],candidate);assert.equal(r.cache.entries.size,2);
  r.cache.prepare([c,d],candidate);assert.equal(r.cache.entries.size,1);assert.equal(r.deleted.length,1);
});
test('One source is left on the existing individual renderer path',()=>{const r=recorder();assert.equal(r.cache.prepare([a],candidate)[0],a);assert.equal(r.uploaded.length,0);});
test('Provenance metadata cannot be mistaken for a generated batch run',()=>{const r=recorder(),d={mesh:'cube',sources:['IGN']};assert.equal(r.cache.prepare([d],candidate)[0],d);assert.equal(r.uploaded.length,0);});
test('No hidden source creates a batch upload',()=>{const r=recorder();r.cache.prepare([{...a,hidden:true},{...b,hidden:true}],candidate);assert.equal(r.uploaded.length,0);});
test('Removing a scene releases every owned GPU upload',()=>{first.cache.prepare([],candidate);assert.equal(first.deleted.length,first.uploaded.length);assert.equal(first.cache.entries.size,0);});
test('Cache clear is idempotent',()=>{const r=recorder();r.cache.prepare([a,b],candidate);r.cache.clear();r.cache.clear();assert.equal(r.deleted.length,1);});
test('WebGL 1 chunk bounds retain all triangles without index wrapping',()=>{
  const vertices=60000,positions=Array(vertices*3).fill(0),normals=Array(vertices*3).fill(0),indices=Array.from({length:vertices},(_,i)=>i);
  for(let i=0;i<vertices;i++){positions[i*3]=i;normals[i*3+1]=1;}
  const data={positions,normals,indices},r=recorder(()=>[data]);r.cache.prepare([prism(1),prism(2)],candidate);
  assert.equal(r.uploaded.reduce((n,m)=>n+m.count,0),vertices*2);
  assert.ok(r.uploaded.length>1);
  for(const m of r.uploaded){assert.ok(m.data.positions.length/3<=54000);assert.ok(m.data.indices.every(i=>i<65536));assert.equal(m.data.colors.length,m.data.positions.length);}
});
test('An invalid index cannot upload corrupt geometry',()=>{
  const r=recorder(()=>[{positions:[0,0,0],normals:[0,1,0],indices:[0,1,2]}]);
  assert.throws(()=>r.cache.prepare([a,b],candidate),/indice invalide/);assert.equal(r.uploaded.length,0);
});
test('Incomplete triangles fail before GPU upload',()=>{
  const r=recorder(()=>[{positions:[0,0,0],normals:[0,1,0],indices:[0,0]}]);
  assert.throws(()=>r.cache.prepare([a,b],candidate),/triangle incomplet/);assert.equal(r.uploaded.length,0);
});
test('A failed upload disposes newly allocated chunks and retains the old entry',()=>{
  const base=recorder(),old=base.cache.prepare([a,b],candidate)[0]._v018Batch;
  const dispose=[];let tries=0;base.cache.dispose=m=>dispose.push(m);base.cache.upload=data=>{if(++tries===2)throw new Error('GPU full');return{data};};
  base.cache.geometry=()=>[{positions:Array(54003*3).fill(0),normals:Array(54003*3).fill(1),indices:Array.from({length:54003},(_,i)=>i)}];
  a.revision=3;b.revision=3;
  assert.throws(()=>base.cache.prepare([a,b],candidate),/GPU full/);assert.equal(dispose.length,1);assert.equal([...base.cache.entries.values()][0],old);
});

// Integration: run the actual production render override, including buffer
// uploads, cleanup, shader attribute state and its batching eligibility rule.
function fakeRenderer(){
  const calls={draws:0,created:0,deleted:0,colorResets:0,alphas:[],vertexColorBinds:0};
  const gl=new Proxy({createBuffer:()=>({id:++calls.created}),deleteBuffer:()=>calls.deleted++,drawElements:()=>calls.draws++,
    uniform1f:(loc,value)=>{if(loc==='alpha')calls.alphas.push(value);},vertexAttrib3f:(loc,x,y,z)=>{if(loc===2&&x===0&&y===0&&z===0)calls.colorResets++;},
    vertexAttribPointer:loc=>{if(loc===2)calls.vertexColorBinds++;},getUniformLocation:()=>1},
    {get:(o,k)=>k in o?o[k]:typeof k==='string'&&k===k.toUpperCase()?1:()=>{}});
  const r=Object.create(context.Renderer.prototype);r.gl=gl;r.canvas={width:640,height:480};r.resize=()=>{};r.program={};r.loc={vertexColor:2,alpha:'alpha'};r.meshes={cube:{p:{},n:{},i:{},count:36}};
  return{r,calls};
}
const camera={pos:[1,20,35],dir:[0,0,-1]};
context.v028LampActive=()=>false;context.v028LampOrigin=()=>[0,0,0];
test('One hundred exact building materials render in one draw call',()=>{
  const f=fakeRenderer(),draws=Array.from({length:100},(_,i)=>prism(i,[.2+i/1000,.4,.6]));
  f.r.render(draws,camera,{});assert.equal(f.calls.draws,1);assert.equal(context.renderInfo().customMeshes,100);assert.equal(context.renderInfo().batchedMeshes,100);assert.equal(context.renderInfo().bufferGroups,1);
});
test('Color attributes are reset before rendering a normal primitive',()=>{
  const f=fakeRenderer();f.r.render([prism(0),prism(1),{mesh:'cube',pos:[0,0,0],scale:[1,1,1],color:[1,0,0]}],camera,{});
  assert.equal(f.calls.vertexColorBinds,1);assert.equal(f.calls.colorResets,1);assert.equal(f.calls.draws,2);
});
test('Transparent draw ordering and alpha uniforms are unchanged',()=>{
  const f=fakeRenderer();f.r.render([prism(0),prism(1),transparent,prism(3),prism(4)],camera,{});
  assert.deepEqual(f.calls.alphas,[1,.5,1]);assert.equal(f.calls.draws,3);
});
test('Wrist-light pieces remain individual; far pieces remain batchable',()=>{
  context.v028LampActive=()=>true;
  try{
    const f=fakeRenderer(),near=prism(0);near.pos=[0,0,0];
    f.r.render([near,prism(1),prism(2)],camera,{});
    assert.equal(f.r.geoMeshes.size,1);assert.equal(context.renderInfo().batchedMeshes,2);assert.equal(f.calls.draws,2);
  }finally{context.v028LampActive=()=>false;}
});
test('Historical geometry retains its individual renderer path',()=>{
  const f=fakeRenderer(),c=prism(0),d=prism(1);delete c.v046Tile;delete d.v046Tile;
  f.r.render([c,d],camera,{});assert.equal(f.r.geoMeshes.size,2);assert.equal(context.renderInfo().batchedMeshes,0);assert.equal(f.calls.draws,2);
});
test('Batch buffers, including vertex colors, are released after leaving a scene',()=>{
  const f=fakeRenderer();f.r.render([prism(0),prism(1)],camera,{});assert.equal(f.calls.created,4);
  f.r.render([],camera,{});assert.equal(f.calls.deleted,4);assert.equal(context.renderInfo().bufferGroups,0);
});
test('Renderer reuses unchanged uploads across frames',()=>{
  const f=fakeRenderer(),draws=[prism(0),prism(1)];f.r.render(draws,camera,{});f.r.render(draws,camera,{});
  assert.equal(f.calls.created,4);assert.equal(f.calls.deleted,0);assert.equal(f.calls.draws,2);
});
const terrain=context.rendererTerrainFixture(),terrainSnapshot=JSON.stringify(terrain.draws);
const terrainBatch=recorder();terrainBatch.cache.prepare(terrain.draws,d=>!!d.v046Terrain);
test('Fine terrain color groups share vertices and one exact batch',()=>{
  assert.equal(terrain.draws[0].vertices,terrain.draws[1].vertices);
  assert.equal(terrainBatch.uploaded.length,1);
  assert.deepEqual(stream([terrainBatch.uploaded[0].data]),plain(terrain.draws.flatMap(d=>stream(context.meshData(d),d.color))));
});
test('Splitting terrain materials neither changes source coordinates nor duplicates faces',()=>{
  assert.equal(JSON.stringify(terrain.draws),terrainSnapshot);
  const split=terrain.draws.flatMap(d=>d.faces.map(f=>f.join(',')));
  assert.equal(new Set(split).size,terrain.faces.length);
  assert.deepEqual(plain(split.slice().sort()),Array.from(terrain.faces,f=>f.join(',')).sort());
});
test('A NoData sample never enters the batched vertex stream',()=>{
  assert.ok(terrain.draws.every(d=>d.faces.every(f=>!f.includes(terrain.missing))));
  const p=terrainBatch.uploaded[0].data.positions;
  for(let i=0;i<p.length;i+=3)assert.ok(p[i]!==16||p[i+2]!==16);
});
test('The exact terrain hole area survives color partitioning and packing',()=>{
  const p=terrainBatch.uploaded[0].data.positions;let area=0;
  for(let i=0;i<p.length;i+=9)area+=Math.abs((p[i+3]-p[i])*(p[i+8]-p[i+2])-(p[i+6]-p[i])*(p[i+5]-p[i+2]))/2;
  assert.equal(terrain.faces.length,122);assert.equal(area,32*32-6*8);
});
test('Production fine-terrain flags batch differently colored groups in one draw',()=>{
  const f=fakeRenderer();f.r.render(terrain.draws,camera,{});
  const info=context.renderInfo();assert.equal(info.drawCalls,1);assert.equal(info.batchedMeshes,2);assert.equal(info.triangles,terrain.faces.length);
  f.r.render(terrain.draws,camera,{});assert.equal(f.calls.created,4);
  f.r.render([],camera,{});assert.equal(f.calls.deleted,4);
});
console.log(JSON.stringify({suite:'renderer_batches',passed:checks,failed:0}));
