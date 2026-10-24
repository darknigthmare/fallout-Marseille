const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const root='/workspace/fallout-Marseille',out=__dirname,source=fs.readFileSync(path.join(out,'interiors-baseline.cjs'),'utf8'),F=require('./facades-baseline.cjs'),square=[[[0,0],[20,0],[20,20],[0,20],[0,0]]];
eval(fs.readFileSync(path.join(out,'runtime-harness.inc'),'utf8'));
(async()=>{
 const f=runtime();
 const doc=f.json(`({schemaVersion:1,frame:'building-local-metre',buildingId:d.v050CityInteriorInfo().doors[0].building,source:{url:'https://example.org/audit-documented-fixture',license:'CC0 fixture',attribution:'Controlled regression fixture',title:'Audit wall plan',accessedAt:'2026-10-24'},levels:[{level:0,elevation:0,height:4,entry:[-8,-8],walls:[{a:[-2,-10],b:[-2,-1],thickness:.2},{a:[-2,1],b:[-2,10],thickness:.2}],rooms:[{id:'west',use:'fixture',ring:[[-10,-10],[-2,-10],[-2,10],[-10,10],[-10,-10]]}]}]})`);
 f.run('d.v050CityRegisterDocument('+JSON.stringify(doc)+')');
 const entered=f.run('d.v050CityInteriorEnter(d.v050CityInteriorInfo().doors[0].id)');
 const before=f.json('d.v050CityInteriorInfo().active');const saved=f.json('state');
 const g=runtime();g.run('state=migrateState('+JSON.stringify(saved)+');loadZone("v050_city_interior",{force:true})');
 const afterCold=g.json('d.v050CityInteriorInfo().active');
 g.run('d.v050CityInteriorExit()');await Promise.resolve();await Promise.resolve();await new Promise(r=>setTimeout(r,0));
 const exterior=g.json('d.v050CityInteriorInfo()');
 g.run('const p=d.v050CityInteriorInfo().doors[0].pos;state.player.pos=[p[0],1.65,p[2]]');
 const reentered=g.run('d.v050CityInteriorEnter(d.v050CityInteriorInfo().doors[0].id)');
 const afterReentry=g.json('d.v050CityInteriorInfo().active');
 const report={scope:'Production08 source from cac50f3 executed in original controlled scene/persistence harness; documentary geometry is an explicit synthetic fixture. No browser/native claim.',sourceSha256:crypto.createHash('sha256').update(source).digest('hex'),entered,before,afterCold,exterior,reentered,afterReentry,documentLost:before.layoutProvenance==='documented'&&afterCold.layoutProvenance==='documented'&&afterReentry.layoutProvenance==='invented'};
 fs.writeFileSync(path.join(out,'DOCUMENT_ROUNDTRIP.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({entered,reentered,before:before.layoutProvenance,cold:afterCold.layoutProvenance,reentry:afterReentry.layoutProvenance,documentLost:report.documentLost}));
})().catch(e=>{console.error(e);process.exitCode=1});
