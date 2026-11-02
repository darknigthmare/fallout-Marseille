"""Run one maintained native pilot against the frozen release, with a real exit."""
from pathlib import Path
import argparse
import json
import shutil
import socket
import subprocess
import sys
import threading

ROOT = Path('/workspace/fallout-Marseille')
BASE = Path(__file__).resolve().parents[1]
PYTHON = Path('/workspace/.cloud-setup/fallout-marseille/venv/bin/python')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('method', choices=['hud', 'fps', 'feedback', 'controller', 'interiors', 'holotapes', 'bestiary', 'landmarks', 'facades', 'legacy'])
    args = parser.parse_args()
    frozen = json.loads((BASE/'FROZEN_INPUTS.json').read_text())
    html = frozen['index.html']
    tasks = {
        'hud': ('hud', 'tests/expansion/fps_hud_native.py', 'FPS_HUD_NATIVE.json', []),
        'fps': ('fps', 'tests/expansion/first_person_native.py', 'FIRST_PERSON_NATIVE.json', ['--run', '--expect-fps-sha', frozen['src/v050/17_first_person.js']]),
        'feedback': ('feedback', 'tests/expansion/fps_feedback_native.py', 'FPS_FEEDBACK_NATIVE.json', []),
        'controller': ('controller', 'tests/expansion/controller_browser.py', 'CONTROLLER_BROWSER.json', []),
        'interiors': ('interiors-native', 'tests/expansion/interior_domestic_native.py', 'INTERIOR_PROGRAMS_NATIVE.json', ['--run', '--expect-interior-sha', frozen['src/v050/08_city_interiors.js'], '--expect-architecture-sha', frozen['data/map_pack/architecture/index.json']]),
        'holotapes': ('holotapes-native', 'tests/expansion/holotapes_native.py', 'HOLOTAPES_NATIVE.json', ['--run', '--expect-holotapes-sha', frozen['src/v050/21_holotapes.js']]),
        'bestiary': ('bestiary', 'tests/expansion/regional_bestiary_native.py', 'BESTIARY_NATIVE.json', ['--run', '--require-iconic', '--require-humanoids', '--expect-bestiary-sha', frozen['src/v050/13_regional_bestiary.js'], '--expect-architecture-sha', frozen['data/map_pack/architecture/index.json']]),
        'landmarks': ('landmarks', 'tests/expansion/landmark_surfaces_native.py', 'LANDMARK_SURFACES_NATIVE.json', ['--run']),
        'facades': ('facades-native', 'tests/expansion/facade_hardware_native.py', 'FACADE_HARDWARE_NATIVE.json', ['--run', '--expect-facade-sha', frozen['src/v050/07_facades.js']]),
        'legacy': ('legacy-final', str(BASE/'legacy-final/run_legacy_audit.py'), 'RUN_AUDIT.json', []),
    }
    directory, script, report, extra = tasks[args.method]
    out = BASE/directory
    out.mkdir(exist_ok=True)
    if args.method == 'interiors':
        for name in ['architecture_native_browser.py', 'interior_programs_native.py', 'interior_doors_native.py', 'interior_storage_native.py', 'interior_services_native.py']:
            shutil.copy2(ROOT/'tests/expansion'/name, out/('EXECUTED_'+name))
        shutil.copy2(ROOT/'tests/expansion/architecture_native_browser.py', out/'architecture_native_browser.imported.py')
    server = thread = None
    try:
        if args.method == 'controller':
            from http.server import ThreadingHTTPServer
            sys.path.insert(0, str(ROOT/'tools'))
            from serve_game import GameHandler
            server = ThreadingHTTPServer(('127.0.0.1', 0), GameHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            extra += ['--url', f'http://127.0.0.1:{server.server_port}/index.html?skipboot=1']
        command = [str(PYTHON), script]
        if args.method != 'legacy':
            flag = '--expected-html-sha256' if args.method == 'controller' else '--expect-html-sha'
            command += ['--output', str(out), flag, html] + extra
        wrapper = [str(PYTHON), str(BASE/'scripts/run_checked.py'), '--repo', str(ROOT), '--output', str(out), '--report', report, '--freeze', str(BASE/'FROZEN_INPUTS.json'), '--'] + command
        return subprocess.run(wrapper, cwd=ROOT).returncode
    finally:
        if server:
            port = server.server_port
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            with socket.socket() as probe:
                code = probe.connect_ex(('127.0.0.1', port))
            (BASE/'CONTROLLER_SERVER.json').write_text(json.dumps({'port': port, 'connectExAfterClose': code, 'closed': code != 0, 'threadAlive': thread.is_alive()}, indent=2)+'\n')


if __name__ == '__main__':
    raise SystemExit(main())
