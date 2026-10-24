# Actual Marseille source coverage audit

Read-only audit of the pinned city source index `3a83c7f821a2f3bd824240d7f065568df7ae786b1f5719c8c57f004dbd817d61`, with objects deduplicated by WFS sourceId. Returned border objects are included. No source files or production code were modified. Areas/dimensions use the current engine's exact Lambert-93 formula, with translation-stable area calculation.

The baseline policy being compared is commit `cac50f3`. Runtime agents may now be changing those policies; these results are not a certification of their new code.

## Corpus

- 291,001 unique building objects, all with one polygon component in this acquired corpus; 344 objects contain actual source holes/courtyards.
- 3,085 objects exceed 1,000 m²; 46 exceed 10,000 m²; 2 exceed 50,000 m².
- No actual component exceeds the present source-projection 2,048-node-per-ring limit, the interior 8,192-node/128-ring limits, or facade 16,384-node/256-ring limits. Maximum observed total is 568 nodes.
- 3,144 effective envelope heights are below 1.95 m. Another 1,593 objects fail the present height/levels < 1.95 m check; 27 of these are only floating-point boundary errors at a mathematically 1.95 m storey.
- 133,248 `nombre_d_etages` values are non-null. Exactly 355 are invalid for the facade integer1..200 contract: all are the numeric value0. No non-null empty-string values occur in this field in this acquisition.

## Concrete bugs and coverage risks

1. **Floating-point rejection:** `batiment.9617675` has ground4.7, roof8.6, levels2, giving JavaScript/Python binary height3.8999999999999995 and storey1.9499999999999997. The strict 1.95 m rejection drops a valid boundary case. There are27 such objects. Complete list: `ATTRIBUTE_CROSS_TABS.json.falseStrict195BoundaryCases`.
2. **Wrong facade program from ambiguous nature:** the baseline facade regex treats every `nature="Industriel, agricole ou commercial"` as industrial. Of its9,983 source objects, primary uses explicitly indicate2,018 commercial/services,483 residential and3 sports buildings. These2,504 explicit nonindustrial uses should not be overwritten by the ambiguous generic nature. The interior classifier starts from primary use, creating a mismatch. The remaining primary uses are5,601 indifferent,786 annexes,1,080 industrial and12 agricultural. Examples and exact original attributes are in `ATTRIBUTE_CROSS_TABS.json.examples`.
3. **Source-level provenance:**355 source `nombre_d_etages=0` values correctly cause facade floor estimation, but baseline08 labels a floor schedule as IGN whenever this property is merely non-null. The label must track whether the floor count was actually accepted, not field presence. Examples are in `SOURCE_SHAPES.json.nonNullInvalidLevelExamples`.
4. **Curved source outlines have no eligible door edge:**301 components contain no exterior segment >=1.6 m, which makes the baseline facade entrance generator return no invented doorway, even for substantial round footprints. Example `batiment.9375075` in `m13055-r01-c12-c869798b17b6560c.json`: diameter about6.10 m, effective height7.6 m,84 exterior segments; all are too short individually. Larger industrial examples include `batiment.9279775` (diameter23.9 m,90 segments) and `batiment.9279780` (diameter29.1 m,92 segments). These are source geometries, not proof of actual public access. A coherent generator can support a portal across adjacent nearly collinear/curved segments without altering the original footprint. Samples: `ATTRIBUTE_CROSS_TABS.json.noDoorDespiteBBoxAtLeast2mExamples`.
5. **Entrance enumeration truncates complex boundaries:**49 components have more than64 exterior edges >=1.6 m. The maximum is536 such edges on `batiment.49696442` (541 exterior nodes), with religious primary use, in `m13055-r04-c08-2-6987b66ce033f6c1.json`. Next is452 edges on `batiment.49696644`. Bounded runtime search should sample the entire boundary rather than permanently excluding later eligible edges. Top15 examples: `ATTRIBUTE_CROSS_TABS.json.mostLongOuterEdges`.
6. **Very large buildings and detail budgets:** at least11,889 source components have >85 candidate facade openings under every applicable baseline bay width; at most15,552 can exceed85 depending on deterministic bay. Three definitely exceed4,096, with at mostfour under the alternate bay bound. These are candidate bounds before overlap/door filtering, not promises that every candidate should render. A bounded LOD is expected; an architectural plan should distinguish complete logical coverage from the displayed subset.

## Representative sources

- Largest: `batiment.49693149` / `BATIMENT0000000040578362`,68,352.437 m², effective height28.4 m, source levels2, primary use commercial/services. Same tile contains `batiment.49693150`,56,993.557 m² with a courtyard.
- Sports: `batiment.39111842`, natureTribune,40,715.481 m², effective height67.3 m, unknown source floors -> baseline estimates22. This demonstrates why usage-specific spatial programs matter; a roof-envelope height is not a documentary storey plan.
- Tall source ambiguity: `batiment.26019993`, effective height143.9 m but source floor count1. This is not grounds to overwrite the source silently; represent the inconsistency and distinguish any coherent generated storeys from the attribute itself.

All object paths, attributes, metric bounds and ranked examples are retained in the two JSON reports. No browser or renderer certification was attempted.

## Curved-outline compatibility qualification

The301 no-edge>=1.6 m cases were checked more narrowly.282 have effective height per source-or-baseline-derived floor >=1.95 m (allowing1e-7 floating-point EPS).192 also have a minimum bounding-box dimension >=2 m.191 of those192 have an explicitly found interior point with at least0.43 m clearance from every exterior/hole segment; the remaining one had no such point in a bounded64×64 search and is not claimed compatible.

Among the192,170 have no segment>=1.45 m (254 of all301). All301 produce no invented windows under the baseline model regardless of that threshold because its smallest bay width is2.8 m. This is a representational granularity problem, not proof that the real structure should be accessible to a player: many round buildings may be tanks or silos. See `CURVED_ELIGIBILITY.json` for all192 qualified records and their clearances.

For `batiment.9375075`, the largest exterior segment is0.316871 m while the explicit interior point has2.981126 m clearance. Its effective envelope is7.6 m high with2 baseline-derived floors. A building-wide flat-wall-edge length threshold therefore excludes an otherwise geometrically roomy round outline.
