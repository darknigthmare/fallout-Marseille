#!/usr/bin/env python3
"""Actual E and dialogue transfers at an existing invented cupboard in an IGN volume.

Extends all the pre-existing programmes, doors and workshop native assertions.
No inventory, save, actor, world, terrain or HTTP reply is injected. Positions,
gaze and a grounded physics step are declared diagnostic assistance. A genuine
document reload, Continue and native DOM withdrawal check the saved stock.
This is not a measurement of the real building's rooms or furniture.
"""
import math
import sys


def probe_local_storage(page, debug, check, shot, report, physical_entry,
                        exit_to_street, wait_metadata, native_document):
    programme = next(r for r in report['programmes'] if r['group'] == 'atelier')
    building = programme['initial']['id']
    door = next((d for d in debug('v050CityInteriorInfo')['doors'] if d['building'] == building), None)
    check('The original acquired industrial portal remains available for a local deposit visit', door is not None)
    entry = physical_entry(door)
    check('Actual E enters the same acquired industrial building for furniture storage', entry is not None)
    layout = debug('v052CityInteriorLayout')
    info = debug('v050CityInteriorInfo')['storage']
    stores = sorted(info['stores'], key=lambda s: (s['furnitureKind'] != 'tool_cabinet', s['id']))
    check('Local deposits belong only to storage furniture actually present in this original layout',
          bool(stores) and all(any(f['id'] == s['furnitureId'] and f['kind'] == s['furnitureKind']
                                   for f in layout['furniture']) for s in stores))
    check('No previous programme or workshop visit has fabricated a stored supply', not info['ledger']
          and all(not s['items'] and s['massKg'] == 0 for s in stores))

    def face(store):
        position = [store['approach'][0], layout['elevation'] + 1.65, store['approach'][1]]
        target = store['meshCenter']
        yaw = math.atan2(target[0] - position[0], -(target[2] - position[2]))
        pitch = math.atan2(target[1] - position[1], math.hypot(target[0] - position[0], target[2] - position[2]))
        if debug('v020Collides', position) or not debug('v020LOS', position, store['target']):
            return None
        debug('v018CaptureAt', position, yaw, pitch)
        debug('v020Tick', .02, True)
        return {'position': position, 'yaw': yaw, 'pitch': pitch,
                'label': page.locator('#interactLabel').inner_text(),
                'aim': debug('v057CityInteriorStorageAimInfo')}

    chosen, camera, attempts = None, None, []
    for store in stores:
        framed = face(store)
        attempts.append({'store': store, 'camera': framed})
        if framed and 'ranger des fournitures' in framed['label'].casefold():
            chosen, camera = store, framed
            break
    check('A collision-free cupboard approach exposes the real local-storage E prompt', chosen is not None, attempts)
    check('The actual player gaze intersects the rendered cupboard and selects its own storage interaction',
          camera['aim']['selected'] == chosen['interactionId']
          and any(h['id'] == chosen['id'] for h in camera['aim']['hits']))
    shot('industry_storage_cupboard', 'Existing invented storage cupboard inside the unchanged measured IGN exterior volume; actual gaze selects its E action.')
    before = debug('getState')
    reserve_before = before['v026']['containers']
    mass_before = debug('v026Mass')['mass']
    resource = next((key for key in ('water', 'ration', 'food', 'scrap', 'cloth')
                     if before['inventory'].get(key, 0) > 0), None)
    check('A real ordinary supply already carried before this probe is available without injection', resource is not None)
    labels = {'water': 'Eau filtrée', 'ration': 'Ration A-03', 'food': 'Vivres', 'scrap': 'Ferraille', 'cloth': 'Tissu'}
    label = labels[resource]
    page.keyboard.press('e')
    page.locator('#dialogue').wait_for(state='visible')
    opened = debug('getState')
    check('Native E opens the empty deposit without changing ordinary quantities or creating stored goods',
          opened['inventory'] == before['inventory'] and opened['v050City']['storage'] == before['v050City']['storage'])
    check('The native dialogue explains local capacity, initially empty stock and protected gear',
          'commence vide' in page.locator('#dialogueLine').inner_text()
          and 'Armes, armures, munitions, capsules' in page.locator('#dialogueLine').inner_text())
    item_button = page.locator('#dialogueChoices button').filter(has_text=label + ' · sac')
    for _ in range(4):
        if item_button.count() or not page.locator('#dialogueChoices button').filter(has_text='Autres fournitures').count():
            break
        page.locator('#dialogueChoices button').filter(has_text='Autres fournitures').click()
    check('Real paginated dialogue controls expose an ordinary supply already in the original bag', item_button.count() == 1)
    item_button.click()
    page.get_by_role('button', name='Déposer 1 × ' + label, exact=True).click()
    after = debug('getState')
    expected_inventory = dict(before['inventory'])
    expected_inventory[resource] -= 1
    check('Actual one-item deposit debits exactly the carried supply and stores one exemplar at this cupboard',
          after['inventory'] == expected_inventory
          and after['v050City']['storage'] == {chosen['id']: {resource: 1}})
    check('Native deposit leaves money, experience, ammo and the original finite salvage ledgers unchanged',
          after['player']['caps'] == before['player']['caps'] and after['player']['xp'] == before['player']['xp']
          and after['ammo'] == before['ammo'] and after['v026']['containers'] == reserve_before)
    stored = next(s for s in debug('v050CityInteriorInfo')['storage']['stores'] if s['id'] == chosen['id'])
    mass_after = debug('v026Mass')['mass']
    check('Storage capacity and carry weight share the existing ordinary item mass',
          0 < stored['massKg'] <= stored['capacityKg']
          and abs((mass_before - mass_after) - stored['massKg']) < 1e-7,
          {'beforeCarry': mass_before, 'afterCarry': mass_after, 'stored': stored['massKg']})
    key = debug('v018PersistentStatus')['key']
    saved = page.evaluate('key=>JSON.parse(localStorage.getItem(key))', key)
    check('Actual browser storage records the exact original inventory payment and one local deposit',
          saved['inventory'] == after['inventory'] and saved['v050City']['storage'] == after['v050City']['storage'])
    check('The deposit modifies no source ring, room, furniture, collision plan or layout signature',
          debug('v052CityInteriorLayout') == layout)
    shot('industry_storage_deposited', 'Actual native quantity dialogue after one original carried supply was deposited, with no generated stock.')
    page.get_by_role('button', name='Fermer le dépôt', exact=True).click()
    wait_metadata()
    native_document(page.reload(wait_until='load', timeout=60000))
    page.locator('#btnContinue').click()
    page.wait_for_function('id=>__MISTRAL_DEBUG.v050CityInteriorInfo().active?.id===id', arg=building, timeout=120000)
    restored = debug('getState')
    check('Cold native Continue preserves exact cupboard stock and its real ordinary inventory debit',
          restored['inventory'] == after['inventory'] and restored['v050City']['storage'] == after['v050City']['storage'])
    check('Cold Continue restores the same source volume, complete layout and storage identities',
          debug('v052CityInteriorLayout') == layout
          and [s['id'] for s in debug('v050CityInteriorInfo')['storage']['stores']] == [s['id'] for s in info['stores']])
    camera_restored = face(chosen)
    check('The continued actual cupboard is physically selectable by the same gaze and E prompt',
          camera_restored is not None and camera_restored['aim']['selected'] == chosen['interactionId'])
    page.keyboard.press('e')
    page.locator('#dialogue').wait_for(state='visible')
    page.get_by_role('button', name='Reprendre des fournitures', exact=True).click()
    page.locator('#dialogueChoices button').filter(has_text=label + ' · sac').click()
    check('The real withdrawal screen reports exactly one exemplar held by this furniture after Continue',
          'ce meuble : 1' in page.locator('#dialogueLine').inner_text())
    shot('industry_storage_continue_withdraw', 'Actual cold Continue and native withdrawal screen show the same one exemplar in this cupboard.')
    page.get_by_role('button', name='Reprendre 1 × ' + label, exact=True).click()
    withdrawn = debug('getState')
    check('Native withdrawal returns exactly the original inventory and frees the empty storage registry entry',
          withdrawn['inventory'] == before['inventory'] and withdrawn['v050City']['storage'] == before['v050City']['storage'])
    check('No second withdrawal button survives after taking the last stored exemplar',
          page.get_by_role('button', name='Reprendre 1 × ' + label, exact=True).count() == 0
          and 'ce meuble : 0' in page.locator('#dialogueLine').inner_text())
    saved_withdrawal = page.evaluate('key=>JSON.parse(localStorage.getItem(key))', key)
    check('Real browser storage retains the completed withdrawal with no residual duplicated goods',
          saved_withdrawal['inventory'] == before['inventory'] and saved_withdrawal['v050City']['storage'] == before['v050City']['storage'])
    page.get_by_role('button', name='Fermer le dépôt', exact=True).click()
    check('Salvage reserves and geometry remain identical after the whole native deposit and withdrawal cycle',
          debug('getState')['v026']['containers'] == reserve_before and debug('v052CityInteriorLayout') == layout)
    shot('industry_storage_emptied', 'Actual cupboard after returning the stored supply; no deposit remains in the save.')
    exit_to_street()
    exterior = debug('getState')
    check('Native landing exit preserves returned supplies and no remote storage entry',
          exterior['inventory'] == before['inventory'] and exterior['v050City']['storage'] == before['v050City']['storage'])
    return {'scope': __doc__, 'entry': entry, 'chosen': chosen, 'camera': camera, 'attempts': attempts,
            'resource': resource, 'quantity': 1, 'before': before, 'after_deposit': after,
            'continued': restored, 'after_withdrawal': withdrawn,
            'scope_limits': 'One actual IGN industrial volume and one originally placed cupboard; floor/building isolation, full capacity and write-failure rollback are controlled models, not claimed native failures.'}


def main():
    from interior_programs_native import main as programme_main
    for flag in ('--room-doors', '--furniture-services', '--local-storage'):
        if flag not in sys.argv:
            sys.argv.append(flag)
    return programme_main()


if __name__ == '__main__':
    raise SystemExit(main())
