'use strict';
const fs=require('node:fs'),Module=require('node:module'),path=require('node:path'),crypto=require('node:crypto');
const root='/workspace/fallout-Marseille',target=root+'/tests/expansion/interior_services.cjs',raw=fs.readFileSync(target,'utf8'),prefix=raw.slice(0,raw.indexOf("\ntest('A furniture service planner")),helpers=raw.slice(raw.indexOf('function selectionFixture('),raw.indexOf("\ntest('Service anchor"));
const baseline='/workspace/.cloud-setup/fallout-marseille/fps-expansion/rebuild-final/src/v050/08_city_interiors.js';
const rows=[];
for(const [name,source]of[['before',baseline],['candidate',root+'/src/v050/08_city_interiors.js']]){
 const initial="source=fs.readFileSync(path.join(root,'src/v050/08_city_interiors.js'),'utf8')";
 if(!prefix.includes(initial))throw Error('Explicit source seam changed');
 const setup=prefix.replace(initial,'source=fs.readFileSync('+JSON.stringify(source)+',"utf8")');
 const body=`const f=selectionFixture(),l=f.json('world.v050CityInterior'),s=f.json('service'),prop=l.furniture.find(v=>v.id===s.furnitureId),part=G.furnitureModel(prop).find(p=>p.material==='wood'&&p.size[0]>1.5),angle=prop.rotation||0,c=Math.cos(angle),z=Math.sin(angle),mesh=[prop.pos[0]+c*part.pos[0]-z*part.pos[2],l.elevation+part.pos[1],prop.pos[1]+z*part.pos[0]+c*part.pos[2]];look(f,mesh);const wood=f.json('selectedInteractable'),container=f.json('Object.values(state.v026.containers)[0]');look(f,[container.pos[0],container.pos[1]+1.05,container.pos[2]]);module.exports={wood, reserve:f.json('selectedInteractable'),mesh,service:s,sourceSha256:require('node:crypto').createHash('sha256').update(fs.readFileSync(${JSON.stringify(source)})).digest('hex')};`;
 const m=new Module(target,module);m.filename=target;m.paths=Module._nodeModulePaths(path.dirname(target));m._compile(setup+helpers+body,target);rows.push({name,...m.exports});
}
console.log(JSON.stringify({scope:'Controlled square source footprint, real production core selection/LOS, actual v026Attach, declared scene/storage/DOM seams; no native geography claim.',rows},null,2));
