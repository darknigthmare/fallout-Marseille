#!/usr/bin/env python3
"""Extend the unchanged native programmes/doors/services/storage pilot with a home.

The existing acquired IGN sector supplies a real residential exterior. All rooms
and domestic equipment are explicitly invented. Entry, paid rest, deposit,
withdrawal and Continue use actual E/DOM and browser storage. Camera framing and
the production grounded tick are declared assistance. No actor, plan, inventory,
save, terrain, HTTP reply or HTML is injected. Requires the base pilot's --run
and coordinated frozen SHA arguments; otherwise it starts no server/browser.
"""
from pathlib import Path
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tests/expansion/fixtures/interior_domestic_source.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probe_domestic(page, debug, check, shot, report, physical_entry,
                   exit_to_street, wait_metadata, native_document):
    fixture = json.loads(FIXTURE.read_text())
    pinned = {str(Path(__file__).relative_to(ROOT)): digest(Path(__file__)),
              str(FIXTURE.relative_to(ROOT)): digest(FIXTURE)}
    originals = {}
    for source_path in sorted({r['sourcePath'] for r in report['programmes']}):
        path = ROOT / source_path
        pinned[source_path] = digest(path)
        for feature in json.loads(path.read_text())['features']:
            if feature['properties'].get('kind') == 'building':
                originals[feature['properties']['cleabs']] = (feature, source_path)
    check('Domestic source fixture equals the originally acquired IGN object and chunk', all(
        digest(ROOT / c['sourcePath']) == c['sourceChunkSha256']
        and originals[c['rawFeature']['properties']['cleabs']][0] == c['rawFeature']
        for c in fixture['cases']))
    preferred = {c['sourceId'] for c in fixture['cases']}
    candidates = []
    for door in debug('v050CityInteriorInfo')['doors']:
        target = debug('v052ArchitectureTarget', door['building'])
        original = originals.get(target['cleabs']) if target else None
        if original and original[0]['properties'].get('usage_1') == 'Résidentiel':
            ring = target['component']['rings'][0]
            area = abs(sum(a[0] * b[1] - b[0] * a[1]
                           for a, b in zip(ring, ring[1:] + ring[:1]))) / 2
            candidates.append((door, target, original, area))
    candidates.sort(key=lambda c: (c[2][0]['properties']['sourceId'] not in preferred,
                                   not 60 <= c[3] <= 250, c[0]['building']))
    attempts, chosen = [], None
    for prior_door, target, original, area in candidates[:8]:
        # Every exterior return rebuilds the portal registry. Reacquire the
        # current interaction for this source identity; do not use a stale ID.
        door = next((d for d in debug('v050CityInteriorInfo')['doors']
                     if d['building'] == prior_door['building']), None)
        entry = physical_entry(door) if door else None
        attempt = {'initialPortal': prior_door, 'portal': door,
                   'sourceId': original[0]['properties']['sourceId'],
                   'footprintArea': area, 'entry': entry}
        attempts.append(attempt)
        if not entry:
            continue
        layout = debug('v052CityInteriorLayout')
        info = debug('v050CityInteriorInfo')
        attempt.update(active=info['active'], services=info['services'],
                       storage=info['storage'], layoutSignature=layout['signature'])
        kinds = {f['kind'] for f in layout['furniture']}
        if layout['layoutVersion'] == 6 and {'sanitary', 'washbasin', 'shower', 'fridge', 'bed'} <= kinds \
                and any(s['kind'] == 'rest' for s in info['services']['stations']) \
                and any(s['furnitureKind'] == 'wardrobe' for s in info['storage']['stores']):
            chosen = {'door': door, 'target': target, 'feature': original[0],
                      'sourcePath': original[1], 'entry': entry, 'layout': layout}
            break
        attempt['omissions'] = layout['programCoverage']
        exit_to_street()
    check('Native E enters a genuinely new acquired IGN dwelling with the domestic programme', chosen is not None, attempts)
    layout, info, state = chosen['layout'], debug('v050CityInteriorInfo'), debug('getState')
    identity, return_point = info['active']['id'], state['v050City']['returnPoint']
    check('Native home retains the exact acquired raw XYZ and metric exterior with invented rooms',
          chosen['target']['rawGeometry'] == chosen['feature']['geometry']
          and layout['rings'] == state['v050City']['active']['building']['rings']
          and layout['theme'] == 'residential' and layout['provenance'] == 'invented'
          and layout['source'] is None
          and layout['programCoverage']['useBasis']['value'] == 'Résidentiel')
    bath = next(r for r in layout['rooms'] if r.get('type') == 'bathroom')
    check('WC, basin and shower occupy one real enclosed invented room with a usable door',
          all(any(f['kind'] == kind and f['roomId'] == bath['id'] for f in layout['furniture'])
              for kind in ('sanitary', 'washbasin', 'shower'))
          and any(d['roomId'] == bath['id'] for d in info['roomDoors']['doors']))
    check('Actual domestic props have rendered parts and production solids within unchanged budgets',
          info['active']['furnishing']['objects'] == info['active']['furnishing']['colliderFurniture']
          and info['active']['furnishing']['renderFurniture'] > len(layout['furniture'])
          and len(layout['furniture']) <= 32 and len(layout['rooms']) <= 10
          and layout['programCoverage']['navigation']['newUnreachableCells'] == 0
          and layout['programCoverage']['navigationChecks'] <= 180)

    def face(position, target):
        yaw = math.atan2(target[0] - position[0], -(target[2] - position[2]))
        pitch = math.atan2(target[1] - position[1], math.hypot(target[0] - position[0], target[2] - position[2]))
        debug('v018CaptureAt', position, yaw, max(-1.3, min(1.3, pitch)))
        debug('v020Tick', .02, True)
        return {'position': position, 'yaw': yaw, 'pitch': pitch}

    shower = next(f for f in layout['furniture'] if f['kind'] == 'shower')
    shower_position = [shower['approach'][0], layout['elevation'] + 1.65, shower['approach'][1]]
    check('The actual shower is solid and its proved actor approach remains clear',
          debug('v020Collides', [shower['pos'][0], layout['elevation'] + 1.65, shower['pos'][1]])
          and not debug('v020Collides', shower_position))
    bathroom_camera = face(shower_position, [shower['pos'][0], layout['elevation'] + .95, shower['pos'][1]])
    shot('home_private_wet_room', 'Real invented private bathroom inside an acquired residential IGN footprint; WC, basin and shower remain unmeasured and the shower is out of service.')
    check('Non-operational shower and fridge add neither a water/food service nor a free reserve',
          not any(s['furnitureKind'] in ('shower', 'fridge') for s in info['services']['stations'])
          and not any(s['furnitureKind'] in ('shower', 'fridge') for s in info['storage']['stores']))

    def face_action(action, aim_api):
        approach, target = action['approach'], action['meshCenter']
        dx, dz = approach[0] - target[0], approach[1] - target[2]
        distance = math.hypot(dx, dz)
        for back in (.6, .3, 0):
            position = [approach[0] + dx / distance * back, layout['elevation'] + 1.65,
                        approach[1] + dz / distance * back]
            if debug('v020Collides', position) or not debug('v020LOS', position, action['target']):
                continue
            camera = face(position, target)
            if debug(aim_api)['selected'] == action['interactionId']:
                return camera
        return None

    bed = next(s for s in info['services']['stations'] if s['kind'] == 'rest')
    bed_camera = face_action(bed, 'v056CityInteriorAimInfo')
    check('Real gaze selects the existing bed service through its rendered mattress', bed_camera is not None)
    before_rest = debug('getState')
    check('The player already carries the original water needed for paid rest', before_rest['inventory'].get('water', 0) >= 1)
    page.keyboard.press('e')
    page.locator('#dialogue').wait_for(state='visible')
    page.locator('#dialogueChoices button').filter(has_text='Se reposer 1 h').click()
    after_rest = debug('getState')
    expected = dict(before_rest['inventory'])
    expected['water'] -= 1
    check('Native domestic rest pays exactly one original water and records one ordinary hour',
          after_rest['inventory'] == expected
          and after_rest['v050City']['services']['restHours'] == before_rest['v050City']['services']['restHours'] + 1
          and abs((after_rest['worldTime'] - before_rest['worldTime']) % 24 - 1) < 1e-7)
    check('Paid rest leaves source geometry, ammunition, experience, caps and finite salvage unchanged',
          debug('v052CityInteriorLayout') == layout and after_rest['ammo'] == before_rest['ammo']
          and after_rest['player']['caps'] == before_rest['player']['caps']
          and after_rest['player']['xp'] == before_rest['player']['xp']
          and after_rest['v026']['containers'] == before_rest['v026']['containers'])
    shot('home_paid_bed', 'Existing invented bed after actual E and paid one-hour rest; no resource injection.')

    store = next(s for s in info['storage']['stores'] if s['furnitureKind'] == 'wardrobe')
    storage_camera = face_action(store, 'v057CityInteriorStorageAimInfo')
    check('The domestic wardrobe has a genuinely selectable local deposit', storage_camera is not None)
    before = debug('getState')
    resource = next((k for k in ('water', 'ration', 'food', 'scrap', 'cloth') if before['inventory'].get(k, 0) > 0), None)
    check('An original carried supply is available for this home without replenishment', resource is not None)
    label = {'water': 'Eau filtrée', 'ration': 'Ration A-03', 'food': 'Vivres', 'scrap': 'Ferraille', 'cloth': 'Tissu'}[resource]

    def select_item():
        for _ in range(4):
            button = page.locator('#dialogueChoices button').filter(has_text=label + ' · sac')
            if button.count():
                button.click()
                return
            page.locator('#dialogueChoices button').filter(has_text='Autres fournitures').click()
        raise AssertionError('Original carried item absent from real paginated deposit dialogue')

    page.keyboard.press('e')
    page.locator('#dialogue').wait_for(state='visible')
    select_item()
    page.get_by_role('button', name='Déposer 1 × ' + label, exact=True).click()
    deposited = debug('getState')
    expected = dict(before['inventory'])
    expected[resource] -= 1
    check('Native home deposit transfers one existing supply into the same empty wardrobe',
          deposited['inventory'] == expected and deposited['v050City']['storage'].get(store['id']) == {resource: 1})
    shot('home_deposited', 'One original carried supply in this dwelling’s local wardrobe; actual native quantity dialogue.')
    page.get_by_role('button', name='Fermer le dépôt', exact=True).click()
    wait_metadata()
    native_document(page.reload(wait_until='load', timeout=60000))
    page.locator('#btnContinue').click()
    page.wait_for_function('id=>__MISTRAL_DEBUG.v050CityInteriorInfo().active?.id===id', arg=identity, timeout=120000)
    restored = debug('getState')
    check('Cold native Continue restores layout6, the exact paid rest and populated wardrobe',
          debug('v052CityInteriorLayout') == layout and debug('v050CityInteriorInfo')['active']['layoutVersion'] == 6
          and restored['inventory'] == deposited['inventory']
          and restored['v050City']['services'] == deposited['v050City']['services']
          and restored['v050City']['storage'] == deposited['v050City']['storage']
          and restored['v050City']['visitLayouts'] == deposited['v050City']['visitLayouts']
          and restored['v050City']['visitEntrances'] == deposited['v050City']['visitEntrances']
          and restored['v050City']['active']['entranceId'] == deposited['v050City']['active']['entranceId'])
    check('Native Continue preserves the source street return point', restored['v050City']['returnPoint'] == return_point)
    check('The continued original cupboard remains physically selectable', face_action(store, 'v057CityInteriorStorageAimInfo') is not None)
    page.keyboard.press('e')
    page.locator('#dialogue').wait_for(state='visible')
    page.get_by_role('button', name='Reprendre des fournitures', exact=True).click()
    select_item()
    page.get_by_role('button', name='Reprendre 1 × ' + label, exact=True).click()
    withdrawn = debug('getState')
    check('Native withdrawal returns exactly the deposited supply without duplicating any stock',
          withdrawn['inventory'] == before['inventory'] and withdrawn['v050City']['storage'] == before['v050City']['storage'])
    page.get_by_role('button', name='Fermer le dépôt', exact=True).click()
    shot('home_continued_wardrobe', 'Actual continued home after returning the same stored supply; no regenerated deposit.')
    exit_to_street()
    exterior = debug('getState')
    check('Native landing exit preserves original street XYZ and the paid-rest inventory',
          math.dist(exterior['player']['pos'], return_point['pos']) < .2
          and exterior['inventory'] == before['inventory'] and exterior['v050City']['active'] is None)
    portal = next((d for d in debug('v050CityInteriorInfo')['doors'] if d['building'] == identity), None)
    check('The original saved home portal remains available after its native exit', portal is not None)
    check('A native E revisit returns to the same layout and saved entrance identity',
          physical_entry(portal) is not None and debug('v052CityInteriorLayout') == layout
          and debug('getState')['v050City']['active']['entranceId'] == deposited['v050City']['active']['entranceId'])
    exit_to_street()
    check('Domestic pilot, fixtures and acquired source chunks stayed unchanged', all(digest(ROOT / p) == h for p, h in pinned.items()))
    return {'scope': __doc__, 'pinned_inputs': pinned, 'source': chosen, 'attempts': attempts,
            'bathroomCamera': bathroom_camera, 'bedCamera': bed_camera, 'storageCamera': storage_camera,
            'afterRest': after_rest, 'afterDeposit': deposited, 'continued': restored,
            'afterWithdrawal': withdrawn, 'limits': 'One acquired residential volume. History saturation, write failure, late document refusal and independent flood-fill remain controlled tests, not native failures.'}


def main():
    # Extend the public probe seam; every original native assertion still runs.
    import interior_storage_native as storage
    from interior_programs_native import main as programme_main
    original = storage.probe_local_storage

    def combined(*args):
        result = original(*args)
        args[4]['domestic'] = probe_domestic(*args)
        return result

    storage.probe_local_storage = combined
    for flag in ('--room-doors', '--furniture-services', '--local-storage'):
        if flag not in sys.argv:
            sys.argv.append(flag)
    return programme_main()


if __name__ == '__main__':
    raise SystemExit(main())
