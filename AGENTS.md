# Fallout: Mistral — Agent development contract

Follow the upstream gamedev-skills router: https://github.com/gamedev-skills/awesome-gamedev-agent-skills (reviewed at 19d93f97c9c1ea0f8b306e77aa81e0d3e352d3e9).

## Project-first rules
- This is an existing custom browser/WebGL game. Do not migrate it to Godot, Unity or Three.js merely because a skill shows an example.
- Inspect README, scripts, existing implementations and tests before editing. Match existing lifecycle, data ownership and version conventions.
- Read only relevant upstream skills for the task: procedural-gen and level-design for geography; save-systems for persistence; game-ui-ux for HUD; camera-systems for FPS; performance-optimization for streaming; rpg for quests; create-game-assets for visuals.
- Preserve geographic source provenance, coordinates, vertical datum, NoData, and SHA-256 validation. Never fabricate surveyed buildings, road links, bridges or elevations. Fallout fiction belongs in a separate authored overlay.
- The same world feature must keep a stable identity across streamed tile boundaries. Test both traversal directions, repeated loads and cancellation.
- Preserve manual saves, autosaves and older save migrations. No silent reset of quest flags, discovered POIs or persistent encounters.
- No claims of tested gameplay without actually running it. Label unit tests, browser smoke tests and human playtests separately.
- For substantial releases provide real in-game screenshots, tested commands, known limitations and regression results. Do not use concept art as proof of implementation.
- Do not silently alter gameplay balance when changing presentation. Keep developer controls out of player-facing menus.
- For commercial release, independently audit trademark, copyright, licensing and franchise rights: this repository is presently described as an unofficial fan prototype.

## Definition of done
1. Describe baseline and exact files to change.
2. Implement the smallest complete feature in existing architecture.
3. Run relevant automated tests and a browser smoke test where available.
4. Verify continuity, persistence, loading failure behavior, accessibility and performance where relevant.
5. Include screenshots captured from the actual build for visual changes.
6. Report passes, failures, untested scenarios and source provenance without exaggeration.
