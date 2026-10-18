/* Authored courtyards attached to the three v0.21 interiors, without a scene change.
 * No cadastral footprint, street or real coastline is represented by these courtyards. */
const V022_COURTS={
 transit_depot:{title:'Cour des couchettes',extent:26,tone:[.66,.52,.37],canopy:[.58,.36,.22],rooms:['Cour de réception','Abri des couvertures','Cantine du retour'],sign:'COUCHETTES'},
 traverse_archives:{title:'Jardin des lecteurs',extent:28,tone:[.64,.66,.53],canopy:[.31,.46,.40],rooms:['Jardin des lecteurs','Dépôt des dossiers','Atelier des radios'],sign:'JARDIN'},
 mooring_station:{title:'Cour des amarres',extent:28,tone:[.61,.62,.51],canopy:[.29,.43,.50],rooms:['Cour des secours','Atelier des amarres','Table des départs'],sign:'SECOURS'}
};
function v022Planks(w,x,z,sx,sz,y,col){const n=Math.max(2,Math.ceil(sx/.33));for(let i=0;i<n;i++)addBox(w,[x-sx/2+(i+.5)*sx/n,y,z],[sx/n-.02,.11,sz],cMix(col,[.32,.25,.17],(i%4)*.035));}
function v022Table(w,x,z,col=[.48,.34,.21]){v022Planks(w,x,z,2.6,1.1,.84,col);for(const dx of[-1.04,1.04])for(const dz of[-.37,.37])addBox(w,[x+dx,.42,z+dz],[.11,.84,.11],[.24,.29,.24]);addCollider(w,x,z,2.6,1.1,{minY:0,maxY:.96});for(let k=0;k<3;k++){addPart(w,'cylinder',[x-.8+k*.8,.94,z],[.30,.035,.30],[.72,.70,.57]);addPart(w,'cylinder',[x-.9+k*.8,1.025,z+.35],[.11,.17,.11],[.62,.58,.44]);}}
function v022Seat(w,x,z,length=2.4){v022Planks(w,x,z,length,.55,.44,[.43,.32,.20]);for(const dx of[-length*.38,length*.38])addBox(w,[x+dx,.22,z],[.13,.44,.49],[.24,.29,.27]);addBox(w,[x,.81,z+.22],[length,.5,.09],[.41,.32,.22]);/* Seats are intentionally passable to let seated actors use their assigned points. */}
function v022Awning(w,x,z,sx,sz,col){for(const dx of[-sx/2,sx/2])for(const dz of[-sz/2,sz/2]){addBox(w,[x+dx,1.6,z+dz],[.13,3.2,.13],[.29,.35,.29]);addCollider(w,x+dx,z+dz,.15,.15,{minY:0,maxY:3.2});}for(let k=0;k<Math.ceil(sx);k++)addBox(w,[x-sx/2+k+.5,3.23,z],[1.01,.09,sz],k%2?col:cMix(col,[.72,.67,.50],.32));}
function v022Cot(w,x,z,ready,id){addBox(w,[x,.40,z],[1.02,.10,2.05],[.29,.34,.30]);for(const dx of[-.44,.44])for(const dz of[-.89,.89])addBox(w,[x+dx,.2,z+dz],[.07,.4,.07],[.35,.4,.34]);addCollider(w,x,z,1.02,2.05,{minY:0,maxY:.65});addBox(w,[x,.55,z],[.94,.23,1.98],[.57,.50,.37],0,{id,hidden:!ready});addBox(w,[x,.69,z-.72],[.76,.16,.45],[.78,.76,.60],0,{id:id+':pillow',hidden:!ready});for(const dx of[-.53,.53])addBox(w,[x+dx,.61,z-.95],[.055,.48,.07],[.28,.34,.27]);}
function v022Planter(w,x,z,tree=false){addBox(w,[x,.4,z],[tree?2.1:3,.8,1.6],[.48,.43,.33]);addBox(w,[x,.84,z],[tree?1.94:2.84,.1,1.43],[.24,.24,.16]);addCollider(w,x,z,tree?2.1:3,1.6,{minY:0,maxY:.9});if(tree){addPart(w,'cylinder',[x,1.8,z],[.25,2.1,.25],[.37,.31,.19]);for(const [dx,dy,dz]of[[-.7,2.7,0],[.7,2.9,.2],[0,3.4,0]])addPart(w,'sphere',[x+dx,dy,z+dz],[1.5,1.1,1.6],[.32,.43,.25]);}else for(let k=0;k<6;k++)addPart(w,'sphere',[x-1.1+k*.44,1.06,z+(k%2-.5)*.38],[.62,.44,.53],[.31+.03*(k%3),.43,.25]);}
function v022Board(w,x,z,text,col){for(const dx of[-1.4,1.4])addBox(w,[x+dx,1.2,z],[.12,2.4,.15],[.34,.31,.23]);addBox(w,[x,1.6,z],[3,1.1,.16],col);for(let k=0;k<5;k++){const xk=x-1.1+k*.55;addBox(w,[xk,1.64,z+.1],[.42,.73,.026],[.74,.71,.56]);for(let j=0;j<4;j++)addBox(w,[xk,1.81-j*.12,z+.12],[.28,.025,.01],[.33,.40,.32]);}v021Sign(w,x,2.43,z,text,.085);}
function v022Facade(w,x,z,sx,sz,col){addBox(w,[x,2.1,z],[sx,4.2,sz],col);addCollider(w,x,z,sx,sz,{minY:0,maxY:4.2});const front=z+sz/2+.02;addBox(w,[x,4.25,z],[sx+.3,.19,sz+.3],[.59,.35,.22]);for(let k=0;k<Math.max(1,Math.floor(sx/2.2));k++){const xx=x-sx/2+1.1+k*2.2;addBox(w,[xx,2.45,front],[.85,1.2,.035],[.22,.29,.26]);for(const d of[-.54,.54]){addBox(w,[xx+d,2.45,front+.035],[.23,1.24,.06],[.34,.45,.36]);for(let j=0;j<6;j++)addBox(w,[xx+d,2.0+j*.17,front+.08],[.2,.03,.02],[.52,.55,.4]);}}addBox(w,[x,.15,front],[sx,.3,.05],[.39,.41,.32]);}
function v022AttachCourt(w){const def=V022_COURTS[w.id];if(!def)return w;const [l,r,t,s]=w.bounds,b=s+def.extent;w.v022Court={south:s,end:b,title:def.title};w.bounds=[l,r,t,b];w.v020NavEpoch++;
 // Remove only the old south perimeter, its small sign and false door leaf.
 w.colliders=w.colliders.filter(c=>!(Math.abs((c.minZ+c.maxZ)/2-s)<.1&&c.maxX-c.minX>r-l-1));
 w.staticDraws=w.staticDraws.filter(d=>!((Math.abs(d.pos[2]-s)<.10&&d.scale?.[0]>r-l-1)||(Math.abs(d.pos[2]-(s-.25))<.035&&Math.abs(d.pos[0])<.2&&Math.abs(d.scale?.[0]-2.5)<.05)||(Math.abs(d.pos[2]-(s-.30))<.12&&Math.abs(d.pos[0])<2&&d.pos[1]>3.1&&d.pos[1]<4)));
 const side=(r-l-5.2)/2;for(const sign of[-1,1])v021Wall(w,sign*(2.6+side/2),s,side,.35,0,6.6,[.56,.55,.43]);addBox(w,[0,5.0,s],[5.2,3.2,.35],[.53,.51,.41]);
 addFloorZone(w,0,s+def.extent/2,r-l,def.extent,0);addBox(w,[0,-.16,s+def.extent/2],[r-l,.3,def.extent],def.tone);for(let z=s+.8;z<b;z+=3.4){addBox(w,[0,.012,z],[r-l-.4,.018,.032],cMix(def.tone,[.24,.29,.21],.3));for(let x=l+1+(Math.round(z)%2)*1.7;x<r-1;x+=3.4)addBox(w,[x,.012,z-1.6],[.033,.018,3.2],cMix(def.tone,[.24,.29,.21],.2));}
 for(const x of[l,r])v021Wall(w,x,(s+b)/2,.35,def.extent,0,3.25,[.63,.61,.48]);for(const sign of[-1,1])v021Wall(w,sign*(2.6+side/2),b,side,.35,0,3.25,[.60,.59,.47]);
 const exit=w.interactables.find(i=>i.id===w.id+':exit');exit.pos=[0,1.1,b-1];addBox(w,[0,1.5,b-.1],[4.3,3,.14],[.30,.41,.35]);v021Sign(w,0,3.45,b-.22,'QUARTIER',.09);v021Sign(w,0,3.7,s+.20,def.sign,.12);
 const y=s;
 // Surface wear and services belong to the perimeter, never to the central path.
 for(const sign of[-1,1]){
  for(let k=0;k<3;k++){const x=sign*(6.5+k*5.7);addBox(w,[x,4.9,s+.21],[3.4,1.02,.10],[.24,.31,.28]);for(let j=0;j<5;j++)addBox(w,[x,4.55+j*.17,s+.275],[3.2,.05,.025],[.52,.53,.4]);}
  for(let k=0;k<7;k++){const x=sign*(4.8+k*2.65);addBox(w,[x,.19,s+.215],[2.58,.30,.055],[.43+.02*(k%3),.43,.34]);}
  addBox(w,[sign*(r-1),2.0,(s+b)/2],[.12,.12,def.extent-1.5],[.45,.40,.28]);
 }
 for(let k=0;k<3;k++){const x=-2+k*2;addBox(w,[x,4.0,(s+b)/2],[.025,.025,def.extent-2],[.31,.30,.23]);for(let j=0;j<4;j++){const z=s+4+j*5;addPart(w,'sphere',[x,3.86,z],[.14,.18,.14],[.84,.75,.47],0,{emissive:.5});}}
 // A central, uninterrupted 6 m approach is kept free in every court.
 for(const dx of[-3.2,3.2]){addBox(w,[dx,.026,(s+b)/2],[.08,.025,def.extent-1],[.78,.70,.45]);for(let k=0;k<4;k++)addBox(w,[dx+Math.sign(dx)*.17,.026,s+3+k*5],[.38,.025,.08],[.78,.70,.45]);}
 if(w.id==='transit_depot'){
  v022Awning(w,-14,y+9,13,11,def.canopy);for(let k=0;k<6;k++)v022Cot(w,-19+k*2,y+7,state.v022.task.beds,w.id+':v22:bed:'+k);
  v022Seat(w,-14,y+12,5.4);v022Table(w,13,y+14);v022Seat(w,13,y+15.5,6.2);v022Awning(w,14,y+14,10,7,[.38,.46,.30]);v022Facade(w,13,y+3,16,3,[.67,.56,.42]);v022Board(w,-9,y+18,'RETOUR',[.28,.37,.29]);v021Rack(w,-21,0,y+18,[.35,.41,.31]);v021Crate(w,20,0,y+22,[.51,.4,.28],2,1.1,1.5);
  addBox(w,[-9,1.06,y+18.3],[.43,.17,.29],[.56,.43,.25]);v020Object(w,'v022:tape',[-9,1.2,y+19.1],'Holodisque · Après le canal six',()=>v022Action('tape'),'loot');
  v020Object(w,'v022:beds',[-14,1.1,y+10.5],'Réparer les six couchettes',()=>v022Action('beds'),'bench');v020Object(w,'v022:kit',[-11,4.3,-20],'Récupérer le paquet de sangles',()=>v022Action('kit'),'loot');addBox(w,[-11,3.5,-20],[.65,.4,.5],[.53,.41,.26]);
 }else if(w.id==='traverse_archives'){
  for(const p of[[-16,y+6],[16,y+6],[-16,y+20],[16,y+20]])v022Planter(w,...p,true);v022Planter(w,-10,y+13);v022Planter(w,10,y+13);
  v022Table(w,-15,y+13);v022Seat(w,-15,y+14.7,3.0);v022Awning(w,15,y+16,9,7,def.canopy);v022Table(w,15,y+16);v022Seat(w,15,y+17.5,4.2);v022Facade(w,-12,y+1.8,16,2.8,[.63,.63,.50]);v022Board(w,8,y+23,'LECTEURS',[.24,.35,.30]);v022Seat(w,-8,y+22,3);
  v021Control(w,'v022:consent',[-17,1.1,y+2.8],'Classer les demandes avec leur consentement',()=>v022Action('consent'),[.34,.65,.50]);
 }else{
  v022Awning(w,-15,y+10,13,10,def.canopy);v022Table(w,-16,y+8);v022Seat(w,-16,y+9.6,4.8);v021Rack(w,-22,0,y+15,[.35,.41,.38]);v022Facade(w,13,y+2,19,3,[.62,.64,.54]);
  for(let k=0;k<3;k++){const x=10+k*5;addPart(w,'cylinder',[x,.48,y+14],[.54,.96,.54],[.31,.35,.30]);addBox(w,[x,.89,y+14],[1.05,.15,.32],[.38,.40,.31]);for(let j=0;j<4;j++)addPart(w,'cylinder',[x, .11+j*.07,y+15],[1.35,.055,1.35],[.46,.42,.28]);}
  v022Board(w,-8,y+22,'DEPARTS',[.26,.35,.32]);v022Seat(w,12,y+23,5.6);v021Crate(w,21,0,y+22,[.42,.43,.29],2,1.6,2);
  v021Control(w,'v022:relay',[-16,1.1,y+13],'Réaccorder la radio de relève',()=>v022Action('relay'),[.34,.66,.54]);
 }
 for(let k=0;k<3;k++){const z=y+4+k*8;addBox(w,[l+.45,2.62,z],[.23,.28,.34],[.86,.79,.52],0,{emissive:.6});addBox(w,[r-.45,2.62,z],[.23,.28,.34],[.86,.79,.52],0,{emissive:.6});}
 w.v020Rooms.push([def.rooms[0],0,y+8,0],[def.rooms[1],-14,y+14,0],[def.rooms[2],12,y+20,0]);for(const a of w.v020Rooms.slice(-3))w.subzones.push({name:a[0],pos:[a[1],0,a[2]]});
 const cachePos=[r-6,1.1,b-5];v021Crate(w,cachePos[0],0,cachePos[2],[.47,.43,.30],1.25,.9,1);v020Object(w,w.id+':v22:cache',cachePos,'Réserve offerte par les équipes',()=>v022Cache(),'loot');
 v022Populate(w);return w;
}
const v022Build=buildWorld;buildWorld=function(id){const w=v022Build(id);v022AttachCourt(w);for(const e of w.enemies){const old=state.v022?.encounters[id+'|'+e.id];if(old?.type===e.type&&e.alive){e.health=clamp(old.health,0,e.maxHealth);e.legDamage=old.leg;e.armDamage=old.arm;if(e.health===0){e.alive=false;state.flags.enemyDead[e.id]=true;}}}return w;};
const v022Environment=currentEnv;currentEnv=function(){const base=v022Environment();if(world?.v022Court&&state.player.pos[2]>world.v022Court.south+.3){const hour=state.worldTime%24,day=hour>=6&&hour<20;return {...base,indoor:false,daylight:day?1:.34,skyTop:day?[76,123,143]:[13,24,32],skyBottom:day?[182,191,160]:[54,67,65],fog:day?[.61,.65,.56]:[.20,.28,.27],sunDir:[.4,.82,.3]};}return base;};
