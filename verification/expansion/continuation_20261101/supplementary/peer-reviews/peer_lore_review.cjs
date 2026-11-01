'use strict';
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),{createRequire}=require('node:module'),assert=require('node:assert/strict');
const root='/workspace/fallout-Marseille',file=path.join(root,'tests/expansion/lore_continuity.cjs'),req=createRequire(file);
const c=vm.createContext({console,__dirname:path.dirname(file),require:id=>id==='node:test'?()=>{}:req(id)});
vm.runInContext(fs.readFileSync(file,'utf8')+';globalThis.peer={runtime,finishRuntime};',c);
const{runtime,finishRuntime}=c.peer,results=[];
function probe(name,fn){try{results.push({name,ok:!!fn()});}catch(e){results.push({name,ok:false,error:String(e.stack)});}}
probe('Partial pack preflight never debits or advances when second component is full',()=>{
 const f=runtime();finishRuntime(f,'passage_libre','balises');const r=f.json('d.v053LoreInfo().returns').find(r=>r.id==='passage_libre');f.run('placeSite('+JSON.stringify(r.targetSite)+');d.v057LoreReturnDeliver("passage_libre",'+JSON.stringify(r.targetSite)+');placeGiver("passage_libre");state.inventory.cloth=999999');const before=f.json('state');assert.equal(f.run('d.v057LoreReturnClaim("passage_libre")'),false);assert.deepEqual(f.json('state'),before);return true;
});
probe('NPC changing relay site invalidates an old delivery callback with no grant',()=>{
 const f=runtime();finishRuntime(f,'partage');const r=f.json('d.v053LoreInfo().returns').find(r=>r.id==='partage');f.run('v042TalkNPC(placeSite('+JSON.stringify(r.targetSite)+'));globalThis.action=test.dialogue.choices.find(c=>c.text.startsWith("Remettre la copie")).onChoose;world.npcs[0].v042Site="other";V042_RUNTIME.npcData.clear()');const before=f.json('state');f.run('action()');assert.deepEqual(f.json('state'),before);return true;
});
probe('A storage refusal also rolls back the ordinary actor checkpoint called by the real save wrapper',()=>{
 const f=runtime();finishRuntime(f,'partage');const r=f.json('d.v053LoreInfo().returns').find(r=>r.id==='partage');f.run('placeSite('+JSON.stringify(r.targetSite)+');d.v057LoreReturnDeliver("partage",'+JSON.stringify(r.targetSite)+');placeGiver("partage")');
 f.run('const V042_INSTANCE_ZONE="v042_instance";function v042EnemyId(site,index,inside=false){return`v042:${site.id}:${inside?"inside":"outside"}:${index}`;}');
 f.run(fs.readFileSync(path.join(root,'src/v049/00_encounters.js'),'utf8'));
 f.run(fs.readFileSync(path.join(root,'src/v049/01_persistence.js'),'utf8').split('const v049SpawnEnemies=')[0]);
 f.run('state.v049={schema:1,actors:{}};state.flags.enemyDead={};world.npcs[0].id="v042-npc:"+world.npcs[0].v042Site+":0";world.npcs[0].home=world.npcs[0].pos.slice();v049Own(world)');
 const saveSource=fs.readFileSync(path.join(root,'src/v049/02_bodies_lifecycle.js'),'utf8');f.run(saveSource.match(/const v049Save=saveGame;\nsaveGame=function[^\n]+/)[0]);
 f.run('test.fail=true');const before=f.json('state');assert.equal(f.run('d.v057LoreReturnClaim("partage")'),false);const after=f.json('state');
 if(JSON.stringify(before)!==JSON.stringify(after)){results.push({detail:'Production v049Checkpoint preserved an actor snapshot on rejected lore transaction',beforeActors:before.v049.actors,afterActors:after.v049.actors,inventoryRestored:JSON.stringify(before.inventory)===JSON.stringify(after.inventory),returnLedgerRestored:JSON.stringify(before.v053Lore)===JSON.stringify(after.v053Lore)});return false;}return true;
});
fs.writeFileSync('/workspace/.cloud-setup/fallout-marseille/continuation-next/landmarks/PEER_LORE_REVIEW.json',JSON.stringify({scope:'Independent controlled probes. No game/test source edits; actual save checkpoint functions composed with test actor/storage seams. Outside root validation assertion sum.',results},null,2)+'\n');console.log(JSON.stringify(results,null,2));
