// Validate partition selection at source/render bounding-box seams.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync('src/v050/04a_city_sources.js','utf8');
const start=source.indexOf('function v051CityDescriptors(');
const end=source.indexOf('/* Only the new plan',start);
assert(start>=0&&end>start);
const context=vm.createContext({
 V051_CITY:{index:{tiles:[
  {id:'source-crosses',path:'b.json',bbox:[0,0,2,2],renderBbox:[0,0,1,1]},
  {id:'render-crosses',path:'a.json',bbox:[3,3,4,4],renderBbox:[1,1,3,3]},
  {id:'far-away',path:'d.json',bbox:[5,5,6,6]},
  {id:'source-only',path:'c.json',bbox:[1,1,3,3]}
 ]}},
 MistralIntegrity:{intersects:(a,b)=>a[0]<b[2]&&a[2]>b[0]&&a[1]<b[3]&&a[3]>b[1]}
});
vm.runInContext(source.slice(start,end),context);
const ids=box=>Array.from(context.v051CityDescriptors(box),d=>d.id);
assert.deepEqual(ids([1.5,1.5,2.5,2.5]),['render-crosses','source-crosses','source-only']);
assert.deepEqual(ids([5,5,6,6]),['far-away']);
assert.deepEqual(ids([6,6,7,7]),[]);
// Ordering must not depend on the order in which the atlas index was received.
context.V051_CITY.index.tiles.reverse();
assert.deepEqual(ids([1.5,1.5,2.5,2.5]),['render-crosses','source-crosses','source-only']);
console.log('City source/render seam partition selection: 4 checks passed');
