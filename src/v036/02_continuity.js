/* Seamless hand-off between overlapping macro-regions while preserving WGS84 position. */
function v036Contains(id,lat,lon,margin=0){const b=V015_GEO_MACROS[id]?.bbox;return!!b&&lat>=b[0]-margin&&lat<=b[2]+margin&&lon>=b[1]-margin&&lon<=b[3]+margin}
function v036BBoxDistance(id,lat,lon){const b=V015_GEO_MACROS[id].bbox,dy=lat<b[0]?b[0]-lat:lat>b[2]?lat-b[2]:0,dx=lon<b[1]?b[1]-lon:lon>b[3]?lon-b[3]:0;return Math.hypot(dx*Math.cos(rad(lat)),dy)}
function v036BestMacro(lat,lon,current){
 const candidates=Object.keys(V015_GEO_MACROS).filter(id=>id!==current&&v036Contains(id,lat,lon,.00025));
 if(!candidates.length)return null;const neighbors=V015_GEO_MACROS[current]?.neighbors||[];
 candidates.sort((a,b)=>(neighbors.includes(a)?-1:0)-(neighbors.includes(b)?-1:0)||v036BBoxDistance(a,lat,lon)-v036BBoxDistance(b,lat,lon));return candidates[0];
}
function v036TryMacroTransfer(){
 if(!world?.geoMacro||state.v036?.autoMacroTransfer===false||inCombat||zoneTransitioning)return false;
 const now=performance.now();if(now-V036.lastTransfer<1800)return false;
 const[lat,lon]=v015GeoUnproject(world.id,state.player.pos[0],state.player.pos[2]);V036.lastLatLon=[lat,lon];state.v036.lastLatLon=[lat,lon];state.v036.lastMacro=world.id;
 if(v036Contains(world.id,lat,lon,.00005))return false;
 const target=v036BestMacro(lat,lon,world.id);if(!target)return false;
 const p=v015GeoProject(target,lat,lon);V036.lastTransfer=now;V036.transferCount++;
 loadZone(target,{geoDirect:true,force:true,noTravel:true,silent:true,spawn:[p[0],1.65,p[2]]});toast(`Territoire continu · ${V015_GEO_MACROS[target].region.replace('MACRO-RÉGION · ','')}`,'good');return true;
}
const v036PlayerUpdate=updatePlayer;updatePlayer=function(dt){v036PlayerUpdate(dt);if(world?.geoMacro&&!V018.qaFreeze){V036.transferClock=(V036.transferClock||0)+dt;if(V036.transferClock>.35){V036.transferClock=0;v036TryMacroTransfer()}}};
