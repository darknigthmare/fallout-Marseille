#!/usr/bin/env python3
"""Native services extension of the unchanged acquired-source interior/door pilot.

Uses an actual IGN workshop and already placed invented furniture. Entry and
service dialogue use real E and DOM buttons; exact original inventory pays for
ordinary rivets. No source, geometry, ingredient, save or response is injected.
Diagnostic collision-free camera placement and the original simulation freeze
remain declared assistance. A real document reload/Continue checks cold storage.
"""
import math
import sys


def probe_furniture_services(page, debug, check, shot, report, physical_entry,
                             exit_to_street, wait_metadata, native_document):
    prior = next(r for r in report['programmes'] if r['group'] == 'atelier')
    building = prior['initial']['id']
    door = next((d for d in debug('v050CityInteriorInfo')['doors'] if d['building'] == building), None)
    check('The acquired industrial portal remains physically available for a service revisit', door is not None)
    entry = physical_entry(door)
    check('A second native E enters the same acquired industrial volume', entry is not None)
    layout = debug('v052CityInteriorLayout')
    services = debug('v050CityInteriorInfo')['services']
    stations = [s for s in services['stations'] if s['kind'] == 'workshop']
    check('Actual workshop service is bound only to a placed physical workbench', bool(stations)
          and all(any(f['id'] == s['furnitureId'] and f['kind'] == 'workbench'
                      for f in layout['furniture']) for s in stations), services)
    chosen = None
    attempts = []
    for s in stations:
        p = [s['approach'][0], layout['elevation'] + 1.65, s['approach'][1]]
        aim = s['meshCenter']
        yaw = math.atan2(aim[0] - p[0], -(aim[2] - p[2]))
        pitch = math.atan2(aim[1] - p[1], math.hypot(aim[0] - p[0], aim[2] - p[2]))
        if debug('v020Collides', p) or not debug('v020LOS', p, s['target']):
            attempts.append({'station': s['id'], 'residual': 'physical-camera-or-LOS'})
            continue
        debug('v018CaptureAt', p, yaw, pitch)
        # Camera placement does not step physics; reconcile grounded support
        # at the actual floor using the original production tick helper.
        debug('v020Tick', .02, True)
        label = page.locator('#interactLabel').inner_text()
        attempts.append({'station': s['id'], 'position': p, 'yaw': yaw, 'pitch': pitch, 'label': label})
        if 'fabriquer' in label.casefold() and 'établi' in label.casefold():
            chosen = s
            break
    check('A clear actual furniture approach exposes the real workshop E prompt', chosen is not None, attempts)
    check('The service anchor follows an actual rendered broad component within sixteen centimetres',
          .034 < chosen['meshPart']['offsetMeters'] <= .16
          and chosen['meshCenter'][1] - layout['elevation'] >= .45
          and abs(attempts[-1]['pitch']) < 1.3, chosen)
    check('The natural camera ray touches real workbench geometry and selects its service',
          any(h['id'] == chosen['id'] for h in debug('v056CityInteriorAimInfo')['hits'])
          and debug('v056CityInteriorAimInfo')['selected'] == chosen['interactionId'])
    # A separate physical angle must still expose the original finite reserve.
    # No priority, collider, reserve coordinate, inventory or source is changed.
    reserve = next(i for i in debug('v020Stats')['interactables'] if i['id'].startswith('v026:'))
    reserve_key = reserve['id'][len('v026:'):]
    reserve_before = debug('getState')['v026']['containers'][reserve_key]
    reserve_attempts, reserve_camera = [], None
    for angle in (math.pi / 2, -math.pi / 2, 0, math.pi, math.pi / 4, -math.pi / 4, 3 * math.pi / 4, -3 * math.pi / 4):
        p = [reserve['pos'][0] + math.sin(angle) * .6, layout['elevation'] + 1.65,
             reserve['pos'][2] + math.cos(angle) * .6]
        if debug('v020Collides', p) or not debug('v020LOS', p, reserve['pos']):
            continue
        yaw = math.atan2(reserve['pos'][0] - p[0], -(reserve['pos'][2] - p[2]))
        pitch = math.atan2(reserve['pos'][1] - p[1], math.hypot(reserve['pos'][0] - p[0], reserve['pos'][2] - p[2]))
        debug('v018CaptureAt', p, yaw, pitch)
        label = page.locator('#interactLabel').inner_text()
        reserve_attempts.append({'position': p, 'yaw': yaw, 'pitch': pitch, 'label': label,
                                 'aim': debug('v056CityInteriorAimInfo')})
        if 'fouiller' in label.casefold():
            reserve_camera = reserve_attempts[-1]
            break
    check('A separate collision-free physical angle keeps the original finite reserve E prompt',
          reserve_camera is not None, reserve_attempts)
    inventory_before_reserve = debug('getState')['inventory']
    page.keyboard.press('e')
    page.locator('#v026Panel').wait_for(state='visible')
    check('Actual E opens the same original finite reserve without replacing its items',
          debug('getState')['v026']['containers'][reserve_key]['items'] == reserve_before['items'])
    shot('industry_reserve_access', 'Actual E opens the unchanged finite reserve from a different clear angle; no item is taken or added.')
    page.locator('#v026Panel [data-v26="close"]').click()
    check('Closing the real reserve leaves every ordinary inventory quantity unchanged',
          debug('getState')['inventory'] == inventory_before_reserve)
    original = attempts[-1]
    debug('v018CaptureAt', original['position'], original['yaw'], original['pitch'])
    before = debug('getState')
    check('Ordinary existing supplies cover four scrap for the chosen rivet recipe', before['inventory'].get('scrap', 0) >= 4,
          {'scrap': before['inventory'].get('scrap', 0), 'resourceInjection': False})
    page.keyboard.press('e')
    page.wait_for_function("!document.getElementById('dialogue').classList.contains('hidden')", timeout=10000)
    check('Native E opens the real furniture service dialogue without early payment',
          debug('getState')['inventory'] == before['inventory'])
    shot('industry_workshop_service', 'Actual E-opened workshop furniture service, original ingredients and a real acquired IGN source volume.')
    for _ in range(3):
        rivets = page.locator('#dialogueChoices button').filter(has_text='Usiner 12 rivets')
        if rivets.count():
            break
        page.locator('#dialogueChoices button').filter(has_text='Autres préparations').click()
    check('The ordinary rivet recipe is available through real paginated service controls', rivets.count() == 1)
    rivets.click()
    page.wait_for_function("document.getElementById('dialogue').classList.contains('hidden')", timeout=10000)
    after = debug('getState')
    expected = dict(before['inventory'])
    expected['scrap'] -= 4
    check('Exactly four original scrap are consumed without other inventory mutation', after['inventory'] == expected,
          {'before': before['inventory'], 'after': after['inventory']})
    check('Twelve crafted rivets go into the original ammo ledger and preserve experience/caps',
          after['ammo'].get('rivets', 0) == before['ammo'].get('rivets', 0) + 12
          and after['player']['xp'] == before['player']['xp'] and after['player']['caps'] == before['player']['caps'])
    prior_ledger = before['v050City']['services']
    check('One successful service records a bounded per-instance use and ordinary recipe count',
          after['v050City']['services']['crafts'] == prior_ledger['crafts'] + 1
          and after['v050City']['services']['uses'].get(chosen['id'], 0) == prior_ledger['uses'].get(chosen['id'], 0) + 1
          and after['v020']['craftCount'].get('rivets', 0) == before['v020']['craftCount'].get('rivets', 0) + 1)
    check('Service leaves source rings, full layout signature, room doors and furniture unchanged',
          debug('v052CityInteriorLayout') == layout and debug('v050CityInteriorInfo')['services']['stations'] == services['stations'])
    key = debug('v018PersistentStatus')['key']
    saved = page.evaluate('key=>JSON.parse(localStorage.getItem(key))', key)
    check('Actual native storage contains the complete single payment and service use',
          saved['inventory'] == after['inventory'] and saved['ammo'] == after['ammo']
          and saved['v050City']['services'] == after['v050City']['services'])
    shot('industry_workshop_crafted', 'Actual original workbench after paid crafting; no ingredient was created by the pilot.')
    wait_metadata()
    native_document(page.reload(wait_until='load', timeout=60000))
    page.locator('#btnContinue').click()
    page.wait_for_function('id=>__MISTRAL_DEBUG.v050CityInteriorInfo().active?.id===id', arg=building, timeout=120000)
    restored = debug('getState')
    check('Cold native Continue preserves exact spent inventory, ammunition and service ledger',
          restored['inventory'] == after['inventory'] and restored['ammo'] == after['ammo']
          and restored['v050City']['services'] == after['v050City']['services'])
    check('Cold native Continue retains full geometry and exact same functional station identities',
          debug('v052CityInteriorLayout') == layout and debug('v050CityInteriorInfo')['services']['stations'] == services['stations'])
    shot('industry_workshop_service_continue', 'Real cold Continue preserves the physical workbench, source volume and single paid crafting result.')
    exit_to_street()
    check('Native landing exit keeps the paid craft and service telemetry outside the instance',
          debug('getState')['inventory'] == after['inventory']
          and debug('getState')['ammo'] == after['ammo']
          and debug('getState')['v050City']['services'] == after['v050City']['services'])
    return {'station': chosen, 'attempts': attempts, 'entry': entry, 'reserve': {'interaction': reserve,
            'key': reserve_key, 'before': reserve_before, 'camera': reserve_camera, 'attempts': reserve_attempts}, 'before': before,
            'after': after, 'restored': restored,
            'scope': 'Actual workshop craft and Continue. Bed/kitchen actions are separately controlled model tests; no native claim for every service.'}


def main():
    from interior_programs_native import main as programme_main
    for flag in ('--room-doors', '--furniture-services'):
        if flag not in sys.argv:
            sys.argv.append(flag)
    return programme_main()


if __name__ == '__main__':
    raise SystemExit(main())
