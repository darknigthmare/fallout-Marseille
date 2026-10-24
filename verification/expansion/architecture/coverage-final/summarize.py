from pathlib import Path
import json, hashlib, collections, os

base = Path(os.environ.get('MISTRAL_AUDIT_OUTPUT_DIR', Path(__file__).parent)).resolve()
repo = Path(os.environ['MISTRAL_REPO_ROOT']).resolve() if os.environ.get('MISTRAL_REPO_ROOT') else None
curves = json.loads((base / 'CURVES_COMPARE.json').read_bytes())
attributes = json.loads((base / 'ATTRIBUTES_COMPARE.json').read_bytes())
cs, ats = curves['summary'], attributes['summary']
floor_conflicts = ats['retainedFloorHeightRejections']['realConflictsBelow195MinusEpsilon']
assert curves['status'] == 'frozen-code-comparison', curves['status']
for current, attribute in [('currentFacade', 'facadesCurrent'), ('currentInterior', 'interiorsCurrent')]:
    binding = attributes['modulesAndEvidence'][attribute]
    assert curves['moduleHashes'][current] == binding['sha256'], (current, 'different comparison versions')
    live_path = repo / 'src/v050' / ('07_facades.js' if current == 'currentFacade' else '08_city_interiors.js') if repo else Path(binding['path'])
    assert hashlib.sha256(live_path.read_bytes()).hexdigest() == binding['sha256'], (current, 'live code changed')
cases = {row['sourceId']: row for row in curves['curves']}
exemplar = cases['batiment.9375075']
missing = [row for row in curves['curves'] if row['baselineCompatible'] and row['residual']]
no_windows = collections.Counter(row['reason'] for row in cs['compatibleWindowOmissions'])
chunk_sources = {}
for chunk in curves['sourceChunks'] + attributes['sourceChunks']:
    if chunk['path'] in chunk_sources:
        assert chunk_sources[chunk['path']]['sha256'] == chunk['sha256']
    chunk_sources[chunk['path']] = chunk
total_bytes = sum(chunk['bytes'] for chunk in chunk_sources.values())
lines = [
    '# Comparaison externe de l’architecture : données IGN réelles',
    '',
    'Comparaison des modules figés avec les snapshots exacts du commit `cac50f305db69fcd4827da2c8ac34295e8b68d7a`. Aucun fichier de production, aucune donnée source et aucun livrable généré n’ont été modifiés par cette QA. Projection Lambert-93 et origine `(43.285, 5.51)` identiques à la production ; hauteurs issues du vrai `buildingProfile`.',
    '',
    f'La sélection ciblée lit {len(chunk_sources)} chunks distincts ({total_bytes:,} octets) déjà référencés par l’audit précédent ; le corpus complet n’a pas été rescanné. Les résultats détaillés et les empreintes figurent dans `ATTRIBUTES_COMPARE.json` et `CURVES_COMPARE.json`.',
    '',
    '| Cas réel vérifié | Baseline | Après correction |',
    '| --- | ---: | ---: |',
    f'| Faux rejets à 1,95 m, acceptés sans changer hauteur ni niveaux | {ats["boundary195"]["baselineAccepted"]}/{ats["boundary195"]["examples"]} | {ats["boundary195"]["currentAccepted"]}/{ats["boundary195"]["examples"]} |',
    f'| Exemples `nombre_d_etages=0` attribués à tort à IGN | {ats["invalidZeroLevels"]["baselineMisattributedIgn"]}/{ats["invalidZeroLevels"]["examples"]} | {ats["invalidZeroLevels"]["currentMisattributedIgn"]}/{ats["invalidZeroLevels"]["examples"]} |',
    f'| Vrais conflits de hauteur toujours refusés, niveaux déclarés conservés | {floor_conflicts["examples"] - floor_conflicts["baselineAccepted"]}/{floor_conflicts["examples"]} | {floor_conflicts["examples"] - floor_conflicts["currentAccepted"]}/{floor_conflicts["examples"]} |',
    f'| Contours courts avec porte passant les contraintes intérieures contrôlées | {cs["baselineCompatibleWithEntrances"]}/191 | {cs["currentCompatibleWithUsableInteriorCandidates"]}/191 |',
    f'| Contours courts avec fenêtres générées | 0/191 | {cs["currentCompatibleWithWindows"]}/191 |',
    f'| Arêtes exclues du premier parcours de 64 candidats, retrouvées et rendues | 0/{cs["sampledExcludedEdges"]} dans la sélection initiale | {cs["sampledRecoveredDoorsRendered"]}/{cs["sampledExcludedEdges"]} avec proximité/préférence |',
    '',
    'Les sept catégories d’usage ambigu ont été comparées sur des objets réels : les usages explicitement résidentiel, commercial et sportif prennent désormais priorité sur la nature générique « Industriel, agricole ou commercial ». Ces exemples ne constituent pas un nouveau comptage individuel des 2 504 objets concernés dans l’audit initial. De même, les 12 exemples de niveaux zéro ne sont pas une nouvelle vérification de l’ensemble des 355 valeurs zéro de l’atlas.',
    '',
    'Les 27 cas de seuil sont isolés par une matrice croisée : le module intérieur actuel les accepte avec les niveaux de façade baseline, tandis que le module intérieur baseline les refuse avec les niveaux actuels. Le résultat provient de la tolérance numérique et conserve les dimensions source. Les véritables conflits de hauteur retenus dans le rapport attributaire restent distingués des arrondis.',
    '',
    'La tribune `batiment.39111842` passe de 22 niveaux inventés à un volume fonctionnel inventé ; le bâtiment religieux `batiment.49696442` passe de 15 à un volume de nef inventé. Le volume commercial de 143,9 m `batiment.26019993` conserve son niveau source déclaré. Ces choix ne sont pas des relevés d’étages ou de pièces.',
    '',
    '## Contours courts : résultats et limites restantes',
    '',
    'Les 191 contours avaient chacun un point intérieur avec au moins 0,43 m de dégagement, une enveloppe suffisamment haute et une bbox minimale de 2 m. Leur compatibilité géométrique ne documente pas un usage habitable. Aucun span d’ouverture contrôlé ne dépasse les segments source ; les anneaux et hauteurs sont inchangés.',
    '',
    '| Objet sans candidat porte | Motif observé |',
    '| --- | --- |',
]
for row in missing:
    d = row['residualDiagnostics']
    spans = ', '.join(f'{surface["length"]:.5f} m / {surface["segments"]} segments' for surface in d['curvedSurfaceLengths']) or 'aucune chaîne admissible'
    lines.append(f'| `{row["sourceId"]}` | {row["sourceOuterSegments"]} segments, maximum {row["maximumOuterEdgeMeters"]:.3f} m ; {d["adjacentTurnsOver45Degrees"]} virages >45° ; {spans}. Limite conservatrice du modèle, pas preuve d’impossibilité physique. |')
lines += [
    '',
    'Absences de fenêtres : ' + '; '.join(f'{reason} : {count}' for reason, count in sorted(no_windows.items())) + '. Les silos techniques sans registre de fenêtres suivent un programme cohérent ; une absence de fenêtre inventée n’est pas un défaut documentaire mesuré.',
    '',
    'Le contrôle négatif `batiment.10615286`, exclu des 191 parce qu’aucun point avec dégagement suffisant n’avait été trouvé, possède des candidats de façade mais aucun candidat passant le contrôle intérieur. Les résultats ne transforment pas un décor de porte en promesse d’accès.',
    '',
    '## Exemple à 84 segments',
    '',
    f'`batiment.9375075` conserve ses 84 segments, environ 6,10 m de diamètre, {exemplar["height"]} m de hauteur et deux niveaux estimés. Sa nature est « Indifférenciée », son usage principal « Indifférencié » ; usage secondaire, nombre d’étages et nombre de logements sont absents. Le programme résidentiel est donc une hypothèse inventée.',
    '',
    f'Le modèle passe de zéro ouverture à {exemplar["current"]["entranceCandidates"]} porte et {exemplar["current"]["windows"]} fenêtres ; {exemplar["current"]["renderedOpenings"]} ouvertures sont entièrement rendues dans le budget de 512 quads. La porte est découpée sur plusieurs segments d’origine, avec {exemplar["candidateChecks"][0]["clearanceMeters"]:.3f} m de dégagement à son point intérieur.',
    '',
]
interior = exemplar.get('exemplarInterior', {})
if interior:
    coverage = interior['programCoverage']
    kinds = ', '.join(f['kind'] for f in interior['furniture'])
    omitted = ', '.join(f['kind'] + ' (' + f['reason'] + ')' for f in coverage['furnishingOmissions']) or 'aucune'
    lines += [f'Le plan intérieur reste inventé : mobilier placé `{kinds}` ; fonctions demandées omises : {omitted}. Pièces encloses : {coverage["enclosedRooms"]}, aire enclose {coverage["enclosedRoomArea"]:.2f} m² sur {coverage["footprintArea"]:.2f} m². Le contrôle de navigation échantillonné rapporte {coverage["navigation"]["newUnreachableCells"]} nouvelle cellule inaccessible. Cela ne certifie pas un ameublement résidentiel complet ni une circulation native exhaustive.', '']
lines += ['## Pagination et accès sur grandes emprises', '', '| Objet réel | Niveaux baseline → actuels | Échantillon actuel plafonné à 4 096 | Inventaire complet paginé |', '| --- | ---: | ---: | ---: |']
for row in curves['pagination']:
    lines.append(f'| `{row["sourceId"]}` | {row["baselineLevels"]} → {row["currentLevels"]} | {row["currentPlan4096"]} | {row["completePagedOpenings"]} |')
lines += [
    '',
    'Les tailles de page 31, 128 et 4 096 produisent la même séquence sans doublon ; chaque parcours atteint le dernier slot et examine exactement l’inventaire déclaré. Les 72 approches testées couvrent des arêtes réellement absentes de la sélection baseline sur six contours complexes. Chaque porte retrouvée passe les contrôles métriques de dégagement/hauteur et est présente dans le rendu borné.',
    '',
    '## Portée de la preuve',
    '',
    'Aucun navigateur, déplacement natif, terrain de seuil, collision avec les voisins, droit d’accès public ou plan réellement documenté n’a été certifié ici. Les façades et les intérieurs générés sont fictifs ; seuls les contours, attributs et hauteurs cités proviennent de la source IGN. Le rapport constate une amélioration quantifiée et ses résidus, sans annoncer une fidélité documentaire intégrale.',
    '',
    'Modules figés :',
    '',
    f'- `07_facades.js` : `{curves["moduleHashes"]["currentFacade"]}`',
    f'- `08_city_interiors.js` : `{curves["moduleHashes"]["currentInterior"]}`',
    '',
    'Reproduction : définir `MISTRAL_REPO_ROOT` vers le clone et `MISTRAL_BASELINE_DIR` vers le dossier `coverage-initial`, puis lancer `node curves_compare.cjs --final`, `node attributes_compare.cjs` et `python summarize.py` depuis ce dossier. `MISTRAL_AUDIT_OUTPUT_DIR` permet de choisir un autre dossier de rapports ; par défaut, les rapports sont écrits à côté des scripts. Les valeurs par défaut conservent le premier environnement de QA.',
]
(base / 'SUMMARY.md').write_text('\n'.join(lines) + '\n')
manifest = {str(p.relative_to(base)): {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in sorted(base.glob('*')) if p.is_file() and p.name != 'MANIFEST.json'}
(base / 'MANIFEST.json').write_text(json.dumps({'files': manifest, 'distinctSourceChunks': len(chunk_sources), 'distinctSourceChunkBytes': total_bytes}, indent=2) + '\n')
print(json.dumps({'summary': str(base / 'SUMMARY.md'), 'files': len(manifest), 'distinctSourceChunks': len(chunk_sources)}, ensure_ascii=False))
