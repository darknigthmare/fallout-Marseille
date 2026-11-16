'use strict';
// Extract only authored constant data from the legacy core, never execute the game.
// This is catalogue evidence, not proof that an item is obtainable or an enemy spawned.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
function snapshot(root=path.resolve(__dirname,'..')){
 const text=fs.readFileSync(path.join(root,'src/core-v017.js'),'utf8'),c=vm.createContext({});
 const run=s=>vm.runInContext(s,c,{timeout:1000});
 const start=text.indexOf('const AMMO_INFO ='),end=text.indexOf('const SHELTER_UNLOCKS=');
 if(start<0||end<start)throw Error('Legacy catalogue boundaries changed');run(text.slice(start,end));
 function decl(id){const marker='const '+id+'=',a=text.indexOf(marker);if(a<0)throw Error('Missing '+id);const b=text.indexOf(';',a);if(b<0)throw Error('Unterminated '+id);run(text.slice(a,b+1));}
 for(const id of ['V012_AMMO','V012_WEAPONS','V012_ENEMIES','V012_REGIONAL_ENEMIES','MISTRAL_WEAPON_IDS','V013_AMMO','V013_WEAPONS','V013_ENEMIES','V014_AMMO','V014_WEAPONS'])decl(id);
 const names=text.match(/const V012_WEAPON_NAMES=(\{[^\n]+?\});/);if(!names)throw Error('Missing weapon names');run(names[0]);
 const a=text.indexOf('const ENEMY_DEFAULTS='),b=text.indexOf('const REGIONAL_ENEMY_TYPES=');if(a<0||b<a)throw Error('Missing enemy catalogue');run(text.slice(a,b));
 const late=text.match(/Object\.assign\(ENEMY_DEFAULTS,\{soapGhoul:[^\n]+?\);Object\.assign\(ENEMY_NAMES,[^\n]+?\);/);
 if(!late)throw Error('Missing v014 enemy declarations');run(late[0]);
 run(`Object.assign(AMMO_INFO,V012_AMMO,V013_AMMO,V014_AMMO);Object.assign(WEAPONS,V012_WEAPONS,V013_WEAPONS,V014_WEAPONS);for(const [id,name] of Object.entries(V012_WEAPON_NAMES))WEAPONS[id].name=name;
  for(const id of Object.keys(V013_WEAPONS))if(id.startsWith('m13_'))MISTRAL_WEAPON_IDS.add(id);
  const enemies=Object.fromEntries(Object.entries(ENEMY_DEFAULTS).map(([id,d])=>[id,{...d,name:ENEMY_NAMES[id]||id}]));Object.assign(enemies,V012_ENEMIES,V013_ENEMIES);
  globalThis.result={weapons:WEAPONS,ammo:AMMO_INFO,mods:WEAPON_MODS,merchants:MERCHANTS,regional:[...MISTRAL_WEAPON_IDS],enemies,regionalEnemies:[...V012_REGIONAL_ENEMIES]};`);
 return JSON.parse(JSON.stringify(c.result));
}
module.exports=snapshot;
if(require.main===module)process.stdout.write(JSON.stringify(snapshot(),null,2)+'\n');
