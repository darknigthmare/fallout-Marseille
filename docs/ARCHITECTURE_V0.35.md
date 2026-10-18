# Architecture v0.35

- `00_state.js` : migration, enveloppes de sauvegarde, autosave et sessions.
- `01_career.js` : chapitres, complétion, rangs, bilan et NG+.
- `02_operations.js` : huit opérations, checkpoints, records et récompenses uniques.
- `03_hub.js` : retour A‑03, repos et services.
- `04_interface.js` : menu, écrans produit et raccourcis.
- `05_prologue.js` : nouvelle campagne A‑03 et transition vers Aubagne.
- `06_product.js` : Continuer, mode sûr, diagnostic, crédits et PWA.
- `style.css` : interface responsive.

Le moteur historique n’est pas réécrit en bloc ; les modules sont chargés après v0.30 et conservent les contrats de sauvegarde existants.
