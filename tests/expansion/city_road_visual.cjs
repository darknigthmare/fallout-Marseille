#!/usr/bin/env node
'use strict';

/* Native WebGL evidence for one complementary-road-fragment regression.
 * Reuses the SHA-checked synthetic fixture helpers from city_streaming.cjs,
 * the actual baseline/current enrichment modules, MistralIntegrity.roadMesh,
 * and the production GLRenderer/shaders. This is not a surveyed city capture.
 *
 * node tests/expansion/city_road_visual.cjs
 * Optional: CHROMIUM_PATH, PLAYWRIGHT_MODULE, MISTRAL_BASELINE_REF,
 *           MISTRAL_ROAD_VISUAL_OUTPUT. No download is performed.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');
const { createRequire } = require('node:module');

const ROOT = path.resolve(__dirname, '../..');
const CITY_MODULE = path.join(ROOT, 'src/v050/04a_city_sources.js');
const DEFAULT_BASELINE_REF = '5cfe4fcdc82bfbc5370024f7a4ca324f34d722af';
const BASELINE_REF = process.env.MISTRAL_BASELINE_REF || DEFAULT_BASELINE_REF;
const OUTPUT = path.resolve(process.env.MISTRAL_ROAD_VISUAL_OUTPUT ||
  path.join(ROOT, 'verification/gamedev-streaming-2026-10-29'));
const IMAGE_NAME = '04_ROAD_FRAGMENTS.png';
const REPORT_NAME = 'ROAD_VISUAL.json';
const integrity = require(path.join(ROOT, 'src/v046/00_integrity.js'));
const sha256 = data => crypto.createHash('sha256').update(data).digest('hex');
const plain = data => JSON.parse(JSON.stringify(data));

function playwright() {
  const candidates = [process.env.PLAYWRIGHT_MODULE, 'playwright',
    process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES &&
      path.join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES, 'playwright')].filter(Boolean);
  for (const candidate of candidates) {
    try { return require(candidate); } catch (error) {
      if (error.code !== 'MODULE_NOT_FOUND') throw error;
    }
  }
  throw Error('Playwright is required locally. Set PLAYWRIGHT_MODULE to an installed package; this test never downloads a browser.');
}

function helpers(citySource) {
  const filename = path.join(__dirname, 'city_streaming.cjs');
  const testSource = fs.readFileSync(filename, 'utf8');
  const firstCase = testSource.indexOf('\ntest(');
  assert.ok(firstCase > 0, 'The existing fixture helper boundary must be identifiable');
  const realRequire = createRequire(filename);
  const localFS = { ...fs, readFileSync(file, ...args) {
    if (path.resolve(String(file)) === CITY_MODULE) return citySource;
    return fs.readFileSync(file, ...args);
  } };
  const context = vm.createContext({
    require: name => name === 'node:fs' ? localFS : realRequire(name),
    __dirname, __filename: filename, console, AbortController, setTimeout, clearTimeout,
    TextDecoder, TextEncoder, Uint8Array, Buffer
  });
  vm.runInContext(testSource.slice(0, firstCase) +
    '\nglobalThis.fixtureHelpers={descriptor,files,sandbox,run,plain,BOX,Q,REGION,PROOF};',
    context, { filename: 'city_streaming.fixture_helpers.cjs' });
  return context.fixtureHelpers;
}

function roadFixture(h) {
  // This is the same two-partition case as the final city_streaming test.
  // The full source line and ID are identical in both receipts; each receipt
  // clips its renderable portion to its own query bounds.
  const fixture = h.files();
  const index = JSON.parse(fixture.data['data/map_pack/city/index.json']);
  index.coverage = { complete: true, uniqueBuildings: 0, uniqueRoads: 1 };
  const roadCoordinates = [[5.351, 43.295], [5.359, 43.295]];
  const boxes = [[43.29, 5.35, 43.30, 5.355], [43.29, 5.355, 43.30, 5.36]];
  index.tiles = boxes.map((queryBbox, i) => {
    const roadProof = { bbox: queryBbox, crs: 'EPSG:4326', complete: true,
      layer: 'BDTOPO_V3:troncon_de_route', returned: 1 };
    const coverages = [{ ...roadProof, layer: 'BDTOPO_V3:batiment', returned: 0 }, roadProof];
    const road = { type: 'Feature', id: 'fixture-road', properties: {
      kind: 'road', sourceId: 'fixture-road', provenance: { ...h.PROOF, coverage: roadProof }
    }, geometry: { type: 'LineString', coordinates: roadCoordinates } };
    const raw = { schemaVersion: 1, region: h.REGION, queryBbox,
      features: [road], source: h.PROOF, coverages };
    const chunk = h.descriptor(raw, 'm13055-road-' + i, h.Q);
    Object.assign(chunk.descriptor, { id: 'm13055-road-' + i, region: h.REGION,
      queryBbox, renderBbox: queryBbox, coverages, counts: { buildings: 0, roads: 1 } });
    fixture.data[chunk.descriptor.path] = chunk.data;
    return plain(chunk.descriptor);
  });
  fixture.data['data/map_pack/city/index.json'] = JSON.stringify(index);
  for (const descriptor of index.tiles) {
    assert.equal(sha256(fixture.data[descriptor.path]), descriptor.sha256);
    assert.equal(Buffer.byteLength(fixture.data[descriptor.path]), descriptor.bytes);
  }
  return { ...fixture, index, roadCoordinates };
}

async function enrich(h, fixture) {
  const context = h.sandbox(fixture.data);
  await h.run(context, 'v051CityReady()');
  context.resource = { source: 'base', z: 14, x: 0, y: 0, layers: {} };
  const result = await h.run(context, 'v051CityEnrich(resource)');
  const roads = plain(result.layers.transportation.features);
  const again = await h.run(context, 'v051CityEnrich(resource)');
  h.run(context, 'V051_CITY.index.tiles.reverse()');
  const reversed = await h.run(context, 'v051CityEnrich(resource)');
  const geometryOf = features => features.map(f => f.v050Paths);
  const paths = roads.flatMap(f => f.v050Paths);
  const meshes = roads.flatMap(feature => feature.v050Paths.map(sourcePath => {
    const mesh = integrity.roadMesh(sourcePath, feature.props, () => 0);
    return { sourceId: feature.sourceId, path: sourcePath, profile: {
      width: mesh.width, widthAssumed: mesh.widthAssumed, widthBasis: mesh.widthBasis,
      heightBasis: mesh.heightBasis
    }, vertices: mesh.vertices, faces: mesh.faces };
  }));
  const length = paths.reduce((total, route) => total + route.slice(1).reduce((sum, point, i) =>
    sum + Math.hypot(point[0] - route[i][0], point[1] - route[i][1]), 0), 0);
  return {
    sourceIds: [...new Set(roads.map(f => f.sourceId))],
    features: roads.length, paths, length,
    sourceGeometrySha256: [...new Set(roads.map(f => sha256(JSON.stringify(f.v050Geometry))))],
    fragmentsSha256: sha256(JSON.stringify(paths)),
    geometryConflicts: h.run(context, 'V051_CITY.geometryConflicts'),
    repeatedLoadStable: JSON.stringify(geometryOf(roads)) ===
      JSON.stringify(geometryOf(plain(again.layers.transportation.features))),
    reverseOrderStable: JSON.stringify(geometryOf(roads)) ===
      JSON.stringify(geometryOf(plain(reversed.layers.transportation.features))),
    triangles: meshes.reduce((total, mesh) => total + mesh.faces.length, 0),
    vertices: meshes.reduce((total, mesh) => total + mesh.vertices.length, 0),
    meshes
  };
}

function rendererSource() {
  const core = fs.readFileSync(path.join(ROOT, 'src/core-v017.js'), 'utf8');
  const geometry = fs.readFileSync(path.join(ROOT, 'src/patches/01_geometry.js'), 'utf8');
  const start = core.indexOf('function v3('), end = core.indexOf('class SoftwareRenderer');
  const patchEnd = geometry.indexOf('/* The software fallback');
  assert.ok(start >= 0 && end > start && patchEnd > 0, 'Production renderer extraction boundaries');
  let source = core.slice(start, end);
  for (const name of ['v017SignedArea', 'v017PointInPoly']) {
    const definition = core.split('\n').find(line => line.startsWith('function ' + name + '('));
    assert.ok(definition, 'Production definition missing: ' + name);
    source += '\n' + definition;
  }
  return source + '\n' + geometry.slice(0, patchEnd);
}

function html(before, after) {
  const card = (key, label, result, detail) => `
    <section class="card ${key}">
      <div class="card-title"><h2>${label}</h2><span>${detail}</span></div>
      <div class="stats"><div><strong>${result.features}<small> / 2</small></strong><span>fragments conservés</span></div>
        <div><strong>${Math.round(result.length / 8 * 100)}<small> %</small></strong><span>du tracé de test</span></div>
        <div><strong>${result.triangles}</strong><span>triangles de route</span></div></div>
      <canvas id="${key}" aria-label="Rendu WebGL natif ${label.toLowerCase()} du banc synthétique"></canvas>
      <div class="partition-labels"><span>PARTITION OUEST</span><span class="seam">⋮ &nbsp; LIMITE DU REÇU &nbsp; ⋮</span><span>PARTITION EST</span></div>
      <p class="card-note">${key === 'before' ?
        'La déduplication élimine la seconde moitié de la route.' :
        'Les fragments complémentaires gardent leur même identité source.'}</p>
    </section>`;
  return `<!doctype html><html lang="fr"><meta charset="utf-8"><title>Fallout : Mistral — banc synthétique des routes</title>
  <style>
    *{box-sizing:border-box}html,body{margin:0;min-height:100%;background:#111916;color:#edf2e9;font-family:Arial,Helvetica,sans-serif}
    body{padding:38px 42px 30px}header{display:flex;justify-content:space-between;gap:26px;align-items:flex-start;margin-bottom:28px}
    .eyebrow{font-size:13px;letter-spacing:2px;font-weight:700;color:#bed29f;margin-bottom:13px}h1{font-size:43px;line-height:1.07;margin:0 0 12px;font-weight:700;letter-spacing:-1px}
    .subtitle{font-size:18px;color:#b7c3b8;line-height:1.5;margin:0}.badge{border:1px solid #6c7548;background:#242c1d;padding:15px 18px;min-width:260px;font-size:14px;line-height:1.6;letter-spacing:1px;color:#d8e5b9;text-align:center}.badge b{font-size:16px;display:block}
    .comparison{display:grid;grid-template-columns:1fr 1fr;gap:26px}.card{overflow:hidden;border:1px solid #3c4b3e;border-radius:8px;background:#18221c}.card-title{display:flex;justify-content:space-between;align-items:center;padding:20px 22px 0;gap:16px}.card-title h2{font-size:21px;letter-spacing:2px;margin:0}.card-title span{font-size:14px;color:#bdc9bf}.before h2{color:#edbf86}.after h2{color:#b5d88d}
    .stats{display:grid;grid-template-columns:1fr 1fr 1fr;padding:22px 22px 18px;gap:12px}.stats strong{font-size:36px;display:block;font-weight:700;line-height:1.1}.stats small{font-size:20px;color:#98a99b;font-weight:400}.stats span{display:block;color:#a7b7aa;font-size:13px;margin-top:8px}
    canvas{display:block;width:100%;aspect-ratio:8/5;background:#101b17}.partition-labels{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:14px 22px 0;font-size:11px;letter-spacing:1px;color:#97a99a}.partition-labels .seam{color:#e0c090;font-size:10px;letter-spacing:.6px}.card-note{font-size:15px;line-height:1.45;padding:0 22px 18px;margin:14px 0 0;color:#d9e3d6}
    footer{margin-top:25px;padding-top:20px;border-top:1px solid #3a493b;display:grid;grid-template-columns:1.08fr 1fr;gap:32px;font-size:14px;line-height:1.55;color:#b5c3b7}footer p{margin:0}footer strong{color:#e5eddd}.method{display:block;font-size:12px;letter-spacing:1px;color:#c1d6a8;margin-bottom:7px}.limits{color:#a6b6aa}
  </style><body>
    <header><div><div class="eyebrow">FALLOUT : MISTRAL · VÉRIFICATION DU STREAMING</div><h1>Une route, deux fragments</h1><p class="subtitle">Même source, mêmes données et même caméra : la seconde moitié doit rester visible.</p></div>
      <div class="badge"><b>BANC SYNTHÉTIQUE</b>RENDU WEBGL NATIF<br>29 OCTOBRE 2026</div></header>
    <main class="comparison">${card('before', 'AVANT', before, 'Régression reproduite')}${card('after', 'APRÈS', after, 'Correctif appliqué')}</main>
    <footer><p><span class="method">CHAÎNE DE RENDU RÉELLE</span><strong>2 partitions vérifiées par SHA-256</strong> → enrichisseur avant / après → <strong>roadMesh + GLRenderer de production</strong>.<br>Une identité source conservée ; aucun conflit de géométrie dans ce cas.</p>
      <p class="limits"><strong>Portée :</strong> fixture déclarée, sans rue réelle ni données de terrain mesurées. Projection et sol constants du test ; même largeur par défaut. Fond et pointillés : repères du banc. Ce contrôle ne certifie pas la carte entière ou les déplacements du joueur.</p></footer>
  </body></html>`;
}

async function capture(before, after) {
  const { chromium } = playwright();
  const executablePath = process.env.CHROMIUM_PATH;
  if (executablePath) assert.ok(fs.statSync(executablePath).isFile(), 'CHROMIUM_PATH must name an existing executable');
  const browser = await chromium.launch({ ...(executablePath ? { executablePath } : {}),
    headless: true, timeout: 45000,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--use-gl=angle',
      '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--disable-background-networking'] });
  const errors = [];
  try {
    const context = await browser.newContext({ offline: true,
      viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1 });
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(String(error)));
    await page.setContent(html(before, after));
    await page.addScriptTag({ content: `
      const TAU=Math.PI*2,COLORS={white:[1,1,1]},settings={quality:'medium'};
      const world={v046:true,geoMacro:true,id:'geo_marseille_commune'};
      const rad=n=>n*Math.PI/180;
    ` + rendererSource() });
    const native = await page.evaluate(({ before, after }) => {
      const camera = { pos: [0, 14, 11], dir: vNorm([0, -14, -11]), fov: 48 };
      const environment = { sunDir: [.3, .85, .4], fog: [.12, .19, .15] };
      const origin = [5355, 0, -43295];
      const reports = {};
      for (const [key, source] of [['before', before], ['after', after]]) {
        const renderer = new GLRenderer(document.getElementById(key));
        const roadDraws = source.meshes.map((mesh, i) => ({ mesh: 'geoSurface',
          id: key + '-source-road-' + i, pos: [0, 0, 0],
          vertices: mesh.vertices.map(p => p.map((value, axis) => value - origin[axis])),
          faces: mesh.faces, color: [.62, .70, .57], v046Tile: 'base:14:synthetic-fixture', revision: 0 }));
        renderer.render(roadDraws, camera, environment);
        const gl = renderer.gl;
        const pixels = new Uint8Array(renderer.canvas.width * renderer.canvas.height * 4);
        gl.readPixels(0, 0, renderer.canvas.width, renderer.canvas.height, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
        let nonempty = 0, leftCoverage = 0, rightCoverage = 0;
        for (let pixel = 0; pixel < pixels.length / 4; pixel++) if (pixels[pixel * 4 + 3]) {
          nonempty++;
          const x = pixel % renderer.canvas.width;
          if (x < renderer.canvas.width / 2 - 5) leftCoverage++;
          if (x > renderer.canvas.width / 2 + 5) rightCoverage++;
        }
        const roadRender = { ...V018.render };
        const guides = [
          { mesh: 'cube', pos: [-3, -.13, 0], scale: [6, .18, 10], color: [.19, .25, .21] },
          { mesh: 'cube', pos: [3, -.13, 0], scale: [6, .18, 10], color: [.14, .20, .17] }
        ];
        // Reference marks are part of the declared synthetic bench, not GIS data.
        for (let z = -4.8; z <= 4.8; z += .8) guides.push({ mesh: 'cube',
          pos: [0, .13, z], scale: [.035, .015, .37], color: [.76, .61, .34], emissive: .2 });
        renderer.render([...guides, ...roadDraws], camera, environment);
        const extension = gl.getExtension('WEBGL_debug_renderer_info');
        reports[key] = { nativeCanvas: [renderer.canvas.width, renderer.canvas.height],
          nonempty, leftCoverage, rightCoverage, roadRender, composedRender: { ...V018.render },
          glError: gl.getError(), backend: gl.getParameter(gl.VERSION),
          renderer: extension ? gl.getParameter(extension.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER) };
      }
      return { ...reports, camera, originTranslation: origin,
        browser: navigator.userAgent, method: 'Direct screenshot of two production-WebGL canvases; no pixel compositing.' };
    }, { before, after });
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    await page.screenshot({ path: path.join(OUTPUT, IMAGE_NAME), fullPage: true, animations: 'disabled' });
    return { ...native, browserVersion: browser.version(), errors };
  } finally { await browser.close(); }
}

async function main() {
  fs.mkdirSync(OUTPUT, { recursive: true });
  const baseline = execFileSync('git', ['show', BASELINE_REF + ':src/v050/04a_city_sources.js'],
    { cwd: ROOT, encoding: 'utf8', maxBuffer: 2 * 1024 * 1024 });
  const corrected = fs.readFileSync(CITY_MODULE, 'utf8');
  assert.notEqual(sha256(baseline), sha256(corrected), 'Baseline and corrected modules must differ');
  const beforeHelpers = helpers(baseline), afterHelpers = helpers(corrected);
  const fixture = roadFixture(afterHelpers);
  const inputFingerprint = sha256(JSON.stringify(fixture.data));
  const before = await enrich(beforeHelpers, fixture);
  const after = await enrich(afterHelpers, fixture);
  assert.deepEqual(before.sourceIds, ['fixture-road']);
  assert.deepEqual(after.sourceIds, ['fixture-road']);
  assert.equal(before.features, 1, 'The requested baseline must reproduce the dropped fragment');
  assert.equal(after.features, 2, 'Both complementary fragments must survive');
  assert.deepEqual(after.paths.map(p => [p[0][0], p.at(-1)[0]]).sort((a, b) => a[0] - b[0]),
    [[5351, 5355], [5355, 5359]]);
  assert.equal(sha256(JSON.stringify(fixture.data)), inputFingerprint, 'The source bytes must remain untouched');
  const native = await capture(before, after);
  const checks = {
    same_sha_checked_two_partition_fixture: fixture.index.tiles.length === 2,
    baseline_reproduces_lost_east_fragment: before.features === 1 && before.length === 4,
    corrected_preserves_both_exact_source_fragments: after.features === 2 && after.length === 8,
    same_complete_source_geometry: JSON.stringify(before.sourceGeometrySha256) === JSON.stringify(after.sourceGeometrySha256),
    no_false_geometry_conflict: before.geometryConflicts === 0 && after.geometryConflicts === 0,
    corrected_repeat_and_reverse_order_stable: after.repeatedLoadStable && after.reverseOrderStable,
    native_production_shader_and_draw: native.errors.length === 0 && native.before.roadRender.backend === 'WebGL' && native.after.roadRender.backend === 'WebGL',
    native_triangle_counts_match_meshes: native.before.roadRender.triangles === before.triangles && native.after.roadRender.triangles === after.triangles,
    before_has_no_east_road_pixels: native.before.leftCoverage > 1000 && native.before.rightCoverage === 0,
    after_has_native_road_pixels_in_both_partitions: native.after.leftCoverage > 1000 && native.after.rightCoverage > 1000,
    corrected_native_coverage_doubles: native.after.nonempty > native.before.nonempty * 1.98 && native.after.nonempty < native.before.nonempty * 2.02,
    no_webgl_errors: native.before.glError === 0 && native.after.glError === 0,
    fixture_bytes_unchanged: sha256(JSON.stringify(fixture.data)) === inputFingerprint
  };
  const report = {
    suite: 'city_road_visual', kind: 'synthetic native WebGL regression evidence',
    createdAt: new Date().toISOString(), passed: Object.values(checks).filter(Boolean).length,
    failed: Object.values(checks).filter(value => !value).length, checks,
    source: { baselineRef: BASELINE_REF, defaultPublishedBaselineRef: DEFAULT_BASELINE_REF,
      module: 'src/v050/04a_city_sources.js', baselineSha256: sha256(baseline), correctedSha256: sha256(corrected),
      productionModules: Object.fromEntries(['src/v046/00_integrity.js', 'src/core-v017.js',
        'src/patches/01_geometry.js', 'src/v050/04_source_geometry.js', 'tests/expansion/city_streaming.cjs']
        .map(file => [file, sha256(fs.readFileSync(path.join(ROOT, file)))])) },
    fixture: { label: 'EXPLICIT SYNTHETIC FIXTURE — NOT REAL CITY GEOGRAPHY',
      projection: 'Existing test helper: x=longitude*1000; z=-latitude*1000. Test units are not surveyed metres.',
      sourceId: 'fixture-road', sourceCoordinates: fixture.roadCoordinates,
      inputSha256: inputFingerprint, partitions: fixture.index.tiles,
      ground: 'constant test sample=0; no real DEM', expectedProjectedExtent: [5351, 5359], boundary: 5355 },
    before, after, native,
    screenshot: { path: path.relative(ROOT, path.join(OUTPUT, IMAGE_NAME)),
      sha256: sha256(fs.readFileSync(path.join(OUTPUT, IMAGE_NAME))) },
    limitations: ['Controlled road-enrichment regression fixture only; not a capture of a real street.',
      'Production roadMesh and GLRenderer are reused, with a translation to center the fixture camera.',
      'The constant test ground and renderer guide cubes are synthetic; road width uses the same production default in both views.',
      'No claim of full-game traversal, collision checks, real-city atlas completeness, hardware GPU performance, or human playtesting.']
  };
  fs.writeFileSync(path.join(OUTPUT, REPORT_NAME), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ suite: report.suite, passed: report.passed, failed: report.failed,
    beforeFragments: before.features, afterFragments: after.features,
    beforeTriangles: before.triangles, afterTriangles: after.triangles,
    screenshot: path.join(OUTPUT, IMAGE_NAME), report: path.join(OUTPUT, REPORT_NAME) }, null, 2));
  if (report.failed) process.exitCode = 1;
}
main().catch(error => { console.error(error.stack || error); process.exitCode = 1; });
