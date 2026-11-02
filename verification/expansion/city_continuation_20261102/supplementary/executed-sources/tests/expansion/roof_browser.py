#!/usr/bin/env python3
"""Execute production roof construction, narrow phase and physics in Chromium.

The declared roof parameters are test fixtures. This validates engine behavior;
it does not certify a real building survey or infer unknown BD TOPO roof shapes.
"""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from qa_support import chromium_path
from playwright.sync_api import sync_playwright


def main():
    script = subprocess.check_output(['node', str(ROOT / 'tests/expansion/roof_harness.cjs'), '--script'], text=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=chromium_path(), headless=True,
                                     args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = browser.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content('<title>Explicit source roof collision fixture</title>')
        page.add_script_tag(content=script)
        checks = page.evaluate('runRoofProof()')
        browser.close()
    report = {'suite': 'roof_browser', 'passed': sum(checks.values()),
              'failed': sum(not ok for ok in checks.values()), 'checks': checks, 'errors': errors,
              'scope': 'Native Chromium executes production roof construction, tessellation, ray/LOS, body collision and player integrator against declared source fixtures.'}
    print(json.dumps(report, indent=2))
    return bool(report['failed'] or errors)


if __name__ == '__main__':
    raise SystemExit(main())
