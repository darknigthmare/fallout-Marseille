/* v0.21 — Built from recovered v0.20. Fictional interiors, not geographic imports. */
const V021={time:0,navCache:new WeakMap(),mapFloor:0,beams:[],lastWorld:null,visualCounts:{},debug:false,attackEvents:[],footsteps:0};
function v021Fresh(){return {schema:1,accepted:false,clues:{},switches:{},witness:false,visited:{},ending:null,rewarded:false,returnPoints:[],journalPage:0,tracked:false};}
const v021Base=baseState;baseState=function(){const s=v021Base();s.v021=v021Fresh();return s;};
const v021Migrator=migrateState;migrateState=function(input={}){const s=v021Migrator(input),f=v021Fresh(),p=input.v021||{};s.v021={...f,...p};for(const k of ['clues','switches','visited'])s.v021[k]={...f[k],...(p[k]||{})};s.v021.returnPoints=Array.isArray(p.returnPoints)?p.returnPoints.slice(-8):[];return s;};state=migrateState(state);
function v021Event(type,detail){V021.attackEvents.push({type,detail,at:+V021.time.toFixed(2)});if(V021.attackEvents.length>40)V021.attackEvents.shift();}
const v021Reset=v020ResetTransient;v020ResetTransient=function(){v021Reset();V021.beams=[];for(const e of world?.enemies||[])e.v021Windup=null;};
const v021Region=worldRegionLabel;worldRegionLabel=function(id){return typeof V021_PLACES!=='undefined'&&V021_PLACES[id]?V021_PLACES[id].name:v021Region(id);};
function v021IsScene(){return !!world?.v021Interior;}
function v021Near(id,range=3.3){const i=world?.interactables.find(x=>x.id===id);return !!(i&&Math.abs(state.player.pos[1]-(i.pos[1]||1))<2.1&&vLen(vSub(state.player.pos,i.pos))<range&&lineOfSight(state.player.pos,i.pos));}
