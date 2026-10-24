const fs = require('node:fs');
const path = require('node:path');
const F = require('./facades-baseline.cjs');

// Explicit synthetic metric fixture. This proves the edge-index contract only.
const ring = [[0, 0], [20, 0], [20, 20], [0, 20]];
const properties = {
  sourceId: 'synthetic-annotation-order',
  facadeDocument: {
    schemaVersion: 1,
    source: 'https://example.org/synthetic-fixture',
    license: 'Synthetic test fixture',
    attribution: 'Independent coverage audit',
    acquiredAt: '2026-10-24',
    openings: [{type: 'door', ringIndex: 0, edgeIndex: 0, offset: 3, bottom: 0, width: 1, height: 2.2}],
    completeEdges: []
  }
};
const make = points => ({mesh: 'prism', rings: [points], baseY: 0, height: 6, geoProperties: properties});
const a = make(ring), b = make(ring.slice(1).concat(ring.slice(0, 1)));
const firstEntrance = F.entrances(a)[0].center, rotatedEntrance = F.entrances(b)[0].center;
const result = {
  scope: 'Explicit synthetic square under exact production07 snapshot at cac50f3; demonstrates annotation edge addressing, not measured city geometry',
  sameStableId: F.describe(a).id === F.describe(b).id,
  firstEntrance,
  rotatedEntrance,
  displacementMeters: Math.hypot(...firstEntrance.map((v, i) => v - rotatedEntrance[i]))
};
fs.writeFileSync(path.join(__dirname, 'DOCUMENT_EDGE_ORDER.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify(result));
