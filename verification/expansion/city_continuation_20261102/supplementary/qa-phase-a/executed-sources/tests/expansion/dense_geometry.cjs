'use strict';
/* Regression for actual native-resolution DEM meshes: a 300,000+ point draw
   must be culled by all its bounds without exceeding JS argument limits. */
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const assert=require('node:assert/strict');
const ctx=vm.createContext({console});
vm.runInContext(`
 let sourceDraws=[];
 let world={v046:true},state={player:{pos:[0,1.65,0]}};
 function collectDraws(){return sourceDraws;}
 function v042WorldPoint(){}function v042SpawnSite(){}function v042UpdateLayer(){}
`,ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname,'../../src/v046/02_environment.js'),'utf8'),ctx);
const run=s=>vm.runInContext(s,ctx);
const json=s=>JSON.parse(JSON.stringify(run(s)));
let passed=0;
function check(name,fn){fn();passed++;console.log('OK '+name);}
check('Dense terrain scans every vertex without a call-stack overflow',()=>{
 run(`var dense={v046Terrain:true,pos:[2000,0,2000],vertices:Array.from({length:300001},(_,i)=>[2000+i%17,Math.sin(i),2000+i%23])};dense.vertices[300000]=[-4,50,-7];sourceDraws=[dense];`);
 assert.equal(run('collectDraws(0).length'),1);
 assert.deepEqual(json('dense.v046Bounds'),{minX:-4,maxX:2016,minZ:-7,maxZ:2022});
 assert.equal(run('dense.vertices.length'),300001);
});
check('Dense offscreen terrain is still culled instead of kept unconditionally',()=>{
 run(`var distant={v046Terrain:true,pos:[2000,0,2000],vertices:Array.from({length:300001},(_,i)=>[2000+i%17,0,2000+i%23])};sourceDraws=[distant];`);
 assert.equal(run('collectDraws(0).length'),0);
});
check('Large polygon rings and their holes contribute their full extents',()=>{
 run(`var polygon={v046Tile:'polygon',rings:[Array.from({length:150001},(_,i)=>[1000+i%20,1100+i%30]),[[-12,-15],[-10,-15],[-10,-13],[-12,-15]]],pos:[2000,0,2000]};sourceDraws=[polygon];`);
 assert.equal(run('collectDraws(0).length'),1);
 assert.deepEqual(json('polygon.v046Bounds'),{minX:-12,maxX:1019,minZ:-15,maxZ:1129});
});
check('Dense roads use planar second coordinates, not vertex height',()=>{
 run(`var road={v046Tile:'road',roadPath:Array.from({length:300001},(_,i)=>[850+i%7,900+i%11]),pos:[2000,0,2000]};road.roadPath[300000]=[3,5];sourceDraws=[road];`);
 assert.equal(run('collectDraws(0).length'),1);
 assert.deepEqual(json('road.v046Bounds'),{minX:3,maxX:856,minZ:5,maxZ:910});
});
check('Bounds are cached on the immutable draw record for later frames',()=>{
 run(`sourceDraws=[dense];var cached=dense.v046Bounds;collectDraws(1);`);
 assert.equal(run('cached===dense.v046Bounds'),true);
});
check('The existing distance boundary remains strict',()=>{
 run(`sourceDraws=[{v046Tile:'edge',vertices:[[720,0,0]],pos:[720,0,0]}];`);
 assert.equal(run('collectDraws(0).length'),0);
 run('state.player.pos[0]=.1');
 assert.equal(run('collectDraws(0).length'),1);
 run('state.player.pos[0]=0');
});
check('Ordinary props retain their existing ten-metre extent fallback',()=>{
 assert.deepEqual(json('v046DrawBounds({pos:[12,100,19]})'),{minX:2,maxX:22,minZ:9,maxZ:29});
});
check('Non-geographic actors and scenes keep the existing collection path',()=>{
 run(`var actor={pos:[5000,0,5000]};sourceDraws=[actor];`);
 assert.equal(run('collectDraws(0)[0]===actor'),true);
 run(`world.v046=false;sourceDraws=[distant];`);
 assert.equal(run('collectDraws(0)[0]===distant'),true);
});
console.log(JSON.stringify({passed,failed:0,total:passed,scope:'Actual geographic draw collector with 300,001-vertex meshes and large 2D source paths'}));
