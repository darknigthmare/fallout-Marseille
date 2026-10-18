/* Some historical instance dividers use descending Z endpoints (34 -> 14).
   Normalise each span so a doorway cannot silently remove the entire wall or
   build a collider past its requested extent. */
v042WallX=function(w,x,z0,z1,gapZ=null,gapW=4.8,h=4.4,col=COLORS.darkMetal){
  for(const [a,b]of MistralWork.spans(z0,z1,gapZ,gapW)) {
    const depth=b-a,z=(a+b)/2;addBox(w,[x,h/2,z],[.36,h,depth],col);
    addCollider(w,x,z,.44,depth,{minY:0,maxY:h});
  }
};
v042WallZ=function(w,z,x0,x1,gapX=null,gapW=4.8,h=4.4,col=COLORS.darkMetal){
  for(const[a,b]of MistralWork.spans(x0,x1,gapX,gapW)) {
    const width=b-a,x=(a+b)/2;addBox(w,[x,h/2,z],[width,h,.36],col);
    addCollider(w,x,z,width,.44,{minY:0,maxY:h});
  }
};
const v048InstanceBase=v042BuildInstance;
v042BuildInstance=function(){const w=v048InstanceBase();w.spawnYaw=0;return w;};
