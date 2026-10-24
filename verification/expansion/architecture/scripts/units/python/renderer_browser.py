#!/usr/bin/env python3
"""Native WebGL pixel comparison between individual and batched geography.

This small driver isolates the rendering change, not game or GIS readiness.
It compiles production shaders and uploads production tessellation output.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from qa_support import chromium_path
from playwright.sync_api import sync_playwright


def source():
    core = (ROOT / 'src/core-v017.js').read_text()
    geometry = (ROOT / 'src/patches/01_geometry.js').read_text()
    definitions = core[core.index('function v3('):core.index('class SoftwareRenderer')]
    for name in ('v017SignedArea', 'v017PointInPoly'):
        definitions += '\n' + next(line for line in core.splitlines() if line.startswith('function ' + name + '('))
    definitions += '\n' + geometry[:geometry.index('/* The software fallback')]
    definitions += '\n' + (ROOT / 'tests/expansion/renderer_terrain_fixture.js').read_text()
    return definitions


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=chromium_path(), headless=True,
                                     args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = browser.new_page(viewport={'width': 640, 'height': 480}, device_scale_factor=1)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content('<canvas id="render"></canvas>')
        page.add_script_tag(content="""
          const TAU=Math.PI*2,COLORS={white:[1,1,1]},settings={quality:'medium'};
          const world={v046:true,geoMacro:true,id:'geo_huveaune'};
          const rad=n=>n*Math.PI/180;
          let lamp=false;
          function v028LampActive(){return lamp;}
          function v028LampOrigin(){return[0,0,0];}
        """ + source())
        result = page.evaluate("""() => {
          const r=new GLRenderer(document.getElementById('render'));
          const camera={pos:[18,24,43],dir:vNorm([0,-20,-35]),fov:67};
          const env={sunDir:[.4,.8,.2],fog:[.45,.58,.58]};
          const draws=Array.from({length:3},(_,id)=>({mesh:'prism',pos:[id*12+5,2,5],baseY:0,height:4,
            rings:[[[id*12,0],[id*12+10,0],[id*12+10,10],[id*12,10],[id*12,0]],
                   [[id*12+3,3],[id*12+3,7],[id*12+7,7],[id*12+7,3],[id*12+3,3]]],
            color:[[.78,.28,.16],[.21,.64,.33],[.18,.32,.77]][id]}));
          function pixels(){const p=new Uint8Array(r.canvas.width*r.canvas.height*4);r.gl.readPixels(0,0,r.canvas.width,r.canvas.height,r.gl.RGBA,r.gl.UNSIGNED_BYTE,p);return p;}
          r.render(draws,camera,env);const before=pixels(),individual={...V018.render};
          draws.forEach(d=>d.v046Tile='cadastre:16:fixture');
          r.render(draws,camera,env);const after=pixels(),batched={...V018.render};
          let nonempty=0,alphaChanges=0,maxColorDelta=0,changedColorChannels=0;
          for(let i=0;i<before.length;i+=4){
            if(before[i+3])nonempty++;
            if(before[i+3]!==after[i+3])alphaChanges++;
            for(let c=0;c<3;c++){const delta=Math.abs(before[i+c]-after[i+c]);maxColorDelta=Math.max(maxColorDelta,delta);if(delta)changedColorChannels++;}
          }
          r.render(draws,camera,env);const cached={...V018.render};
          r.render([],camera,env);const cleared={...V018.render};
          return{individual,batched,cached,cleared,nonempty,alphaChanges,maxColorDelta,changedColorChannels,glError:r.gl.getError(),browser:navigator.userAgent};
        }""")
        result['terrain'] = page.evaluate("""() => {
          const r=new GLRenderer(document.getElementById('render'));
          const fixture=rendererTerrainFixture(),draws=fixture.draws;
          const camera={pos:[16,48,30],dir:vNorm([0,-46,-14]),fov:67};
          const env={sunDir:[.4,.8,.2],fog:[.45,.58,.58]};
          const sourceSnapshot=JSON.stringify({vertices:fixture.vertices,faces:draws.map(d=>d.faces)});
          function pixels(){const p=new Uint8Array(r.canvas.width*r.canvas.height*4);r.gl.readPixels(0,0,r.canvas.width,r.canvas.height,r.gl.RGBA,r.gl.UNSIGNED_BYTE,p);return p;}
          draws.forEach(d=>delete d.v046Terrain);
          r.render(draws,camera,env);const before=pixels(),individual={...V018.render};
          draws.forEach(d=>d.v046Terrain=true);
          r.render(draws,camera,env);const after=pixels(),batched={...V018.render};
          let nonempty=0,alphaChanges=0,maxColorDelta=0,changedColorChannels=0;
          for(let i=0;i<before.length;i+=4){
            if(before[i+3])nonempty++;
            if(before[i+3]!==after[i+3])alphaChanges++;
            for(let c=0;c<3;c++){const delta=Math.abs(before[i+c]-after[i+c]);maxColorDelta=Math.max(maxColorDelta,delta);if(delta)changedColorChannels++;}
          }
          const vp=m4Multiply(m4Perspective(rad(camera.fov),r.canvas.width/r.canvas.height,.08,8000),m4LookAt(camera.pos,vAdd(camera.pos,camera.dir)));
          const p=fixture.hole,clip=Array.from({length:4},(_,i)=>vp[i]*p[0]+vp[i+4]*p[1]+vp[i+8]*p[2]+vp[i+12]);
          const x=Math.floor((clip[0]/clip[3]+1)*r.canvas.width/2),y=Math.floor((clip[1]/clip[3]+1)*r.canvas.height/2),holeOffset=(y*r.canvas.width+x)*4;
          const holeAlpha=after[holeOffset+3];
          // Positive control: deliberately fill only this fixture's missing
          // sample. The same pixel must now be covered, proving the hole test
          // is aimed inside the visible surface rather than outside the mesh.
          const completeVertices=fixture.vertices.map(v=>v.slice());completeVertices[fixture.missing]=fixture.hole.slice();
          r.render([{...draws[0],vertices:completeVertices,faces:fixture.completeFaces}],camera,env);
          const filled=pixels(),filledHoleAlpha=filled[holeOffset+3];let extraCoverage=0;
          for(let i=3;i<after.length;i+=4)if(filled[i]&&!after[i])extraCoverage++;
          r.render(draws,camera,env);const restored=pixels();let restoredChanges=0;
          for(let i=0;i<after.length;i++)if(after[i]!==restored[i])restoredChanges++;
          r.render([],camera,env);
          return{individual,batched,nonempty,alphaChanges,maxColorDelta,changedColorChannels,holePixel:[x,y],holeAlpha,filledHoleAlpha,extraCoverage,restoredChanges,
            sourceUnchanged:sourceSnapshot===JSON.stringify({vertices:fixture.vertices,faces:draws.map(d=>d.faces)}),
            sharedVertices:draws[0].vertices===draws[1].vertices,noDataReferenced:draws.some(d=>d.faces.some(f=>f.includes(fixture.missing))),glError:r.gl.getError()};
        }""")
        browser.close()
    checks = {
        'native_shader_and_draw_without_exception': not errors,
        'real_pixels_rendered': result['nonempty'] > 1000,
        'same_geometry_coverage': result['alphaChanges'] == 0,
        'same_materials_with_one_byte_rounding_tolerance': result['maxColorDelta'] <= 1,
        'three_sources_one_draw': result['individual']['drawCalls'] == 3 and result['batched']['drawCalls'] == 1,
        'same_triangle_count': result['individual']['triangles'] == result['batched']['triangles'],
        'frame_reuses_native_uploads': result['batched']['batchBuilds'] == result['cached']['batchBuilds'],
        'native_buffers_released': result['cleared']['bufferGroups'] == 0,
        'no_webgl_error': result['glError'] == 0,
    }
    terrain = result['terrain']
    checks.update({
        'shared_fine_terrain_vertices_and_source_faces_unchanged': terrain['sharedVertices'] and terrain['sourceUnchanged'],
        'fine_terrain_real_pixels_rendered': terrain['nonempty'] > 1000,
        'fine_terrain_two_materials_one_draw': terrain['individual']['drawCalls'] == 2 and terrain['batched']['drawCalls'] == 1,
        'fine_terrain_source_triangle_count': terrain['individual']['triangles'] == terrain['batched']['triangles'] == 122,
        'fine_terrain_identical_coverage_and_materials': terrain['alphaChanges'] == 0 and terrain['maxColorDelta'] <= 1,
        'fine_terrain_nodata_sample_never_referenced': not terrain['noDataReferenced'],
        'fine_terrain_visible_nodata_hole_preserved': terrain['holeAlpha'] == 0 and terrain['filledHoleAlpha'] == 255 and terrain['extraCoverage'] > 100,
        'fine_terrain_republication_restores_exact_pixels': terrain['restoredChanges'] == 0,
        'fine_terrain_no_webgl_error': terrain['glError'] == 0,
    })
    report = {'suite': 'renderer_browser', 'passed': sum(checks.values()),
              'failed': sum(not ok for ok in checks.values()), 'checks': checks,
              'errors': errors, 'result': result}
    print(json.dumps(report, indent=2))
    return bool(report['failed'])


if __name__ == '__main__':
    raise SystemExit(main())
