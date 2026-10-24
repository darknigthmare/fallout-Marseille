# Marseille architecture continuation: independent baseline audit

This is an independent read-only audit of baseline commit `cac50f305db69fcd4827da2c8ac34295e8b68d7a`. It does not certify code being changed concurrently by the facade, interior, or documentary-persistence agents. No production files, city source chunks, or generated release files were changed by this audit. No browser, terrain-collision, or native-player accessibility check is claimed.

The acquired city index is pinned by SHA-256 `3a83c7f821a2f3bd824240d7f065568df7ae786b1f5719c8c57f004dbd817d61`. Its 291,001 unique building source IDs include returned border objects. Every acquired building currently has one polygon component; 344 have source holes/courtyards. All current geometries fit the engine's point/ring limits. This finding concerns the acquired atlas, not completeness of authoritative records for every real structure.

## Priority findings and reproductions

| Finding | Baseline evidence | Concrete correction |
| --- | --- | --- |
| Documentary plan disappears after a cold load, exit and reentry | `DOCUMENT_ROUNDTRIP.json`: documentary first entry and cold-loaded interior become an invented plan after reentry | Persist the validated building/document registry, recover current documentary snapshots from old saves, and resolve it again on entry |
| Stable building identity does not make indexed annotation edges stable | `DOCUMENT_EDGE_ORDER.json`: rotating the same square's ring leaves the building ID unchanged but moves its annotated door by 16.867 m | Bind an annotation to exact ordered source geometry or explicitly canonical physical edge coordinates |
| Strict actor-height comparison rejects valid boundary cases | 27 actual objects have mathematically 1.95 m floor intervals represented as `1.949999999999…` | Use a documented small numerical tolerance consistently, preserving measured heights |
| Floor provenance accepts field presence instead of accepted source value | 355 non-null `nombre_d_etages` values are exactly 0 and correctly cause estimation, but baseline interior labels them IGN | Label source levels only when the accepted positive integer agrees with the retained schedule |
| Generic nature overrides explicit facade usage | 2,504 explicit non-industrial uses under `nature="Industriel, agricole ou commercial"` become industrial: 2,018 commercial, 483 residential, 3 sports | Prefer explicit primary/secondary usage before generic nature |
| Polygonized curves receive no facade entrance or window | 301 footprints have no exterior segment at least 1.6 m long. 191 have sufficient envelope height, a minimum bbox of 2 m, and an explicitly found interior point with at least 0.43 m clearance | Support doors/windows across adjacent short source segments while preserving the measured footprint; classify tank/silo utility uses coherently |
| Complex boundary candidates truncate at 64 edges | 49 actual footprints contain more than 64 eligible outer edges; maximum 536 | Bound search work while covering the entire boundary, using approach proximity and deterministic pagination rather than permanently excluded edges |

The documentary reproducers use an explicit, attributed synthetic fixture and exact baseline source snapshots in a controlled runtime/persistence harness. They do not assert that an actual public building plan was acquired. The geometry, classification, height and complexity counts use the acquired IGN atlas. The two kinds of evidence are intentionally distinguished.

## Actual-source entrance examples

`ACTUAL_ENTRANCE_COVERAGE.json` retains source paths, SHA-256 hashes and complete original features for three examples. Projection uses the engine's exact Lambert-93 formula and active origin `v018Lambert93(43.285, 5.51)`.

* `batiment.9375075`: approximately 6.10 m diameter, effective envelope 7.6 m high, two estimated levels, 84 source outer edges, maximum edge length 0.316871 m and an interior point with 2.981 m clearance. The baseline produces zero entrances and zero windows. This is a representational-granularity gap rather than rejection by the point budget. Geometry alone does not establish whether the real object should be publicly habitable.
* `batiment.49693149`: 68,352.437 m², explicit commercial/services usage, source height 28.4 m and two source levels. It has 90 outer edges at least 1.6 m long, but only 64 entrance candidates. Its most distant sampled outer-edge midpoint approach lies 20.633 m from a retained candidate. The baseline facade is wrongly industrial.
* `batiment.49696442`: religious primary usage, 45.8 m effective envelope height and unknown source floor count. The baseline invents 15 floors, 64 entrance candidates from 536 eligible outer edges, and reaches the 4,096-opening plan cap. The most distant sampled outer-edge midpoint approach is 28.349 m from a retained candidate. A tall religious envelope is not evidence for a stack of conventional storeys.

These last two examples do not prove that the cap causes a missed entrance near a player: no terrain or neighboring-object accessibility was simulated, and no sampled nearest-candidate distance exceeds 100 m. They demonstrate the permanent enumeration limit and make its scope reproducible.

## Other quantitative limits

The acquired corpus contains 3,144 effective whole envelopes below 1.95 m. A separate 1,593 have a higher whole envelope but baseline source-or-derived levels below 1.95 m per floor; that second count includes the 27 rounding cases. These source conflicts must remain visible rather than stretching measured envelopes.

There are 3,085 buildings over 1,000 m², 46 over 10,000 m² and two over 50,000 m². Baseline bay-size bounds predict more than approximately 85 facade candidates for between 11,889 and 15,552 components, and more than 4,096 for between three and four. These are candidate bounds before overlap/door filtering. A logical complete facade description should be distinguishable from a bounded displayed LOD.

The source has 431 religious, 327 sports and 18,887 annex primary uses. The representative `Tribune` object `batiment.39111842` has a 67.3 m effective envelope, no source floor count, and 22 conventional floors inferred by the baseline. Unknown floor/program generation should use source typology; explicit source floors should remain retained with conflicts reported. The tall commercial example `batiment.26019993` has source floor count 1 and effective height 143.9 m, which demonstrates why an attribute is not a surveyed complete interior plan.

## Files and reruns

* `document_roundtrip.cjs`, `facades-baseline.cjs`, `interiors-baseline.cjs`, `runtime-harness.inc`: pinned documentary cold-load roundtrip reproducer and source snapshots.
* `document_edge_order.cjs`, `DOCUMENT_EDGE_ORDER.json`: minimal ring-order annotation reproducer and result.
* `actual_entrances.cjs`: rerun with Node to regenerate the three actual-source baseline entrance cases.
* `source-shapes/SUMMARY.md`: corpus audit, precise source counts, qualification and representative structures.
* `source-shapes/scan.py`, `cross_tabs.py`, `curved_eligibility.py`: bounded-memory source scans; their JSON files retain actual source examples.
* `source-shapes/AUDIT_FILES.json`: hashes of the source scan scripts and results.

The final `COVERAGE_MANIFEST.json` hashes all audit evidence and scripts. The evidence remains outside the repository so implementation owners can independently inspect it without introducing source-data or generated-release changes.
