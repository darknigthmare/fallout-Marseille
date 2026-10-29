# Mistral QA checklist

## Automated
- [ ] Existing geometry and source integrity tests pass
- [ ] HUD and first-person presentation tests pass
- [ ] Deterministic generation from a fixed seed
- [ ] Save/load round trip and older-version migration
- [ ] Tile cancellation, retries and missing-resource handling
- [ ] POI discovery and persistence

## Browser playtest
- [ ] New game starts in a coherent playable vault
- [ ] No overlapping introductory actors or UI
- [ ] Continuous exterior travel, both directions
- [ ] Building/road seams match visually and physically
- [ ] FPS camera and weapon HUD do not jitter or flash
- [ ] Sky animation remains independent of camera movement
- [ ] Pause, resume, save, quit, reload
- [ ] Keyboard, controller (if supported), narrow screen and desktop layouts
- [ ] Screenshots captured from the build, with resolution and location

## Performance and delivery
- [ ] Record baseline and final FPS/frame-time and peak retained cache size
- [ ] No regression in source provenance or licensing
- [ ] Report skipped tests and missing real-world data explicitly
- [ ] PR includes change summary, evidence and remaining issues
