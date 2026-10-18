/* A local occupancy graph, derived from the actual loaded scene. This is NOT
 * a geographic map. Unreachable pins stay unreachable; no straight-line fallback. */
function v020Nav(){
  if(!world||world.geoMacro)return null;
  const epoch=world.v020NavEpoch||0,cached=V020.navCache.get(world);if(cached?.epoch===epoch)return cached;
  const [x0,x1,z0,z1]=world.bounds,step=Math.max(1,Math.max(x1-x0,z1-z0)/150),nx=Math.floor((x1-x0)/step)+1,nz=Math.floor((z1-z0)/step)+1;
  const blocked=new Uint8Array(nx*nz),height=new Float32Array(nx*nz);
  for(let z=0;z<nz;z++)for(let x=0;x<nx;x++){const i=z*nx+x,px=x0+x*step,pz=z0+z*step,y=groundHeightAt(px,pz,0);height[i]=y;blocked[i]=collidesAt(px,pz,.39,y+1.5)?1:0;}
  const nav={epoch,x0,z0,step,nx,nz,blocked,height};V020.navCache.set(world,nav);return nav;
}
function v020Node(nav,pos){const x=Math.round((pos[0]-nav.x0)/nav.step),z=Math.round((pos[2]-nav.z0)/nav.step);if(x<0||z<0||x>=nav.nx||z>=nav.nz)return -1;return z*nav.nx+x;}
function v020NodePos(n,i){return [n.x0+(i%n.nx)*n.step,n.height[i],n.z0+Math.floor(i/n.nx)*n.step];}
function v020Route(a,b){
  const n=v020Nav();if(!n)return null;
  let s=v020Node(n,a),end=v020Node(n,b);if(s<0||end<0)return null;
  const nearest=(i)=>{if(!n.blocked[i])return i;const ix=i%n.nx,iz=Math.floor(i/n.nx);let best=-1,bd=Infinity;for(let dz=-2;dz<=2;dz++)for(let dx=-2;dx<=2;dx++){const x=ix+dx,z=iz+dz,j=z*n.nx+x;if(x<0||z<0||x>=n.nx||z>=n.nz||n.blocked[j])continue;const d=dx*dx+dz*dz;if(d<bd){bd=d;best=j;}}return best;};
  s=nearest(s);end=nearest(end);if(s<0||end<0)return null;
  const total=n.nx*n.nz,cost=new Float64Array(total).fill(Infinity),parent=new Int32Array(total).fill(-1),closed=new Uint8Array(total),heap=[];
  const push=(i,f)=>{let k=heap.length;heap.push([i,f]);while(k>0){const p=(k-1)>>1;if(heap[p][1]<=f)break;heap[k]=heap[p];k=p;}heap[k]=[i,f];};
  const pop=()=>{const top=heap[0],last=heap.pop();if(heap.length){let i=0;while(i*2+1<heap.length){let c=i*2+1;if(c+1<heap.length&&heap[c+1][1]<heap[c][1])c++;if(heap[c][1]>=last[1])break;heap[i]=heap[c];i=c;}heap[i]=last;}return top[0];};
  const h=i=>Math.hypot(i%n.nx-end%n.nx,Math.floor(i/n.nx)-Math.floor(end/n.nx));cost[s]=0;push(s,h(s));
  while(heap.length){const i=pop();if(closed[i])continue;closed[i]=1;if(i===end){const p=[];let k=end;while(k!==-1){p.push(v020NodePos(n,k));k=parent[k];}p.reverse();return p;}
    const x=i%n.nx,z=Math.floor(i/n.nx);
    for(let dz=-1;dz<=1;dz++)for(let dx=-1;dx<=1;dx++){if(!dx&&!dz)continue;const xx=x+dx,zz=z+dz,j=zz*n.nx+xx;if(xx<0||zz<0||xx>=n.nx||zz>=n.nz||n.blocked[j]||closed[j]||Math.abs(n.height[j]-n.height[i])>.72)continue;
      if(dx&&dz&&(n.blocked[z*n.nx+xx]||n.blocked[zz*n.nx+x]))continue;
      const g=cost[i]+Math.hypot(dx,dz);if(g<cost[j]){cost[j]=g;parent[j]=i;push(j,g+h(j));}
    }
  }
  return null;
}
function v020WalkLine(a,b){const d=dist2(a,b),steps=Math.ceil(d/.6);for(let i=1;i<=steps;i++){const t=i/steps,x=lerp(a[0],b[0],t),z=lerp(a[2],b[2],t),y=groundHeightAt(x,z,a[1]||0);if(collidesAt(x,z,.36,y+1.5))return false;}return true;}
function v020Move(n,target,speed,dt){
  if(!world||!target||!Number.isFinite(dt))return false;const d=dist2(n.pos,target);if(d<.35){n.moving=false;return true;}
  let aim=target;const a=[n.pos[0],n.pos[1]+1.3,n.pos[2]],b=[target[0],(target[1]||0)+1.3,target[2]];
  if(!lineOfSight(a,b)||!v020WalkLine(n.pos,target)){
    const key=n.v020NavTarget,refresh=!n.v020Route||!key||dist2(key,target)>2||(n.v020NavEpoch!==world.v020NavEpoch);
    if(refresh){n.v020Route=v020Route(n.pos,target);n.v020NavTarget=[...target];n.v020NavEpoch=world.v020NavEpoch;n.v020RouteIndex=0;}
    const route=n.v020Route;if(!route?.length){n.moving=false;return false;}
    while(n.v020RouteIndex<route.length-1&&dist2(n.pos,route[n.v020RouteIndex])<.7)n.v020RouteIndex++;
    aim=route[n.v020RouteIndex];
  }else n.v020Route=null;
  let dx=aim[0]-n.pos[0],dz=aim[2]-n.pos[2],len=Math.hypot(dx,dz);if(len<.05)return true;const step=Math.min(len,speed*dt);dx=dx/len*step;dz=dz/len*step;
  const before=[...n.pos],tryMove=(x,z)=>{const y=groundHeightAt(x,z,n.pos[1]||0);if(Math.abs(y-(n.pos[1]||0))>.75||collidesAt(x,z,.36,y+1.5))return; n.pos=[x,y,z];};
  tryMove(n.pos[0]+dx,n.pos[2]);tryMove(n.pos[0],n.pos[2]+dz);n.moving=dist2(before,n.pos)>.0001;if(n.moving)n.yaw=Math.atan2(dx,-dz);return n.moving;
}
updateNPCSchedules=function(dt){
  if(!world||world.id==='vault')return;
  for(const n of world.npcs){if(!n.alive||n.companion||n.v020Static)continue;n.moving=false;const phase=n.schedule?.find(s=>{const h=state.worldTime%24;return (s.start??0)<=(s.end??24)?h>=(s.start??0)&&h<(s.end??24):h>=s.start||h<s.end;});
    if(phase?.pos){n.activity=phase.activity||'routine';v020Move(n,phase.pos,1.35,dt);continue;}
    if(!n.route?.length)continue;n.routePause=Math.max(0,(n.routePause||0)-dt);if(n.routePause>0)continue;
    const t=n.route[(n.routeIndex||0)%n.route.length];if(dist2(n.pos,t)<.75){n.routeIndex=((n.routeIndex||0)+1)%n.route.length;n.routePause=1.2+(n.id.length%4)*.4;n.activity='pause';}else{n.activity='déplacement';v020Move(n,t,1.5,dt);}
  }
  v020Separate(world.npcs.filter(n=>n.alive));
};
function v020Separate(list){
  for(let i=0;i<list.length;i++)for(let j=i+1;j<list.length;j++){const a=list[i],b=list[j];if(Math.abs(a.pos[1]-b.pos[1])>1)continue;let dx=b.pos[0]-a.pos[0],dz=b.pos[2]-a.pos[2],d=Math.hypot(dx,dz);if(d>=.82)continue;if(d<.001){dx=(i+j)%2?1:-1;dz=.2;d=Math.hypot(dx,dz);}const push=Math.min(.13,(.82-d)/2);for(const [n,sgn] of [[a,-1],[b,1]]){const x=n.pos[0]+dx/d*push*sgn,z=n.pos[2]+dz/d*push*sgn;if(!collidesAt(x,z,.32,n.pos[1]+1.5)){n.pos[0]=x;n.pos[2]=z;}}}
}
function v020Command(){const d=activeCompanion();if(!d)return null;return state.v020.companionOrders[d.id]??=( {move:'follow',fire:'defend',zone:world?.id,pos:null} );}
function v020SetOrder(type,value){const d=activeCompanion(),c=v020Command();if(!d||!c)return false;if(type==='move'&&['follow','hold'].includes(value)){c.move=value;c.zone=world.id;const a=v020CompanionActor();c.pos=a?[...a.pos]:[...state.player.pos];}
 else if(type==='fire'&&['defend','quiet'].includes(value))c.fire=value;else return false;saveGame(false);return true;}
function v020CompanionActor(){
  const d=activeCompanion();if(!d||!world||world.id==='vault'||world.vehicleMode)return null;
  if(d.type==='dog'){
    let a=V020.actors.get('roux');if(!a){const p=state.flags.rouxPos||[state.player.pos[0]-1.5,groundHeightAt(state.player.pos[0]-1.5,state.player.pos[2]),state.player.pos[2]];a={id:'roux',pos:[...p],yaw:0,moving:false,attackCooldown:0};V020.actors.set('roux',a);}return a;
  }
  let a=world.npcs.find(n=>n.id===d.id);if(!a){const x=state.player.pos[0]-1.5,z=state.player.pos[2]+1; a=addHumanNPC(world,d.id,d.fullName,d.role,[x,groundHeightAt(x,z),z],d.color,{skin:d.skin,dialogue:d.id});a.v020Spawned=true;}
  a.companion=true;return a;
}
updateCompanion=function(dt){
  const d=activeCompanion(),a=v020CompanionActor(),c=v020Command();if(!d||!a||!c)return;
  if(c.zone!==world.id){c.zone=world.id;c.move='follow';c.pos=null;}
  const p=state.player.pos,desired=c.move==='hold'?c.pos:[p[0]-Math.cos(state.player.yaw)*1.7,groundHeightAt(p[0],p[2],p[1]-playerEyeHeight()),p[2]-Math.sin(state.player.yaw)*1.7];
  if(desired&&dist2(a.pos,desired)>1.3)v020Move(a,desired,d.type==='dog'?4.1:3.2,dt);else a.moving=false;
  a.attackCooldown=Math.max(0,(a.attackCooldown||0)-dt);a.healCooldown=Math.max(0,(a.healCooldown||0)-dt);
  if(d.id==='naima'&&dist2(a.pos,p)<5&&lineOfSight([a.pos[0],a.pos[1]+1.3,a.pos[2]],p)&&state.player.hp<state.player.maxHp*.4&&a.healCooldown<=0){state.player.hp=Math.min(state.player.maxHp,state.player.hp+18);a.healCooldown=35;subtitle('Naïma','Restez près de moi. Je comprime la blessure.');}
  if(c.fire==='defend'&&a.attackCooldown<=0){const origin=[a.pos[0],a.pos[1]+(d.type==='dog'?.55:1.35),a.pos[2]],range=d.type==='dog'?2.2:17;
    const targets=world.enemies.filter(e=>e.alive&&e.alerted&&dist2(a.pos,e.pos)<=range&&lineOfSight(origin,[e.pos[0],e.pos[1]+.9,e.pos[2]])).sort((x,y)=>dist2(a.pos,x.pos)-dist2(a.pos,y.pos));
    if(targets.length){const e=targets[0];a.yaw=Math.atan2(e.pos[0]-a.pos[0],-(e.pos[2]-a.pos[2]));damageEnemy(e,(d.damage||8)*(1+companionLoyalty(d.id)/300),d.type==='dog'?'legs':'body');a.attackCooldown=d.cooldown||1.5;}
  }
  if(d.type==='dog')state.flags.rouxPos=[...a.pos];
  else v020Separate(world.npcs.filter(n=>n.alive));
};
const v020EnemyUpdate=updateEnemies;
updateEnemies=function(dt){
  const before=new Map((world?.enemies||[]).filter(e=>e.alive).map(e=>[e.id,[...e.pos]]));v020EnemyUpdate(dt);
  for(const e of world?.enemies||[]){if(!e.alive)continue;if(collidesAt(e.pos[0],e.pos[2],.38,(e.pos[1]||0)+1.4)&&before.has(e.id))e.pos=before.get(e.id);}
  for(const c of world?.coverPoints||[])if(c.occupied&&!world.enemies.some(e=>e.id===c.occupied&&e.alive&&e.coverTarget===c.id&&dist2(e.pos,c.pos)<24))c.occupied=null;
};
