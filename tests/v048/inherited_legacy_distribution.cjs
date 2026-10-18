const vm=require('node:vm'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');const root=path.resolve(__dirname,'../..'),sw=fs.readFileSync(path.join(root,'sw.js'),'utf8'),tests=[];
const run=(name,fn)=>{try{fn();tests.push({name,ok:true});}catch(e){tests.push({name,ok:false,error:e.stack});}};
const html=fs.readFileSync(path.join(root,'JOUER_FALLOUT_MISTRAL_v0.48.html'));
run('Index identique au HTML livré',()=>assert.ok(html.equals(fs.readFileSync(path.join(root,'index.html')))));
run('Version PWA et lanceurs v046',()=>{assert.match(sw,/fallout-mistral-v048-1/);assert.match(fs.readFileSync(path.join(root,'LANCER_JEU.bat'),'utf8'),/v0.48.html/);});
run('Noyau offline existe',()=>{for(const p of ['index.html','manifest.webmanifest','icons/mistral-192.png','icons/mistral-512.png'])assert.ok(fs.existsSync(path.join(root,p)));});
const events={};let requests=0,match=0,removed=[];
const C={self:{addEventListener:(k,f)=>events[k]=f,skipWaiting:()=>Promise.resolve(),clients:{claim:()=>Promise.resolve()}},location:{origin:'https://local.test'},URL,Response,caches:{open:async()=>({addAll:async()=>{}}),keys:async()=>['other-app','fallout-mistral-v042-1','fallout-mistral-v048-1'],delete:async k=>{removed.push(k);return true;},match:async()=>{match++;return new Response('SHELL');}},fetch:async()=>{requests++;throw Error('hors ligne');}};
vm.runInNewContext(sw,C);
async function request(url,mode='cors'){let result;events.fetch({request:{method:'GET',url,mode},respondWith:p=>result=p});return result;}
(async()=>{
for(const url of ['/data/map_pack/france-vector/14/1/2.pbf','/data/map_pack/terrain/geo_marseille.json','/__mistral/local-data']){const r=await request('https://local.test'+url);run('Absence '+url+' retourne 503, pas HTML',()=>{assert.equal(r.status,503);assert.equal(match,0);});assert.doesNotMatch(await r.text(),/SHELL/);}
const r=await request('https://local.test/index.html','navigate');run('Shell offline disponible',()=>assert.equal(r.status,200));
let waits;events.activate({waitUntil:p=>waits=p});await waits;run('Les caches d’autres applications sont conservés',()=>assert.deepEqual(removed,['fallout-mistral-v042-1']));
run('Catalogue v042 conservé à 248 sites',()=>{const data=JSON.parse(fs.readFileSync(path.join(root,'data/fallout_layer_v042.json'),'utf8'));const arr=Array.isArray(data)?data:data.sites||data.catalog||data.nodes;assert.ok(arr && arr.length===248);});
let report={passed:tests.filter(t=>t.ok).length,failed:tests.filter(t=>!t.ok).length,total:tests.length,tests,scope:'Contrats de fichiers et événements service-worker exécutés dans Node ; aucune inscription native PWA revendiquée'};fs.writeFileSync(path.join(root,'verification/v048/QA_DISTRIBUTION.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));if(report.failed)process.exitCode=1;
})();
