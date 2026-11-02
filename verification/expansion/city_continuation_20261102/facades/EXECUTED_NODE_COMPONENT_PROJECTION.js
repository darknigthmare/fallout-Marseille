
const fs=require('node:fs'),vm=require('node:vm');
const F=require('./src/v050/07_facades.js'),I=require('./src/v046/00_integrity.js');
const text=fs.readFileSync('src/patches/01_geometry.js','utf8');
const context=vm.createContext({rad:x=>x*Math.PI/180});
vm.runInContext(text.slice(text.indexOf('function v018Lambert93'),text.indexOf('const V018_OLD_SCALES')),context);
const origin=context.v018Lambert93(43.285,5.51);
const cases=require('./tests/expansion/fixtures/facades_joinery_ign.json').cases.map(c=>{
 const f=c.feature,p=I.buildingProfile(f.properties),polygon=f.geometry.type==='MultiPolygon'?f.geometry.coordinates[0]:f.geometry.coordinates;
 const rings=polygon.map(r=>r.map(v=>{const q=context.v018Lambert93(v[1],v[0]);return[q[0]-origin[0],origin[1]-q[1]];}));
 const d=F.describe({mesh:'prism',geoLayer:'building',rings,baseY:p.groundElevation??0,height:p.height,geoProperties:f.properties});
 return{role:c.role,id:d.id,rings:d.rings};
});
console.log(JSON.stringify({nodeVersion:process.version,v8Version:process.versions.v8,cases}));
