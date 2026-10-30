// Synthetic extents follow the publication contract: whole buildings, clipped roads.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync('src/v050/04a_city_sources.js','utf8');
const geometry=fs.readFileSync('src/v050/04_source_geometry.js','utf8');
const MistralIntegrity=require('../../src/v046/00_integrity.js');
const descriptorStart=source.indexOf('function v051CityDescriptor(');
const descriptorEnd=source.indexOf('async function v051CityIndex(',descriptorStart);
const start=source.indexOf('function v051CityDescriptors(');
const end=source.indexOf('/* Only the new plan',start);
const boxStart=geometry.indexOf('function v050SourceBox(');
const boxEnd=geometry.indexOf('\n',boxStart);
assert(descriptorStart>=0&&descriptorEnd>descriptorStart&&start>=0&&end>start&&boxStart>=0&&boxEnd>boxStart);
const REGION='geo_marseille_commune',sha='a'.repeat(64);
const descriptor=(id,path,bbox,queryBbox,renderBbox)=>({id,path:'data/map_pack/city/'+path+'-'+sha.slice(0,16)+'.json',sha256:sha,bytes:1,region:REGION,bbox,queryBbox,coverages:[{},{}],counts:{buildings:1,roads:1},...(renderBbox?{renderBbox}:{} )});
const tiles=[
 descriptor('whole-building','b',[0,0,2,3],[0,0,1,1],[0,0,2,3]),
 descriptor('road-tail','a',[0,0,2,9],[0,0,2,2],[0,0,2,2]),
 descriptor('legacy-source','c',[1,1,3,3],[1,1,3,3]),
 descriptor('far-away','d',[5,5,6,6],[5,5,6,6])
];
const context=vm.createContext({V051_CITY:{index:{tiles}},V051_CITY_ID:REGION,MistralIntegrity});
vm.runInContext(geometry.slice(boxStart,boxEnd)+'\n'+source.slice(descriptorStart,descriptorEnd)+'\n'+source.slice(start,end),context);
for(const d of tiles)context.v051CityDescriptor(d);
const ids=box=>Array.from(context.v051CityDescriptors(box),d=>d.id);
assert.deepEqual(ids([1.5,1.5,2.5,2.5]),['road-tail','whole-building','legacy-source']);
assert.deepEqual(ids([.5,2.5,1.5,2.9]),['whole-building','legacy-source'],'Whole buildings remain available beyond their query edge');
assert.deepEqual(ids([.5,7,1.5,8]),[],'Unrendered road tails cannot pull distant partitions into the tile window');
assert.deepEqual(ids([5,5,6,6]),['far-away']);
assert.deepEqual(ids([6,6,7,7]),[]);
assert.deepEqual(tiles[1].bbox,[0,0,2,9],'Selecting a rendered extent must preserve the raw surveyed extent');
assert.throws(()=>context.v051CityDescriptor({...tiles[1],renderBbox:[-1,0,2,2]}),/Emprise rendue/,'An out-of-source rendered extent is not a valid partition fixture');
context.V051_CITY.index.tiles.reverse();
assert.deepEqual(ids([1.5,1.5,2.5,2.5]),['road-tail','whole-building','legacy-source']);
console.log('Validated city partition extents: whole buildings, clipped roads, legacy fallback and stable order');
