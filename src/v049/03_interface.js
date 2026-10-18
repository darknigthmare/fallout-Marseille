/* Read-only encounter diagnostics. Counters always describe the current session,
   not an invented population simulated off-screen. */
function v049Info(){const entries=Object.values(state.v049.actors),bodies=Object.values(state.v026.containers).filter(c=>v049BodyIdentity(c.id));
 return {version:V049.version,entries:entries.length,enemies:entries.filter(a=>a.kind==='enemy').length,npcs:entries.filter(a=>a.kind==='npc').length,
 wounded:entries.filter(a=>a.kind==='enemy'&&a.alive&&a.health<a.maxHealth).length,dead:entries.filter(a=>a.kind==='enemy'&&!a.alive).length,
 sites:new Set(entries.map(a=>a.site)).size,bytes:new TextEncoder().encode(JSON.stringify(state.v049)).byteLength,budget:MistralEncounters.MAX_BYTES,
 corpses:bodies.length,availableCorpses:bodies.filter(c=>c.zone===world?.id).length,stats:{...V049.stats},last:V049.last,lab:V046.lab,
 rows:entries.slice(-30).map(a=>({id:a.id,site:a.site,scope:a.scope,kind:a.kind,hp:a.health??null,max:a.maxHealth??null,alive:a.alive}))};
}
const v049Panel=v047Panel;
v047Panel=function(c){v049Panel(c);const box=c.querySelector('.v047-integrity');if(!box)return;const s=v049Info();const el=document.createElement('section');el.className='v049-memory';
 el.innerHTML=`<p class="p27-kicker">v0.49 / PERSISTANCE DES RENCONTRES</p><h2>LE QUARTIER SE SOUVIENT</h2><p>${s.lab?'Banc synthétique : ces rencontres servent à vérifier la persistance, pas à représenter un quartier réel.':'Le journal conserve les rencontres des lieux effectivement visités.'}</p><div class="v049-metrics"><article><b>${s.wounded}</b><span>Adversaires blessés mémorisés</span></article><article><b>${s.corpses}</b><span>Dépouilles à contenu fini</span></article><article><b>${s.npcs}</b><span>Habitants mémorisés</span></article><article><b>${s.stats.restored}</b><span>Acteurs rétablis cette session</span></article></div><p>${s.sites} lieux · ${s.entries} fiches · ${(s.bytes/1024).toFixed(1)} Kio de journal. Les données des combats sont distinctes entre l’intérieur et l’extérieur d’un même lieu.</p><p>Une décharge de secteur n’efface ni la santé restante ni les membres blessés. Le nom de région affiché n’est plus la clé d’une dépouille. Les prises de butin restent consommées après retour.</p><small>Les acteurs éloignés sont suspendus, pas simulés hors écran. Seuls les sites ordinaires autorisés à repeupler changent de cycle après leur délai de jeu ; les boss et lieux uniques ne sont pas réinitialisés.</small>`;
 box.prepend(el);
};
function v049AfterInit(){document.title='Fallout : Mistral · v0.49 · Le quartier se souvient';const label=$('menuScreen')?.querySelector('.menu-version');if(label)label.textContent='v0.49 · LE QUARTIER SE SOUVIENT';
 const credits=document.querySelector('#creditsScreen .credits-card');if(credits){credits.innerHTML='<h2>FALLOUT : MISTRAL</h2><p>0.49.0 · Le quartier se souvient</p><p>Reprise directe du projet complet v0.48 fourni. Rencontres persistantes, blessures localisées, dépouilles finies et retours compatibles avec les sauvegardes.</p><p>248 implantations inchangées. Prototype de fan non officiel. Le pack géographique intégral n’est pas embarqué ; les essais cartographiques utilisent le banc synthétique signalé à l’écran.</p><button id="btnCreditsClose" class="primary">Fermer</button>';$('btnCreditsClose').onclick=closeCredits;}
 Object.assign(window.__MISTRAL_DEBUG,{v049Info,v049Checkpoint:()=>v049Checkpoint(),v046Lab:v046StartLab,v046Campaign:v048LeaveLab,v042Enter:v042EnterSite,
 v042Unload:v042UnloadSite,v049Actors:()=>[...(world?.enemies||[]),...(world?.npcs||[])].filter(a=>v049Identify(a.id)).map(a=>({id:a.id,kind:v049Identify(a.id).kind,site:a.v042Site,pos:a.pos.slice(),home:a.home.slice(),alive:a.alive,hp:a.health,max:a.maxHealth,limbs:a.v025LimbLoss||{},yaw:a.yaw,status:a.status||{},alerted:!!a.alerted})),
 v049Bodies:()=>Object.entries(state.v026.containers).filter(([k,c])=>v049BodyIdentity(c.id)).map(([key,c])=>({key,...deepClone(c)})),
 v049Damage:(id,n,part='body')=>{const e=world.enemies.find(e=>e.id===id);if(!e)throw Error('Cible absente');damageEnemy(e,n,part);return e.health;},
 v049ProbeSpawn:(id,offset=[0,0])=>{if(!V046.lab||!world?.v046)throw Error('Banc requis');const s=v042Site(id);if(!s)throw Error('Site inconnu');v049Own(world);state.v046.placements[id]=[state.player.pos[0]+offset[0],groundHeightAt(state.player.pos[0],state.player.pos[2]),state.player.pos[2]+offset[1]];return !!v042SpawnSite(world,s);},
 v049ProbePose:(id,pos,yaw=0)=>{if(!V046.lab)throw Error('Banc requis');const a=[...world.enemies,...world.npcs].find(a=>a.id===id);if(!a||!MistralEncounters.vector(pos))throw Error('Acteur/position invalide');a.pos=pos.slice();a.yaw=yaw;return true;},
 v049ProbeState:(id,fields)=>{if(!V046.lab)throw Error('Banc requis');const a=world.enemies.find(a=>a.id===id);if(!a)return false;for(const k of ['alerted','attackCooldown','searchTimer','state'])if(k in fields)a[k]=fields[k];return true;},
 v049RebuildInstance:()=>{if(!V046.lab||world?.id!==V042_INSTANCE_ZONE)throw Error('Instance du banc requise');const p=state.player.pos.slice(),yaw=state.player.yaw;return loadZone(V042_INSTANCE_ZONE,{force:true,silent:true,instance:true,spawn:p,yaw});},
 v049Bind:()=>v049BindBodies(world,true),v049RegionLabel:id=>{if(!V046.lab||!world?.v046||!V015_GEO_MACROS[id])throw Error('Banc requis');world.id=id;state.player.zone=id;v049BindBodies(world,true);return id;},
 v049ReloadState:raw=>{if(!V046.lab)throw Error('Banc requis');const next=migrateState(JSON.parse(raw));state=next;return true;},
 v049ProbeTime:t=>{if(!V046.lab||!Number.isFinite(t)||t<0)throw Error('Banc/temps requis');state.playTime=t;return t;},
 v049Respawn:id=>v042ResetRespawn(v042Site(id)),v049BodyDraws:()=>collectDraws(gameClock).filter(d=>d.v026Corpse).map(d=>d.v026Corpse),
 v049SiteGeometry:id=>MistralIntegrity.hash(world.staticDraws.filter(d=>d.v042Site===id).map(d=>[d.mesh,d.pos,d.scale,d.rotY,d.color]))});
}
