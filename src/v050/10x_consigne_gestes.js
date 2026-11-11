/* Consigne: recognition gestures after an authoritative, saved handoff.
 * Presentation only: no new save fields, rewards, movement or IGN geometry.
 * The object is already received when this gesture starts (not hand-to-hand IK).
 */
const MistralConsigneGestures = (() => {
  const ids = ['clef', 'bague', 'sifflet'];
  const duration = 2900;
  const idle = [.33, .73, .02];
  const inspect = {clef: [.24, 1.23, -.43], bague: [.21, 1.29, -.44], sifflet: [.23, 1.20, -.43]};
  const kept = {clef: [.24, .82, -.20], bague: [.33, .73, -.045], sifflet: [.08, 1.02, -.205]};
  const smooth = t => { t = Math.max(0, Math.min(1, t)); return t*t*(3-2*t); };
  const lerp3 = (a,b,t) => a.map((v,i) => v+(b[i]-v)*t);
  function pose(id, ms) {
    if (!ids.includes(id) || !Number.isFinite(ms) || ms < 0) throw Error('Invalid consignment gesture');
    let hand, item, phase, attachment = 0;
    if (ms < 450) { phase='receive'; hand=lerp3([.33,.94,-.32],inspect[id],smooth(ms/450)); item=hand.slice(); }
    else if (ms < 1550) { phase='recognise'; hand=inspect[id].slice(); item=hand.slice(); }
    else if (ms < 2350) { phase='keep'; hand=lerp3(inspect[id],kept[id],smooth((ms-1550)/800)); item=hand.slice(); attachment=smooth((ms-1950)/400); }
    else { phase=ms<duration?'release':'done'; hand=lerp3(kept[id],idle,smooth((ms-2350)/550)); item=kept[id].slice(); attachment=1; }
    return {phase,hand,item,attachment,done:ms>=duration};
  }
  function elapsed(ms,dt,playing=true) {
    if (!Number.isFinite(ms)||ms<0||!Number.isFinite(dt)||dt<0) throw Error('Invalid gesture clock');
    return playing ? Math.min(duration,ms+Math.min(dt,100)) : ms;
  }
  function point(p,yaw,v,scale=1) {
    const c=Math.cos(yaw),s=Math.sin(yaw);
    return [p[0]+(v[0]*c+v[2]*s)*scale,p[1]+v[1]*scale,p[2]+(-v[0]*s+v[2]*c)*scale];
  }
  function elbow(hand) {
    const shoulder=[.32,1.34,0],delta=hand.map((v,i)=>v-shoulder[i]),length=Math.hypot(...delta);
    if (!(length>0&&length<=.72)) throw Error('Unreachable hand pose');
    const d=delta.map(v=>v/length),bend=[1-d[0]*d[0],-d[0]*d[1],-d[0]*d[2]],norm=Math.hypot(...bend);
    const radius=Math.sqrt(Math.max(0,.36*.36-length*length/4));
    return shoulder.map((v,i)=>v+delta[i]/2+bend[i]/norm*radius);
  }
  return {ids:ids.slice(),duration,pose,elapsed,point,elbow};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralConsigneGestures;

if(typeof humanParts==='function'&&typeof MistralGabians!=='undefined'){
  const G=MistralConsigneGestures, pending=new Map();
  let owner=null, scene=null, lastTime=null;
  const local=()=>!!world?.v073Gabians&&state.v042?.activeInterior===MistralGabians.SITE;
  const keyOf=n=>G.ids.find(k=>n?.id==='g73:owner:'+k);
  function reset(){pending.clear();owner=state;scene=world;lastTime=null;}
  function sync(){if(state!==owner||world!==scene||!local())reset();}
  function begin(key){
    sync();
    if(!local()||settings.reduceMotion||!state.v073Gabians.handoffs[key])return;
    pending.set(key,{ms:0});lastTime=gameClock;
  }
  function step(time){
    sync();if(!Number.isFinite(time))return;
    const dt=lastTime===null?0:Math.max(0,(time-lastTime)*1000);lastTime=lastTime===null?time:Math.max(lastTime,time);
    if(!local())return;
    if(settings.reduceMotion){pending.clear();return;}
    const running=gameStarted&&['PLAYING','DIALOGUE'].includes(mode)&&state.player.hp>0&&!zoneTransitioning&&!V046.busy&&!V047.pending&&!V046.lab;
    for(const [key,a] of pending){
      a.ms=G.elapsed(a.ms,dt,running);
      if(a.ms>=G.duration||!state.v073Gabians.handoffs[key])pending.delete(key);
    }
  }
  // Decorate only the three native handoff choices. The original callback owns
  // validation and the save transaction; a failed/stale callback never animates.
  const dialog=openDialogue;
  openDialogue=function(speaker,text,choices,...rest){
    if(!local())return dialog(speaker,text,choices,...rest);
    const key=G.ids.find(k=>MistralGabians.OBJECTS[k].owner===speaker?.name);
    if(!key)return dialog(speaker,text,choices,...rest);
    const decorated=(choices||[]).map(choice=>{
      if(choice.v075Gesture||!/^Remettre en main propre : |^Passer depuis le comptoir : /.test(choice.text||''))return choice;
      return {...choice,v075Gesture:true,onChoose:function(...args){
        const oldState=state,oldWorld=world,before=state.v073Gabians.handoffs[key];
        const result=choice.onChoose(...args);
        if(before===null&&state===oldState&&world===oldWorld&&state.v073Gabians.handoffs[key]!==null)begin(key);
        return result;
      }};
    });
    return dialog(speaker,text,decorated,...rest);
  };
  function shape(out,n,key,pos,attachment=1){
    const gold=[.78,.63,.28],silver=[.68,.69,.61],dark=[.16,.19,.18];
    const sc=n.scale||1,yaw=n.yaw||0;
    function add(mesh,off,size,color){out.push({mesh,pos:G.point(n.pos,yaw,pos.map((v,i)=>v+off[i]),sc),scale:size.map(v=>v*sc),color,rotY:yaw,emissive:0,alpha:1,v075Object:key});}
    function ring(off,r,color){for(let i=0;i<12;i++){const a=i*Math.PI/6;add('sphere',[off[0]+Math.cos(a)*r,off[1]+Math.sin(a)*r,off[2]],[.019,.019,.019],color);}}
    if(key==='clef'){ring([0,.075,0],.042,gold);add('cube',[0,-.025,0],[.025,.15,.025],gold);for(const y of [-.064,-.094])add('cube',[.025,y,0],[.065,.02,.025],gold);}
    else if(key==='bague')ring([0,0,0],.052,silver);
    else{add('cube',[0,0,0],[.085,.075,.085],silver);add('cube',[0,.069,0],[.042,.075,.04],silver);add('cube',[0,.014,-.046],[.048,.018,.012],dark);}
    if(key==='sifflet'&&attachment>0){
      // A local neck cord; no whistle sound, ferry or alarm is implied.
      for(const side of [-1,1])for(let i=0;i<9;i++){
        const t=i/8,v=[side*.13*(1-t)+.08*t,1.33*(1-t)+1.06*t,-.19];
        out.push({mesh:'sphere',pos:G.point(n.pos,yaw,v,sc),scale:[.016,.025,.016].map(v=>v*sc),color:dark,rotY:yaw,alpha:attachment,emissive:0,v075Cord:true});
      }
    }
  }
  function arm(out,n,hand){
    const shoulder=[.32,1.34,0],joint=G.elbow(hand),skin=n.skin||COLORS.skin,cloth=n.color||COLORS.clothBlue,sc=n.scale||1;
    for(const [a,b,color]of [[shoulder,joint,cloth],[joint,hand,skin]])for(let i=0;i<6;i++){
      const t=i/5,p=a.map((v,j)=>v+(b[j]-v)*t);
      out.push({mesh:'sphere',pos:G.point(n.pos,n.yaw||0,p,sc),scale:[.155,.155,.155].map(v=>v*sc),color,rotY:n.yaw||0,alpha:1,emissive:0,v075Arm:true});
    }
    out.push({mesh:'sphere',pos:G.point(n.pos,n.yaw||0,hand,sc),scale:[.16,.18,.15].map(v=>v*sc),color:skin,rotY:n.yaw||0,alpha:1,emissive:0,v075Hand:true});
  }
  const human=humanParts;
  humanParts=function(out,n,t){
    sync();const key=local()&&keyOf(n);
    if(!key||state.v073Gabians.handoffs[key]===null)return human(out,n,t);
    const active=pending.get(key),pose=G.pose(key,active?active.ms:G.duration),native=[];
    const proxy=active?{...n,moving:false}:n;human(native,proxy,t);
    let removed=0;
    if(active){
      const signatures=[[.32,1.16,0],[.33,.89,.025],[.33,.73,.02]];
      for(let i=native.length-1;i>=0;i--){
        if(signatures.some(v=>{const p=G.point(proxy.pos,proxy.yaw||0,v,proxy.scale||1);return native[i].pos.every((x,j)=>Math.abs(x-p[j])<.001);})){
          native.splice(i,1);removed++;
        }
      }
    }
    // Keep the original body, head, face, clothing, left arm and identity.
    // Fail closed if the upstream rig ever changes instead of showing two arms.
    if(active&&removed!==3){human(out,n,t);shape(out,n,key,G.pose(key,G.duration).item);return;}
    out.push(...native);if(active)arm(out,proxy,pose.hand);shape(out,proxy,key,pose.item,pose.attachment);
  };
  const draws=collectDraws;
  collectDraws=function(t){step(t);return draws(...arguments);};
  // Once both the original quest and its optional epilogue are done, stop
  // sending the player back to Nora for a reward already received.
  const marker=getObjectiveMarker;
  getObjectiveMarker=function(){
    if(local()&&state.v073Gabians.finished&&G.ids.every(k=>state.v073Gabians.handoffs[k]!==null))
      return {zone:world.id,pos:[0,1.25,28.4],label:'La consigne · Retour au Vieux-Port'};
    return marker(...arguments);
  };
  const questUI=updateQuestUI;
  updateQuestUI=function(...args){const result=questUI(...args);if(local()&&state.v073Gabians.finished){
    const done=G.ids.every(k=>state.v073Gabians.handoffs[k]!==null);
    $('questTitle').textContent=done?'DE MAIN EN MAIN · TERMINÉ':'LES OBJETS TROUVÉS · TERMINÉ';
    $('questObjective').textContent=done?'Éloi, Mina et Rachid ont retrouvé leurs affaires. Retour au Vieux-Port par la sortie de la cour.':'La prime de Nora a été reçue. Facultatif : rencontrer les propriétaires au comptoir, sans nouvelle récompense.';
  }return result;};
  const after=globalThis.v053LoreAfterInit;
  globalThis.v053LoreAfterInit=function(){after?.();Object.assign(window.__MISTRAL_DEBUG,{
    v075GesturesInfo:()=>{sync();return {active:[...pending].map(([id,a])=>({id,ms:a.ms,...G.pose(id,a.ms)})),local:local(),duration:G.duration};}
  });};
}
