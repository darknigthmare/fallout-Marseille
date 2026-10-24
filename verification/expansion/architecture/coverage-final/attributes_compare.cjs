#!/usr/bin/env node
'use strict';

// Bounded QA on the exact source examples retained by the earlier corpus audit.
// This script never scans the remaining city atlas, writes into the repository,
// requests a network resource, builds the game, or changes source properties.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const root = path.resolve(process.env.MISTRAL_REPO_ROOT || '/workspace/fallout-Marseille');
const previous = path.resolve(process.env.MISTRAL_BASELINE_DIR || path.resolve(__dirname, '../coverage'));
const outputDirectory = path.resolve(process.env.MISTRAL_AUDIT_OUTPUT_DIR || __dirname);
const sourceAudit = path.join(previous, 'source-shapes');
const paths = {
  script: __filename,
  facadesBaseline: path.join(previous, 'facades-baseline.cjs'),
  interiorsBaseline: path.join(previous, 'interiors-baseline.cjs'),
  facadesCurrent: path.join(root, 'src/v050/07_facades.js'),
  interiorsCurrent: path.join(root, 'src/v050/08_city_interiors.js'),
  integrity: path.join(root, 'src/v046/00_integrity.js'),
  projection: path.join(root, 'src/patches/01_geometry.js'),
  importer: path.join(root, 'src/v046/01_world.js'),
  sourceGeometry: path.join(root, 'src/v050/04_source_geometry.js'),
  sourceShapesReport: path.join(sourceAudit, 'SOURCE_SHAPES.json'),
  attributeReport: path.join(sourceAudit, 'ATTRIBUTE_CROSS_TABS.json')
};
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const digest = value => sha(JSON.stringify(value));
const fileHashes = () => Object.fromEntries(Object.entries(paths).map(([key, file]) => [key, { path: file, sha256: sha(fs.readFileSync(file)) }]));
const initialHashes = fileHashes();
const finalFreezeHashes = {
  facadesCurrent: '9ccc2c01a9c91d5b1c2f0611f8d18c814f2616e0ec9711b37393c2cb78ec8335',
  interiorsCurrent: '94fc240ce308f71c0618ae1c1fec611b00b9867b2a91355579c3615b33cf7ce5'
};
for (const [name, expected] of Object.entries(finalFreezeHashes)) {
  assert.equal(initialHashes[name].sha256, expected, 'Current module must match its final frozen SHA-256');
}
// Verified against `git show cac50f3:src/v050/{07_facades,08_city_interiors}.js`.
const baselineCommitHashes = {
  facadesBaseline: '4a54881ba8b8fe973048814d2f47d6a450df004a8e511e0e535ee34889f870b6',
  interiorsBaseline: 'f279ef34cba9adce3371ac29f16f25ecca127ae87712f2ad98b095447e55c1a1'
};
for (const [name, expected] of Object.entries(baselineCommitHashes)) {
  assert.equal(initialHashes[name].sha256, expected, 'Baseline snapshot must match the exact cac50f3 module');
}
const F0 = require(paths.facadesBaseline), G0 = require(paths.interiorsBaseline);
const F1 = require(paths.facadesCurrent), G1 = require(paths.interiorsCurrent);
const Integrity = require(paths.integrity);
const shapeReport = JSON.parse(fs.readFileSync(paths.sourceShapesReport));
const attributeReport = JSON.parse(fs.readFileSync(paths.attributeReport));
const projectionText = fs.readFileSync(paths.projection, 'utf8');
const projectionCode = projectionText.slice(projectionText.indexOf('function v018Lambert93'), projectionText.indexOf('const V018_OLD_SCALES'));
assert.ok(projectionCode.startsWith('function v018Lambert93'));
const ctx = vm.createContext({ rad: angle => angle * Math.PI / 180 });
vm.runInContext(projectionCode, ctx);
const origin = ctx.v018Lambert93(43.285, 5.51);
const targets = new Map();
function addTarget(entry, group) {
  assert.ok(entry?.id && entry?.path, 'Source example must carry its source path');
  const existing = targets.get(entry.id);
  if (existing) {
    assert.equal(existing.path, entry.path, 'An example must bind one exact source chunk');
    existing.groups.push(group);
  } else targets.set(entry.id, { id: entry.id, path: entry.path, groups: [group] });
}
for (const entry of attributeReport.falseStrict195BoundaryCases) addTarget(entry, 'float-boundary-1.95');
for (const entry of shapeReport.nonNullInvalidLevelExamples) addTarget(entry, 'invalid-zero-levels');
for (const entry of shapeReport.floorHeightRejectedExamples) addTarget(entry, 'reported-floor-height-rejection');
for (const [use, entry] of Object.entries(attributeReport.examples)) addTarget(entry, 'ambiguous-nature:' + use);
const specialIds = new Map([
  ['batiment.49696442', 'religious-complex'],
  ['batiment.39111842', 'sports-grandstand'],
  ['batiment.26019993', '143.9m-one-declared-level']
]);
function findSpecialEntries(value) {
  if (!value || typeof value !== 'object') return;
  if (specialIds.has(value.id) && !targets.has(value.id)) addTarget(value, specialIds.get(value.id));
  for (const nested of Object.values(value)) findSpecialEntries(nested);
}
findSpecialEntries(shapeReport);
assert.equal(attributeReport.falseStrict195BoundaryCases.length, 27);
assert.equal(shapeReport.nonNullInvalidLevelExamples.length, 12);
assert.equal(shapeReport.floorHeightRejectedExamples.length, 20);
assert.equal(Object.keys(attributeReport.examples).length, 7);
// Two reported floor-height rejections also occur in the 27 float boundaries.
assert.equal(targets.size, 67);
for (const id of specialIds.keys()) assert.ok(targets.has(id), 'Missing special example ' + id);

const groupsByChunk = new Map();
for (const target of targets.values()) {
  if (!groupsByChunk.has(target.path)) groupsByChunk.set(target.path, []);
  groupsByChunk.get(target.path).push(target);
}
function freeze(value) {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    for (const nested of Object.values(value)) freeze(nested);
    Object.freeze(value);
  }
  return value;
}
function facadeResult(description) {
  if (!description) return { accepted: false, error: 'Facade descriptor rejected source draw' };
  return {
    accepted: true, id: description.id, sourceId: description.sourceId,
    style: description.style, styleBasis: description.styleBasis ?? null,
    typology: description.typology ?? null,
    levels: description.levels, levelHeight: description.levelHeight,
    levelsBasis: description.levelsBasis,
    levelInferenceBasis: description.levelInferenceBasis ?? null,
    height: description.height, baseY: description.baseY,
    heightBasis: description.heightBasis, provenance: description.provenance,
    footprintSha256: digest(description.rings)
  };
}
function interiorResult(module, description) {
  if (!description) return { accepted: false, error: 'No facade descriptor' };
  try {
    const building = module.building(description);
    return {
      accepted: true, id: building.id, sourceId: building.sourceId,
      name: building.name, use: building.use, levels: building.levels,
      levelHeight: building.levelHeight, levelsBasis: building.levelsBasis,
      height: building.height, origin: building.origin,
      schema: building.schema, layoutVersion: building.layoutVersion ?? 1,
      outlineBasis: building.outlineBasis,
      localFootprintSha256: digest(building.rings),
      programTheme: typeof module.programTheme === 'function' ? module.programTheme(building.use) : null
    };
  } catch (error) { return { accepted: false, error: String(error.message || error) }; }
}

const rows = [], sourceChunks = [];
for (const [relative, entries] of groupsByChunk) {
  const absolute = path.join(root, relative), bytes = fs.readFileSync(absolute);
  const bundle = JSON.parse(bytes);
  sourceChunks.push({ path: relative, bytes: bytes.length, sha256: sha(bytes), targetIds: entries.map(entry => entry.id) });
  const wanted = new Map(entries.map(entry => [entry.id, entry]));
  for (const feature of bundle.features) {
    const sourceId = feature.properties?.sourceId;
    const target = wanted.get(sourceId);
    if (!target) continue;
    wanted.delete(sourceId);
    const beforeFeature = digest(feature);
    freeze(feature);
    const geometry = feature.geometry;
    assert.ok(['Polygon', 'MultiPolygon'].includes(geometry.type));
    const polygons = geometry.type === 'Polygon' ? [geometry.coordinates] : geometry.coordinates;
    // All retained cases have one source component. Refuse an unnoticed change
    // instead of silently auditing only the first part of a MultiPolygon.
    assert.equal(polygons.length, 1, 'Retained example changed component count: ' + sourceId);
    const rings = polygons[0].map(ring => ring.map(coordinate => {
      const q = ctx.v018Lambert93(coordinate[1], coordinate[0]);
      return [q[0] - origin[0], origin[1] - q[1]];
    }));
    const profile = Integrity.buildingProfile(feature.properties);
    // These examples all carry an absolute source ground elevation and no
    // modeled non-flat roof. Refuse to introduce a guessed ground or roof.
    assert.ok(Number.isFinite(profile.groundElevation), 'No source ground for ' + sourceId);
    assert.equal(profile.roofHeight, 0, 'Roof case needs actual roofMesh evaluation');
    const draw = freeze({
      mesh: 'prism', geoLayer: 'building', rings,
      baseY: profile.groundElevation + profile.minHeight, height: profile.height,
      heightAssumed: profile.estimated, heightBasis: profile.basis,
      sourceProfile: profile, geoFeatureId: sourceId,
      geoProperties: feature.properties, sourceGeometry: geometry
    });
    const beforeDraw = digest(draw), beforeRings = digest(draw.rings);
    const d0 = F0.describe(draw), d1 = F1.describe(draw);
    const oldInterior = interiorResult(G0, d0), newInterior = interiorResult(G1, d1);
    const checks = {
      rawFeatureUnchanged: digest(feature) === beforeFeature,
      rawGeometryUnchanged: digest(draw.sourceGeometry) === digest(geometry),
      drawUnchanged: digest(draw) === beforeDraw,
      projectedFootprintUnchanged: digest(draw.rings) === beforeRings,
      facadeFootprintsIdentical: !!d0 && !!d1 && digest(d0.rings) === digest(d1.rings),
      heightsIdentical: !!d0 && !!d1 && d0.height === d1.height && d0.baseY === d1.baseY,
      stableComponentIdsIdentical: !!d0 && !!d1 && d0.id === d1.id,
      successfulInteriorFootprintsIdentical: oldInterior.accepted && newInterior.accepted
        ? oldInterior.localFootprintSha256 === newInterior.localFootprintSha256 : null
    };
    assert.ok(Object.entries(checks).every(([, value]) => value !== false), 'Source/footprint mutation for ' + sourceId);
    rows.push({
      sourceId, cleabs: feature.properties.cleabs,
      sourcePath: relative, groups: target.groups,
      sourceFeatureSha256: beforeFeature,
      rawGeometrySha256: digest(geometry), projectedFootprintSha256: beforeRings,
      sourceValues: Object.fromEntries(['nature', 'usage_1', 'usage_2', 'nombre_d_etages', 'building:levels', 'levels', 'hauteur', 'altitude_minimale_sol', 'altitude_maximale_toit'].map(key => [key, feature.properties[key] ?? null])),
      buildingProfile: profile,
      sourceGeometry: { type: geometry.type, components: polygons.length, rings: rings.length, verticesIncludingClosure: rings.reduce((sum, ring) => sum + ring.length, 0) },
      baseline: { facade: facadeResult(d0), interior: oldInterior },
      current: { facade: facadeResult(d1), interior: newInterior },
      crossCheck: { baselineInteriorOnCurrentFacade: interiorResult(G0, d1), currentInteriorOnBaselineFacade: interiorResult(G1, d0) },
      checks
    });
  }
  assert.equal(wanted.size, 0, 'Missing target source features: ' + [...wanted.keys()].join(', '));
}
rows.sort((a, b) => a.sourceId.localeCompare(b.sourceId));
const finalHashes = fileHashes();
assert.deepEqual(finalHashes, initialHashes, 'A compared module changed during this run; rerun after code freeze');
const count = (selected, predicate) => selected.filter(predicate).length;
const select = group => rows.filter(row => row.groups.includes(group));
const boundaries = select('float-boundary-1.95'), zeroes = select('invalid-zero-levels');
const retainedRejections = select('reported-floor-height-rejection');
const numericEpsilon = G1.EPS;
assert.ok(Number.isFinite(numericEpsilon) && numericEpsilon > 0);
const trueHeightConflicts = retainedRejections.filter(row => row.current.facade.levelHeight < 1.95 - numericEpsilon);
const roundedHeightBoundaries = retainedRejections.filter(row => row.current.facade.levelHeight < 1.95 && row.current.facade.levelHeight >= 1.95 - numericEpsilon);
const validDeclaredLevelsPreserved = selected => selected.every(row => Number.isInteger(row.sourceValues.nombre_d_etages) && row.sourceValues.nombre_d_etages > 0 && row.baseline.facade.levels === row.sourceValues.nombre_d_etages && row.current.facade.levels === row.sourceValues.nombre_d_etages && row.current.facade.levelsBasis === 'source-declared');
const report = {
  schemaVersion: 1,
  generatedAt: new Date().toISOString(),
  scope: '67 retained real IGN source cases only; exact production Lambert93 with shared metric origin (43.285, 5.51), Integrity.buildingProfile and an identical immutable source draw passed to baseline/current facade and interior modules. No city-wide rescan or survey-fidelity claim.',
  baselineCommit: 'cac50f3',
  baselineSnapshotHashesVerified: true,
  finalFreezeHashesVerified: true,
  moduleAndEvidenceHashesUnchangedDuringRun: true,
  limitations: [
    'The 27 boundary cases and 12 invalid-level cases are the retained examples, not a fresh count of the full city corpus.',
    'Interior acceptance concerns G.building volume eligibility; no browser, terrain/neighbor access, layout, furniture or navigation execution is asserted.',
    'Source usage and floor attributes are respected; tall or unusual source envelopes do not establish an independently verified internal floor layout.'
  ],
  projection: { source: paths.projection, extractedFunctionSha256: sha(projectionCode), originLatLon: [43.285, 5.51], originLambert93: [...origin], axes: ['east minus origin easting', 'origin northing minus north'], unit: 'metre' },
  modulesAndEvidence: initialHashes,
  sourceChunks,
  summary: {
    targetBuildings: rows.length, chunksRead: sourceChunks.length,
    sourceChunkBytesRead: sourceChunks.reduce((sum, chunk) => sum + chunk.bytes, 0),
    allDrawsAndFootprintsUnchanged: rows.every(row => Object.values(row.checks).every(value => value !== false)),
    baselineInteriorAccepted: count(rows, row => row.baseline.interior.accepted),
    currentInteriorAccepted: count(rows, row => row.current.interior.accepted),
    boundary195: { examples: boundaries.length, baselineAccepted: count(boundaries, row => row.baseline.interior.accepted), currentAccepted: count(boundaries, row => row.current.interior.accepted), facadeLevelsUnchanged: boundaries.every(row => row.baseline.facade.levels === row.current.facade.levels), baselineInteriorOnCurrentFacadeAccepted: count(boundaries, row => row.crossCheck.baselineInteriorOnCurrentFacade.accepted), currentInteriorOnBaselineFacadeAccepted: count(boundaries, row => row.crossCheck.currentInteriorOnBaselineFacade.accepted), rescuedIds: boundaries.filter(row => !row.baseline.interior.accepted && row.current.interior.accepted).map(row => row.sourceId) },
    invalidZeroLevels: { examples: zeroes.length, baselineMisattributedIgn: count(zeroes, row => row.baseline.interior.accepted && row.baseline.interior.levelsBasis.startsWith('nombre_d_etages IGN')), currentMisattributedIgn: count(zeroes, row => row.current.interior.accepted && row.current.interior.levelsBasis.startsWith('nombre_d_etages IGN')), currentEstimated: count(zeroes, row => row.current.interior.accepted && row.current.interior.levelsBasis.startsWith('estimation')) },
    retainedFloorHeightRejections: {
      examples: retainedRejections.length, numericEpsilon,
      realConflictsBelow195MinusEpsilon: {
        examples: trueHeightConflicts.length,
        baselineAccepted: count(trueHeightConflicts, row => row.baseline.interior.accepted),
        currentAccepted: count(trueHeightConflicts, row => row.current.interior.accepted),
        declaredLevelsPreserved: validDeclaredLevelsPreserved(trueHeightConflicts),
        ids: trueHeightConflicts.map(row => row.sourceId)
      },
      floatBoundariesWithinEpsilon: {
        examples: roundedHeightBoundaries.length,
        baselineAccepted: count(roundedHeightBoundaries, row => row.baseline.interior.accepted),
        currentAccepted: count(roundedHeightBoundaries, row => row.current.interior.accepted),
        declaredLevelsPreserved: validDeclaredLevelsPreserved(roundedHeightBoundaries),
        ids: roundedHeightBoundaries.map(row => row.sourceId)
      },
      otherAtOrAbove195: retainedRejections.filter(row => row.current.facade.levelHeight >= 1.95).map(row => row.sourceId)
    },
    ambiguousClassification: rows.filter(row => row.groups.some(group => group.startsWith('ambiguous-nature:'))).map(row => ({ sourceId: row.sourceId, primaryUse: row.sourceValues.usage_1, baselineStyle: row.baseline.facade.style, currentStyle: row.current.facade.style, currentStyleBasis: row.current.facade.styleBasis, currentTypology: row.current.facade.typology, baselineLevels: row.baseline.facade.levels, currentLevels: row.current.facade.levels })),
    specialVolumes: rows.filter(row => specialIds.has(row.sourceId)).map(row => ({ sourceId: row.sourceId, case: specialIds.get(row.sourceId), sourceDeclaredLevels: row.sourceValues.nombre_d_etages, height: row.buildingProfile.height, baselineLevels: row.baseline.facade.levels, currentLevels: row.current.facade.levels, currentLevelsBasis: row.current.interior.levelsBasis ?? null, currentTypology: row.current.facade.typology, currentUse: row.current.interior.use ?? null }))
  },
  rows
};
fs.mkdirSync(outputDirectory, { recursive: true });
fs.writeFileSync(path.join(outputDirectory, 'ATTRIBUTES_COMPARE.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report.summary, null, 2));
