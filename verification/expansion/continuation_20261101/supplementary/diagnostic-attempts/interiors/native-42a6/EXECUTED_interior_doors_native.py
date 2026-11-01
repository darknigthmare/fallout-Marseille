#!/usr/bin/env python3
"""Extend the existing real-source interior pilot with physical room doors.

Run with the same explicit frozen HTML/module SHA arguments as
interior_programs_native.py. The original programme, source, collision,
inventory, exit and cold Continue assertions all still run. No scene, source,
storage or door state is mocked. Cameras use declared diagnostic placement;
opening and closing use actual E events and movement uses native KeyW with
stepped production physics. The open-passage walk restarts at the original
clear camera after the closed-door attempt may slide along its jamb.
"""
import math
import sys


def probe_room_door(page, debug, check, shot, group):
    layout = debug('v052CityInteriorLayout')
    info = debug('v050CityInteriorInfo')['roomDoors']
    # Actual small or proof-limited source halls can intentionally contain
    # no enclosed support room. Preserve that programme; do not fabricate
    # a door simply to satisfy a browser fixture assumption.
    if not info['doors']:
        check('Native ' + group + ' keeps its honest open programme without a fabricated physical room door',
              len(info['omissions']) == len(layout['roomDoors'])
              and all(o['reason'] == 'insufficient-pocket-wall' for o in info['omissions']),
              {'rooms': len(layout['rooms']), 'roomOpenings': len(layout['roomDoors']),
               'omissions': info['omissions'], 'programmeCoverage': layout['programCoverage']})
        return {'door': None, 'eligibleDoors': 0, 'scope': 'No eligible generated room opening in this real source programme.',
                'omissions': info['omissions']}
    chosen = None
    attempts = []
    for door in info['doors']:
        for side in (1, -1):
            position = [door['center'][0] + door['normal'][0] * .95 * side,
                        door['elevation'] + 1.65,
                        door['center'][1] + door['normal'][1] * .95 * side]
            opposite = [door['center'][0] - door['normal'][0] * .7 * side,
                        door['elevation'] + 1.65,
                        door['center'][1] - door['normal'][1] * .7 * side]
            if debug('v020Collides', position) or debug('v020Collides', opposite):
                continue
            yaw = math.atan2(door['center'][0] - position[0], -(door['center'][1] - position[2]))
            debug('v018CaptureAt', position, yaw, -.3)
            label = page.locator('#interactLabel').inner_text()
            attempts.append({'door': door['id'], 'side': side, 'label': label, 'position': position})
            if 'fermer' in label.casefold() and 'coulissante' in label.casefold():
                chosen = {'door': door, 'side': side, 'position': position, 'yaw': yaw, 'attempts': attempts}
                break
        if chosen:
            break
    check('Native ' + group + ' contains an accessible invented physical pocket door', chosen is not None, attempts)
    door, side, position, yaw = chosen['door'], chosen['side'], chosen['position'], chosen['yaw']
    identity, inventory = door['id'], debug('getState')['inventory']

    def current():
        return next(d for d in debug('v050CityInteriorInfo')['roomDoors']['doors'] if d['id'] == identity)

    check('Door starts open with retracted leaves, clear passage and disabled leaf solid',
          door['closed'] is False and not door['colliderEnabled'] and door['renderedParts'] == 2)
    page.keyboard.press('e')
    page.wait_for_function("id=>__MISTRAL_DEBUG.v050CityInteriorInfo().roomDoors.doors.find(d=>d.id===id)?.closed===true", arg=identity, timeout=10000)
    center = [door['center'][0], door['elevation'] + 1.65, door['center'][1]]
    check('Actual E closes the rendered twin leaf and enables its real solid',
          current()['colliderEnabled'] and current()['renderedParts'] == 6 and debug('v020Collides', center))
    shot(group + '_room_door_closed', 'Actual native E-closed invented twin pocket door in an acquired IGN footprint.')
    trace = []
    page.keyboard.down('w')
    try:
        for _ in range(14):
            debug('v020Tick', .05, True)
            trace.append(debug('getState')['player']['pos'])
    finally:
        page.keyboard.up('w')
    final = trace[-1]
    signed = ((final[0] - door['center'][0]) * door['normal'][0]
              + (final[2] - door['center'][1]) * door['normal'][1]) * side
    advance = math.hypot(final[0] - position[0], final[2] - position[2])
    check('Native movement advances and stops on the closed leaf without crossing it',
          .01 < advance < .75 and signed > .35 and not debug('v020Collides', final),
          {'from': position, 'trace': trace, 'advanceMeters': advance, 'distanceOnOriginalSide': signed})
    debug('v018CaptureAt', final, yaw, -.3)
    check('Native prompt exposes opening from the actual stopped actor', 'ouvrir' in page.locator('#interactLabel').inner_text().casefold())
    page.keyboard.press('e')
    page.wait_for_function("id=>__MISTRAL_DEBUG.v050CityInteriorInfo().roomDoors.doors.find(d=>d.id===id)?.closed===false", arg=identity, timeout=10000)
    check('Actual E reopens the same leaf, restores its original clear aperture and hides the handles',
          not current()['colliderEnabled'] and current()['renderedParts'] == 2 and not debug('v020Collides', center))
    # Native axis collision may slide the actor sideways against a closed
    # door until its capsule meets the jamb. Restart the open walk from the
    # same declared, collision-free original camera; no scene solid changes.
    debug('v018CaptureAt', position, yaw, -.3)
    chosen['openWalkCameraReset'] = {'position': position, 'reason': 'Restore original centreline after native sliding against the closed jamb.'}
    crossing = []
    page.keyboard.down('w')
    try:
        for _ in range(20):
            debug('v020Tick', .05, True)
            now = debug('getState')['player']['pos']
            crossing.append(now)
            signed = ((now[0] - door['center'][0]) * door['normal'][0]
                      + (now[2] - door['center'][1]) * door['normal'][1]) * side
            if signed < -.65:
                break
    finally:
        page.keyboard.up('w')
    check('Native actor crosses the identical source opening after the leaf retracts',
          signed < -.65 and not debug('v020Collides', crossing[-1]), {'positions': crossing, 'signedSide': signed})
    reverse = yaw + math.pi
    debug('v018CaptureAt', crossing[-1], reverse, -.3)
    check('The opposite side exposes the same physical close interaction', 'fermer' in page.locator('#interactLabel').inner_text().casefold())
    page.keyboard.press('e')
    page.wait_for_function("id=>__MISTRAL_DEBUG.v050CityInteriorInfo().roomDoors.doors.find(d=>d.id===id)?.closed===true", arg=identity, timeout=10000)
    shot(group + '_room_door_inside', 'Actual closed pocket door viewed from the room after native passage and E from the opposite side.')
    check('Door operations retain full layout signature, source outline and finite inventory',
          debug('v052CityInteriorLayout')['signature'] == layout['signature']
          and debug('v052CityInteriorLayout')['rings'] == layout['rings']
          and debug('getState')['inventory'] == inventory)
    key = debug('v018PersistentStatus')['key']
    saved = page.evaluate('key=>JSON.parse(localStorage.getItem(key))', key)
    check('Closed state is written to actual browser storage with the same active source floor',
          saved['v050City']['roomDoorStates'].get(identity) is True
          and saved['v050City']['active']['floor'] == layout['level'])
    return {'door': current(), 'nativeInteraction': 'E from both sides', 'nativeMovement': 'KeyW with v020Tick(.05,true)',
            'cameraPlacement': 'Declared diagnostic placement at measured collision-free floor points',
            'selection': chosen, 'closedTrace': trace, 'openCrossing': crossing}


def main():
    from interior_programs_native import main as programme_main
    if '--room-doors' not in sys.argv:
        sys.argv.append('--room-doors')
    return programme_main()


if __name__ == '__main__':
    raise SystemExit(main())
