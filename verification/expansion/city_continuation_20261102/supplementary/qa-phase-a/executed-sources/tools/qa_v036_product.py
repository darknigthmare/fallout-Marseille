#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
from qa_support import chromium_path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'verification';H=(R/'JOUER_FALLOUT_MISTRAL_v0.36.html').read_text();rows=[];errs=[]
def ck(n,c,d=None):rows.append({'name':n,'ok':bool(c),'detail':d});print(('OK ' if c else 'FAIL ')+n,flush=True)
manifest=json.loads((R/'manifest.webmanifest').read_text());sources=json.loads((O/'SOURCES_OFFICIELLES_V036.json').read_text());audit=json.loads((O/'AUDIT_CARTE_REELLE_V036.json').read_text());plan=json.loads((R/'data/map_pack/manifest_v036.json').read_text());pkg=json.loads((R/'package.json').read_text())
ck('Webmanifest v0.36',manifest['name'].endswith('Territoire réel') and manifest['start_url']=='./index.html',manifest)
ck('Service worker v0.36',"fallout-mistral-v036-1" in (R/'sw.js').read_text() and 'JOUER_FALLOUT_MISTRAL_v0.36.html' in (R/'sw.js').read_text())
ck('Installateurs directs et relais présents',all((R/x).exists() for x in ['INSTALLER_CARTE_REELLE_WINDOWS.bat','INSTALLER_CARTE_REELLE_RELAIS_WINDOWS.bat','INSTALLER_CARTE_REELLE_LINUX_MAC.sh']))
ck('Auditeurs présents',all((R/x).exists() for x in ['AUDITER_CARTE_REELLE_WINDOWS.bat','AUDITER_CARTE_REELLE_LINUX_MAC.sh','tools/audit_real_map_v036.py']))
ck('Relais officiel vérifié côté serveur',sources['truth']['onlineVectorServiceVerified'] and all(x['directStatus']==200 for x in sources['samples'][:2]),sources)
ck('Relief non revendiqué',sources['truth']['officialNumericTerrainInstalled'] is False and plan['licenses']['terrain'].endswith('not included in this build'))
ck('Audit local ne ment pas',audit['valid']==0 and audit['missing']==5884 and audit['truth']['complete'] is False,audit)
edge=(R/'tools/edge/fallout-mistral-map-v036/index.ts').read_text();ck('Relais borné aux zooms/emprise',"zoom:14" in edge and "zoom:16" in edge and "outside" in edge and "5.755" in edge)
ck('Scripts npm cartographiques',all(k in pkg['scripts'] for k in ['map:manifest','map:audit']),pkg['scripts'])
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path=chromium_path(),args=['--no-sandbox','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1280,'height':800});p.on('pageerror',lambda e:errs.append(str(e)))
 p.set_content(H,wait_until='load');p.wait_for_timeout(3500)
 ck('Menu annonce v0.36 Territoire réel','v0.36.0' in p.locator('#menuScreen .menu-version').inner_text() and 'TERRITOIRE RÉEL' in p.locator('#menuScreen .menu-version').inner_text())
 p.click('#btnCredits');txt=p.locator('#creditsScreen').inner_text();ck('Crédits et licences à jour','0.36.0 · Territoire réel' in txt and 'OpenStreetMap' in txt and 'Cadastre Etalab' in txt,txt[:800]);b.close()
rep={'version':'0.36.0','html_sha256':hashlib.sha256(H.encode()).hexdigest(),'passed':sum(x['ok'] for x in rows),'failed':sum(not x['ok'] for x in rows),'total':len(rows),'errors':errs,'checks':rows};(O/'QA_V036_PRODUCT.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'passed':rep['passed'],'failed':rep['failed'],'total':rep['total'],'errors':errs},ensure_ascii=False));raise SystemExit(bool(rep['failed'] or errs))
