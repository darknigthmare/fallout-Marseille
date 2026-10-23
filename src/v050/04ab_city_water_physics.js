/* A surveyed water polygon is not a walking floor, even when the elevation
   service reports zero. This boundary is deliberately non-swimmable; measured
   bridges and roof supports retain their existing collision behavior. */
const MistralCityWaterPhysics=(()=>{
 const finite=n=>typeof n==='number'&&Number.isFinite(n);
 function measured(support){return !!(support&&support.measured===true&&finite(support.height));}
 function blocked({water=false,deck=null,roof=null,vehicle=false,lab=false,exterior=false}={}){
  return exterior===true&&lab!==true&&vehicle!==true&&water===true&&!measured(deck)&&!measured(roof);
 }
 function waterAt({x,z,records,inside,inExtent=()=>false}={}){
  if(!finite(x)||!finite(z)||typeof inside!=='function'||!records)return false;
  const indexed=records.v047Index?.surface;
  const draws=indexed&&typeof indexed.at==='function'?indexed.at(x,z).filter(item=>item?.type==='water').map(item=>item.draw):typeof records.values==='function'?[...records.values()].flatMap(record=>Array.isArray(record?.water)?record.water:[]):[];
  let extent;
  for(const draw of draws){
   if(!Array.isArray(draw?.rings)||!draw.rings.length||!inside(draw.rings,x,z))continue;
   if(draw.v051Water===true||draw.geoProperties?.v051Water===true)return true;
   if(extent===undefined)extent=typeof inExtent==='function'&&inExtent()===true;
   if(extent)return true;
  }
  return false;
 }
 return{blocked,measured,waterAt};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=MistralCityWaterPhysics;

if(typeof window!=='undefined'&&typeof collidesAt==='function'){
 const v051CityWaterCollisionBase=collidesAt;
 collidesAt=function(x,z,r=.38,eyeY=null){
  // A support over water can never erase a wall, vehicle or footprint collision.
  if(v051CityWaterCollisionBase(x,z,r,eyeY))return true;
  const w=typeof world==='undefined'?null:world;
  if(!w?.v046||typeof V046==='undefined'||V046.lab||typeof isBoatZone==='function'&&isBoatZone())return false;
  const water=MistralCityWaterPhysics.waterAt({x,z,records:w.v046Records,inside:MistralIntegrity.inside,inExtent:()=>{
   if(typeof V051_CITY_BOUNDS==='undefined'||typeof v015GeoUnproject!=='function')return false;
   const point=v015GeoUnproject(w.id,x,z);
   return Array.isArray(point)&&point.length>=2&&point.slice(0,2).every(Number.isFinite)&&MistralIntegrity.contains(V051_CITY_BOUNDS,point[0],point[1]);
  }});
  if(!water)return false;
  const player=typeof state==='undefined'?null:state?.player;
  const eye=Number.isFinite(eyeY)?eyeY:Number.isFinite(player?.pos?.[1])?player.pos[1]:1.65;
  const atPlayer=!!player&&Math.abs(x-player.pos[0])<1e-7&&Math.abs(z-player.pos[2])<1e-7&&Math.abs(eye-player.pos[1])<1e-7;
  const roofState=typeof V050_ROOFS==='undefined'?null:V050_ROOFS;
  const movingPlayer=Number.isFinite(roofState?.actorEye)||atPlayer;
  const eyeHeight=movingPlayer&&typeof playerEyeHeight==='function'?playerEyeHeight():1.65;
  const feet=Number.isFinite(roofState?.body?.feet)?roofState.body.feet:eye-eyeHeight;
  const allowStep=!movingPlayer||typeof onGround==='undefined'||onGround;
  const deck=typeof v050DeckSupport==='function'?v050DeckSupport(x,z,feet,allowStep):null;
  const roof=typeof v050RoofSupport==='function'?v050RoofSupport(x,z,feet,allowStep,r):null;
  return MistralCityWaterPhysics.blocked({water,deck,roof,exterior:true});
 };
}
