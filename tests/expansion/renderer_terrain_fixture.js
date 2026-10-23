// Shared bounded fixture for the recording driver and native WebGL driver.
// The center sample is deliberately NoData: its placeholder may never be used
// by a rendered face. The complete mesh exists only as a hole-visibility control.
function rendererTerrainFixture(){
  const size=9,vertices=[],faces=[],completeFaces=[],groups=[[],[]],missing=40;
  const height=(x,z)=>x*.35+z*.2+((x%3)-1)*.3;
  for(let z=0;z<size;z++)for(let x=0;x<size;x++)vertices.push([x*4,z*size+x===missing?0:height(x,z),z*4]);
  for(let z=0;z<size-1;z++)for(let x=0;x<size-1;x++){
    const a=z*size+x,b=a+1,c=a+size,d=c+1;
    for(const face of [[a,c,b],[b,c,d]]){
      completeFaces.push(face);
      if(face.includes(missing))continue;
      faces.push(face);groups[x<4?0:1].push(face);
    }
  }
  const colors=[[.267,.561,.193],[.683,.477,.299]];
  const draws=groups.map((faces,i)=>({mesh:'terrain',pos:[16,2,16],vertices,faces,
    color:colors[i],v046Terrain:true,v050FineTerrain:true,revision:0}));
  return{vertices,faces,draws,completeFaces,missing,hole:[16,height(4,4),16]};
}
