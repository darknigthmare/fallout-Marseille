# Rapport QA — Fallout : Mistral v0.49

**434/434 contrôles réussis**, 0 échec ; aucune exception JavaScript remontée. Toutes les suites navigateur correspondent au même HTML final `b5c1a7b59a6635964020cb0595a0cb3ed5f2330eaf92c1f2cb818cd17e77f546`.

## Nouveaux tests
- Sérialisation et migrations : 22/22.
- Rencontres, blessures, corps et repeuplement : 47/47.
- Sauvegardes, imports et isolation du banc : 15/15.
- Total nouveau : 84/84.

## Régression
Les 350 contrôles v0.48 sont conservés. Les scripts sont adaptés uniquement au chemin du HTML courant, aux numéros de build attendus et au chemin portable de Chromium, sans modifier leurs assertions fonctionnelles.

| Rapport | Résultat |
|---|---:|
| QA_ENCOUNTER_KERNEL.json | 22/22 |
| QA_ENCOUNTERS.json | 47/47 |
| QA_ENCOUNTER_SAVES.json | 15/15 |
| QA_BUDGET_PASSAGES.json | 25/25 |
| QA_PREPARATION_RETURNS.json | 62/62 |
| QA_KERNEL_NEW.json | 33/33 |
| QA_KERNEL_LEGACY.json | 23/23 |
| QA_DISTRIBUTION.json | 9/9 |
| QA_STREAMING_NEW.json | 52/52 |
| QA_SERVER_IO.json | 10/10 |
| QA_LAB_ISOLATION.json | 14/14 |
| QA_RUNTIME.json | 49/49 |
| QA_CAMPAIGN.json | 41/41 |
| QA_PROLOGUE.json | 22/22 |
| QA_PRODUCT.json | 10/10 |

## Défaut de base
Le rapport BASELINE_V048.json reproduit sur le programme antérieur le passage 85 → 68,35 → 85 PV après un déchargement de proximité. Il ne participe pas au total de contrôles positifs v0.49.

## Captures
Les images avant/après proviennent du vrai programme : dégâts appliqués, site déchargé, acteurs réinstanciés, santé/position/membre comparés. Aucun compteur de blessure n’est injecté pour faire croire à un test réussi. Les positions et caméras sont préparées dans le banc synthétique identifié.

## Portée et exclusions
Serveur testé séparément par HTTP Python ; programme exécuté via Playwright set_content et adaptateurs mémoire pour le stockage. Pas d’installation du pack réel, de navigation native, d’IndexedDB natif ni de certification GPU/mobile. Les 434 assertions ne signifient pas un parcours humain de toutes les quêtes ou rues.
