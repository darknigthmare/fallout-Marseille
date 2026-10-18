# FALLOUT : MISTRAL — v0.49
## Le quartier se souvient

Prototype de fan non officiel. Reprise directe du projet complet v0.48 fourni.

Lancez `LANCER_APP_WINDOWS.bat` après extraction, ou son équivalent Linux/macOS. Le HTML autonome reste disponible.

La v0.49 conserve les rencontres au-delà du chargement de proximité : santé restante, membres blessés, positions, orientation, état de recherche et dépouilles à contenu fini. Intérieur et extérieur possèdent des identités séparées. Les boss uniques ne réapparaissent pas ; les sites ordinaires ne changent de cycle qu’après leur délai historique de jeu.

Les 248 implantations sont inchangées. Le streaming, les retours d’intérieur, le lore reconstruit, la campagne et le prologue de la v0.48 sont conservés.

434 contrôles ciblés sont réussis sur le même HTML final. Les captures sont prises dans le programme, sur le banc synthétique signalé. Le pack réel de 5 884 coordonnées et huit grilles n’est pas embarqué : les rues réelles ne sont pas certifiées dans cette livraison.

Build : `python3 tools/build_single.py`. QA : `npm run qa`. Rapport visuel : `npm run captures`. Banc : Ctrl + Maj + F9, avec sauvegardes de campagne désactivées pendant l’essai.
