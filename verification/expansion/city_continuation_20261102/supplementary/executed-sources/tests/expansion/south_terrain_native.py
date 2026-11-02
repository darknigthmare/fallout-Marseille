#!/usr/bin/env python3
"""Assisted native pilot of the two real south Marseille terrain windows.

Production HTML and HTTP, installed source files, actual terrain reads and
rendered triangles are used. Diagnostic sector selection, render/simulation
freeze and measured collision-free camera placement are declared assistance.
No HTML, responses, terrain, actors or storage are injected or substituted.
"""
from pathlib import Path
from http.server import ThreadingHTTPServer
import argparse
import hashlib
import json
import math
import sys
import threading
import time
import traceback
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[2]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expect-html-sha', required=True)
    parser.add_argument('--expect-index-sha', required=True)
    parser.add_argument('--ready-timeout', type=int, default=300)
    args = parser.parse_args()
    if not args.run:
        print('Prepared only; --run and frozen input hashes are required.')
        return 0
    sys.path.insert(0, str(ROOT/'tools'))
    from rasterio.warp import transform
    from serve_game import GameHandler
    from qa_support import chromium_path
    from playwright.sync_api import sync_playwright
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    report = {'scope': __doc__, 'stage': 'preflight', 'checks': [], 'shots': [], 'placements': [],
              'pinned_inputs': {}, 'page_errors': [], 'console_errors': [], 'request_failures': [],
              'responses': [], 'http_errors': [], 'contexts_created': 0, 'html_injected': False,
              'network_mocked': False, 'storage_mocked': False, 'synthetic_geography': False,
              'assistance': ['Existing native map/sector diagnostic APIs.',
                             'Render and simulation frozen for repeatable terrain observations.',
                             'Camera placed only after finite measured source and actual body-collision checks.'],
              'limitations': ['Two bounded south Marseille rectangles; not whole Marseille or complete monument reconstruction.',
                              'WGS84 nearest-resampled nodes, requested spacing 1 m, not the original native half-metre lattice.',
                              'Rendered triangle samples and screenshots are assisted observations, not a human walk through every place.']}
    browser = context = page = pw = server = None
    origin = None

    def save():
        report.update(total=len(report['checks']), passed=sum(row['ok'] for row in report['checks']),
                      failed=sum(not row['ok'] for row in report['checks']), elapsed_seconds=round(time.monotonic()-started, 3))
        (args.output/'SOUTH_TERRAIN_NATIVE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

    def check(name, ok, detail=None):
        report['checks'].append({'name': name, 'ok': bool(ok), 'detail': detail})
        print(('OK ' if ok else 'FAIL ')+name, flush=True)
        save()
        if not ok:
            raise AssertionError(name)

    def pin(relative):
        raw = (ROOT/relative).read_bytes()
        expected = report['pinned_inputs'].setdefault(relative, sha(raw))
        if expected != sha(raw):
            raise AssertionError('Frozen input changed: '+relative)
        return raw

    def debug(name, *values):
        return page.evaluate('([name,values])=>__MISTRAL_DEBUG[name](...values)', [name, list(values)])

    def ready():
        deadline = time.monotonic()+args.ready_timeout
        while time.monotonic() < deadline:
            info = debug('v047Info')
            if info['phase'] == 'failed':
                raise RuntimeError('Production source staging failed: '+json.dumps(debug('v046Info')))
            if info['tiles'] > 0 and not info['loading'] and not info['anticipating']:
                return info
            page.wait_for_timeout(250)
        raise TimeoutError('Actual map did not reach a stable published state')

    def node(grid, ix, iy):
        s, w, n, e = grid['bbox']
        return [n-(n-s)*iy/(grid['height']-1), w+(e-w)*ix/(grid['width']-1)]

    def camera(grid):
        lat, lon = node(grid, grid['width']//2, grid['height']//2)
        points = [[lat+dz/111320, lon+dx/(111320*math.cos(math.radians(lat)))]
                  for dz in range(-180, 181, 20) for dx in range(-180, 181, 20)]
        candidates = page.evaluate("""points=>points.map(ll=>{const d=__MISTRAL_DEBUG,p=d.v046Project('geo_marseille',...ll),h=d.v046Height(...ll);return{ll,p,h,clear:Number.isFinite(h.height)&&h.height>.3&&!h.missing&&!d.v046Collide(p[0],p[2])};})""", points)
        candidates = sorted((p for p in candidates if p['clear']), key=lambda p: (p['ll'][0]-lat)**2+((p['ll'][1]-lon)*math.cos(math.radians(lat)))**2)
        check('Camera has actual measured terrain and production collision clearance', bool(candidates))
        placed = candidates[0]
        target = debug('v046Project', 'geo_marseille', lat, lon)
        yaw = math.atan2(target[0]-placed['p'][0], -(target[2]-placed['p'][2]))
        debug('v018CaptureAt', [placed['p'][0], placed['h']['height']+1.65, placed['p'][2]], yaw, -.16)
        report['placements'].append(placed)

    try:
        html = pin('index.html')
        report['html_sha256'] = sha(html)
        check('Frozen production HTML is exact', sha(html) == args.expect_html_sha)
        index = json.loads(pin('data/map_pack/enrichment/index.json'))
        check('Frozen installed source index is exact', report['pinned_inputs']['data/map_pack/enrichment/index.json'] == args.expect_index_sha)
        descriptor = index['regions']['geo_marseille']
        bundle_raw = pin(descriptor['path'])
        bundle = json.loads(bundle_raw)
        check('Both real southern grids belong to the receipt-pinned regional bundle', sha(bundle_raw) == descriptor['sha256'] and len(bundle['terrainTiles']) == 2 and sum(g['width']*g['height'] for g in bundle['terrainTiles']) == 384832)
        for relative in ('src/v050/04_source_geometry.js', 'src/v050/04a_city_sources.js', 'src/v050/14_precise_terrain.js',
                         'tools/serve_game.py', 'tools/world_source_bundle.py', 'data/map_pack/enrichment_archives/manifest.json'):
            raw = pin(relative)
            if relative.startswith('src/'):
                check('Actual inline dependency is pinned: '+relative, raw.strip() in html)
        report['script_sha256'] = sha(Path(__file__).read_bytes())
        (args.output/'EXECUTED_SOUTH_TERRAIN_NATIVE.py').write_bytes(Path(__file__).read_bytes())

        class Handler(GameHandler):
            def log_message(self, *_):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        origin = f'http://127.0.0.1:{server.server_port}'
        report['origin'] = origin
        with urllib.request.urlopen(origin+'/__mistral/world-sources', timeout=300) as response:
            audit = json.load(response)
            check('Actual source HTTP audit includes two southern grids', response.headers.get('Cache-Control') == 'no-store' and audit['ok'] and any(row['id'] == 'geo_marseille' and len(row['terrain']) == 2 for row in audit['regions']), audit)
        pw = sync_playwright().start()
        browser = pw.chromium.launch(executable_path=chromium_path(), headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(viewport={'width': 1440, 'height': 900}, service_workers='block')
        report['contexts_created'] += 1
        page = context.new_page()
        page.set_default_timeout(30000)
        page.on('pageerror', lambda error: report['page_errors'].append(str(error)))
        page.on('console', lambda message: report['console_errors'].append({'text': message.text, 'location': message.location}) if message.type == 'error' and not message.text.startswith('Failed to load resource:') else None)
        page.on('requestfailed', lambda request: report['request_failures'].append({'url': request.url, 'failure': request.failure, 'stage': report['stage']}))

        def response_received(response):
            if response.url.startswith(origin+'/'):
                row = {'url': response.url, 'status': response.status, 'from_service_worker': response.from_service_worker}
                report['responses'].append(row)
                if response.status >= 400:
                    report['http_errors'].append(row)

        page.on('response', response_received)
        response = page.goto(origin+'/index.html?skipboot', wait_until='load', timeout=60000)
        check('Native document bytes equal production HTML', response.status == 200 and sha(response.body()) == args.expect_html_sha)
        page.wait_for_function("!document.getElementById('bootScreen').classList.contains('active')", timeout=120000)
        page.wait_for_function("typeof __MISTRAL_DEBUG.v054PreciseTerrainRenderedAt==='function'")
        debug('setRenderPaused', True)
        debug('v047Control', {'auto': False})
        player = debug('getState')['player']
        debug('v018CaptureAt', player['pos'], player['yaw'], player['pitch'])
        debug('v018LoadMacro', 'geo_marseille_commune')
        ready()
        check('Pilot uses actual territory outside the synthetic lab', debug('v046Info')['lab'] is False)
        for number, grid in enumerate(sorted(bundle['terrainTiles'], key=lambda g: g['bbox'][0], reverse=True), 1):
            report['stage'] = 'velodrome' if number == 1 else 'borely'
            lat, lon = node(grid, grid['width']//2, grid['height']//2)
            check('Actual requested sector loads: '+report['stage'], debug('v046Load', lat, lon) is True)
            ready()
            source_info = debug('v050GeographyInfo')
            report.setdefault('source_info', []).append(source_info)
            check('Southern source is really loaded without native-atlas relabeling', 'geo_marseille' in source_info['loadedRegions'] and any(s['id'] == grid['macro'] and s['conversion']['resampled'] and s['conversion']['resampling'] == 'nearest' for s in source_info['terrainSources']), source_info['terrainSources'])
            for ix, iy in ((0, 0), (grid['width']-1, 0), (0, grid['height']-1), (grid['width']-1, grid['height']-1), (grid['width']//2, grid['height']//2)):
                ll = node(grid, ix, iy)
                actual = debug('v046Height', *ll)
                expected = grid['values'][iy*grid['width']+ix]
                check('Physics reads the actual imported southern node '+str([ix, iy]), actual['height'] is not None and abs(actual['height']-expected) < 1e-5 and actual['sources'] == [grid['macro']], {'latlon': ll, 'expected': expected, 'actual': actual})
            mesh = source_info['terrainMesh']
            check('Published local terrain mesh uses the finer source nodes and bounded vertices', any(m['source'] == 'ign_lidar_hd_mnt' and max(m['nodeSpacingMeters']) < 1.01 and m['vertices'] <= 262144 and m['faces'] > 0 for m in mesh), mesh)
            east, north = transform('EPSG:4326', 'EPSG:2154', [lon], [lat])
            rendered = debug('v054PreciseTerrainRenderedAt', east[0], north[0])
            fine = next((draw for draw in rendered if not draw['native'] and not draw['seam'] and draw['id'].startswith('source-terrain:')), None)
            check('Actual rendered triangle at southern centre belongs to imported fine LOD', fine is not None, rendered)
            projected = debug('v046Project', 'geo_marseille', lat, lon)
            origin_e, origin_n = east[0]-projected[0], north[0]+projected[2]
            for position in fine['triangle']:
                vx, vy = transform('EPSG:2154', 'EPSG:4326', [position[0]+origin_e], [origin_n-position[2]])
                s, w, n, e = grid['bbox']
                ix, iy = round((vx[0]-w)/(e-w)*(grid['width']-1)), round((n-vy[0])/(n-s)*(grid['height']-1))
                expected = grid['values'][iy*grid['width']+ix]
                check('Actual rendered triangle vertex retains source height and visual offset', abs(position[1]+.06-expected) < 1e-6, {'position': position, 'gridNode': [ix, iy], 'expected': expected, 'visualOffset': -.06})
            camera(grid)
            output = args.output/(f'{number:02d}_'+report['stage']+'_real_terrain.png')
            page.screenshot(path=str(output))
            report['shots'].append({'file': output.name, 'sha256': sha(output.read_bytes()), 'label': 'Actual assisted eye-level source terrain; no claim of reconstructed stadium/château detail.'})
            save()
        for relative in tuple(report['pinned_inputs']):
            pin(relative)
        check('Frozen runtime and source inputs stay identical throughout native pilot', True, report['pinned_inputs'])
        check('No application JavaScript exception is observed', not report['page_errors'] and not report['console_errors'], {'page': report['page_errors'], 'console': report['console_errors']})
        local = [row for row in report['request_failures'] if row['url'].startswith(origin+'/')]
        metadata = [row for row in local if urllib.parse.urlsplit(row['url']).path == '/__mistral/local-data' and row['failure'] == 'net::ERR_ABORTED']
        report['declared_metadata_cancellations'] = metadata
        report['external_network_observations'] = [row for row in report['request_failures'] if row not in local]
        check('Actual source HTTP succeeds; metadata cancellation remains explicit', not report['http_errors'] and all(row in metadata for row in local), {'httpErrors': report['http_errors'], 'localFailures': local})
        check('One native browser context and zero service worker replacements', report['contexts_created'] == 1 and not any(row['from_service_worker'] for row in report['responses']))
        report['stage'] = 'complete'
        return 0
    except Exception as error:
        report['exception'] = {'message': str(error), 'traceback': traceback.format_exc()}
        if page:
            try:
                output = args.output/'FAILED_NATIVE_STATE.png'
                page.screenshot(path=str(output))
                report['failure_capture'] = {'file': output.name, 'sha256': sha(output.read_bytes())}
            except Exception as capture:
                report['failure_capture_error'] = str(capture)
        print(traceback.format_exc(), flush=True)
        return 1
    finally:
        for name, resource in (('context', context), ('browser', browser)):
            if resource:
                try:
                    resource.close()
                    report[name+'_closed'] = True
                except Exception as error:
                    report[name+'_close_error'] = str(error)
        if pw:
            pw.stop()
            report['playwright_stopped'] = True
        if server:
            server.shutdown()
            server.server_close()
            report['server_closed'] = True
        save()


if __name__ == '__main__':
    raise SystemExit(main())
