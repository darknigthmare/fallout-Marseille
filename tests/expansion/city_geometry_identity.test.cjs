const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync('src/v050/04a_city_sources.js','utf8');
const start=source.indexOf('async function v051CityEnrich(');
const end=source.indexOf('const v051CityPlanBase=',start);
assert(start>=0&&end>start);
// Force a 32-bit hash collision: identity must not rely on a short hash.
const records=[
 {props:{kind:'building'},sourceId:'B-1',v050Geometry:{type:'Polygon',coordinates:[[[0,0],[1,0],[1,1],[0,0]]]},v050Bounds:{minX:0,maxX:1,minZ:0,maxZ:1}},
 {props:{kind:'building'},sourceId:'B-1',v050Geometry:{type:'Polygon',coordinates:[[[1,0],[2,0],[2,1],[1,0]]]},v050Bounds:{minX:1,maxX:2,minZ:0,maxZ:1}}
];
const ctx=vm.createContext({
 V051_CITY:{registered:true,index:{}},
 v017TileBounds:()=>({south:0,west:0,north:2,east:2}),
 v015GeoProject:(_id,x,y)=>[x,0,y],
 V051_CITY_ID:'geo_marseille_commune',
 v017PolyBounds:()=>({cx:1,cz:1,minX:0,maxX:2,minZ:0,maxZ:2}),
 v051CityDescriptors:()=>[{path:'a'},{path:'b'}],
 v051CityChunk:async d=>({spatial:{around:()=>[records[d.path==='a'?0:1]]},coverages:[]}),
 v051CityAbort:()=>{},
 v050BoxesTouch:()=>true,
 v050ApplySourceOverlays:(_resource,features)=>features,
 MistralIntegrity:{hash:()=> '00000000'}
});
vm.runInContext(source.slice(start,end),ctx);
(async()=>{
 const result=await ctx.v051CityEnrich({source:'cadastre',z:16,x:0,y:0});
 assert.equal(result.length,2,'Different geometry with same source ID must survive partition aggregation');
 assert.equal(ctx.V051_CITY.geometryConflicts,1,'Conflicting variants must be reported');
 assert.deepEqual(Array.from(ctx.V051_CITY.geometryConflictIds),['building:B-1']);
 const same=records[0];
 ctx.v051CityChunk=async()=>({spatial:{around:()=>[same]},coverages:[]});
 const dedup=await ctx.v051CityEnrich({source:'cadastre',z:16,x:0,y:0});
 assert.equal(dedup.length,1,'Identical source geometry must deduplicate');
 assert.equal(ctx.V051_CITY.geometryConflicts,0,'Identical copies are not conflicts');
 assert.deepEqual(Array.from(ctx.V051_CITY.geometryConflictIds),[]);
 console.log('City geometry identity: distinct shapes survive even under hash collisions; exact copies deduplicate');
})().catch(e=>{console.error(e);process.exitCode=1});
