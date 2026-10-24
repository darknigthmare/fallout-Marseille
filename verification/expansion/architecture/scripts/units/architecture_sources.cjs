'use strict';
/* Production architecture registry, adapters and offline installer. All plans
   and site labels below are explicit synthetic fixtures, never atlas records. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawnSync} = require('node:child_process');
const test = require('node:test');
const root = path.resolve(__dirname, '../..');
const A = require('../../src/v050/06_architecture_sources.js');
const F = require('../../src/v050/07_facades.js');
const I = require('../../src/v050/08_city_interiors.js');
const adapters = {facades: F, interiors: I};
const copy = value => JSON.parse(JSON.stringify(value));
const rawGeometry = {type: 'Polygon', coordinates: [[[5.4,43.3],[5.4002,43.3],[5.4002,43.3002],[5.4,43.3002],[5.4,43.3]]]};
const source = {url: 'https://example.org/synthetic-architecture-fixture', title: 'Explicit synthetic architecture fixture', license: 'CC0 test fixture', attribution: 'Automated registry test', accessedAt: '2026-10-24', responseSha256: 'a'.repeat(64)};
const rings = [[[100,-200],[120,-200],[120,-180],[100,-180],[100,-200]]];
function draw(properties = {}) {
  return {mesh: 'prism', geoLayer: 'building', rings: copy(rings), baseY: 31.25, height: 12, sourceGeometry: copy(rawGeometry), geoProperties: {cleabs: 'SYNTHETIC-ARCHITECTURE-TEST', sourceId: 'fixture.source.1', nombre_d_etages: 3, usage_1: 'Indifférencié', ...properties}};
}
function target(d = draw()) {
  const p = F.describe(d);
  return {cleabs: d.geoProperties.cleabs, rawGeometry: copy(d.sourceGeometry), component: {id: p.id, baseY: p.baseY, height: p.height, levels: p.levels, rings: copy(p.rings)}};
}
const label = () => ({kind: 'site-context', text: 'Synthetic hospital building', siteName: 'Synthetic test site', use: 'Hôpital', precisionMeters: 1, geometryFictive: false, buildingOverlapRatio: .999, centroidInside: true});
function interiorDocument(t) {
  const b = I.building({...t.component, sourceId: t.cleabs, properties: {}});
  return {schemaVersion: 1, frame: 'building-local-metre', buildingId: b.id, source: copy(source), levels: [{level: 0, elevation: 0, height: 4, entry: [-8,-8], walls: [{a: [-2,-10], b: [-2,-1], thickness: .2}, {a: [-2,1], b: [-2,10], thickness: .2}], rooms: [{id: 'west', use: 'Bureau', ring: [[-10,-10],[-2,-10],[-2,10],[-10,10],[-10,-10]]}]}]};
}
const facadeDocument = () => ({schemaVersion: 1, source: source.url, license: source.license, attribution: source.attribution, acquiredAt: source.accessedAt, openings: [{type: 'door', ringIndex: 0, edgeIndex: 0, offset: 3, bottom: 0, width: 1, height: 2.2}, {type: 'window', ringIndex: 0, edgeIndex: 1, offset: 5, bottom: 5, width: 1.2, height: 1.4}], completeEdges: [{ringIndex: 0, edgeIndex: 0}]});
function record({plans = true, bound = true} = {}) {
  const t = target();
  return {id: 'synthetic-attribution-fixture', target: {...t, ...(bound ? {} : {component: null})}, source: copy(source), label: label(), ...(plans ? {facadeDocument: facadeDocument(), interiorDocument: interiorDocument(t)} : {})};
}
const atlas = (records = [record()]) => ({schemaVersion: 1, frame: 'engine-lambert93-metre', records});
function freeze(value) { if (value && typeof value === 'object' && !Object.isFrozen(value)) { Object.freeze(value); for (const child of Object.values(value)) freeze(child); } return value; }
function registry(records) { return new A.Registry(atlas(records), adapters); }

test('Actual facade and interior validators accept the attributed metric fixture without changing it', () => {
  const raw = atlas(), before = copy(raw), out = A.validate(freeze(raw), adapters), d = draw();
  assert.deepEqual(raw, before);
  assert.equal(out.records.length, 1);
  assert.notEqual(out.records[0].source, raw.records[0].source);
  const reg = new A.Registry(raw, adapters);
  assert.equal(reg.apply(d), true);
  const description = F.describe(d), b = I.building(description), plan = I.layout(b, 0, null, d.geoProperties.interiorDocument);
  assert.equal(description.id, target().component.id);
  assert.equal(description.baseY, 31.25);
  assert.equal(description.height, 12);
  assert.deepEqual(b.origin, [110,31.25,-190]);
  assert.equal(plan.provenance, 'documented');
  assert.equal(plan.elevation, 0);
  assert.equal(plan.height, 4);
  assert.deepEqual(plan.rooms[0].ring, before.records[0].interiorDocument.levels[0].rooms[0].ring.slice(0,-1));
  assert.equal(plan.source.url, source.url);
  assert.equal(F.entrances(d).find(e => e.provenance === 'documented').center[0], 103.5);
  assert.deepEqual(reg.info(), {records: 1, siteLabels: 1, facadeDocuments: 1, interiorDocuments: 1, appliedRecords: 1, rejected: []});
});

test('Applying an overlay preserves exact source properties, geometry, rings and collider ownership', () => {
  const d = draw(), oldProps = freeze(d.geoProperties), raw = freeze(d.sourceGeometry), sourceRings = freeze(d.rings);
  d.colliders = freeze([{id: 'original-solid'}]);
  const before = copy(d), reg = registry();
  assert.equal(reg.apply(d), true);
  assert.notEqual(d.geoProperties, oldProps);
  assert.deepEqual(oldProps, before.geoProperties);
  assert.equal(d.sourceGeometry, raw);
  assert.equal(d.rings, sourceRings);
  assert.deepEqual(d.rings, before.rings);
  assert.deepEqual(d.colliders, before.colliders);
  assert.equal(d.baseY, before.baseY);
  assert.equal(d.height, before.height);
});

test('Registry records and independently applied draws do not alias caller annotations', () => {
  const raw = atlas(), reg = new A.Registry(raw, adapters), first = draw(), second = draw();
  raw.records[0].source.title = 'caller edit';
  raw.records[0].facadeDocument.openings[0].offset = 999;
  assert.equal(reg.apply(first), true);
  first.geoProperties.facadeDocument.openings[0].offset = 999;
  first.geoProperties.interiorDocument.levels[0].walls[0].a[0] = 999;
  first.geoProperties.architectureSite.source.title = 'applied draw edit';
  assert.equal(reg.apply(second), true);
  assert.equal(second.geoProperties.facadeDocument.openings[0].offset, 3);
  assert.equal(second.geoProperties.interiorDocument.levels[0].walls[0].a[0], -2);
  assert.equal(second.geoProperties.architectureSite.source.title, source.title);
});

test('A site label without plans does not claim documentary facade or room geometry', () => {
  const r = record({plans: false, bound: false}), d = draw(), reg = registry([r]);
  assert.equal(reg.apply(d), true);
  assert.equal(d.geoProperties.name, r.label.text);
  assert.equal(d.geoProperties.facadeDocument, undefined);
  assert.equal(d.geoProperties.interiorDocument, undefined);
  assert.equal(reg.info().facadeDocuments, 0);
  assert.equal(reg.info().interiorDocuments, 0);
  assert.equal(F.describe(d).provenance, 'invented');
});

test('A context changing inferred storeys cannot attach a plan bound to the former floor count', () => {
  const d=draw({nombre_d_etages:null}),r=record();r.target=target(d);r.label.use='Religieux';r.interiorDocument=interiorDocument(r.target);r.interiorDocument.levels[0].height=3;
  const reg=registry([r]),before=copy(d);assert.equal(F.describe(d).levels,4);assert.equal(reg.apply(d),false);assert.deepEqual(d,before);assert.equal(reg.info().appliedRecords,0);assert.deepEqual(reg.info().rejected,[{id:r.id,reason:'component-or-edge-order-changed'}]);
});

test('A plan bound to the final contextual volume remains valid and idempotent', () => {
  const d=draw({nombre_d_etages:null}),r=record();r.label.use='Religieux';const contextual=copy(d);contextual.geoProperties.architectureUse=r.label.use;r.target=target(contextual);r.interiorDocument=interiorDocument(r.target);r.interiorDocument.levels[0].height=12;
  const reg=registry([r]);assert.equal(r.target.component.levels,1);assert.equal(reg.apply(d),true);assert.equal(F.describe(d).levels,1);assert.doesNotThrow(()=>I.document(d.geoProperties.interiorDocument,I.building(F.describe(d))));const once=copy(d);assert.equal(reg.apply(d),true);assert.deepEqual(d,once);assert.deepEqual(reg.info().rejected,[]);
});

test('Generic feminine nature and building=yes allow context, while a specific IGN nature retains priority', () => {
  const r=record({plans:false,bound:false}),generic=draw({nature:'Indifférenciée',building:'yes'}),specific=draw({nature:'Église'});r.label.use='Hôpital';const reg=registry([r]);assert.equal(reg.apply(generic),true);assert.equal(generic.geoProperties.architectureUse,'Hôpital');assert.equal(F.describe(generic).style,'civic');assert.equal(reg.apply(specific),true);assert.equal(specific.geoProperties.architectureUse,undefined);assert.equal(F.describe(specific).style,'religious');
});

test('A missing identity or source geometry leaves a draw untouched', () => {
  const reg = registry();
  for (const d of [draw({cleabs: 'another-building'}), {...draw(), sourceGeometry: null}]) {
    const before = copy(d);
    assert.equal(reg.apply(d), false);
    assert.deepEqual(d, before);
  }
  assert.equal(reg.info().appliedRecords, 0);
});

test('The exact acquired geographic geometry must match, including coordinate order and elevation', () => {
  for (const change of [d => d.sourceGeometry.coordinates[0][1][0] += 1e-9, d => d.sourceGeometry.coordinates[0].forEach(p => p.push(0)), d => { const r = d.sourceGeometry.coordinates[0].slice(0,-1); r.push(r.shift()); r.push(r[0].slice()); d.sourceGeometry.coordinates[0] = r; }]) {
    const reg = registry(), d = draw(); change(d); const before = copy(d);
    assert.equal(reg.apply(d), false);
    assert.deepEqual(d, before);
    assert.deepEqual(reg.info().rejected, [{id: 'synthetic-attribution-fixture', reason: 'source-geometry-changed'}]);
  }
});

test('The same stable building ID cannot relocate documented edges after metric ring rotation or reversal', () => {
  for (const change of [r => r.slice(1,-1).concat([r[0],r[1]]), r => r.slice().reverse()]) {
    const reg = registry(), d = draw(), id = F.describe(d).id;
    d.rings = [change(d.rings[0])];
    assert.equal(F.describe(d).id, id);
    const before = copy(d);
    assert.equal(reg.apply(d), false);
    assert.deepEqual(d, before);
    assert.equal(reg.info().rejected[0].reason, 'component-or-edge-order-changed');
  }
});

for (const [name, change] of [
  ['height', d => d.height += .01],
  ['absolute base', d => d.baseY += .01],
  ['floor count', d => d.geoProperties.nombre_d_etages = 4],
  ['metric footprint', d => d.rings[0][1][0] += .01]
]) test('A changed source '+name+' rejects all parts of its bound annotation atomically', () => {
  const reg = registry(), d = draw(); change(d); const before = copy(d);
  assert.equal(reg.apply(d), false);
  assert.deepEqual(d, before);
  assert.equal(reg.info().appliedRecords, 0);
  assert.equal(reg.info().rejected[0].reason, 'component-or-edge-order-changed');
});

test('An established source name and use win over a contextual site label', () => {
  const d = draw({name: 'Source name', usage_1: 'Résidentiel'}), reg = registry();
  assert.equal(reg.apply(d), true);
  assert.equal(d.geoProperties.name, 'Source name');
  assert.equal(d.geoProperties.usage_1, 'Résidentiel');
  assert.equal(d.geoProperties.architectureUse, undefined);
  assert.equal(F.describe(d).style, 'residential');
  assert.equal(I.building(F.describe(d)).use, 'Résidentiel');
});

for (const field of ['nom', 'nom_du_batiment']) test('Existing source '+field+' remains the displayed name', () => {
  const d = draw({[field]: 'Source display name'}); registry().apply(d);
  assert.equal(d.geoProperties.name, undefined);
  assert.equal(I.building(F.describe(d)).name, 'Source display name');
});

test('Unknown source usage can consume attributed context without overwriting IGN fields', () => {
  const d = draw(); registry().apply(d);
  assert.equal(d.geoProperties.usage_1, 'Indifférencié');
  assert.equal(d.geoProperties.architectureUse, 'Hôpital');
  assert.equal(F.describe(d).style, 'civic');
  assert.equal(I.programTheme(I.building(F.describe(d)).use), 'medical');
});

test('An explicit secondary source use also wins over site context', () => {
  const d = draw({usage_2: 'Commercial et services'}); registry().apply(d);
  assert.equal(d.geoProperties.architectureUse, undefined);
  assert.equal(d.geoProperties.usage_1, 'Indifférencié');
  assert.equal(d.geoProperties.usage_2, 'Commercial et services');
  assert.equal(F.describe(d).style, 'commercial');
  assert.equal(I.programTheme(I.building(F.describe(d)).use), 'commercial');
});

test('Existing documentary parts retain priority while missing parts may be filled', () => {
  const existing = facadeDocument(), d = draw({facadeDocument: existing});
  existing.openings[0].offset = 8;
  registry().apply(d);
  assert.equal(d.geoProperties.facadeDocument, existing);
  assert.equal(d.geoProperties.facadeDocument.openings[0].offset, 8);
  assert.equal(d.geoProperties.interiorDocument.buildingId, target().component.id);
});

for (const [name, change] of [
  ['HTTP source', r => r.source.url = 'http://example.org/plan'],
  ['credential source', r => r.source.url = 'https://user:pass@example.org/plan'],
  ['missing attribution', r => delete r.source.attribution],
  ['response digest', r => r.source.responseSha256 = 'bad'],
  ['fictive site geometry', r => r.label.geometryFictive = true],
  ['inadequate site overlap', r => r.label.buildingOverlapRatio = .98],
  ['site centroid outside', r => r.label.centroidInside = false],
  ['site precision', r => r.label.precisionMeters = 3.1],
  ['open geographic ring', r => r.target.rawGeometry.coordinates[0].pop()],
  ['invalid longitude', r => r.target.rawGeometry.coordinates[0][0][0] = 181],
  ['non-finite metric point', r => r.target.component.rings[0][0][0] = Infinity],
  ['open metric ring', r => r.target.component.rings[0].pop()],
  ['facade private URL', r => r.facadeDocument.source = 'https://user:secret@example.org/plan'],
  ['facade invalid acquisition date', r => r.facadeDocument.acquiredAt = 'yesterday'],
  ['facade width outside edge', r => r.facadeDocument.openings[0].width = 50],
  ['facade above roof', r => r.facadeDocument.openings[0].height = 50],
  ['unknown facade edge', r => r.facadeDocument.completeEdges[0].edgeIndex = 900],
  ['foreign interior identity', r => r.interiorDocument.buildingId = 'another-building'],
  ['missing interior source', r => delete r.interiorDocument.source.license],
  ['interior wall outside', r => r.interiorDocument.levels[0].walls[0].a = [200,200]],
  ['plan without metric binding', r => r.target.component = null]
]) test('Invalid '+name+' rejects the whole atlas without changing input or an existing registry', () => {
  const reg = registry(), raw = atlas(), beforeInfo = copy(reg.info()); change(raw.records[0]);
  const before = copy(raw);
  assert.throws(() => A.validate(raw, adapters));
  assert.deepEqual(copy(raw), before);
  assert.deepEqual(reg.info(), beforeInfo);
  const d = draw(); assert.equal(reg.apply(d), true);
  assert.equal(d.geoProperties.facadeDocument.openings[0].offset, 3);
});

test('Duplicate record identities or component targets cannot create order-dependent overlays', () => {
  const first = record(), second = copy(first); second.id = 'second-fixture';
  assert.throws(() => A.validate(atlas([first, copy(first)]), adapters), /dupliqué/);
  assert.throws(() => A.validate(atlas([first, second]), adapters), /dupliquée/);
});

test('Atlas budgets reject large unbounded collections before application', () => {
  assert.throws(() => A.validate({schemaVersion: 1, frame: 'degrees', records: []}, adapters));
  assert.throws(() => A.validate(atlas(Array.from({length: A.MAX_RECORDS + 1}, () => record())), adapters), /budget/);
  const raw = atlas(); raw.unused = 'x'.repeat(A.MAX_BYTES);
  assert.throws(() => A.validate(raw, adapters), /budget/);
  assert.throws(() => A.validate(atlas(), {facades: F}), /validateurs/);
});

test('Delivered IGN site labels retain acquired building geometry, source hashes and honest site-only claims', () => {
  const installed = JSON.parse(fs.readFileSync(path.join(root, 'data/map_pack/architecture/index.json')));
  const reg = new A.Registry(installed, adapters), cache = new Map();
  const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
  const indexHash = digest(fs.readFileSync(path.join(root, 'data/map_pack/city/index.json')));
  assert.ok(installed.records.length >= 12);
  for (const entry of installed.records) {
    assert.doesNotMatch(JSON.stringify(entry), /example\.org|synthetic|fixture/i);
    const evidence = entry.associationEvidence, binding = evidence.buildingSource;
    assert.equal(binding.indexSha256, indexHash);
    assert.match(binding.chunkPath, /^data\/map_pack\/city\/[a-z0-9-]+\.json$/);
    let chunk = cache.get(binding.chunkPath);
    if (!chunk) {
      const bytes = fs.readFileSync(path.join(root, binding.chunkPath));
      chunk = {sha256: digest(bytes), data: JSON.parse(bytes)};
      cache.set(binding.chunkPath, chunk);
    }
    assert.equal(binding.chunkSha256, chunk.sha256);
    const feature = chunk.data.features.find(f => f.properties.cleabs === entry.target.cleabs);
    assert.ok(feature, entry.target.cleabs + ' must exist in its acquired chunk');
    assert.deepEqual(entry.target.rawGeometry, feature.geometry);
    assert.equal(evidence.scope, 'site-membership-only');
    assert.deepEqual(evidence.claims, {measuredFacade: false, measuredInterior: false, nameIsBuildingIdentity: false});
    assert.equal(entry.facadeDocument, undefined);
    assert.equal(entry.interiorDocument, undefined);
    const d = draw({...feature.properties}), before = copy(feature);
    d.sourceGeometry = freeze(feature.geometry);
    const oldProperties = freeze(d.geoProperties);
    assert.equal(reg.apply(d), true);
    assert.deepEqual(feature, before);
    assert.deepEqual(oldProperties, before.properties);
    assert.equal(d.geoProperties.architectureSite.text, entry.label.text);
    assert.deepEqual(d.geoProperties.architectureSite.source, entry.source);
    assert.equal(d.geoProperties.facadeDocument, undefined);
    assert.equal(d.geoProperties.interiorDocument, undefined);
  }
  assert.equal(reg.info().appliedRecords, installed.records.length);
});

function cli(args, cwd = root) { return spawnSync(process.execPath, [path.join(root, 'tools/architecture_documents.cjs'), ...args], {cwd, encoding: 'utf8'}); }
function temporary(run) { const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'mistral-architecture-test-')); try { return run(dir); } finally { fs.rmSync(dir, {recursive: true, force: true}); } }

test('CLI help documents local validation and installation without writing a destination', () => {
  const result = cli(['--help']);
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /validate/);
  assert.match(result.stdout, /install/);
  assert.match(result.stdout, /--input/);
  assert.match(result.stdout, /--output/);
});

test('CLI validates locally without producing or altering an installed atlas', () => temporary(dir => {
  const input = path.join(dir, 'fixture.json'); fs.writeFileSync(input, JSON.stringify(atlas()));
  const before = fs.readFileSync(input), result = cli(['validate', '--input', input], dir);
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual(fs.readdirSync(dir), ['fixture.json']);
  assert.deepEqual(fs.readFileSync(input), before);
  assert.equal(JSON.parse(result.stdout).records, 1);
}));

test('CLI installs a fully revalidable atlas with one atomic replacement and no temporary residue', () => temporary(dir => {
  const input = path.join(dir, 'fixture.json'), output = path.join(dir, 'installed', 'index.json');
  const raw = atlas();
  raw.createdAt = '2026-10-24T00:00:00Z';
  raw.metadata = {title: 'Explicit local installation fixture', acquiredResponseSha256: 'b'.repeat(64)};
  raw.records[0].associationEvidence = {scope: 'explicit synthetic fixture', measurements: [1,2,3], original: {keep: true}};
  fs.writeFileSync(input, JSON.stringify(raw));
  fs.mkdirSync(path.dirname(output)); fs.writeFileSync(output, 'previous complete output');
  const result = cli(['install', '--input', input, '--output', output], dir);
  assert.equal(result.status, 0, result.stderr);
  const installed = JSON.parse(fs.readFileSync(output));
  assert.equal(A.validate(installed, adapters).records.length, 1);
  assert.deepEqual(installed, raw, 'Installation must not discard acquired metadata or association evidence');
  assert.equal(installed.records[0].geometryKey, undefined);
  assert.deepEqual(fs.readdirSync(path.dirname(output)), ['index.json']);
  assert.equal(JSON.parse(result.stdout).records, 1);
}));

test('CLI failed atomic rename preserves the destination and removes its temporary file', () => temporary(dir => {
  const input = path.join(dir, 'fixture.json'), output = path.join(dir, 'existing-directory');
  fs.writeFileSync(input, JSON.stringify(atlas()));
  fs.mkdirSync(output); fs.writeFileSync(path.join(output, 'keep.txt'), 'existing destination');
  const result = cli(['install', '--input', input, '--output', output], dir);
  assert.notEqual(result.status, 0);
  assert.equal(fs.readFileSync(path.join(output, 'keep.txt'), 'utf8'), 'existing destination');
  assert.deepEqual(fs.readdirSync(dir).sort(), ['existing-directory', 'fixture.json']);
}));

test('CLI rejects an invalid late record before replacing an existing atlas or creating directories', () => temporary(dir => {
  const input = path.join(dir, 'bad.json'), output = path.join(dir, 'index.json'), untouched = Buffer.from('previous complete output');
  const invalid = atlas(); invalid.records.push({...record(), id: 'bad-second-record', source: {}});
  fs.writeFileSync(input, JSON.stringify(invalid)); fs.writeFileSync(output, untouched);
  const result = cli(['install', '--input', input, '--output', output], dir);
  assert.notEqual(result.status, 0);
  assert.deepEqual(fs.readFileSync(output), untouched);
  assert.deepEqual(fs.readdirSync(dir).sort(), ['bad.json', 'index.json']);
  const absent = path.join(dir, 'uncreated', 'index.json');
  assert.notEqual(cli(['install', '--input', input, '--output', absent], dir).status, 0);
  assert.equal(fs.existsSync(path.dirname(absent)), false);
}));

test('CLI malformed JSON, excess bytes and ambiguous arguments fail without output changes', () => temporary(dir => {
  const input = path.join(dir, 'bad.json'), output = path.join(dir, 'index.json'); fs.writeFileSync(output, 'unchanged');
  for (const content of ['{not JSON', ' '.repeat(A.MAX_BYTES + 1)]) {
    fs.writeFileSync(input, content);
    assert.notEqual(cli(['install', '--input', input, '--output', output], dir).status, 0);
    assert.equal(fs.readFileSync(output, 'utf8'), 'unchanged');
  }
  assert.notEqual(cli(['install', '--input', input, '--bogus'], dir).status, 0);
  assert.equal(fs.readFileSync(output, 'utf8'), 'unchanged');
}));
