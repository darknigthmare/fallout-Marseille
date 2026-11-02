#!/usr/bin/env python3
"""External execution receipt for the unchanged maintained service-worker test."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, signal, socket, subprocess, sys
from urllib.parse import urlsplit

ROOT = Path('/workspace/fallout-Marseille')
OUT = Path(__file__).resolve().parent
NODE = '/opt/codex/runtimes/codex-primary-runtime/dependencies/node/bin/node'
MODULE = '/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages/playwright/driver/package'
HTML_SHA = '4581c0c29ce5c74da3aba7430227fba844aed1eb40f1b1fc4d7965c7a6600d78'
SOURCES = ['tests/expansion/service_worker_delivery.cjs', 'index.html', 'JOUER_FALLOUT_MISTRAL_v0.50.html', 'sw.js', 'manifest.webmanifest', 'icons/mistral-192.png', 'icons/mistral-512.png']

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def snapshot(copy=False):
    result = {}
    for name in SOURCES:
        source = ROOT / name
        item = {'sha256': digest(source), 'bytes': source.stat().st_size}
        if copy:
            # Core icon bytes are archived as .raw, never presented as screenshots.
            archive = OUT / 'inputs-before' / (name + '.raw' if name.endswith('.png') else name)
            archive.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, archive)
            item.update(copy=str(archive), copySha256=digest(archive))
        result[name] = item
    return result

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / 'EXECUTION.json').exists() or (OUT / 'SERVICE_WORKER.json').exists():
        raise RuntimeError('Execution output already exists; previous evidence must be preserved.')
    argv = [NODE, 'tests/expansion/service_worker_delivery.cjs']
    overrides = {'MISTRAL_QA_OUTPUT': str(OUT), 'MISTRAL_PLAYWRIGHT_MODULE': MODULE, 'CHROMIUM_PATH': '/usr/bin/chromium'}
    receipt = {
        'scope': 'One execution of the unchanged maintained Node/Chromium service-worker lifecycle test. Old cached HTML is an explicitly synthetic fixture, not a historical production build.',
        'startedAtUtc': now(), 'workingDirectory': str(ROOT), 'argv': argv,
        'envOverridesNonSecret': overrides, 'inheritedEnvironmentValuesRecorded': False,
        'wrapperPath': str(Path(__file__).resolve()), 'wrapperSha256': digest(Path(__file__)),
        'expectedHtmlSha256': HTML_SHA, 'before': snapshot(copy=True),
        'supplementOutsideExistingCheckAndScreenshotTotals': True,
        'priorAutomatedChecksTotalNotIncremented': 3318,
        'priorScreenshotTotalNotIncremented': 100,
        'screenshotsRequested': False, 'expectedNativeChecks': 6,
        'nodeVersion': subprocess.check_output([NODE, '--version'], text=True).strip(),
        'playwrightPackageVersion': json.loads((Path(MODULE) / 'package.json').read_text())['version'],
        'pythonExecutable': sys.executable,
    }
    if receipt['before']['index.html']['sha256'] != HTML_SHA or receipt['before']['JOUER_FALLOUT_MISTRAL_v0.50.html']['sha256'] != HTML_SHA:
        raise RuntimeError('Production HTML differs from the assigned final45 freeze.')
    write_json(OUT / 'BEFORE_EXECUTION.json', receipt)
    env = os.environ.copy()
    env.update(overrides)
    log_path = OUT / 'EXECUTION.log'
    process = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
    receipt['nodePid'] = process.pid
    receipt['timeoutSeconds'] = 180
    print(json.dumps({'event': 'started', 'nodePid': process.pid, 'argv': argv, 'output': str(OUT)}), flush=True)
    timed_out = False
    try:
        stdout, _ = process.communicate(timeout=180)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, _ = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, _ = process.communicate()
    log_path.write_text(stdout)
    print(stdout, end='', flush=True)
    receipt.update(finishedAtUtc=now(), exitCode=process.returncode, timedOut=timed_out, nodeProcessExited=process.poll() is not None, after=snapshot(), logPath=str(log_path), logSha256=digest(log_path))
    receipt['sourceInputsUnchanged'] = all(receipt['before'][name]['sha256'] == receipt['after'][name]['sha256'] for name in SOURCES)
    receipt['preExecutionCopiesExact'] = all(item['sha256'] == item['copySha256'] for item in receipt['before'].values())
    report_path = OUT / 'SERVICE_WORKER.json'
    cleanup = {'method': 'Read origin from cached response URL in the native report; attempt a TCP connection after the child has exited.', 'nodeProcessExited': receipt['nodeProcessExited'], 'serverPortObservable': False}
    if report_path.exists():
        report = json.loads(report_path.read_text())
        receipt.update(reportPath=str(report_path), reportSha256=digest(report_path), existingNativePassed=report.get('passed'), existingNativeFailed=report.get('failed'), browserVersion=report.get('browser'))
        urls = [entry['url'] for entries in report.get('cacheSnapshot', {}).values() for entry in entries if 'url' in entry]
        parsed = next((urlsplit(url) for url in urls if urlsplit(url).hostname == '127.0.0.1' and urlsplit(url).port), None)
        if parsed:
            with socket.socket() as conn:
                conn.settimeout(2)
                result = conn.connect_ex(('127.0.0.1', parsed.port))
            cleanup.update(serverPortObservable=True, host='127.0.0.1', port=parsed.port, tcpConnectEx=result, serverPortClosed=result == 111, interpretation='ECONNREFUSED after Node exit' if result == 111 else 'See TCP result; no closure claim')
    receipt['pngScreenshotFiles'] = [str(p.relative_to(OUT)) for p in OUT.rglob('*.png')]
    receipt['pngScreenshotCount'] = len(receipt['pngScreenshotFiles'])
    write_json(OUT / 'SERVER_CLOSED.json', cleanup)
    receipt.update(cleanupReceiptPath=str(OUT / 'SERVER_CLOSED.json'), cleanupReceiptSha256=digest(OUT / 'SERVER_CLOSED.json'))
    write_json(OUT / 'EXECUTION.json', receipt)
    print(json.dumps({'event': 'finished', 'exitCode': process.returncode, 'nativePassed': receipt.get('existingNativePassed'), 'nativeFailed': receipt.get('existingNativeFailed'), 'sourceInputsUnchanged': receipt['sourceInputsUnchanged'], 'pngScreenshotCount': receipt['pngScreenshotCount'], 'serverPortClosed': cleanup.get('serverPortClosed'), 'executionSha256': digest(OUT / 'EXECUTION.json')}), flush=True)
    return process.returncode if process.returncode >= 0 else 128 - process.returncode

if __name__ == '__main__':
    sys.exit(main())
