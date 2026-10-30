# World streaming and geographical integrity

## Authoritative geography
- The surveyed map and terrain are authoritative; fictional factions, enemies, loot, POIs and damage are separate deterministic overlays.
- Preserve source feature IDs, original geometry, acquisition metadata, attribution, CRS and vertical datum. Missing terrain remains missing, never zero-height terrain.
- Stream by immutable world-space identities, not tile-local random indices.
- A building or road crossing a tile edge must be identical on both sides; clipping affects presentation, not its identity or geometry.
- Prepare new terrain/geometry off-screen and publish only after all required resources validate. On failed loading, retain the last valid world and show an actionable loading error.
- Cache eviction must not mutate active world records. Cancellation must not publish stale plans.

## Regression scenarios
1. Walk across an exterior tile boundary and back without confirmation.
2. Compare building footprints and road endpoints at both sides of every sampled seam.
3. Travel away and return: geometry and persistent world flags must match.
4. Simulate a missing or corrupted source partition: show failure, do not substitute synthetic geography.
5. Validate NoData, altitude and bridge/roof collision against the same source geometry.
6. Discover a POI, save, reload, and verify map marker and fast-travel eligibility.
7. Check memory budgets and frame time under repeated streaming.
8. Record screenshots and source IDs for every reported discrepancy.

## Release gate
Do not call the map complete merely because an index says coverage complete. Verify terrain availability, physical accessibility, traversable roads and representative gameplay on the actual build.
